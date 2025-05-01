from pyspark import keyword_only
from pyspark.ml import Transformer
from pyspark.ml.param.shared import Param, Params, TypeConverters, HasOutputCols, HasInputCols
from pyspark.ml.util import DefaultParamsReadable, DefaultParamsWritable
from pyspark.ml import Estimator
from pyspark.sql import DataFrame
from pyspark.sql.functions import desc
from pyspark.sql.functions import col, abs
from typing import List
from pyspark.sql.types import TimestampType, LongType
from finance_complaint.logger import logging as logger
from finance_complaint.config.spark_manager import spark_session

class FrequencyEncoder(Estimator, HasInputCols, HasOutputCols,
                       DefaultParamsReadable, DefaultParamsWritable):
    frequencyInfo = Param(Params._dummy(), "getfrequencyInfo", "getfrequencyInfo",
                          typeConverter=TypeConverters.toList)
    @keyword_only
    def __init__(self, inputCols: List[str] = None, outputCols:List[str] = None,):
        super(FrequencyEncoder, self).__init__()
        kwargs = self._input_kwargs

        self.frequencyInfo = Param(self, "frequencyInfo", "")
        self._setDefault(frequencyInfo="")
        #self._set(**kwargs)

        self.setParams(**kwargs)

    @keyword_only
    def setParams(self, inputCols: List[str] = None, outputCols: List[str] = None,):
        kwargs = self._input_kwargs
        return self._set(**kwargs)
    
    def setInputCols(self, value: List[str]):
        """ 
        Set the value of :py:attr:`inputCol`.
        """
        return self._set(inputCol=value)
    
    def setOutputCols(self, value: List[str]):
        """ 
        Set the value of :py:attr:`outputCol`
        """
        return self._set(outputCols=value)
    
    def setfrequencyInfo(self):
        return self.getOrDefault(self.frequencyInfo)
    
    def _fit(self, dataframe: DataFrame):
        input_columns = self.getInputCols()
        print(f"Input columns: {input_columns}")
        output_columns = self.getOutputCols()
        print(f"Output columns: {output_columns}")
        replace_info = []
        for column, new_column in zip(input_columns, output_columns):
            freq = (dataframe.select(col(column).alias(f'g_{column}')).groupby(f'g_{column}').count().withColumn(new_column, col('count')))
            freq = freq.drop('count')
            logger.info(f"{column} has [{freq.count()}] unique category.")
            replace_info.append(freq.collect())

        self.setfrequencyInfo(frequencyInfo=replace_info)
        estimator = FrequencyEncoderModel(inputCols=input_columns, outputCols=output_columns)
        estimator.setfrequencyInfo(frequencyInfo=replace_info)
        return estimator
    
class FrequencyEncoderModel(FrequencyEncoder, Transformer):

    def __init__(self, inputCols: List[str] = None, outputCols: List[str] = None):
        super(FrequencyEncoderModel, self).__init__(inputCols=inputCols, outputCols=outputCols)

    def _transform(self, dataframe: DataFrame):
        inputCols = self.getInputCols()
        outputCols = self.getOutputCols()

        print(f"Input Columns: {inputCols}")
        print(f"Output Columns: {outputCols}")

        freqInfo = self.getfrequencyInfo()


        for in_col, out_col , freq_info in zip(inputCols, outputCols, freqInfo):
            frequency_dataframe: DataFrame = spark_session.createDataFrame(freq_info)

            columns = frequency_dataframe.columns

            dataframe = dataframe.join(frequency_dataframe,
                                       on= dataframe[in_col] == frequency_dataframe[columns[0]])
            
            dataframe = dataframe.drop(columns[0])

            if out_col not in dataframe.columns:
                dataframe = dataframe.withColumn(out_col, col(columns[1]))
                dataframe= dataframe.drop(columns[1])

        return dataframe
    
