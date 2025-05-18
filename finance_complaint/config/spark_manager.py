from pyspark.sql import SparkSession
from dotenv import load_dotenv
import os

load_dotenv()

# to avoid version problem between "Driver" and "Wroker"
# Replace with your actual Conda env Python path
os.environ["PYSPARK_PYTHON"] = "/Users/rahulshelke/Documents/Data-Science/Data-Science-Projects/finance_complaint/venv/bin/python"
os.environ["PYSPARK_DRIVER_PYTHON"] = "/Users/rahulshelke/Documents/Data-Science/Data-Science-Projects/finance_complaint/venv/bin/python"




spark_session = (SparkSession.builder.master('local[*]').appName('finance_complaint')
    .config("spark.executor.instances", "2")
    .config("spark.executor.memory", "8g")
    .config("spark.driver.memory", "8g")
    .config("spark.executor.memoryOverhead", "8g")
    .getOrCreate())
