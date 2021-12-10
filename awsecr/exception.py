"""Exceptions of awsecr."""


class BaseException(Exception):
    pass


class MissingAWSEnvVar(BaseException):
    def __init__(self) -> None:
        self.message = 'Missing AWS environment variables to configure access'

    def __str__(self) -> str:
        return self.message


class InvalidPayload(BaseException):
    def __init__(self, missing_key: str, api_method: str):
        self.message = f'Unexpected payload received, missing "{missing_key}" \
from "{api_method}" call response'

    def __str__(self) -> str:
        return self.message


class ECRClientException(BaseException):
    def __init__(self, error_code: str, message: str):
        if error_code == 'RepositoryNotFoundException':
            self.message = (message.split(':')[1].lstrip())
        else:
            self.message = message

    def __str__(self) -> str:
        return self.message
