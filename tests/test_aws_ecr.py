"""Tests for `awsecr` package."""
import pytest
import inspect
import base64
from datetime import datetime
from mypy_boto3_sts.type_defs import GetCallerIdentityResponseTypeDef

from awsecr.awsecr import (
    account_info,
    registry_fqdn,
    _extract_credentials,
    _ecr_token
)
from awsecr.exception import (
    MissingAWSEnvVar,
    InvalidPayload,
    BaseException,
)
from .shared import AwsEcrMetaStub


class AwsEcrStub:
    meta = AwsEcrMetaStub()

    @staticmethod
    def ecr_token():
        return base64.b64encode(b'AWS:foobar')

    def get_authorization_token(self, registryIds):
        return self.auth_data

    def __init__(self):
        self.auth_data = {
                'authorizationData': [
                    {
                        'authorizationToken': self.ecr_token(),
                        'expiresAt': datetime(2015, 1, 1),
                        'proxyEndpoint': 'string'
                    },
                ]
            }

    def _break(self):
        self.auth_data['authorizationData'][0].pop('authorizationToken')


class AwsStsStub:
    user = 'foobar'
    meta = AwsEcrMetaStub()

    def __init__(self, account):
        self.account = account
        email = 'arfreitas@cpan.org'
        arn = f'arn:aws:sts::{self.account}:assumed-role/{self.user}/{email}'
        self.payload = {
                        'Account': self.account,
                        'Arn': arn,
                        'ResponseMetadata': {
                            'HTTPHeaders': {
                                'content-length': '516',
                                'content-type': 'text/xml',
                                'date': 'Thu, 02 Dec 2021 22:27:26 GMT',
                                'x-amzn-requestid': 'bdad68ca-001e-435b-df8c29'
                            },
                            'HTTPStatusCode': 200,
                            'RequestId': 'bdad68ca-001e-435b-9215-9ff5d9df8c2',
                            'RetryAttempts': 0,
                            'HostId': ''
                        },
                        'UserId': f'AROAQS8CASQSLK3MZM2GM:{email}'}

    def get_caller_identity(self) -> GetCallerIdentityResponseTypeDef:
        return self.payload

    def _break(self):
        self.payload.pop('Account')


@pytest.fixture
def broken_sts_client(registry_id):
    client = AwsStsStub(registry_id)
    client._break()
    return client


@pytest.fixture
def broken_ecr_client():
    client = AwsEcrStub()
    client._break()
    return client


def test_aws_account_id(registry_id):
    client = AwsStsStub(registry_id)
    result = account_info(client=client)
    assert result.__class__.__name__ == 'tuple'
    assert result[0] == client.account
    assert result[1] == AwsStsStub.user


def test_aws_account_id_exception(broken_sts_client):
    with pytest.raises(InvalidPayload) as excinfo:
        account_info(broken_sts_client)

    assert 'Account' in str(excinfo.value)


def test_ecr_repos_exceptions():
    assert inspect.isclass(BaseException)
    assert issubclass(BaseException, Exception)
    assert inspect.isclass(MissingAWSEnvVar)
    assert issubclass(MissingAWSEnvVar, BaseException)
    assert inspect.isclass(InvalidPayload)
    assert issubclass(InvalidPayload, BaseException)


def test_registry_fqdn():
    account_id = 'foo'
    region = 'bar'
    fqdn = registry_fqdn(account_id, region)
    assert account_id in fqdn
    assert region in fqdn


def test__extract_credentials():
    credentials = _extract_credentials(AwsEcrStub.ecr_token())
    assert credentials.__class__.__name__ == 'tuple'


def test__ecr_token(registry_id):
    result = _ecr_token(registry_id, AwsEcrStub())
    assert result.__class__.__name__ == 'tuple'
    assert result[0] == AwsEcrStub.ecr_token()
    assert result[1] == AwsEcrMetaStub.region_name


def test__ecr_token_with_region(registry_id):
    expected = 'foobar'
    result = _ecr_token(registry_id, AwsEcrStub(), expected)
    assert result[1] == expected


def test__ecr_token_with_exception(broken_ecr_client, registry_id):
    with pytest.raises(InvalidPayload) as excinfo:
        _ecr_token(registry_id, broken_ecr_client)

    assert 'get_authorization_token' in str(excinfo.value)


@pytest.mark.skip(reason='To be implemented together with stub')
def test_login_ecr():
    pass


@pytest.mark.skip(reason='To be implemented together with stub')
def test_image_push():
    pass
