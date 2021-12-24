"""ECR image module."""
from typing import List, Dict, Union, Literal
from mypy_boto3_ecr.type_defs import ImageDetailTypeDef

from awsecr.exception import InvalidPayload


class ECRImage():
    def __init__(self,
                 registry: str,
                 repository: str,
                 image: ImageDetailTypeDef):

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
            raise InvalidPayload(str(e), 'describe_images')

        self.vulnerabilities: int = sum(findings.values())

    def to_list(self) -> List[str]:
        return [self.name, self.status, '{:.4n}'.format(self.size_in_mb()),
                self.pushed_at, str(self.vulnerabilities)]

    def size_in_mb(self):
        return self.size / (1024 * 1000)

    @staticmethod
    def fields() -> List[str]:
        return ['Image', 'Scan status', 'Size (MB)', 'Pushed at',
                'Vulnerabilities']
