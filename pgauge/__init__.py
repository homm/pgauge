import plistlib
import subprocess
from collections import deque
from colorama import Fore, Style


def echo(*args):
    print(*args, end='')


class StatsPrinter:
    def __init__(self, summary_size, rollup=False, per_core_load=False):
        self.summary_size = summary_size
        self.history = deque(maxlen=summary_size)
        self.rollup = rollup
        self.per_core_load = per_core_load
        self.headers_printed = False

    def feed(self, stats):
        if 'clusters' in stats:
            stats = self.convert_arm(stats)
        else:
            stats = self.convert_intel(stats)
        if not self.headers_printed:
            self.print_headers(stats)
        self.history.append(stats)
        self.print_stats(stats, self.power_summary())

    def convert_arm(self, stats):
        return {
            'power': {
                'cpu': stats['cpu_power'] / 1000,
                'gpu': stats['gpu_power'] / 1000,
                'total': stats['combined_power'] / 1000,
            },
            'cpu': [
                {
                    'name': cl['name'],
                    'freq': cl['freq_hz'] / 1e9,
                    'load': sum(
                        max(0, (1 - cpu['idle_ratio'] - cpu.get('down_ratio', 0)))
                        for cpu in cl['cpus']
                    ) * 100 / (1 if self.per_core_load else len(cl['cpus'])),
                    'number': len(cl['cpus']),
                }
                for cl in stats['clusters']
            ]
        }

    def convert_intel(self, stats):
        def pkg_freq(pkg):
            freq = [
                cpu['freq_hz']
                for core in pkg['cores']
                for cpu in core['cpus']
            ]
            return sum(freq) / len(freq)
        return {
            'power': {
                'cpu': None,
                'gpu': None,
                'total': stats['package_watts'],
            },
            'cpu': [
                {
                    'name': f"P{i}",
                    'freq': pkg_freq(pkg) / 1e9,
                    'load': pkg['average_num_cores'] * 100 /
                        (1 if self.per_core_load else len(pkg['cores'])),
                    'number': len(pkg['cores']),
                }
                for i, pkg in enumerate(stats['packages'])
            ]
        }

    def power_summary(self):
        if not self.history:
            return None
        return {
            metric: (
                min(s['power'][metric] for s in self.history),
                max(s['power'][metric] for s in self.history)
            )
            for metric in ['cpu', 'gpu', 'total']
            if self.history[0]['power'][metric] is not None
        }

    def print_headers(self, stats):
        self.headers_printed = True

        padding = 19 if self.summary_size else 5
        cols = []
        if stats['power']['cpu'] is not None:
            cols.append('CPU')
        if stats['power']['gpu'] is not None:
            cols.append('GPU')
        if stats['power']['total'] is not None:
            cols.append('Total W' if self.summary_size else 'Tot W')
        echo(Style.BRIGHT + " ".join(col.ljust(padding) for col in cols) + Style.NORMAL + ' ')

        names = [cpu['name'] for cpu in stats['cpu']]
        names = [name[:-8] if name.endswith('-Cluster') else name for name in names]
        print(
            Style.BRIGHT, ", ".join(names), "load,", Style.DIM + "GHz" + Style.NORMAL,
            end="" if self.rollup else None
        )

    def print_stats(self, stats, summary):
        echo('\n' if self.rollup else '\r\33[2K')

        if stats['power']['cpu'] is not None:
            echo(f"{stats['power']['cpu']:5.2f} ")
            if summary:
                echo(f"{Style.DIM}({Fore.GREEN}{summary['cpu'][0]:.2f}{Fore.RESET}"
                     f"...{Fore.RED}{summary['cpu'][1]:.2f}{Fore.RESET}){Style.NORMAL} ")

        if stats['power']['gpu'] is not None:
            echo(f"{stats['power']['gpu']:5.2f} ")
            if summary:
                echo(f"{Style.DIM}({Fore.GREEN}{summary['gpu'][0]:.2f}{Fore.RESET}"
                     f"...{Fore.RED}{summary['gpu'][1]:.2f}{Fore.RESET}){Style.NORMAL} ")

        if stats['power']['total'] is not None:
            echo(f"{Fore.MAGENTA}{stats['power']['total']:5.2f}{Fore.RESET} ")
            if summary:
                echo(f"{Style.DIM}({Fore.GREEN}{summary['total'][0]:.2f}{Fore.RESET}"
                     f"...{Fore.RED}{summary['total'][1]:.2f}{Fore.RESET}){Style.NORMAL} ")
        print(
            *(
                f" {cpu['load']:.0f}% {Style.DIM}{cpu['freq']:4.2f}{Style.NORMAL}"
                for cpu in stats['cpu']
            ),
            end=" ",
            flush=True
        )


class Powermetrics:
    def __init__(self, interval=1000):
        self.interval = interval
        cmd = "sudo powermetrics --samplers cpu_power --format plist -i".split()
        cmd.append(str(interval))
        self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE)

    def iter_plists(self):
        buffer = []
        for line in iter(self.process.stdout.readline, b''):
            line = line.strip(b'\t\n\r \x00')
            buffer.append(line)
            if line == b"</plist>":
                plist = b''.join(buffer)
                yield plistlib.loads(plist)
                buffer.clear()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.process.stdout.close()
        self.process.wait()
