"""Console script for awsecr."""
import argparse
import sys
from terminaltables import SingleTable

from awsecr.awsecr import account_info, ECRRepos, list_ecr, image_push
from awsecr.exception import ECRClientException


def _die(message: str) -> None:
    print(message, file=sys.stderr)
    sys.exit(1)


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
    parser.add_argument('--image', help='the local Docker image to use together\
 with the image --push sub operation.')

    group = parser.add_mutually_exclusive_group()
    metavar = 'REPOSITORY'
    group.add_argument(
        '--list',
        metavar=metavar,
        help='Sub operation for "image" operation. List all images from the \
repository.')

    group.add_argument(
        '--push',
        metavar=metavar,
        help='Sub operation for "image" operation. Pushes a Docker image to \
the repository.')

    args = parser.parse_args()

    if args.operation == 'image':

        if args.list:
            account_id, user, _ = account_info()

            try:
                images = list_ecr(account_id=account_id, repository=args.list)
            except ECRClientException as e:
                _die(str(e))
            except Exception as e:
                _die('Unexpected exception "{0}": {1}'.format(
                    e.__class__.__name__, str(e)))

            table = SingleTable(images,
                                title=f' Docker images at {args.list} ')
            print(table.table)
            return 0

        elif args.push:
            account_id, user, region = account_info()

            if args.image is None:
                print('Missing --image parameter!', file=sys.stderr)
                parser.print_help()
                return 1

            for status in image_push(account_id=account_id,
                                     repository=args.push,
                                     region=region,
                                     current_image=args.image):
                print(status, end='', flush=True)

            print(' done!')
            print('Upload finished')
            return 0

        else:
            print('image operation requires --list or --push options',
                  file=sys.stderr)
            parser.print_help()
            return 1

    if args.operation == 'repos':
        repos = ECRRepos()
        table = SingleTable(repos.list_repositories(),
                            title=' All ECR repositories ')
        print(table.table)
        return 0
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
