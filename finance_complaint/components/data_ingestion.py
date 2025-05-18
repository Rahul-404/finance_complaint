from collections import namedtuple
from finance_complaint.entity.artifact_entity import DataIngestionArtifact
from finance_complaint.entity.metadata_entity import DataIngestionMetadata
from finance_complaint.entity.config_entity import DataIngestionConfig
from finance_complaint.exception import FinanceException
from finance_complaint.logger import logging as logger
from datetime import datetime
from typing import List
import pandas as pd
import requests
import os, sys
import json
import uuid
import time
import re

from finance_complaint.config.spark_manager import spark_session

DownloadUrl = namedtuple("DownloadUrl", ["url", "file_path", "n_retry"])

class DataIngestion:
    # used to download data in chunks.
    def __init__(self, data_ingestion_config: DataIngestionConfig, n_retry: int = 5,):
        """ 
        data_ingestion_config: Data Ingestion config
        n_retry: Number of retry filed should be tried to download in case of failuer encountered
        n_month_interval: n month data will be downloaded 
        """
        try:
            logger.info(f"{'>>'*20} Strting data ingestion.{'<<'*20}")
            self.data_ingestion_config = data_ingestion_config
            self.failed_download_urls: List[DownloadUrl] = []
            self.n_retry = n_retry
        except Exception as e:
            raise FinanceException(e, sys)
        
    def get_required_interval(self):
        '''
        if date gap is too huge, i.e 2011 to 2022 size can be huge

        so instead of downloading entire data at once
        we can download yearly data like
        2011 - 2012
        2012 - 2013
        . 
        . 
        2021 - 2022
        following is the function
        '''
        # reading dates from config start and end date in yy-mm-dd format 
        start_date = datetime.strptime(self.data_ingestion_config.from_date, "%Y-%m-%d")
        end_date = datetime.strptime(self.data_ingestion_config.to_date, "%Y-%m-%d")
        # checing number of days between end and start date
        n_diff_days = (end_date - start_date).days
        freq = None
        # if diff is more than 365
        if n_diff_days > 365:
            freq = "YE"
        # else if diff is more than 30 
        elif n_diff_days > 30:
            freq = "ME"
        # else if diff is more than 7
        elif n_diff_days > 7:
            freq = "W"
        logger.debug(f"{n_diff_days} hance freq: {freq}")

        # still if frequency is None mean less than 7
        if freq is None:
            intervals = pd.date_range(
                start = self.data_ingestion_config.from_date,
                end = self.data_ingestion_config.to_date,
                periods=2
            ).astype('str').tolist()
        else:
            intervals = pd.date_range(
                start=self.data_ingestion_config.from_date,
                end=self.data_ingestion_config.to_date,
                freq=freq
            ).astype('str').tolist()
        logger.debug(f"Prepared Interval: {intervals}")

        # check if to_date is not in intervals ? -> then add it to intervals list
        if self.data_ingestion_config.to_date not in intervals:
            intervals.append(self.data_ingestion_config.to_date)

        return intervals
    
    def download_files(self, n_day_interval_url: int = None):
        """ 
        n_month_interval_url: if not provided then information default value will be set
        =================================================================================
        returns: List of DownloadUrl = namestuple("DownloadUrl", ["url", "file_path", "n_retry"])
        """
        try:
            # here will call function to get interval list
            required_interval = self.get_required_interval()
            logger.info("Started downloading files")

            # iterate over the interval
            for index in range(1, len(required_interval)):
                # fetching from_date and to_date
                from_date, to_date = required_interval[index - 1], required_interval[index]
                logger.debug(f"Generating data download url between {from_date} and {to_date}")

                # getting data source url
                datasource_url: str = self.data_ingestion_config.datasource_url
                # replacing the exisiting values with new from_date and to_date
                url = datasource_url.replace("<todate>", to_date).replace("<fromdate>", from_date)

                logger.debug(f"Url: {url}")

                # creating json file name
                file_name = f"{self.data_ingestion_config.file_name}_{from_date}_{to_date}.json"
                # getting complete path to json file
                file_path = os.path.join(self.data_ingestion_config.download_dir, file_name)

                # download url
                download_url = DownloadUrl(url=url, file_path=file_path, n_retry=self.n_retry)

                # this function downloads data from passed url
                self.download_data(download_url=download_url)

            logger.info(f"File download completed")
        except Exception as e:  
            raise FinanceException(e, sys)
        
    def download_data(self, download_url: DownloadUrl):
        """ 
        this function responsible to download data and store it to data ingestion directory
        """
        try:
            logger.info(f"Starting download operation: {download_url}")
            download_dir = os.path.dirname(download_url.file_path)

            # creating download directory
            os.makedirs(download_dir, exist_ok=True)

            # downloading data: by requesting to the url
            data = requests.get(download_url.url, params={'User-agent': f'your bot {uuid.uuid4()}'})

            try:
                logger.info(f"Started writing downloaded data into json file: {download_url.file_path}")
                # saving downloaded data into hard disk
                with open(download_url.file_path, "w") as file_obj:
                    finance_complaint_data = list(map(lambda x: x["_source"], filter(lambda x: "_source" in x.keys(), json.loads(data.content))))
                    json.dump(finance_complaint_data, file_obj)
                logger.info(f"Download data has been written into file: {download_url.file_path}")
            except Exception as e:
                logger.info("Failed to download hance retry again.")
                # removing file failed file exists
                if os.path.exists(download_url.file_path):
                    os.remove(download_url.file_path)
                self.retry_download_data(data, download_url=download_url)
            
        except Exception as e:
            logger.info(e)
            raise FinanceException(e, sys)
        
    def retry_download_data(self, data, download_url: DownloadUrl):
        """ 
        This function helps to avoid failure as it help to download failed file again

        data: failed response
        download_url: DownloadUrl
        """
        try:
            # if retry still possible try else return the response
            if download_url.n_retry == 0:
                self.failed_download_urls.append(download_url.url)
                logger.info(f"Unable to download file: {download_url.url}")
                return
            
            # if in case it is not zero, to handle throatling requestion and can be solve if we wait for some second.
            content = data.content.decode("utf-8")
            wait_second = re.findall(r'\d+', content)

            if len(wait_second) > 0:
                time.sleep(int(wait_second[0]) + 2)

            # Writing response to understand why request was failed
            failed_file_path = os.path.join(self.data_ingestion_config.failed_dir,
                                            os.path.basename(download_url.file_path))
            os.makedirs(self.data_ingestion_config.failed_dir, exist_ok=True)
            with open(failed_file_path, "wb") as file_obj:
                file_obj.write(data.content)

            # calling download function again to retry
            download_url = DownloadUrl(download_url.url, file_path=download_url.file_path,
                                       n_retry=download_url.n_retry - 1)
            self.download_data(download_url=download_url)
        except Exception as e:
            raise FinanceException(e, sys)
        
    def convert_files_to_parquet(self,) -> str:
        """ 
        downloaded files will be converted and merged into single parquet file
        json_data_dir: downloaded json file directory
        data_dir: convrted and combine file will be generated in data_dir
        output_file_name: output file name
        ========================================================================
        returns output_file_path
        """
        try:
            # json file download directory
            json_data_dir = self.data_ingestion_config.download_dir
            # feature store directoy 
            data_dir = self.data_ingestion_config.feature_store_dir
            # aftre merging file will get a paruqet file, so its parquet file name
            output_file_name = self.data_ingestion_config.file_name
            #  creating features store folder
            os.makedirs(data_dir, exist_ok=True)
            file_path = os.path.join(data_dir, f"{output_file_name}")
            logger.info(f"Parquet file will be created at: {file_path}")
            # check 1st do we have json directory or not?
            if not os.path.exists(json_data_dir):
                return file_path
            
            # after listing all the files will iterate over it
            for file_name in os.listdir(json_data_dir):
                json_data_path = os.path.join(json_data_dir, file_name)
                logger.debug(f"Converting {json_data_path} into parquet format at {file_path}")

                df = spark_session.read.json(json_data_path)
                if df.count() > 0:
                    df.write.mode('append').parquet(file_path)
            return file_path
        except Exception as e:
            raise FinanceException(e, sys)
    
    def write_metadata(self, file_path: str) -> None:
        """ 
        This function help us to update metadata information
        so that we can avoid redundant download and merging.
        """
        try:
            logger.info("Write metadata into into metadata file")
            metadata_info = DataIngestionMetadata(
                metadata_file_path=self.data_ingestion_config.metadata_file_path,
            )

            metadata_info.write_metadata_info(
                from_date=self.data_ingestion_config.from_date,
                to_date=self.data_ingestion_config.to_date,
                data_file_path=file_path
            )
            logger.info(f"Metadata had been written.")
        except Exception as e:
            raise FinanceException(e, sys)
        
    def initiate_data_ingestion(self) -> DataIngestionArtifact:
        """ 
        this function responsible to initiate data ingestion
        """
        try:
            logger.info(f"Started downloading json file")

            # check if we downloading new data or not
            if self.data_ingestion_config.from_date != self.data_ingestion_config.to_date:
                self.download_files()

            # if json data exists start converting to parquet and update the metadata info
            if os.path.exists(self.data_ingestion_config.download_dir):
                logger.info(f"Converting and combining downloaded json into parquet file.")
                file_path = self.convert_files_to_parquet()
                self.write_metadata(file_path=file_path)

            # path to new parquet file
            feature_store_file_path = os.path.join(self.data_ingestion_config.feature_store_dir,
                                                   self.data_ingestion_config.file_name)
            
            # store it to artifact
            artifact = DataIngestionArtifact(
                feature_store_file_path=feature_store_file_path,
                download_dir=self.data_ingestion_config.download_dir,
                metadata_file_path=self.data_ingestion_config.metadata_file_path,
            )
            logger.info(f"Data ingestion artifact: {artifact}")
            logger.info(f"{'--'*20} Completed data ingestion.{'--'*20}\n")
            return artifact
        except Exception as e:
            raise FinanceException(e, sys)