"""ECR image module."""
from typing import List, Dict, Union, Literal, Deque, Callable
from mypy_boto3_ecr.type_defs import ImageDetailTypeDef
from botocore.exceptions import ClientError
from collections import deque

from awsecr.exception import InvalidPayload, ECRClientException
from awsecr.awsecr import registry_fqdn

Vulnerabilities = Dict[Union[Literal['CRITICAL'], Literal['HIGH'],
                             Literal['INFORMATIONAL'], Literal['LOW'],
                             Literal['MEDIUM'], Literal['UNDEFINED']], int]


class ECRImage():
    """Represent a single ECR repository image."""
    ecr_client_creator = 'describe_images'

    def __init__(self,
                 registry: str,
                 repository: str,
                 image: ImageDetailTypeDef):
        """Configure a class instance.

        Arguments:
        registry -- the AWS ECR registry name
        repository -- the AWS ECR repository name
        image -- the result of boto3 ECR client describe_images method
        """

        self.findings: Vulnerabilities

        try:
            self.name: str = image['imageTags'][0]
            self.fullname: str = f"{registry}/{repository}:{self.name}"
            self.status: str = image['imageScanStatus']['status']
            self.size: int = image['imageSizeInBytes']
            self.pushed_at: str = str(image['imagePushedAt'])

            if 'imageScanFindingsSummary' not in image:
                self.findings = {'UNDEFINED': -1}
            else:
                summary = image['imageScanFindingsSummary']
                self.findings = summary['findingSeverityCounts']
        except KeyError as e:
            raise InvalidPayload(str(e), self.ecr_client_creator)

    def to_list(self) -> List[str]:
        """Convert a list attributes to a list of strings."""
        return [self.fullname, self.status, '{:.4n}'.format(self.size_in_mb()),
                self.pushed_at, self.findings]

    def size_in_mb(self):
        """Convert the image size to MB."""
        return self.size / (1024 * 1000)

    @staticmethod
    def fields() -> List[str]:
        """Return all the fields names of a instance as a list of strings."""
        return ['Image', 'Scan status', 'Size (MB)', 'Pushed at',
                'Vulnerabilities']

    def __cmp__(self, other):
        if self.name < other.name:
            return -1
        else:
            if self.name == other.name:
                return 0
            return 1


def list_ecr(account_id: str,
             repository: str,
             ecr_client,
             region: str = None,
             ansi: Callable = None) -> List[List[str]]:
    """List all ECR images from a repository.

    Arguments:

    account_id -- the AWS account ID
    repository -- the name of the ECR repository
    ecr_client -- the AWS ECR client
    region -- the AWS region where the repository is. Optional, defaults to the
    default region of the given ecr_client.
    ansi -- Optional, a callable to be used to format the vulnerabilities scan
    result and return a string. The callable should expect as parameters a dict
    as ECRImage.findings and a string as ECRImage.status.
    """

    if region is None:
        region = ecr_client.meta.region_name

    images: Deque[List[str]]
    images = deque()
    registry = registry_fqdn(account_id=account_id, region=region)

    try:
        resp = ecr_client.describe_images(registryId=account_id,
                                          repositoryName=repository)

        if ansi:
            for image in resp['imageDetails']:
                instance = ECRImage(registry, repository, image)
                instance.findings = ansi(instance.findings, instance.status)
                images.append(instance.to_list())
        else:
            for image in resp['imageDetails']:
                images.append(ECRImage(registry, repository, image).to_list())
    except ValueError as e:
        raise InvalidPayload(missing_key=str(e),
                             api_method='get_authorization_token')
    except ClientError as e:
        print(e)
        raise ECRClientException(error_code=e.response['Error']['Code'],
                                 message=str(e))

    result = list(images)
    result.sort()
    result.insert(0, ECRImage.fields())
    return result
