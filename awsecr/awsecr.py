"""Main module."""

import boto3
from typing import Tuple, List, Set, Generator
import os
import docker
import base64
from collections import deque


class BaseException(Exception):
    pass


class MissingAWSEnvVar(BaseException):
    def __init__(self):
        self.message = 'Missing configuration of awscli (AWS_PROFILE \
environment variable)'

    def __str__(self):
        return self.message


class InvalidPayload(BaseException):
    def __init__(self, missing_key: str, api_method: str):
        self.message = f'Unexpected payload received, missing "{missing_key}" \
from "{api_method}" call response'

    def __str__(self):
        return self.message


def aws_account_info() -> Tuple[str, str]:
    client = boto3.client('sts')

    try:
        account_id = client.get_caller_identity()['Account']
        iam_user = client.get_caller_identity()['Arn'].split('/')[1]
    except ValueError as e:
        raise InvalidPayload(missing_key=str(e),
                             api_method='get_authorization_token')
    return account_id, iam_user


def registry_fqdn(account_id: str, region: str = 'us-east-1'):
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
    return resp, docker_client


def list_ecr(account_id: str,
             repository: str,
             region: str = 'us-east-1') -> List[List[str]]:
    ecr = boto3.client('ecr')
    images: deque = deque()
    images.append(['Image', 'Scan status', 'Vulnerabilities'])
    registry = registry_fqdn(account_id=account_id, region=region)

    try:
        resp = ecr.describe_images(registryId=account_id,
                                   repositoryName=repository)

        for image in resp['imageDetails']:
            images.append([
                f"{registry}/{repository}:{image['imageTags'][0]}",
                image['imageScanStatus']['status'],
                len(image['imageScanFindingsSummary']['findingSeverityCounts'])
                ])
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
    """List allowed ECR repositories."""
    def __init__(self, user: str, client=boto3.client('iam')):

        if 'AWS_PROFILE' not in os.environ:
            raise MissingAWSEnvVar()

        self.client = client
        self.user = user

    def list_repositories(self) -> Set[str]:
        pass

