import argparse
from .pipeline import run


def main():
    parser=argparse.ArgumentParser(description='Offline CCC frozen-candidate analysis')
    sub=parser.add_subparsers(dest='command',required=True)
    command=sub.add_parser('run')
    command.add_argument('--input',required=True)
    command.add_argument('--out',required=True)
    args=parser.parse_args()
    return run(args.input,args.out)


if __name__=='__main__':
    raise SystemExit(main())
