"""Main module."""

import boto3
from typing import Tuple, List, Generator, Dict, Deque, Any
import os
import docker
import base64
from collections import deque


class BaseException(Exception):
    pass


class MissingAWSEnvVar(BaseException):
    def __init__(self) -> None:
        self.message = 'Missing AWS environment variables to configure access'

    def __str__(self) -> str:
        return self.message


class InvalidPayload(BaseException):
    def __init__(self, missing_key: str, api_method: str):
        self.message = f'Unexpected payload received, missing "{missing_key}" \
from "{api_method}" call response'

    def __str__(self) -> str:
        return self.message


def aws_account_info() -> Tuple[str, str]:
    client = boto3.client('sts')

    try:
        account_id = client.get_caller_identity()['Account']
        iam_user = client.get_caller_identity()['Arn'].split('/')[1]
    except ValueError as e:
        raise InvalidPayload(missing_key=str(e),
                             api_method='get_authorization_token')
    return tuple([account_id, iam_user])


def registry_fqdn(account_id: str, region: str = 'us-east-1') -> str:
    return f'{account_id}.dkr.ecr.{region}.amazonaws.com'


def login_ecr(account_id: str,
              region: str = 'us-east-1') -> Tuple[dict, docker.DockerClient]:
    ecr = boto3.client('ecr')
    response = ecr.get_authorization_token(registryIds=[account_id])

    try:
        token = response['authorizationData'][0]['authorizationToken']
    except ValueError as e:
        raise InvalidPayload(missing_key=str(e),
                             api_method='get_authorization_token')

    username, password = base64.b64decode(token).decode('utf-8').split(':')
    docker_client = docker.DockerClient(base_url='unix://var/run/docker.sock')

    resp = docker_client.login(
        username=username,
        password=password,
        registry=registry_fqdn(account_id=account_id, region=region),
        reauth=True
    )
    return tuple([resp, docker_client])


class ECRImage():
    def __init__(self, registry: str, repository: str, image: Dict[str, Any]):
        self.name: str = f"{registry}/{repository}:{image['imageTags'][0]}"
        self.status: str = image['imageScanStatus']['status']
        findings: Dict[str, int]
        findings = image['imageScanFindingsSummary']['findingSeverityCounts']
        self.vulnerabilities: int = sum(findings.values())

    def to_list(self) -> List[str]:
        return [self.name, self.status, self.vulnerabilities]

    @staticmethod
    def fields() -> List[str]:
        return ['Image', 'Scan status', 'Vulnerabilities']


def list_ecr(account_id: str,
             repository: str,
             region: str = 'us-east-1') -> List[List[str]]:
    ecr = boto3.client('ecr')
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

    return list(images)


def image_push(account_id: str,
               repository: str, current_image: str) -> Generator:
    registry = registry_fqdn(account_id=account_id)
    print(f'Authenticating against {registry}... ', end='')
    ignore, client = login_ecr(account_id)
    print('done')
    image = client.images.get(current_image)
    image_tag = current_image.split(':')[1]
    image.tag(repository=f'{registry}/{repository}',
              tag=image_tag)

    for line in client.images.push(repository=f'{registry}/{repository}',
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

    def list_repositories(self) -> List[str]:
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
