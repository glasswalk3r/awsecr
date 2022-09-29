"""Tests for AWS ECR images."""
import pytest
import inspect
from datetime import datetime
from dateutil.tz import tzlocal
from botocore.exceptions import ClientError

from awsecr.image import ECRImage, list_ecr
from awsecr.exception import InvalidPayload, ECRClientException
from awsecr.cli import _ansi_vulnerabilities
from .shared import AwsMetaStub


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


class AWSECRClientStub:
    meta = AwsMetaStub()
    artifact_media_type = 'application/vnd.docker.container.image.v1+json'
    manifest_media_type = 'application/vnd.docker.distribution.manifest.v2+\
json'
    only_repository = 'nodejs'
    _scan_completed = 'The scan was completed successfully.'

    def __init__(self, registry_id):
        self.registry_id = registry_id
        self._force_exception = False
        self._payload = {
            'ResponseMetadata': {
                'HTTPHeaders': {
                    'content-length': '2477',
                    'content-type': 'application/x-amz-json-1.1',
                    'date': 'Sat, 25 Dec 2021 18:51:48 GMT',
                    'x-amzn-requestid': '168c7399-cb10-4c0f-8cdd-3be2afdc7b41'
                },
                'HTTPStatusCode': 200,
                'RequestId': '168c7399-cb10-4c0f-8cdd-3be2afdc7b41',
                'RetryAttempts': 0
            },
            'imageDetails': [
                {
                    'artifactMediaType': self.artifact_media_type,
                    'imageDigest': 'sha256:1107d18937b5bf116497028214d714d3921\
    fc45bbb8f7001b452a3da7988bbb6',
                    'imageManifestMediaType': self.manifest_media_type,
                    'imagePushedAt': datetime(
                        2021, 12, 15, 18, 54, 58, tzinfo=tzlocal()),
                    'imageScanFindingsSummary': {
                        'findingSeverityCounts': {'LOW': 1},
                        'imageScanCompletedAt': datetime(
                            2021, 12, 15, 18, 55, 3, tzinfo=tzlocal()),
                        'vulnerabilitySourceUpdatedAt': datetime(
                            2021, 12, 14, 13, 8, 57, tzinfo=tzlocal())
                    },
                    'imageScanStatus': {
                        'description': self._scan_completed,
                        'status': 'COMPLETE'
                    },
                    'imageSizeInBytes': 30007575,
                    'imageTags': ['12-0.1.1'],
                    'registryId': self.registry_id,
                    'repositoryName': self.only_repository
                },
                {
                    'artifactMediaType': self.artifact_media_type,
                    'imageDigest': 'sha256:aa5c5956c88de0b7d34f393f3135ef72da1\
    2cbf0bb5b3282a2e8ad3e30a8d8aa',
                    'imageManifestMediaType': self.manifest_media_type,
                    'imagePushedAt': datetime(
                        2021, 12, 1, 18, 26, 46, tzinfo=tzlocal()),
                    'imageScanFindingsSummary': {
                        'findingSeverityCounts': {'MEDIUM': 1},
                        'imageScanCompletedAt': datetime(
                            2021, 12, 1, 18, 26, 49, tzinfo=tzlocal()),
                        'vulnerabilitySourceUpdatedAt': datetime(
                            2021, 11, 24, 13, 11, 37, tzinfo=tzlocal())
                    },
                    'imageScanStatus': {
                        'description': self._scan_completed,
                        'status': 'COMPLETE'
                    },
                    'imageSizeInBytes': 41711442,
                    'imageTags': ['14-0.1.0'],
                    'registryId': self.registry_id,
                    'repositoryName': self.only_repository
                },
                {
                    'artifactMediaType': self.artifact_media_type,
                    'imageDigest': 'sha256:f9f04088665977d127c2034caaa0adcb820\
    e2f3e0ffacd608df43cf77f76585d',
                    'imageManifestMediaType': self.manifest_media_type,
                    'imagePushedAt': datetime(
                        2021, 12, 15, 19, 9, 13, tzinfo=tzlocal()),
                    'imageScanFindingsSummary': {
                        'findingSeverityCounts': {'LOW': 1},
                        'imageScanCompletedAt': datetime(
                            2021, 12, 15, 19, 9, 17, tzinfo=tzlocal()),
                        'vulnerabilitySourceUpdatedAt': datetime(
                            2021, 12, 14, 13, 8, 57, tzinfo=tzlocal())
                    },
                    'imageScanStatus': {
                        'description': self._scan_completed,
                        'status': 'COMPLETE'
                    },
                    'imageSizeInBytes': 41752369,
                    'imageTags': ['14-0.1.1'],
                    'registryId': self.registry_id,
                    'repositoryName': self.only_repository
                },
                {
                    'artifactMediaType': self.artifact_media_type,
                    'imageDigest': 'sha256:d20b69e3f9da4d969f50ee3f8a40889abc7\
    8cd48f26d8238f946451fcffba9e3',
                    'imageManifestMediaType': self.manifest_media_type,
                    'imagePushedAt': datetime(
                        2021, 12, 1, 17, 27, 27, tzinfo=tzlocal()),
                    'imageScanFindingsSummary': {
                        'findingSeverityCounts': {'LOW': 1},
                        'imageScanCompletedAt': datetime(
                            2021, 12, 1, 17, 27, 31, tzinfo=tzlocal()),
                        'vulnerabilitySourceUpdatedAt': datetime(
                            2021, 11, 24, 13, 11, 37, tzinfo=tzlocal())
                    },
                    'imageScanStatus': {
                        'description': self._scan_completed,
                        'status': 'COMPLETE'
                    },
                    'imageSizeInBytes': 30008240,
                    'imageTags': ['12-0.1.0'],
                    'registryId': self.registry_id,
                    'repositoryName': self.only_repository
                }
            ]
        }

    def describe_images(self, registryId: str, repositoryName: str):

        # see https://github.com/boto/botocore/blob/develop/tests/unit/test_exceptions.py
        if self._force_exception:
            response = {
                'ResponseMetadata': {
                    'HTTPHeaders': {},
                    'HTTPStatusCode': 503,
                    'MaxAttemptsReached': True,
                    'RetryAttempts': 4,
                },
                'Error': {'Code': 401}
            }
            raise ClientError(response, 'DescribeImages')  # type: ignore

        return self._payload

    def break_one_image_payload(self):
        self._payload['imageDetails'][0].pop('imageSizeInBytes')

    def break_all_images_payload(self):
        self._payload.pop('imageDetails')

    def force_client_exception(self):
        self._force_exception = True


