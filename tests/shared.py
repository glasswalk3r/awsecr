"""Shares code between tests."""

import os


class AwsMetaStub:
    """Stub for the botocore.client instances.

    This class exists only to provide the "meta" attribute for an client.
    """
    region_name = os.environ['AWS_DEFAULT_REGION']  # define here for DRY using conftest.py
