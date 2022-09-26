"""Shares code between tests."""

import base64
from datetime import datetime
import os


class AwsMetaStub:
    """Stub for the botocore.client instances.

    This class exists only to provide the "meta" attribute for an client.
    """
    region_name = os.environ['AWS_DEFAULT_REGION']  # define here for DRY using conftest.py


class AwsEcrStub():
    """Stub for a botocore.client.ECR instance."""
    meta = AwsMetaStub()

    @staticmethod
    def ecr_token():
        """Return a string encoded with MIME64.

        This method is not available in a botocore.client.ECR instance, exists here only to facilitate testing.
        """
        return base64.b64encode(b'AWS:foobar')

    def get_authorization_token(self, registryIds):
        return self.auth_data

    def __init__(self):
        self.auth_data = {
                'authorizationData': [
                    {
                        'authorizationToken': self.ecr_token(),
                        'expiresAt': datetime(2015, 1, 1),
                        'proxyEndpoint': 'string'
                    },
                ]
            }

    def _break(self):
        self.auth_data['authorizationData'][0].pop('authorizationToken')