class DerivedFeatureGenerator(Transformer, HasInputCols, HasOutputCols,
                              DefaultParamsReadable, DefaultParamsWritable):
    @keyword_only
    def __init__(self, inputCols: List[str] = None, outputCols: List[str] = None,):
        super(DerivedFeatureGenerator, self).__init__()
        kwargs = self._input_kwargs
        # self._set(**kwargs)
        self.second_within_day = 60 * 60 * 24
        self.setParams(**kwargs)

    @keyword_only
    def setParams(self, inputCols: List[str] = None, outputCols: List[str] = None,):
        kwargs = self._input_kwargs
        return self._set(**kwargs)
    
    def setInputCols(self, value: List[str]):
        """ 
        Sets the value of :py:attr:`inputCol`.
        """
        return self._set(inputCols=value)
    
    def setOutputCols(self, value: List[str]):
        """ 
        Sets the value of :py:attr:`outputCol`.
        """
        return self._set(outputCols=value)
    
    def _fit(self, dataframe: DataFrame):
        return self

    def _transform(self, dataframe: DataFrame):
        inputCols = self.getInputCols()

        for column in inputCols:
            dataframe = dataframe.withColumn(column, col(column).cast(TimestampType()))

        dataframe = dataframe.withColumn(self.getOutputCols()[0],
                                         abs(col(inputCols[1]).cast(LongType()) - col(inputCols[0]).cast(LongType()))/ (self.second_within_day))
        return dataframe
    
class FrequencyImputer(
    Estimator,
    HasInputCols,
    HasOutputCols,
    DefaultParamsReadable,
    DefaultParamsWritable
):
    topCategories = Param(Params._dummy(), "getTopCategories", "getTopCategories", 
                          typeConverter=TypeConverters.toListString)
    
    @keyword_only
    def __init__(self, inputCols: List[str] = None, outputCols: List[str] = None):
        super(FrequencyImputer, self).__init__()
        self.topCategories = Param(self, "topCategories", "")
        self._setDefault(topCategories="")
        kwargs = self._input_kwargs
        print(kwargs)
        self.setParams(**kwargs)


    @keyword_only
    def setParams(self, inputCols: List[str] = None, outputCols: List[str] = None, ):
        kwargs = self._input_kwargs
        return self._set(**kwargs)
    
    def setTopCategories(self, value: List[str]):
        return self._set(topCategories=value)

    def getTopCategories(self):
        return self.getOrDefault(self.topCategories)
    
    def setInputCols(self, value: List[str]):
        """ 
        set the value of :py:attr:`inputCol`
        """
        return self._set(inputCols=value)
    
    def setOutputCols(self, value: List[str]):
        """ 
        set the value of :py:attr:`outputCol`
        """
        return self._set(outputCols=value)
    
    def _fit(self, dataset: DataFrame):
        inputCols = self.getInputCols()
        topCategories = []
        for column in inputCols:
            categoryCountByDesc = dataset.groupBy(column).count().filter(f'{column} IS NOT NULL').sort(desc('count'))
            topCat = categoryCountByDesc.take(1)[0][column]
            topCategories.append(topCat)
        
        self.setTopCategories(value=topCategories)

        estimator = FrequencyImputerModel(inputCols = self.getInputCols(),
                                          outputCols = self.getOutputCols())
        
        estimator.setTopCategories(value=topCategories)
        return estimator
    
class FrequencyImputerModel(FrequencyImputer, Transformer):

    def __init__(self, inputCols: List[str] = None, outputCols: List[str] = None,):
        super(FrequencyImputerModel, self).__init__(inputCols=inputCols, outputCols=outputCols)

    def _transform(self, dataset: DataFrame):
        topCategories = self.getTopCategories()
        outputCols = self.getOutputCols()

        updateMissingValues = dict(zip(outputCols, topCategories))

        inputCols = self.getInputCols()

        for outputColumn, inputColumn in zip(outputCols, inputCols):
            dataset = dataset.withColumn(outputColumn, col(inputColumn))
            # print(dataset.columns)
            # print(outputColumn, inputColumn)

        dataset = dataset.na.fill(updateMissingValues)

        return dataset