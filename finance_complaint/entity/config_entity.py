from finance_complaint.exception import FinanceException
from finance_complaint.entity.metadata_entity import DataIngestionMetadata
from finance_complaint.constant import TIMESTAMP
from dataclasses import dataclass
from datetime import datetime
import sys
import os

# Data Ingestion Constants
DATA_INGESTION_DIR = "data_ingestion"
DATA_INGESTION_DOWNLOADED_DATA_DIR = "downloaded_files"
DATA_INGESTION_FILE_NAME = "finance_complaint"
DATA_INGESTION_FEATURE_STORE_DIR = "feature_store"
DATA_INGESTION_FAILED_DIR = "failed_downloaded_files"
DATA_INGESTION_METADATA_FILE_NAME = "meta_info.yaml"
DATA_INGESTION_MIN_START_DATE = "2022-05-01"
DATA_INGESTION_DATA_SOURCE_URL = f"https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1"\
                                f"?date_received_max=<todate>&date_received_min=<fromdate>"\
                                f"&field=all&format=json"
# Data Validation Constants
DATA_VALIDATION_DIR = "data_validation"
DATA_VALIDATION_FILE_NAME = "finance_complaint"
DATA_VALIDATION_ACCEPTED_DATA_DIR = "accepted_data"
DATA_VALIDATION_REJECTED_DATA_DIR = "rejected_data"


@dataclass
class TrainingPipelineConfig:
    pipeline_name: str = "artifact"
    artifact_dir: str = os.path.join(pipeline_name, TIMESTAMP)

@dataclass
class DataIngestionConfig:

    def __init__(self, training_pipeline_config: TrainingPipelineConfig, from_date=DATA_INGESTION_MIN_START_DATE,
                 to_date=None):
        try:
            self.from_date = from_date
            min_start_date = datetime.strptime(DATA_INGESTION_MIN_START_DATE, "%Y-%m-%d")
            from_date_obj = datetime.strptime(from_date, "%Y-%m-%d")

            # date should not be smaller than minimum date
            if from_date_obj < min_start_date:
                self.from_date = DATA_INGESTION_MIN_START_DATE

            # to_date is none then consider todays date
            if to_date is None:
                self.to_date = datetime.now().strftime("%Y-%m-%d")

            # create master directory
            data_ingestion_master_dir = os.path.join(os.path.dirname(training_pipeline_config.artifact_dir), DATA_INGESTION_DIR)

            self.data_ingestion_dir = os.path.join(data_ingestion_master_dir, TIMESTAMP)

            self.metadate_file_path = os.path.join(data_ingestion_master_dir, DATA_INGESTION_METADATA_FILE_NAME)

            data_ingestion_metadata = DataIngestionMetadata(metadata_file_path=self.metadate_file_path)

            if data_ingestion_metadata.is_metadata_file_present:
                metadata_info = data_ingestion_metadata.get_meta_data_info()
                self.from_date = metadata_info.to_date

            self.download_dir = os.path.join(self.data_ingestion_dir, DATA_INGESTION_DOWNLOADED_DATA_DIR)

            self.failed_dir = os.path.join(self.data_ingestion_dir, DATA_INGESTION_FAILED_DIR)

            self.file_name = DATA_INGESTION_FILE_NAME

            self.feature_store_dir = os.path.join(data_ingestion_master_dir, DATA_INGESTION_FEATURE_STORE_DIR)

            self.datasource_url = DATA_INGESTION_DATA_SOURCE_URL 
        except Exception as e:
            raise FinanceException(e, sys)
        
@dataclass
class DataValidationConfig:

    def __init__(self, training_pipeline_config: TrainingPipelineConfig) -> None:
        try:
            data_validation_dir = os.path.join(training_pipeline_config.artifact_dir, 
                                               DATA_VALIDATION_DIR)
            self.accepted_data_dir = os.path.join(data_validation_dir, DATA_VALIDATION_ACCEPTED_DATA_DIR)
            self.rejected_data_dir = os.path.join(data_validation_dir, DATA_VALIDATION_REJECTED_DATA_DIR)
            self.file_name = DATA_VALIDATION_FILE_NAME
        except Exception as e:
            raise FinanceException(e, sys)
        
@dataclass
class DataTransformationConfig:

    def __init__(self):
        try:
            pass
        except Exception as e:
            raise FinanceException(e, sys)
        
@dataclass
class ModelTrainerConfig:

    def __init__(self):
        try:
            pass
        except Exception as e:
            raise FinanceException(e, sys)
    
@dataclass
class ModelPusherConfig:

    def __init__(self):
        try:
            pass
        except Exception as e:
            raise FinanceException(e, sys)
        
