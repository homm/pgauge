import plistlib
import subprocess
from collections import deque
from colorama import Fore, Style


class StatsPrinter:
    def __init__(self, summary_size, rollup=False):
        self.summary_size = summary_size
        self.history = deque(maxlen=summary_size)
        self.rollup = rollup
        self.headers_printed = False

    def feed(self, stats):
        if not self.headers_printed:
            self.print_headers(stats)
        self.history.append(stats)
        self.print_stats(stats, self.power_summary())

    def power_summary(self):
        if not self.history:
            return None
        return {
            'cpu_min': min(s['cpu_power'] for s in self.history),
            'cpu_max': max(s['cpu_power'] for s in self.history),
            'gpu_min': min(s['gpu_power'] for s in self.history),
            'gpu_max': max(s['gpu_power'] for s in self.history),
            'total_min': min(s['combined_power'] for s in self.history),
            'total_max': max(s['combined_power'] for s in self.history),
        }

    def print_headers(self, stats):
        self.headers_printed = True
        if self.summary_size:
            print(Style.BRIGHT + f"CPU{'':16} GPU{'':16} Total W{'':12}" + Style.NORMAL, end='')
        else:
            print(Style.BRIGHT + f"CPU{'':2} GPU{'':2} Total W  " + Style.NORMAL, end='')
        names = [cl['name'] for cl in stats['clusters']]
        names = [name[:-8] if name.endswith('-Cluster') else name for name in names]
        print(
            Style.BRIGHT, ", ".join(names), "GHz", Style.DIM + "utilization", Style.NORMAL,
            end="" if self.rollup else None
        )

    def print_stats(self, stats, summary):
        print(
            ('\n' if self.rollup else '\r\33[2K') +
            f"{stats['cpu_power'] / 1000:5.2f} " +
            (f"{Style.DIM}({Fore.GREEN}{summary['cpu_min'] / 1000:.2f}{Fore.RESET}"
             f"...{Fore.RED}{summary['cpu_max'] / 1000:.2f}{Fore.RESET}){Style.NORMAL} "
             if summary else '') +
            f"{stats['gpu_power'] / 1000:5.2f} " +
            (f"{Style.DIM}({Fore.GREEN}{summary['gpu_min'] / 1000:.2f}{Fore.RESET}"
             f"...{Fore.RED}{summary['gpu_max'] / 1000:.2f}{Fore.RESET}){Style.NORMAL} "
             if summary else '') +
            f"{Fore.MAGENTA}{stats['combined_power'] / 1000:5.2f}{Fore.RESET} " +
            (f"{Style.DIM}({Fore.GREEN}{summary['total_min'] / 1000:.2f}{Fore.RESET}"
             f"...{Fore.RED}{summary['total_max'] / 1000:.2f}{Fore.RESET}){Style.NORMAL}"
             if summary else ''),
            end=" "
        )
        clusters = [
            (
                cl['freq_hz'] / 1e9,
                sum(
                    1 - cpu['idle_ratio']
                    for cpu in cl['cpus']
                ) / len(cl['cpus']) * 100,
            )
            for cl in stats['clusters']
        ]
        print(
            *(f" {cl[0]:4.2f} {Style.DIM}{cl[1]:.0f}%{Style.NORMAL}" for cl in clusters),
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
