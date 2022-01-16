"""Exceptions of awsecr."""


class BaseException(Exception):
    def __init__(self, message) -> None:
        self.message = message

    def __str__(self) -> str:
        return self.message


class MissingAWSEnvVar(BaseException):
    def __init__(self) -> None:
        super().__init__(
            'Missing AWS environment variables to configure access')


class InvalidPayload(BaseException):
    def __init__(self, missing_key: str, api_method: str):
        super().__init__(
            f'Unexpected payload received, missing "{missing_key}" from \
"{api_method}" call response')


class ECRClientException(BaseException):
    def __init__(self, error_code: str, message: str):
        if error_code == 'RepositoryNotFoundException':
            super().__init__(message.split(':')[1].lstrip())
        else:
            super().__init__(message)
