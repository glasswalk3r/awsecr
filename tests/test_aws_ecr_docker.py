import inspect
import docker

from awsecr.docker import BaseDockerClient, DockerClientLocal


def test_docker_base_class():
    assert inspect.isclass(BaseDockerClient)

    for method in 'login image push'.split():
        assert inspect.isfunction(getattr(BaseDockerClient, method))


def test_concrete_class():
    assert inspect.isclass(DockerClientLocal)
    assert issubclass(DockerClientLocal, BaseDockerClient)


def test_concrete_init():
    client = DockerClientLocal()
    assert inspect.ismethod(getattr(client, '__init__'))
    assert hasattr(client, '_client')
    assert type(client._client) == docker.DockerClient
    assert client._base_url.startswith('unix:')
