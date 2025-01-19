from setuptools import setup, find_packages
from typing import List

# Declaring variables for setup functions
PROJECT_NAME = "finanace-complaint"
VERSION = "0.0.1"
AUTHOR = "Rahul Shelke",
DESCRIPTION  = """This project utilizes Natural Language Processing (NLP) and machine learning techniques to 
                analyze consumer complaints and predict whether a consumer will dispute the resolution. The system processes 
                complaint descriptions and other relevant features to classify complaints as potentially leading to disputes, 
                enabling more efficient customer service and issue resolution."""
REQUIREMENT_FILE_NAME = "requirements.txt"
HYPHEN_E_DOT = "-e ."

def get_requirements_list() -> List[str]:
    """
    Description : This function is going to return list of requirement
    mention in requirement.txt file
    return This function is going to return a list which contain name
    of libraries mentioned in requirements.txt file
    """
    with open(REQUIREMENT_FILE_NAME) as requirement_file:
        requirement_list = requirement_file.readlines()
        requirement_list = [requirement_name.replace("\n", "") for requirement_name in requirement_list]
        if HYPHEN_E_DOT in requirement_list:
            requirement_list.remove(HYPHEN_E_DOT)
        return requirement_list

setup(
    name = PROJECT_NAME,
    version = VERSION,
    author = AUTHOR,
    description = DESCRIPTION,
    packages = find_packages(),
    install_requirements = get_requirements_list()
)