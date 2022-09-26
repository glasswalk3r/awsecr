"""Main module."""
import boto3
from typing import Tuple, Generator, Optional, Dict
import docker
import base64
import mypy_boto3_sts
import mypy_boto3_ecr
from abc import ABCMeta, abstractmethod

from awsecr.exception import InvalidPayload, InvalidResponseStatus


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


# {'IdentityToken': '', 'Status': 'Login Succeeded'}
LoginResponse = Dict[str, str]


class BaseDockerClient(metaclass=ABCMeta):
    @abstractmethod
    def login(self, username, password, registry, reauth) -> LoginResponse:
        pass

    @abstractmethod
    def image(self, image_name: str) -> docker.models.images.Image:
        pass

    @abstractmethod
    def push(self, registry: str, tag: str, stream: bool, decode: bool):
        pass


class DockerClient(BaseDockerClient):
    def __init__(self):
        self._client = docker.DockerClient(base_url='unix://var/run/docker.sock')

    def login(self, username, password, registry, reauth) -> LoginResponse:
        return self._client.login(
            username=username,
            password=password,
            registry=registry,
            reauth=reauth
        )

    def image(self, image_name: str) -> docker.models.images.Image:
        return self._client.images.get(image_name)

    def push(self, registry: str, tag: str, stream: bool, decode: bool):
        return self._client.push(repository=registry, tag=tag, stream=stream, decode=stream)


def login_ecr(account_id: str,
              docker_client: BaseDockerClient = DockerClient(),
              region: Optional[str] = None) -> BaseDockerClient:

    token: str
    token, region = _ecr_token(account_id=account_id, region=region)
    username: str
    password: str
    username, password = _extract_credentials(token)

    response: LoginResponse = docker_client.login(
        username=username,
        password=password,
        registry=registry_fqdn(account_id=account_id, region=region),
        reauth=True
    )

    if 'Status' not in response:
        raise ValueError(f'Invalid response, missing "Status" key: "{response}"')

    if response['Status'] != 'Login Succeeded':
        raise InvalidResponseStatus(response['Status'])

    return docker_client


def image_push(account_id: str, repository: str, region: str, docker: BaseDockerClient,
               current_image: str) -> Generator:
    registry = registry_fqdn(account_id=account_id, region=region)
    image = docker.image(current_image)
    image_tag = current_image.split(':')[1]
    image.tag(repository=f'{registry}/{repository}',
              tag=image_tag)

    for line in docker.push(registry=f'{registry}/{repository}', tag=image_tag, stream=True, decode=True):

        if 'status' in line:
            if line['status'] == 'Pushing':
                if 'progress' in line and 'id' in line:
                    yield f"layer: {line['id']}, progress: {line['progress']}"
            else:
                yield '.'
