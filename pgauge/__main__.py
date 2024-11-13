import subprocess
from argparse import ArgumentParser

from . import Powermetrics, StatsPrinter


def parse_size(val):
    if val.lower() == 'auto':
        return True
    if 'x' not in val:
        raise ValueError("Size should be WxH or 'auto'")
    w, _, h = val.partition('x')
    return (int(w), int(h))


parser = ArgumentParser('pgauge')
parser.add_argument('-i', '--interval', default=1000, type=int, metavar='mS',
                    help="Stats update interval in ms. Default is 1000 (one second).")
parser.add_argument('-s', '--summary', default=60, type=int, metavar='S',
                    help="Show min and max value for this period in sec. "
                         "Set 0 to disable history. Default is 60 (one minute).")
parser.add_argument('-k', '--keep-history', action='store_true',
                    help="Print each update on a new line.")
parser.add_argument('-r', '--resize', type=parse_size, metavar="WxH",
                    help="Resize terminal window to this size. Could be 'auto'.")


def main():
    args = parser.parse_args()
    summary_size = int(args.summary * 1000 / args.interval)

    if args.resize:
        if args.resize == True:
            w, h = 96, 2
            if args.keep_history:
                h = 6
            if not summary_size:
                w = 55
            args.resize = w, h
        subprocess.run(f'printf "\e[8;{args.resize[1]};{args.resize[0]}t"', shell=True)

    printer = StatsPrinter(summary_size, rollup=args.keep_history)
    with Powermetrics(args.interval) as powermetrics:
        try:
            for plist in powermetrics.iter_plists():
                printer.feed(plist['processor'])
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()
