import pymongo
import os
import certifi
from finance_complaint.constant import env_var
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

ca = certifi.where()

mongo_client = MongoClient(host=env_var.mongo_db_url, server_api=ServerApi('1'))

print(mongo_client)