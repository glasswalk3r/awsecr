import boto3
from typing import List, Dict, Deque, Any
import os
from collections import deque

from awsecr.exception import (
    InvalidPayload,
    MissingAWSEnvVar
)


class ECRRepos:
    """List allowed ECR repositories from default registry."""
    def __init__(self, client=boto3.client('ecr')) -> None:
        """Configure a class instance.

        Arguments:
        client -- an AWS ECR client that behaves like boto3.client('ecr').
        Optional, defaults to boto3.client('ecr')

        Returns None.
        """

        if 'AWS_PROFILE' not in os.environ:
            secret = 'AWS_SECRET_ACCESS_KEY' in os.environ
            access = 'AWS_ACCESS_KEY_ID' in os.environ

            if not (secret and access):
                raise MissingAWSEnvVar()

        self.client = client

    def list_repositories(self) -> Deque[List[str]]:
        """List the repositories under the registry.

        Returns a collections.deque, where each entry is a list of strings.
        """
        resp = self.client.describe_repositories()
        all: Deque[List[str]] = deque()
        all.append(ECRRepo.fields())
        temp = deque()

        try:
            for repo in resp['repositories']:
                temp.append(ECRRepo(repo))
        except KeyError as e:
            raise InvalidPayload(missing_key=str(e),
                                 api_method='describe_repositories')

        intermediary = list(temp)
        intermediary.sort()

        for repo in intermediary:
            all.append(repo.to_list())

        return all


class ECRRepo:
    """Represent a single ECR repository."""
    def __init__(self, raw: Dict[str, Any]) -> None:
        """Configure a class instance.

        Arguments:
        raw -- a dict with the details of the repository, as returned by boto3
        ECR client describe_repositories() method.

        Returns None.
        """
        try:
            self.name = raw['repositoryName']
            self.uri = raw['repositoryUri']
            self.tag_mutability = raw['imageTagMutability']
            self.scan_on_push = raw['imageScanningConfiguration']['scanOnPush']
        except KeyError as e:
            raise InvalidPayload(missing_key=str(e),
                                 api_method='describe_repositories')

    def __lt__(self, other):
        return self.name < other.name

    def __gt__(self, other):
        return self.name > other.name

    def __str__(self) -> str:
        return str(self.to_list())

    def to_list(self) -> List[str]:
        """Represent the instance data as a list of strings.

        Require no arguments, returns a list of strings.
        """
        return [self.name, self.uri, self.tag_mutability, self.scan_on_push]

    @staticmethod
    def fields() -> List[str]:
        """Return all the fields names of a instance as a list of strings."""
        return ['Name', 'URI', 'Tag Mutability', 'Scan on push?']
