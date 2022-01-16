"""Tests for awsecr exceptions."""
import inspect

from awsecr.exception import (
    MissingAWSEnvVar,
    InvalidPayload,
    BaseException,
)


def test_ecr_repos_exceptions():
    assert inspect.isclass(BaseException)
    assert issubclass(BaseException, Exception)
    assert inspect.isclass(MissingAWSEnvVar)
    assert issubclass(MissingAWSEnvVar, BaseException)
    assert inspect.isclass(InvalidPayload)
    assert issubclass(InvalidPayload, BaseException)
