"""Shares code between tests."""

import os


class AwsEcrMetaStub:
    # DRY
    region_name = os.environ['AWS_DEFAULT_REGION']
