"""Tests for `awsecr` package."""
import pytest
from docker.models.images import Image

from awsecr.awsecr import (
    BaseDockerClient,
    LoginResponse,
    login_ecr
)
from awsecr.exception import InvalidResponseStatus
from .shared import AwsEcrStub


class DockerClientMock(BaseDockerClient):
    def __init__(self, login_fails: bool = False):
        self._mock: LoginResponse = {'IdentityToken': ''}

        if login_fails:
            self._mock['Status'] = 'Login Failed'
        else:
            self._mock['Status'] = 'Login Succeeded'

    def login(self, username, password, registry, reauth) -> LoginResponse:
        return self._mock

    def image(self, image_name: str) -> Image:
        """Currently not in use."""
        pass

    def push(self, registry: str, tag: str, stream: bool, decode: bool):
        """Currently not in use."""
        pass

    def break_response(self):
        self._mock.pop('Status')


def test_login_ecr():
    client_mock: DockerClientMock = DockerClientMock()
    client_mock = login_ecr(account_id='123456789', docker_client=client_mock, region='us-east-1',
                            ecr_client=AwsEcrStub())
    assert issubclass(client_mock.__class__, BaseDockerClient)


def test_login_ecr_fail():
    client_mock: DockerClientMock = DockerClientMock(login_fails=True)

    with pytest.raises(InvalidResponseStatus) as excinfo:
        login_ecr(account_id='123456789', docker_client=client_mock, region='us-east-1', ecr_client=AwsEcrStub())

    assert 'Failed' in str(excinfo.value)


def test_login_ecr_missing():
    client_mock: DockerClientMock = DockerClientMock(login_fails=True)
    client_mock.break_response()

    with pytest.raises(ValueError) as excinfo:
        login_ecr(account_id='123456789', docker_client=client_mock, region='us-east-1', ecr_client=AwsEcrStub())

    assert 'missing' in str(excinfo.value)
