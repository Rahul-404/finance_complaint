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
DATA_INGESTION_MIN_START_DATE = "2013-01-01"
DATA_INGESTION_DATA_SOURCE_URL = f"https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/"\
                                f"?date_received_max=<todate>&date_received_min=<fromdate>"\
                                f"&field=all&format=json"
# Data Validation Constants
DATA_VALIDATION_DIR = "data_validation"
DATA_VALIDATION_FILE_NAME = "finance_complaint"
DATA_VALIDATION_ACCEPTED_DATA_DIR = "accepted_data"
DATA_VALIDATION_REJECTED_DATA_DIR = "rejected_data"

# Data Transformation Constants
DATA_TRANSFORMATION_DIR = "data_transformation"
DATA_TRANSFORMATION_PIPELINE_DIR = "transformed_pipeline"
DATA_TRANSFORMATION_TRAIN_DIR = "train"
DATA_TRANSFORMATION_FILE_NAME = "finance_complaint"
DATA_TRANSFORMATION_TEST_DIR = "test"
DATA_TRANSFORMATION_TEST_SIZE = 0.3

# Model Trainer Constants
MODEL_TRAINER_BASE_ACCURACY = 0.6
MODEL_TRAINER_DIR = "model_trainer"
MODEL_TRAINER_TRAINED_MODEL_DIR = "trained_model"
MODEL_TRAINER_MODEL_NAME = "finance_estimator"
MODEL_TRAINER_LABEL_INDEXER_DIR = "label_indexer"
MODEL_TRAINER_MODEL_METRIC_NAMES = [
    'f1',
    "weightedPrecision",
    "weightedRecall",
    "weightedTruePositiveRate",
    "weightedFalsePositiveRate",
    "weightedFMeasure",
    "truePositiveRateByLabel",
    "falsePositiveRateByLabel",
    "precisionByLabel",
    "recallByLabel",
    "fMeasureByLabel"
]

# Model Evaluation Constants
MODEL_EVALUATION_DIR = "model_evaluation"
MODEL_EVALUATION_REPORT_DIR = "report"
MODEL_EVALUATION_REPORT_FILE_NAME = "evaluation_report"
MODEL_EVALUATION_THRESHOLD_VALUE = 0.002
MODEL_EVALUATION_METRIC_NAMES = ["f1",]

# Model Pusher Constants
MODEL_PUSHER_SAVED_MODEL_DIRS = "saved_models"
MODEL_PUSHER_DIR = "model_pusher"
MODEL_PUSHER_MODEL_NAME = MODEL_TRAINER_MODEL_NAME

@dataclass
class TrainingPipelineConfig:
    pipeline_name: str = "artifact"
    artifact_dir: str = os.path.join(pipeline_name, TIMESTAMP)

@dataclass
class DataIngestionConfig:

    def __init__(self, training_pipeline_config: TrainingPipelineConfig, from_date=DATA_INGESTION_MIN_START_DATE,
                 to_date='2019-01-01'):
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
            else:
                self.to_date = to_date

            # create master directory
            data_ingestion_master_dir = os.path.join(os.path.dirname(training_pipeline_config.artifact_dir), DATA_INGESTION_DIR)

            self.data_ingestion_dir = os.path.join(data_ingestion_master_dir, TIMESTAMP)

            self.metadata_file_path = os.path.join(data_ingestion_master_dir, DATA_INGESTION_METADATA_FILE_NAME)

            data_ingestion_metadata = DataIngestionMetadata(metadata_file_path=self.metadata_file_path)

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

    def __init__(self, training_pipeline_config: TrainingPipelineConfig) -> None:
        try:
            data_transformation_dir = os.path.join(training_pipeline_config.artifact_dir, DATA_TRANSFORMATION_DIR)
            self.transformed_train_dir = os.path.join(data_transformation_dir, DATA_TRANSFORMATION_TRAIN_DIR)
            self.transformed_test_dir = os.path.join(data_transformation_dir, DATA_TRANSFORMATION_TEST_DIR)
            self.export_pipeline_dir = os.path.join(data_transformation_dir, DATA_TRANSFORMATION_PIPELINE_DIR)
            self.file_name = DATA_TRANSFORMATION_FILE_NAME
            self.test_size = DATA_TRANSFORMATION_TEST_SIZE
        except Exception as e:
            raise FinanceException(e, sys)
        
@dataclass
class ModelTrainerConfig:

    def __init__(self, training_pipeline_config: TrainingPipelineConfig) -> None:
        try:
            model_trained_dir = os.path.join(training_pipeline_config.artifact_dir, MODEL_TRAINER_DIR)
            self.trained_model_file_path = os.path.join(model_trained_dir, MODEL_TRAINER_TRAINED_MODEL_DIR, MODEL_TRAINER_MODEL_NAME)
            self.label_indexer_model_dir = os.path.join(model_trained_dir, MODEL_TRAINER_LABEL_INDEXER_DIR)
            self.base_accuracy = MODEL_TRAINER_BASE_ACCURACY
            self.metric_list = MODEL_TRAINER_MODEL_METRIC_NAMES
        except Exception as e:
            raise FinanceException(e, sys)
    
@dataclass
class ModelEvaluationConfig:

    def __init__(self, training_pipeline_config: TrainingPipelineConfig) -> None:
        self.model_evaluation_dir = os.path.join(training_pipeline_config.artifact_dir, MODEL_EVALUATION_DIR)
        self.threshold=MODEL_EVALUATION_THRESHOLD_VALUE
        self.metric_list = MODEL_EVALUATION_METRIC_NAMES

@dataclass
class ModelPusherConfig:

    def __init__(self, training_pipeline_config: TrainingPipelineConfig) :
        try:
            self.pusher_model_dir = os.path.join(training_pipeline_config.artifact_dir, MODEL_PUSHER_DIR, "model", MODEL_PUSHER_MODEL_NAME)
            self.saved_model_dir = MODEL_PUSHER_SAVED_MODEL_DIRS
        except Exception as e:
            raise FinanceException(e, sys)
        
class BatchPredictionConfig:

    def __init__(self):
        try:
            self.inbox_dir = os.path.join("data", "inbox")
            self.outbox_dir = os.path.join("data", "outbox")
            self.archive_dir = os.path.join("data", "archive")
            # os.makedirs(self.inbox_dir , exist_ok=True)
            os.makedirs(self.outbox_dir , exist_ok=True)
            os.makedirs(self.archive_dir, exist_ok=True)
        except Exception as e:
            raise FinanceException(e, sys)