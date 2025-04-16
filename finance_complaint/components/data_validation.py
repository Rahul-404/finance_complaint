import os, sys
from collections import namedtuple
from typing import List, Dict

from pyspark.sql import DataFrame
from pyspark.sql.functions import col

from finance_complaint.config.spark_manager import spark_session
from finance_complaint.entity.artifact_entity import DataIngestionArtifact
from finance_complaint.entity.config_entity import DataValidationConfig
from finance_complaint.entity.schema import FinanceDataSchema
from finance_complaint.exception import FinanceException
from finance_complaint.logger import logging as logger

from pyspark.sql.functions import lit
from finance_complaint.entity.artifact_entity import DataValidationArtifact

ERROR_MESSAGE = "error_msg"
MissingReport = namedtuple("MissingReport",
                           ["total_row", "missing_row", "missing_percentage"])


class DataValidation():
    def __init__(self,
                data_validation_config: DataValidationConfig,
                data_ingestion_artifact: DataIngestionArtifact,
                schema=FinanceDataSchema()
                ):
        try:
            # super().__init__()
            self.data_ingestion_artifact: DataIngestionArtifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config
            self.schema = schema       
        except Exception as e:
            raise FinanceException(e, sys)
        
    def read_data(self) -> DataFrame:
        """ 
        function to read a dataframe
        """
        try:
            dataframe: DataFrame = spark_session.read.parquet(
                self.data_ingestion_artifact.feature_store_file_path
            ).limit(10000) # only reading 10 thiusands of records , when go for deployment will remove it
            logger.info(f"Data frame is created using file: {self.data_ingestion_artifact.feature_store_file_path}")
            logger.info(f"Number of row: {dataframe.count()} and column: {len(dataframe.columns)}")
            return dataframe
        except Exception as e:
            raise FinanceException(e, sys)
        
    @staticmethod
    def get_missing_report(dataframe: DataFrame, ) -> Dict[str, MissingReport]:
        """ 
        this function is responsible for creating report of missing data for each columns
        """
        try:
            missing_report: Dict[str: MissingReport] = Dict()
            logger.info(f"Prepraing missing reports for each column")
            number_of_row = dataframe.count()

            for column in dataframe.columns:
                missing_row = dataframe.filter(f"{column} is null").count()
                missing_percentage = (missing_row * 100) / number_of_row
                missing_report[column] = MissingReport(
                    total_row=number_of_row,
                    missing_row=missing_row,
                    missing_percentage=missing_percentage
                )
            logger.info(f"Missing report prepared: {missing_report}")
            return missing_report
        except Exception as e:
            raise FinanceException(e, sys)
        
    def get_unwanted_and_high_missing_value_columns(self, dataframe: DataFrame, threshold: float = 0.2) -> List[str]:
        """ 
        this function removes columns with threshold missing values
        """
        try:
            missing_report: Dict[str, MissingReport] = self.get_missing_report(dataframe=dataframe)

            unwanted_column: List[str] = self.schema.unwanted_columns
            for column in missing_report:
                if missing_report[column].missing_percentage > (threshold * 100):
                    unwanted_column.append(column)
                    logger.info(f"Missing report {column}: [{missing_report[column]}]")
            unwanted_column = list(set(unwanted_column))

            return unwanted_column
        except Exception as e:
            raise FinanceException(e, sys)
        
    def drop_unwanted_columns(self, dataframe: DataFrame) -> DataFrame:
        """ 
        this function will drop the unwanted columns from the dataframe
        """
        try:
            # get all unwanted columns to drop
            unwanted_columns: List = self.get_unwanted_and_high_missing_value_columns(dataframe=dataframe,)
            # log those columns
            logger.info(f"Droppping fetaures: {','.join(unwanted_columns)}")
            # after dropping columns get the dataframe
            unwanted_dataframe: DataFrame = dataframe.select(unwanted_columns)
            # adding one new column `ERROR_MESSAGE and for each rwo there is a value given in lit("message_")` to move 
            # to rejected directory
            unwanted_dataframe = unwanted_dataframe.withColumn(ERROR_MESSAGE, lit("Contains many missing values"))

            # preparing rejection directory
            rejected_dir = os.path.join(self.data_validation_config.rejected_data_dir, "missing_data")
            # creating directory in memory
            os.makedirs(rejected_dir, exist_ok=True)
            # prepare the file path
            file_path = os.path.join(rejected_dir, self.data_validation_config.file_name)

            # logging the file path
            logger.info(f"writing dropped column into file: [{file_path}]")
            # then write the content to file
            unwanted_dataframe.write.mode('append').parquet(file_path)
            # now from original data frame will drop the unwanted columns
            dataframe: DataFrame = dataframe.drop(*unwanted_columns)
            # logging the remaining columns of original dataframe
            logger.info(f"Remaining columns of dataframe: [{dataframe.columns}]")
            # return the dataframe which will have required columns
            return dataframe
        except Exception as e:
            raise FinanceException(e, sys)
        
    def is_required_columns_exist(self, dataframe: DataFrame):
        """ 
        this function checks if dataframe have required columns or not
        """
        try:
            # check for required columns
            columns = list(filter(lambda x: x in self.schema.required_columns, dataframe.columns))

            # then check for length
            if len(columns) != len(self.schema.required_columns):
                raise Exception(f"Required column missing\n\
                                Expected columns: {self.schema.required_columns}\n\
                                Found columns: {columns}\
                                    ")
        except Exception as e:
            raise FinanceException(e, sys)
        
    def initiate_data_validation(self) -> DataValidationArtifact:
        """ 
        this function resonable to perform data validation
        """
        try:
            logger.info(f"initiating data processing.")
            # 1st read the data
            dataframe: DataFrame = self.read_data()

            logger.info(f"Dropping unwanted columns")
            # 2nd drop unwanted oclumns
            dataframe: DataFrame = self.drop_unwanted_columns(dataframe=dataframe)

            # validation to ensure that all required column available
            self.is_required_columns_exist(dataframe=dataframe)
            # logging log
            logger.info("Saving preprocessed data.")
            # printing number of rows and columns
            print(f"Row: [{dataframe.count()}] Column: [{len(dataframe.columns)}]")
            # printing expected columns and present columns
            print(f"Expected Column: {self.required_columns}\nPresent Columns: {dataframe.columns}")
            # creating directory for accepted data
            os.makedirs(self.data_validation_config.accepted_data_dir, exist_ok=True)
            # preparing artifact path
            accepted_file_path = os.path.join(self.data_validation_config.accepted_data_dir,
                                              self.data_validation_config.file_name)
            
            # saving dataframe in parquet format to accepted folder
            dataframe.write.parquet(accepted_file_path)
            # preparing the artifact
            artifact = DataValidationArtifact(
                accepted_file_path=self.data_validation_config.accepted_data_dir,
                rejected_dir=self.data_validation_config.rejected_data_dir
            )
            logger.info(f"Data validation artifact: [{artifact}]")
            # returning artifact
            return artifact
        except Exception as e:
            raise FinanceException(e, sys)
