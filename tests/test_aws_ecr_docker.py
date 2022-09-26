# import pytest
import inspect
import docker

from awsecr.docker import BaseDockerClient, DockerClient


def test_docker_base_class():
    assert inspect.isclass(BaseDockerClient)

    for method in 'login image push'.split():
        assert inspect.isfunction(getattr(BaseDockerClient, method))


def test_concrete_class():
    assert inspect.isclass(DockerClient)
    assert issubclass(DockerClient, BaseDockerClient)


def test_concrete_init():
    client = DockerClient()
    assert inspect.ismethod(getattr(client, '__init__'))
    assert hasattr(client, '_client')
    assert type(client._client) == docker.DockerClient
    assert client._base_url.startswith('unix:')