def test_ecr_image_class():
    assert inspect.isclass(ECRImage)

    for method in '__init__ to_list size_in_mb fields'.split():
        assert inspect.isfunction(getattr(ECRImage, method))


def test_ecr_image_methods(new_instance):
    for method in '__init__ to_list size_in_mb'.split():
        assert inspect.ismethod(getattr(new_instance, method))


def test_ecr_image_attributes(new_instance, now):
    for attribute in 'name status size pushed_at findings'.split():
        assert hasattr(new_instance, attribute)

    assert new_instance.status == 'COMPLETE'
    assert new_instance.size == 62380145
    assert new_instance.pushed_at == str(now)
    assert new_instance.findings == {'UNDEFINED': 1}


def test_ecr_image_size_in_mb(new_instance):
    assert new_instance.size_in_mb() == 60.9181103515625


def test_ecr_image_to_list(new_instance, now):
    assert new_instance.to_list() == [
        '012345678910.dkr.ecr.us-east-2.amazonaws.com/foobar:0.1.0',
        'COMPLETE',
        '60.92',
        str(now),
        {'UNDEFINED': 1}
    ]


RESPONSE_HEADER = ['Image', 'Scan status', 'Size (MB)', 'Pushed at', 'Vulnerabilities']


def test_ecr_image_fields(new_instance):
    expected = RESPONSE_HEADER
    assert new_instance.fields() == expected


def test_ecr_image_cmp(registry_id):
    client = AWSECRClientStub(registry_id)
    repository = 'nodejs'
    resp = client.describe_images(registryId=registry_id,
                                  repositoryName=repository)
    images = []

    for image in resp['imageDetails']:
        images.append(ECRImage(registry_id, repository, image))

    assert images[0].__cmp__(images[1]) == -1
    assert images[0].__cmp__(images[0]) == 0
    assert images[1].__cmp__(images[0]) == 1


def test_ecr_image_exception(image_details):
    image_details.pop('imageSizeInBytes')

    with pytest.raises(InvalidPayload) as excinfo:
        ECRImage('0123', 'foobar', image_details)

    assert 'describe_images' in str(excinfo.value)


def test_ecr_image_no_scan_summary(image_details):
    image_details.pop('imageScanFindingsSummary')
    instance = ECRImage('0123', 'foobar', image_details)
    assert instance.findings == {'UNDEFINED': -1}


