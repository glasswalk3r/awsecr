"""Docker client module."""
import docker
from abc import ABCMeta, abstractmethod
from typing import Dict

# {'IdentityToken': '', 'Status': 'Login Succeeded'}
LoginResponse = Dict[str, str]


class BaseDockerClient(metaclass=ABCMeta):
    """Wrapper for Docker clients abstract base class."""
    @abstractmethod
    def login(self, username, password, registry, reauth) -> LoginResponse:  # pragma: no cover
        raise NotImplementedError('Not implemented')

    @abstractmethod
    def image(self, image_name: str) -> docker.models.images.Image:  # pragma: no cover
        pass

    @abstractmethod
    def push(self, registry: str, tag: str, stream: bool, decode: bool):  # pragma: no cover
        pass


class DockerClientLocal(BaseDockerClient):
    """Implementation of a Docker client using docker.DockerClient.

    This class wraps docker.DockerClient in order to follow the interface defined by awsecr.awsecr.BaseDockerClient.
    """

    def __init__(self):
        """Create a new instance.

        It will connect to a Docker daemon running locally by default.
        """
        self._base_url = 'unix://var/run/docker.sock'
        self._client = docker.DockerClient(base_url=self._base_url)

    def login(self, username: str, password: str, registry: str, reauth: bool) -> LoginResponse:  # pragma: no cover
        return self._client.login(
            username=username,
            password=password,
            registry=registry,
            reauth=reauth
        )

    def image(self, image_name: str) -> docker.models.images.Image:  # pragma: no cover
        return self._client.images.get(image_name)

    def push(self, registry: str, tag: str, stream: bool, decode: bool):  # pragma: no cover
        return self._client.push(repository=registry, tag=tag, stream=stream, decode=stream)

    def __str__(self):
        return '{0}, base URL={1}'.format(self._client.__class__, self._base_url)
