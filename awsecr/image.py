"""ECR image module."""
from typing import List, Dict, Union, Literal
from mypy_boto3_ecr.type_defs import ImageDetailTypeDef

from awsecr.exception import InvalidPayload


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

        findings: Dict[Union[Literal['CRITICAL'], Literal['HIGH'],
                             Literal['INFORMATIONAL'], Literal['LOW'],
                             Literal['MEDIUM'], Literal['UNDEFINED']], int]

        try:
            self.name: str = f"{registry}/{repository}:{image['imageTags'][0]}"
            self.status: str = image['imageScanStatus']['status']
            self.size: int = image['imageSizeInBytes']
            self.pushed_at: str = str(image['imagePushedAt'])
            summary = image['imageScanFindingsSummary']
            findings = summary['findingSeverityCounts']
        except KeyError as e:
            raise InvalidPayload(str(e), self.ecr_client_creator)

        self.vulnerabilities: int = sum(findings.values())

    def to_list(self) -> List[str]:
        """Convert a list attributes to a list of strings."""
        return [self.name, self.status, '{:.4n}'.format(self.size_in_mb()),
                self.pushed_at, str(self.vulnerabilities)]

    def size_in_mb(self):
        """Convert the image size to MB."""
        return self.size / (1024 * 1000)

    @staticmethod
    def fields() -> List[str]:
        """Return all the fields names of a instance as a list."""
        return ['Image', 'Scan status', 'Size (MB)', 'Pushed at',
                'Vulnerabilities']
