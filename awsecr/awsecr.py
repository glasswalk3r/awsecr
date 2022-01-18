"""Main module."""
import boto3
from typing import Tuple, Generator, Any
import docker
import base64
import mypy_boto3_sts
import mypy_boto3_ecr

from awsecr.exception import (
    InvalidPayload
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
    """Generate a ECR registry FQDN.

    Arguments:
    account_id -- the AWS account ID
    region -- the AWS region of the ECR registry

    Returns the FQDN as a string.
    """
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
