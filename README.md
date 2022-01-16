# awsecr

CLI to interact with AWS ECR service.

## Description

awsecr is a Python module that allows an end user to access an AWS ECR
repository to do the following:

- pull/push images
- list available repositories
- list available images per repository, summarizing all founded vulnerabilities.

Authentication between AWS ECR and the local Docker client is automatic.

See `TODO.txt` for next planned features.

## Samples outputs

The output samples will *roughly* look like the ones generated at the terminal
by the CLI. Expect to have better output in the terminal.

Listing repositories available:

```
$ awsecr repos
┌ All ECR repositories ────────────┬───────────────────────────────────────────────────────────────────────────────────┬─────────────┐
│ Name                               │ URI                                                                             │ Tag Mutability │ Scan on push? │
├───────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────┼────────────┤
│ nodejs                             │ 012345678910.dkr.ecr.us-east-1.amazonaws.com/nodejs                             │ IMMUTABLE      │ True          │
│ spark-py                           │ 012345678910.dkr.ecr.us-east-1.amazonaws.com/spark-py                           │ MUTABLE        │ False         │
│ hive-metastore                     │ 012345678910.dkr.ecr.us-east-1.amazonaws.com/hive-metastore                     │ IMMUTABLE      │ True          │
└──────────────────────────────┴────────────────────────────────────────────────────────────────────────────────────┴────────────┘
```

Listing images from a repository:

```
┌ Docker images at api-foobar123  ────────────────────────────┬───────────┬───────────┬───────────────────────┬─────────────────┐
│ Image                                                            │ Scan status │ Size (MB)   │ Pushed at                 │ Vulnerabilities    │
├────────────────────────────────────────────────────────┼───────────┼───────────┼───────────────────────┼─────────────────┤
│ 012345678910.dkr.ecr.us-east-1.amazonaws.com/api-foobar123:1.3.5 │ COMPLETE    │ 205.1       │ 2021-12-09 18:06:20-03:00 │ 1/10/118/51/274/22 │
│ 012345678910.dkr.ecr.us-east-1.amazonaws.com/api-foobar123:1.3.6 │ COMPLETE    │ 133.8       │ 2021-12-09 15:42:28-03:00 │ 1/10/118/51/274/22 │
└────────────────────────────────────────────────────────────────────┴───────────┴───────────────────────┴─────────────────┘
```

Except that the *Vulnerabilities* column will have <font color="#AA0000">1</font>/<font color="#FF5555">10</font>/<font color="#AA5500">118</font>/<font color="#FFFF55">51</font>/<font color="#55FF55">274</font>/<font color="#00AA00">22</font> as values in
the terminal. Colors goes from highest severity to lesser, left to right.

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
