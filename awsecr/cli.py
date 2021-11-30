"""Console script for awsecr."""
import argparse
import sys
from terminaltables import SingleTable

from awsecr.awsecr import aws_account_info, ECRRepos, list_ecr
from awsecr.awsecr import image_push


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
            account_id, user = aws_account_info()
            images = list_ecr(account_id=account_id, repository=args.list)
            table = SingleTable(images,
                                title=f' Docker images at {args.list} ')
            print(table.table)
            return 0

        elif args.push:
            account_id, user = aws_account_info()

            for status in image_push(account_id=account_id,
                                     repository=args.push,
                                     current_image=args.image):
                print(status)

            print('Upload finished')
            return 0

        else:
            print('image operation requires --list or --push options')
            parser.print_help()
            return 1

    if args.operation == 'repos':
        account_id, user = aws_account_info()
        repos = ECRRepos()
        table = SingleTable(repos.list_repositories(),
                            title=f' All ECR repositories ')
        print(table.table)
        return 0
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
