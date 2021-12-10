"""Main module."""

import boto3
from typing import Tuple, List, Generator, Dict, Deque, Any, Union, Literal
import os
import docker
import base64
from collections import deque
from mypy_boto3_ecr.type_defs import ImageDetailTypeDef
import mypy_boto3_sts
import mypy_boto3_ecr
import sys
from botocore.exceptions import ClientError
from awsecr.exception import (
    InvalidPayload,
    MissingAWSEnvVar,
    ECRClientException
)


def account_info(
                    client: mypy_boto3_sts.Client = boto3.client('sts')
                ) -> Tuple[str, ...]:

    try:
        resp = client.get_caller_identity()
        account_id: str = resp['Account']
        iam_user: str = resp['Arn'].split('/')[1]
        region: str = client.meta.region_name
    except KeyError as e:
        raise InvalidPayload(missing_key=str(e),
                             api_method='get_authorization_token')
    return tuple([account_id, iam_user, region])


def registry_fqdn(account_id: str, region: str) -> str:
    return f'{account_id}.dkr.ecr.{region}.amazonaws.com'


def _extract_credentials(token: str) -> Tuple[str, ...]:
    decoded = base64.b64decode(token).decode('utf-8')
    return tuple(decoded.split(':'))


def _ecr_token(account_id: str,
               client: mypy_boto3_ecr.Client = boto3.client('ecr'),
               region: str = None) -> Tuple[str, ...]:

    if region is None:
        region = client.meta.region_name

    response = client.get_authorization_token(registryIds=[account_id])

    try:
        token = response['authorizationData'][0]['authorizationToken']
    except KeyError as e:
        raise InvalidPayload(missing_key=str(e),
                             api_method='get_authorization_token')

    return tuple([token, region])


def login_ecr(account_id: str,
              region: str = None) -> Tuple[Any, ...]:

    token, region = _ecr_token(account_id=account_id, region=region)
    username, password = _extract_credentials(token)
    docker_client = docker.DockerClient(base_url='unix://var/run/docker.sock')

    resp = docker_client.login(
        username=username,
        password=password,
        registry=registry_fqdn(account_id=account_id, region=region),
        reauth=True
    )
    return tuple([resp, docker_client])


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
            summary = image['imageScanFindingsSummary']
            findings = summary['findingSeverityCounts']
            self.size: int = image['imageSizeInBytes']
            self.pushed_at: str = str(image['imagePushedAt'])
        except KeyError as e:
            print(f'Missing image scanning {e} information', sys.stderr)
            findings = {'UNDEFINED': 0}

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


def list_ecr(account_id: str,
             repository: str,
             region: str = None) -> List[List[str]]:
    ecr = boto3.client('ecr')

    if region is None:
        region = ecr.meta.region_name

    images: Deque[List[str]]
    images = deque()
    images.append(ECRImage.fields())
    registry = registry_fqdn(account_id=account_id, region=region)

    try:
        resp = ecr.describe_images(registryId=account_id,
                                   repositoryName=repository)

        for image in resp['imageDetails']:
            images.append(ECRImage(registry, repository, image).to_list())
    except ValueError as e:
        raise InvalidPayload(missing_key=str(e),
                             api_method='get_authorization_token')
    except ClientError as e:
        raise ECRClientException(error_code=e.response['Error']['Code'],
                                 message=str(e))

    return list(images)


def image_push(account_id: str, repository: str, region: str,
               current_image: str) -> Generator:
    registry = registry_fqdn(account_id=account_id, region=region)
    print(f'Authenticating against {registry}... ', end='')
    ignore, docker = login_ecr(account_id)
    print('done')
    image = docker.images.get(current_image)
    image_tag = current_image.split(':')[1]
    image.tag(repository=f'{registry}/{repository}',
              tag=image_tag)

    for line in docker.images.push(repository=f'{registry}/{repository}',
                                   tag=image_tag,
                                   stream=True,
                                   decode=True):

        if 'status' in line:
            if line['status'] == 'Pushing':
                if 'progress' in line and 'id' in line:
                    yield f"layer: {line['id']}, progress: {line['progress']}"
            else:
                yield '.'


class ECRRepos:
    """List allowed ECR repositories from default registry."""
    def __init__(self, client=boto3.client('ecr')) -> None:

        if 'AWS_PROFILE' not in os.environ:
            secret = 'AWS_SECRET_ACCESS_KEY' in os.environ
            access = 'AWS_ACCESS_KEY_ID' in os.environ

            if not (secret and access):
                raise MissingAWSEnvVar()

        self.client = client

    def list_repositories(self) -> Deque[List[str]]:
        resp = self.client.describe_repositories()
        all: Deque[List[str]] = deque()
        all.append(ECRRepo.fields())

        try:
            for repo in resp['repositories']:
                all.append(ECRRepo(repo).to_list())
        except KeyError as e:
            raise InvalidPayload(missing_key=str(e),
                                 api_method='describe_repositories')

        return all


class ECRRepo:
    """Represent a single ECR repository."""
    def __init__(self, raw: Dict[str, Any]):
        try:
            self.name = raw['repositoryName']
            self.uri = raw['repositoryUri']
            self.tag_mutability = raw['imageTagMutability']
            self.scan_on_push = raw['imageScanningConfiguration']['scanOnPush']
        except KeyError as e:
            raise InvalidPayload(missing_key=str(e),
                                 api_method='describe_repositories')

    def to_list(self) -> List[str]:
        return [self.name, self.uri, self.tag_mutability, self.scan_on_push]

    @staticmethod
    def fields() -> List[str]:
        return ['Name', 'URI', 'Tag Mutability', 'Scan on push?']
