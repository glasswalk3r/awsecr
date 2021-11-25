"""Tests for `awsecr` package."""
import pytest
import inspect

from awsecr.awsecr import ECRRepos, MissingAWSEnvVar, InvalidPayload


def test_ecr_repos_exceptions():
    assert inspect.isclass(MissingAWSEnvVar)
    assert inspect.isclass(InvalidPayload)


def test_ecr_repos(monkeypatch):
    monkeypatch.setenv("AWS_PROFILE", "dev")
    assert inspect.isclass(ECRRepos)
    instance = ECRRepos()
    methods = ('list_repositories')

    for method in methods:
        assert inspect.ismethod(getattr(instance, method))


def test_ecr_repos_no_aws_cfg():
    with pytest.raises(MissingAWSEnvVar):
        ECRRepos(user='foobar')