def test_list_ecr_ansi(registry_id):
    client = AWSECRClientStub(registry_id)
    result = list_ecr(account_id=registry_id, repository='nodejs',
                      ecr_client=client, ansi=_ansi_vulnerabilities)
    assert result.__class__.__name__ == 'list'
    expected = [
        RESPONSE_HEADER,
        ['012345678910.dkr.ecr.us-east-1.amazonaws.com/nodejs:12-0.1.0',
         'COMPLETE', '29.3',
         str(datetime(2021, 12, 1, 17, 27, 27, tzinfo=tzlocal())),
         '\x1b[31m0\x1b[0m/\x1b[91m0\x1b[0m/\x1b[33m0\x1b[0m/\x1b[93m1\x1b[0m/\x1b[92m0\x1b[0m/\x1b[32m0\x1b[0m'],
        ['012345678910.dkr.ecr.us-east-1.amazonaws.com/nodejs:12-0.1.1',
         'COMPLETE', '29.3',
         str(datetime(2021, 12, 15, 18, 54, 58, tzinfo=tzlocal())),
         '\x1b[31m0\x1b[0m/\x1b[91m0\x1b[0m/\x1b[33m0\x1b[0m/\x1b[93m1\x1b[0m/\x1b[92m0\x1b[0m/\x1b[32m0\x1b[0m'],
        ['012345678910.dkr.ecr.us-east-1.amazonaws.com/nodejs:14-0.1.0',
         'COMPLETE', '40.73',
         str(datetime(2021, 12, 1, 18, 26, 46, tzinfo=tzlocal())),
         '\x1b[31m0\x1b[0m/\x1b[91m0\x1b[0m/\x1b[33m1\x1b[0m/\x1b[93m0\x1b[0m/\x1b[92m0\x1b[0m/\x1b[32m0\x1b[0m'],
        ['012345678910.dkr.ecr.us-east-1.amazonaws.com/nodejs:14-0.1.1',
         'COMPLETE', '40.77',
         str(datetime(2021, 12, 15, 19, 9, 13, tzinfo=tzlocal())),
         '\x1b[31m0\x1b[0m/\x1b[91m0\x1b[0m/\x1b[33m0\x1b[0m/\x1b[93m1\x1b[0m/\x1b[92m0\x1b[0m/\x1b[32m0\x1b[0m'],
    ]

    assert result == expected


def test_list_ecr(registry_id):
    client = AWSECRClientStub(registry_id)
    result = list_ecr(account_id=registry_id, repository='nodejs',
                      ecr_client=client)
    assert result.__class__.__name__ == 'list'
    expected = [
        RESPONSE_HEADER,
        ['012345678910.dkr.ecr.us-east-1.amazonaws.com/nodejs:12-0.1.0',
         'COMPLETE', '29.3',
         str(datetime(2021, 12, 1, 17, 27, 27, tzinfo=tzlocal())),
         {'LOW': 1}],
        ['012345678910.dkr.ecr.us-east-1.amazonaws.com/nodejs:12-0.1.1',
         'COMPLETE', '29.3',
         str(datetime(2021, 12, 15, 18, 54, 58, tzinfo=tzlocal())),
         {'LOW': 1}],
        ['012345678910.dkr.ecr.us-east-1.amazonaws.com/nodejs:14-0.1.0',
         'COMPLETE', '40.73',
         str(datetime(2021, 12, 1, 18, 26, 46, tzinfo=tzlocal())),
         {'MEDIUM': 1}],
        ['012345678910.dkr.ecr.us-east-1.amazonaws.com/nodejs:14-0.1.1',
         'COMPLETE', '40.77',
         str(datetime(2021, 12, 15, 19, 9, 13, tzinfo=tzlocal())),
         {'LOW': 1}],
    ]

    assert result == expected


def test_list_ecr_client_exception(registry_id):
    client = AWSECRClientStub(registry_id)
    client.force_client_exception()

    with pytest.raises(ECRClientException) as excinfo:
        list_ecr(account_id=registry_id, repository='nodejs',
                 ecr_client=client)

    assert 'DescribeImages' in str(excinfo.value)


def test_list_ecr_invalid_payload(registry_id):
    client = AWSECRClientStub(registry_id)
    client.break_all_images_payload()

    with pytest.raises(InvalidPayload) as excinfo:
        list_ecr(account_id=registry_id, repository='nodejs',
                 ecr_client=client)

    assert 'imageDetails' in str(excinfo.value)


def test_list_ecr_invalid_image_payload(registry_id):
    client = AWSECRClientStub(registry_id)
    client.break_one_image_payload()

    with pytest.raises(InvalidPayload) as excinfo:
        list_ecr(account_id=registry_id, repository='nodejs',
                 ecr_client=client)

    assert 'imageSizeInBytes' in str(excinfo.value)
