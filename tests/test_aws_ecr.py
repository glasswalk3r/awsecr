"""Tests for `awsecr` package."""
import pytest
import inspect
from mypy_boto3_sts.type_defs import GetCallerIdentityResponseTypeDef

from awsecr.awsecr import ECRRepos, MissingAWSEnvVar, InvalidPayload, aws_account_info


class AwsStsStub:
    account = '012345678910'
    user = 'foobar'

    def get_caller_identity(self) -> GetCallerIdentityResponseTypeDef:
        email = 'arfreitas@cpan.org'
        arn = f'arn:aws:sts::{self.account}:assumed-role/{self.user}/{email}'
        return {
                'Account': self.account,
                'Arn': arn,
                'ResponseMetadata': {
                    'HTTPHeaders': {
                        'content-length': '516',
                        'content-type': 'text/xml',
                        'date': 'Thu, 02 Dec 2021 22:27:26 GMT',
                        'x-amzn-requestid': 'bdad68ca-001e-435b-9215-9ffdf8c29'
                    },
                    'HTTPStatusCode': 200,
                    'RequestId': 'bdad68ca-001e-435b-9215-9ff5d9df8c29',
                    'RetryAttempts': 0,
                    'HostId': ''
                },
                'UserId': f'AROAQS8CASQSLK3MZM2GM:{email}'}


def test_aws_account_id():
    result = aws_account_info(client=AwsStsStub())
    assert result.__class__.__name__ == 'tuple'
    assert result[0] == AwsStsStub.account
    assert result[1] == AwsStsStub.user


def test_ecr_repos_exceptions():
    assert inspect.isclass(MissingAWSEnvVar)
    assert inspect.isclass(InvalidPayload)


def test_ecr_repos(monkeypatch):
    monkeypatch.setenv("AWS_PROFILE", "dev")
    assert inspect.isclass(ECRRepos)
    instance = ECRRepos()
    methods = tuple(['list_repositories'])

    for method in methods:
        assert inspect.ismethod(getattr(instance, method))


def test_ecr_repos_no_aws_cfg():
    with pytest.raises(MissingAWSEnvVar) as excinfo:
        ECRRepos()

    assert 'AWS environment' in str(excinfo.value)
