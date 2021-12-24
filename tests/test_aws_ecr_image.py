"""Tests for AWS ECR images."""
import pytest
import inspect
from datetime import datetime

from awsecr.image import ECRImage
from awsecr.exception import InvalidPayload


@pytest.fixture(scope='module')
def now():
    return datetime.now()


@pytest.fixture
def image_details(now):
    return {
            'imageTags': ['0.1.0'],
            'imageScanStatus': {'status': 'COMPLETE'},
            'imageScanFindingsSummary': {
                'findingSeverityCounts': {'UNDEFINED': 1}},
            'imageSizeInBytes': 62380145,
            'imagePushedAt': now
        }


@pytest.fixture
def new_instance(now, image_details):
    return ECRImage(
        '012345678910.dkr.ecr.us-east-2.amazonaws.com',
        'foobar',
        image_details)


def test_ecr_image_class():
    assert inspect.isclass(ECRImage)

    for method in '__init__ to_list size_in_mb fields'.split():
        assert inspect.isfunction(getattr(ECRImage, method))


def test_ecr_image_methods(new_instance):
    for method in '__init__ to_list size_in_mb'.split():
        assert inspect.ismethod(getattr(new_instance, method))


def test_ecr_image_attributes(new_instance, now):
    for attribute in 'name status size pushed_at vulnerabilities'.split():
        assert hasattr(new_instance, attribute)

    assert new_instance.status == 'COMPLETE'
    assert new_instance.size == 62380145
    assert new_instance.pushed_at == str(now)
    assert new_instance.vulnerabilities == 1


def test_ecr_image_size_in_mb(new_instance):
    assert new_instance.size_in_mb() == 60.9181103515625


def test_ecr_image_to_list(new_instance, now):
    assert new_instance.to_list() == [
        '012345678910.dkr.ecr.us-east-2.amazonaws.com/foobar:0.1.0',
        'COMPLETE',
        '60.92',
        str(now),
        '1'
    ]


def test_ecr_image_fields(new_instance):
    expected = ['Image', 'Scan status', 'Size (MB)', 'Pushed at',
                'Vulnerabilities']

    assert new_instance.fields() == expected


def test_ecr_image_exception(image_details):
    image_details.pop('imageScanFindingsSummary')

    with pytest.raises(InvalidPayload) as excinfo:
        ECRImage('0123', 'foobar', image_details)

    assert 'describe_images' in str(excinfo.value)
