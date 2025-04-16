from finance_complaint.exception import FinanceException
from finance_complaint.logger import logging as logger
from finance_complaint.entity.config_entity import (DataIngestionConfig, DataValidationConfig)
from finance_complaint.entity.artifact_entity import (DataIngestionArtifact, DataValidationArtifact)
from finance_complaint.entity.config_entity import TrainingPipelineConfig
from finance_complaint.components.data_ingestion import DataIngestion
from finance_complaint.components.data_validation import DataValidation
import sys, os

class TrainingPipeline:
    """ 
    this is a training pipeline comprising each components from flow chart
    """
    def __init__(self, training_pipeline_config: TrainingPipelineConfig):
        self.training_pipeline_config: TrainingPipelineConfig = training_pipeline_config

    def start_data_ingestion(self) -> DataIngestionArtifact:
        """
        responsible for starting data ingestion 
        """
        try:
            data_ingestion_config = DataIngestionConfig(training_pipeline_config=self.training_pipeline_config)
            data_ingestion = DataIngestion(data_ingestion_config=data_ingestion_config)
            data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
            return data_ingestion_artifact
        
        except Exception as e:
            logger.debug(f"Error: {e}")
            raise FinanceException(e, sys)
        
    def start_data_validation(self, data_ingestion_artifact: DataIngestionArtifact) -> DataValidationArtifact:
        """
        takes ingested data artifact and validate that data by generating validation artifact
        """
        try:
            data_validation_config = DataValidationConfig(training_pipeline_config=self.training_pipeline_config)
            data_validation = DataValidation(
                data_validation_config=data_validation_config,
                data_ingestion_artifact=data_ingestion_artifact
            )
            data_validation_artifact = data_validation.initiate_data_validation()
            return data_validation_artifact
        except Exception as e:
            raise FinanceException(e, sys)
        
    def start(self):
        try:
            # initalizating data ingestion
            data_ingestion_artifact = self.start_data_ingestion()
            # initalizing data validation
            data_validation_artifact = self.start_data_validation(data_ingestion_artifact=data_ingestion_artifact)

        except Exception as e:
            raise FinanceException(e, sys)    
        
    
        
