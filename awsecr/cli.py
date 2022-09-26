"""Console script for awsecr."""
import argparse
import sys
from terminaltables import SingleTable
import boto3
from colorama import Fore, Style
from collections import defaultdict

from awsecr.awsecr import account_info, image_push, BaseDockerClient, login_ecr
from awsecr.repository import ECRRepos
from awsecr.image import list_ecr, Vulnerabilities
from awsecr.exception import ECRClientException, InvalidResponseStatus


def main() -> int:
    """Console script for awsecr."""
    epilog = """
    The "repos" operation requires no additional options. It lists the
    available ECR repositories for the current AWS user credentials.
    """
    parser = argparse.ArgumentParser(description='Easier interaction with AWS \
ECR to manage Docker images.',
                                     usage='%(prog)s [OPERATION]',
                                     epilog=epilog
                                     )
    parser.add_argument('operation', choices=['repos', 'image'],
                        help='the desired operation with the registry')
    parser.add_argument('--image', help='the local Docker image to use \
together with the image --push sub operation.')

    group = parser.add_mutually_exclusive_group()
    metavar = 'REPOSITORY'
    group.add_argument(
        '--list',
        metavar=metavar,
        help='Sub operation for "image" operation. List all images from the \
repository. Uses ANSI colors to match vulnerabilities severities, going from \
CRITICAL (red) to UNDEFINED (green)')

    group.add_argument(
        '--push',
        metavar=metavar,
        help='Sub operation for "image" operation. Pushes a Docker image to \
the repository.')

    args = parser.parse_args()

    if args.operation == 'image':

        if args.list:
            return list_images(args)

        elif args.push:
            account_id, user, region = account_info()

            if args.image is None:
                ret = _die('Missing --image parameter!')
                parser.print_help()
                return ret

            print(f'Authenticating against {args.push}... ', end='')

            try:
                docker_client: BaseDockerClient = login_ecr(account_id)
            except InvalidResponseStatus as e:
                return _die(str(e))
            else:
                print('done', flush=True)

            for status in image_push(account_id=account_id,
                                     repository=args.push,
                                     region=region,
                                     docker=docker_client,
                                     current_image=args.image):
                print(status, end='', flush=True)

            print(' done!')
            print('Upload finished')
            return 0

        else:
            ret = _die('image operation requires --list or --push options')
            parser.print_help()
            return ret

    if args.operation == 'repos':

        if args.push or args.list:
            ret = _die('The repos operations does not support any argument!\n')
            parser.print_help()
            return ret

        repos = ECRRepos()
        table = SingleTable(repos.list_repositories(),
                            title=' All ECR repositories ')
        print(table.table)
        return 0
    else:
        parser.print_help()
        return 1


def list_images(args):
    account_id, user, _ = account_info()

    try:
        images = list_ecr(account_id=account_id,
                          repository=args.list,
                          ecr_client=boto3.client('ecr'),
                          ansi=_ansi_vulnerabilities)
    except ECRClientException as e:
        return _die(str(e))
    except Exception as e:
        return _die('Unexpected exception "{0}": {1}'.format(
            e.__class__.__name__, str(e)))

    table = SingleTable(images,
                        title=f' Docker images at {args.list} ')
    print(table.table)
    return 0


def _die(message: str) -> int:
    print(message, file=sys.stderr)
    return 1


def _ansi_vulnerabilities(current: Vulnerabilities, scan_status: str):
    """
    Change the vulnerabilities scan result to a string using ANSI terminal
    colors to classify the severity by color.
    """
    if scan_status == 'FAILED':
        return f'{Fore.RED}{current["UNDEFINED"]}{Style.RESET_ALL}'

    findings: Vulnerabilities = defaultdict(int)

    for k in current:
        findings[k] += current[k]

    return '/'.join([
        f'{Fore.RED}{findings["CRITICAL"]}{Style.RESET_ALL}',
        f'{Fore.LIGHTRED_EX}{findings["HIGH"]}{Style.RESET_ALL}',
        f'{Fore.YELLOW}{findings["MEDIUM"]}{Style.RESET_ALL}',
        f'{Fore.LIGHTYELLOW_EX}{findings["LOW"]}{Style.RESET_ALL}',
        f'{Fore.LIGHTGREEN_EX}{findings["INFORMATIONAL"]}{Style.RESET_ALL}',
        f'{Fore.GREEN}{findings["UNDEFINED"]}{Style.RESET_ALL}',
        ])


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
