from setuptools import setup, find_packages


long_description = """
This Python package provides an interface for interacting with typical cloud storage systems. 
It allows users to create, retrieve, update, and delete data objects, each with associated 
metadata and content. The library includes support for session management, access control, 
transfer tracking, and metadata serialization, making it suitable for prototyping 
storage workflows or testing data processing pipelines. It offers a lightweight and 
dependency-free environment for modeling storage behavior in local or embedded applications.
"""

setup(
    name='cloud-ds-api',
    version='1.2.11',
    packages=find_packages(),
    description='cloud-ds-api',
    long_description_content_type='text/plain',
    long_description=long_description,
    url='https://github.com/MartinSahlen/cloud-functions-python',
    download_url='https://github.com/MartinSahlen/cloud-functions-python',
    project_urls={
        'Documentation': 'https://github.com/MartinSahlen/cloud-functions-python'},
    author='Martin Sahlen',
    author_email='msahlen@alvinnet.com',
)
