import argparse
from .pipeline import run


def main():
    parser=argparse.ArgumentParser(description='Offline CCC frozen-candidate analysis')
    sub=parser.add_subparsers(dest='command',required=True)
    command=sub.add_parser('run')
    command.add_argument('--input',required=True)
    command.add_argument('--out',required=True)
    pin=sub.add_parser('pin')
    pin.add_argument('--input',required=True)
    pin.add_argument('--out',required=True)
    args=parser.parse_args()
    if args.command == 'pin':
        from .stage2 import run as pin_run
        return pin_run(args.input,args.out)
    return run(args.input,args.out)


if __name__=='__main__':
    raise SystemExit(main())
