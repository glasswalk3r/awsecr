import pytest
import inspect
from collections import deque

from awsecr.exception import (
    MissingAWSEnvVar,
    InvalidPayload
)
from awsecr.repository import ECRRepos, ECRRepo


class AWSECRClientStub:
    def __init__(self):
        registry = '012345678910.dkr.ecr.us-east-1.amazonaws.com'

        self._data = {
            'repositories': [
                {
                    'repositoryName': 'nodejs',
                    'repositoryUri': f'{registry}/nodejs',
                    'imageTagMutability': 'IMMUTABLE',
                    'imageScanningConfiguration': {'scanOnPush': True}
                },
                {
                    'repositoryName': 'spark-py',
                    'repositoryUri': f'{registry}/spark-py',
                    'imageTagMutability': 'MUTABLE',
                    'imageScanningConfiguration': {'scanOnPush': False}
                },
                {
                    'repositoryName': 'hive-metastore',
                    'repositoryUri': f'{registry}/hive-metastore',
                    'imageTagMutability': 'IMMUTABLE',
                    'imageScanningConfiguration': {'scanOnPush': True}
                },
            ]
        }
        self.tag_to_remove = 'imageTagMutability'

    def corrupt_data(self):
        self._data['repositories'][0].pop(self.tag_to_remove)

    def describe_repositories(self):
        return self._data

    def repos_to_list(self):
        result = deque()
        result.append(['Name', 'URI', 'Tag Mutability', 'Scan on push?'])

        # "mannually" sorting
        isc = 'imageScanningConfiguration'

        for i in [2, 0, 1]:
            result.append([
                self._data['repositories'][i]['repositoryName'],
                self._data['repositories'][i]['repositoryUri'],
                self._data['repositories'][i]['imageTagMutability'],
                self._data['repositories'][i][isc]['scanOnPush']
            ])

        return result


@pytest.fixture
def new_repos(monkeypatch):
    monkeypatch.setenv("AWS_PROFILE", "dev")
    return ECRRepos()


def test_ecr_repos_no_aws_cfg(monkeypatch):
    monkeypatch.delenv("AWS_PROFILE", False)
    monkeypatch.delenv("AWS_SECRET_ACCESS_KEY", False)
    monkeypatch.delenv("AWS_ACCESS_KEY_ID", False)

    with pytest.raises(MissingAWSEnvVar) as excinfo:
        ECRRepos()

    assert 'AWS environment' in str(excinfo.value)


def test_ecr_repos(new_repos):
    assert inspect.isclass(ECRRepos)
    methods = tuple(['list_repositories'])

    for method in methods:
        assert inspect.ismethod(getattr(new_repos, method))


def test_ecr_repos_list_repositories(new_repos):
    new_repos.client = AWSECRClientStub()
    actual = new_repos.list_repositories()
    assert actual.__class__.__name__ == 'deque'
    assert actual == new_repos.client.repos_to_list()


def test_ecr_repos_list_repositories_exception(new_repos):
    new_repos.client = AWSECRClientStub()
    new_repos.client.corrupt_data()

    with pytest.raises(InvalidPayload) as excinfo:
        new_repos.list_repositories()

    assert 'describe_repositories' in str(excinfo.value)
    assert new_repos.client.tag_to_remove in str(excinfo.value)


@pytest.fixture
def new_repo():
    instance = AWSECRClientStub()
    return ECRRepo(instance.describe_repositories()['repositories'][0])


def test_ecr_repository_class():
    assert inspect.isclass(ECRRepo)

    for method in '__init__ to_list fields'.split():
        assert inspect.isfunction(getattr(ECRRepo, method))


def test_ecr_repository_methods(new_repo):
    for method in '__init__ to_list'.split():
        assert inspect.ismethod(getattr(new_repo, method))


def test_ecr_repository_instance_exception(registry_id):
    with pytest.raises(InvalidPayload) as excinfo:
        ECRRepo({})

    assert 'describe_repositories' in str(excinfo.value)


def test_ecr_repository_to_list(new_repo):
    assert new_repo.to_list() == [
        'nodejs',
        '012345678910.dkr.ecr.us-east-1.amazonaws.com/nodejs',
        'IMMUTABLE',
        True
    ]


def test_ecr_repository_fields():
    assert ECRRepo.fields() == [
        'Name', 'URI', 'Tag Mutability', 'Scan on push?']
