import pytest
import os

# https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#using-environment-variables
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'


@pytest.fixture
def registry_id():
    return '012345678910'
