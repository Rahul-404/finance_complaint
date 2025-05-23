from finance_complaint.entity.schema import FinanceDataSchema
from pyspark.ml.feature import StandardScaler, VectorAssembler, OneHotEncoder, StringIndexer, Imputer
from pyspark.ml.pipeline import Pipeline
from finance_complaint.config.spark_manager import spark_session
from finance_complaint.exception import FinanceException
from finance_complaint.logger import logging as logger
from finance_complaint.entity.artifact_entity import DataValidationArtifact, DataTransformationArtifact
from finance_complaint.entity.config_entity import DataTransformationConfig
from pyspark.sql import DataFrame
from finance_complaint.ml.feature import FrequencyImputer, DerivedFeatureGenerator
from pyspark.ml.feature import IDF, Tokenizer, HashingTF
from pyspark.sql.functions import col, rand
import os,sys

class DataTransformation:

    def __init__(self, data_validation_artifact: DataValidationArtifact,
                 data_transformation_config: DataTransformationConfig,
                 schema=FinanceDataSchema()
                 ):
        try:
            logger.info(f"{'>>'*20} Strting data transformation.{'<<'*20}")
            self.data_val_artifact = data_validation_artifact
            self.data_tf_config = data_transformation_config
            self.schema = schema
        except Exception as e:
            raise FinanceException(e, sys)
        
    def read_data(self) -> DataFrame:
        try:
            file_path = self.data_val_artifact.accepted_file_path
            dataframe : DataFrame = spark_session.read.parquet(file_path)
            dataframe.printSchema()
            return dataframe
        except Exception as e:
            raise FinanceException(e, sys)
        
    def get_data_transformation_pipeline(self,) -> Pipeline:
        try:
            stages = []
            derived_features = DerivedFeatureGenerator(
                inputCols=self.schema.derived_input_features,
                outputCols=self.schema.derived_output_features
            )
            stages.append(derived_features)

            imputer = Imputer(inputCol=self.schema.numerical_columns[-1], outputCol=self.schema.im_numerical_columns[-1])

            stages.append(imputer)

            frequency_imputer = FrequencyImputer(inputCols=self.schema.one_hot_encoding_features, outputCols=self.schema.im_one_hot_encoding_features)
            stages.append(frequency_imputer)

            string_indexer = StringIndexer(inputCols=self.schema.im_one_hot_encoding_features, outputCols=self.schema.string_indexer_one_hot_features, handleInvalid="keep") 
            stages.append(string_indexer)

            one_hot_encoder = OneHotEncoder(inputCols=self.schema.string_indexer_one_hot_features,
                                            outputCols=self.schema.tf_one_hot_encoding_features, handleInvalid="keep")

            stages.append(one_hot_encoder)

            tokenizer = Tokenizer(inputCol=self.schema.tfidf_features[0], outputCol="words")

            stages.append(tokenizer)

            hashing_tf = HashingTF(inputCol=tokenizer.getOutputCol(), outputCol="rawFeatures", numFeatures=40)

            stages.append(hashing_tf)

            idf = IDF(inputCol= hashing_tf.getOutputCol(), outputCol=self.schema.tf_tfidf_features[0])

            stages.append(idf)

            vector_assembler = VectorAssembler(inputCols=self.schema.input_features,
                                               outputCol=self.schema.vector_assembler_output)
            
            stages.append(vector_assembler)

            standard_scaler = StandardScaler(inputCol=self.schema.vector_assembler_output,
                                             outputCol=self.schema.scaled_vector_input_features)
            stages.append(standard_scaler)

            pipeline = Pipeline(
                stages=stages
            )

            logger.info(f"Data transformation pipeline: [{pipeline}]")
            print(pipeline.stages)
            return pipeline
    
        except Exception as e:
            raise FinanceException(e, sys)
        

    def initiate_data_transformation(self) -> DataTransformationArtifact:

        try:
            logger.info(f">>>>>>>>>>>>>>>Stated data transformation<<<<<<<<<<<<<<<<")
            dataframe: DataFrame = self.read_data()
            logger.info(f"Number of row: [{dataframe.count()}] and column: [{len(dataframe.columns)}]")

            test_size = self.data_tf_config.test_size

            logger.info(f"Splitting dataset into train and test set using ration : {1 - test_size}:{test_size}")

            train_dataframe, test_dataframe = dataframe.randomSplit([1 - test_size, test_size])

            logger.info(f"Train dataset has number of row: [{train_dataframe.count()}] and"
                        f"column: [{len(train_dataframe.columns)}]")
            
            logger.info(f"Test dataset has number of row: [{test_dataframe.count()}] and"
                        f"column: [{len(test_dataframe.columns)}]")
            
            pipline = self.get_data_transformation_pipeline()

            print(f"train_dataframe: {train_dataframe}")

            transformed_pipeline = pipline.fit(train_dataframe)

            required_column = [self.schema.scaled_vector_input_features, self.schema.target_column]

            transformed_train_dataframe = transformed_pipeline.transform(train_dataframe)
            transformed_train_dataframe = transformed_train_dataframe.select(required_column)

            transformed_test_dataframe = transformed_pipeline.transform(test_dataframe)
            transformed_test_dataframe = transformed_test_dataframe.select(required_column)

            export_pipeline_file_path = self.data_tf_config.export_pipeline_dir
            os.makedirs(export_pipeline_file_path, exist_ok=True)
            os.makedirs(self.data_tf_config.transformed_test_dir, exist_ok=True)
            os.makedirs(self.data_tf_config.transformed_train_dir, exist_ok=True)

            transformed_train_data_file_path = os.path.join(self.data_tf_config.transformed_train_dir,
                                                            self.data_tf_config.file_name)
            
            transformed_test_data_file_path = os.path.join(self.data_tf_config.transformed_test_dir,
                                                            self.data_tf_config.file_name)
            logger.info(f"Saving transformation pipeline at: [{export_pipeline_file_path}]")

            transformed_pipeline.save(export_pipeline_file_path)
            logger.info(f"Saving tranformation train data at: [{transformed_train_data_file_path}]")
            print(transformed_train_dataframe.count(), len(transformed_train_dataframe.columns))
            transformed_train_dataframe.write.parquet(transformed_train_data_file_path)

            logger.info(f"Saving transformation test data at: [{transformed_test_data_file_path}]")
            print(transformed_test_dataframe.count(), len(transformed_train_dataframe.columns))
            transformed_test_dataframe.write.parquet(transformed_test_data_file_path)

            data_tf_artifact = DataTransformationArtifact(
                transformed_train_file_path = transformed_train_data_file_path,
                transformed_test_file_path = transformed_test_data_file_path,
                exported_pipeline_file_path = export_pipeline_file_path,
            )
            logger.info(f"Data tranformation artifact: [{data_tf_artifact}]")

            logger.info(f"{'--'*20} Strting data transformation.{'--'*20}\n")

            return data_tf_artifact
        
        except Exception as e:
            raise FinanceException(e, sys)