"""Tests for awsecr exceptions."""
import inspect

from awsecr.exception import (
    MissingAWSEnvVar,
    InvalidPayload,
    ECRClientException,
    BaseException,
)


def test_ecr_repos_exceptions():
    assert inspect.isclass(BaseException)
    assert issubclass(BaseException, Exception)
    assert inspect.isclass(MissingAWSEnvVar)
    assert issubclass(MissingAWSEnvVar, BaseException)
    assert inspect.isclass(InvalidPayload)
    assert issubclass(InvalidPayload, BaseException)
    assert inspect.isclass(ECRClientException)
    assert issubclass(ECRClientException, BaseException)


def test_baseexception():
    expected = 'this is an error'
    instance = BaseException(expected)
    assert hasattr(instance, 'message')
    assert instance.message == expected
    assert inspect.ismethod(getattr(instance, '__str__'))


def test_ecr_client_exception_unexpected():
    expected = 'This is a FUBAR situation'
    instance = ECRClientException(error_code='UnexpectedException',
                                  message=expected)
    assert instance.message == expected


def test_ecr_client_exception_expected():
    expected = "The repository with name 'foobar' does not exist in the \
registry with id '012345678910'"
    full_msg = f"An error occurred (RepositoryNotFoundException) when calling \
the DescribeImages operation: {expected}"

    instance = ECRClientException(error_code='RepositoryNotFoundException',
                                  message=full_msg)
    assert instance.message == expected
