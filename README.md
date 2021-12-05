# awsecr

CLI to interact with AWS ECR service.

## Description

awsecr is a Python module that allows an end user to access an AWS ECR
repository to do the following:

- pull/push images
- list available repositories
- list available images per repository

Authentication between AWS ECR and the local Docker client is automatic.

See `TODO.txt` for next planned features.

## Samples outputs

Listing repositories available:

```
$ awsecr repos
┌ All ECR repositories ──────────────┬─────────────────────────────────────────────────────────────────────────────────┬────────────────┬───────────────┐
│ Name                               │ URI                                                                             │ Tag Mutability │ Scan on push? │
├────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────┼────────────────┼───────────────┤
│ nodejs                             │ 012345678910.dkr.ecr.us-east-1.amazonaws.com/nodejs                             │ IMMUTABLE      │ True          │
│ spark-py                           │ 012345678910.dkr.ecr.us-east-1.amazonaws.com/spark-py                           │ MUTABLE        │ False         │
│ hive-metastore                     │ 012345678910.dkr.ecr.us-east-1.amazonaws.com/hive-metastore                     │ IMMUTABLE      │ True          │
└────────────────────────────────────┴─────────────────────────────────────────────────────────────────────────────────┴────────────────┴───────────────┘
```

Listing images from a repository:

```
$ awsecr image --list nodejs
┌ Docker images at nodejs ─────────────────────────────────────┬─────────────┬───────────┬─────────────────┐
│ Image                                                        │ Scan status │ Size (MB) │ Vulnerabilities │
├──────────────────────────────────────────────────────────────┼─────────────┼───────────┼─────────────────┤
│ 012345678910.dkr.ecr.us-east-1.amazonaws.com/nodejs:14-0.1.0 │ COMPLETE    │ 40.73     │ 1               │
│ 012345678910.dkr.ecr.us-east-1.amazonaws.com/nodejs:12-0.1.0 │ COMPLETE    │ 29.3      │ 1               │
└──────────────────────────────────────────────────────────────┴─────────────┴───────────┴─────────────────┘
```

## How to install

The preferred way is to install it from https://pypi.org with:

```
pip install awsecr
```

## How to use it

You can check the `awsecr` CLI online help:

```
$ awsecr -h
usage: awsecr [OPERATION]

Easier interaction with AWS ECR to manage Docker images.

positional arguments:
  {repos,image}      the desired operation with the registry.

optional arguments:
  -h, --help         show this help message and exit.
  --image IMAGE      the local Docker image to use together with the image --push sub operation.
  --list REPOSITORY  sub operation for "image" operation. List all images from the repository.
  --push REPOSITORY  sub operation for "image" operation. Pushes a Docker image to the repository.

The "repos" operation requires no additional options. It lists the available
ECR repositories for the current AWS user credentials.
```

## References

Other open source projects that are related to awsecr:

- https://pypi.org/project/ecrtools/
- https://pypi.org/project/ecr-scan-reporter/
- https://github.com/muckamuck/ecrscan
