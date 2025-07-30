#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###################
#    This script prints memory usages and statistics (by process,
#    executable and for the full system).
#    Copyright (C) 2025  LinuxMemoryStatistics

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
###################

'''
This script prints memory usages and statistics (by process,
executable and for the full system).
'''

__version__ = "0.0.1"
__author__ = "Maurice Lambert"
__author_email__ = "mauricelambert434@gmail.com"
__maintainer__ = "Maurice Lambert"
__maintainer_email__ = "mauricelambert434@gmail.com"
__description__ = '''
This script prints memory usages and statistics (by process,
executable and for the full system).
'''
__url__ = "https://github.com/mauricelambert/LinuxMemoryStatistics"

# __all__ = []

__license__ = "GPL-3.0 License"
__copyright__ = '''
LinuxMemoryStatistics  Copyright (C) 2025  Maurice Lambert
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.
'''
copyright = __copyright__
license = __license__

print(copyright)

from sys import exit, stderr
from os.path import realpath
from os import listdir, sysconf
from dataclasses import dataclass
from argparse import Namespace, ArgumentParser
from collections import namedtuple, defaultdict
from typing import Dict, List, Tuple, Set, Iterator

fields = ["pid", "private", "shared", "rss", "pss", "executable", "cmd"]
MemoryStatistics = namedtuple("MemoryStatistics", fields)
PAGE_SIZE = sysconf("SC_PAGE_SIZE")


@dataclass
class ExecutableStatistics:
    executable: str
    number_of_process: int
    private: int
    shared: int
    total: int
    pss: int
    pfn_size: int
    missing_pfn_size: int


def parse_smaps(pid: str) -> Tuple[int, int, int, int]:
    """
    This function returns private memory, shared memory,
    rss (total memory used by process) and pss (memory cost by process)
    for a process.
    """

    private = rss = pss = shared = 0

    try:
        with open(f"/proc/{pid}/smaps", "r") as f:
            for line in f:
                if line.startswith("Private_Clean:") or line.startswith(
                    "Private_Dirty:"
                ):
                    private += int(line.split()[1])
                elif line.startswith("Shared_Clean:") or line.startswith(
                    "Shared_Dirty:"
                ):
                    shared += int(line.split()[1])
                elif line.startswith("Rss:"):
                    rss += int(line.split()[1])
                elif line.startswith("Pss:"):
                    pss += int(line.split()[1])
    except (FileNotFoundError, PermissionError):
        return None
    return private, shared, rss, pss


def get_cmdline(pid: str) -> List[str]:
    """
    This function returns the process command line arguments.
    """

    try:
        with open(f"/proc/{pid}/cmdline", "rb") as f:
            return f.read().decode().split("\x00")
    except PermissionError:
        return []


def get_process(pid: str) -> str:
    """
    This function returns the process command line arguments.
    """

    try:
        return realpath(f"/proc/{pid}/exe")
    except PermissionError:
        return ""


def get_memory_statistics() -> Tuple[List[MemoryStatistics], List[str]]:
    """
    This function returns memory statistics from smaps and PID with errors.
    """

    statistics = []
    pid_errors = []

    for pid in filter(str.isdigit, listdir("/proc")):
        smaps = parse_smaps(pid)
        if smaps:
            statistics.append(
                MemoryStatistics(
                    int(pid), *smaps, get_process(pid), get_cmdline(pid)
                )
            )
        else:
            pid_errors.append(pid)

    return statistics, pid_errors


def print_details(
    statistics: List[MemoryStatistics],
    meminfo: Dict[str, int],
    color: bool = True,
    order: str = "pss",
) -> None:
    """
    This function prints memory usages by process.
    """

    if order == "total":
        order = "pss"

    print(
        f"{'PID':>6} {'Private KB':>12} {'Shared KB':>12} "
        f"{'RSS KB':>12} {'PSS KB':>12} CMD"
    )
    order = order.casefold()
    order_position = [
        i for i, x in enumerate(fields) if x.casefold() == order
    ][0]

    for process in sorted(statistics, key=lambda x: x[order_position]):
        print_colored_size_value(
            f"{process.pid:>6} {process.private:12} {process.shared:12} "
            f"{process.rss:12} {process.pss:12} {process.cmd}",
            value=process.pss,
            total=meminfo["MemTotal"],
            color=color,
        )


def parse_meminfo() -> Dict[str, int]:
    """
    This function returns the system memory usages.
    """

    meminfo = {}
    with open("/proc/meminfo", "r") as f:
        for line in f:
            parts = line.split(":")
            key = parts[0]
            value = parts[1].strip().split()[0]
            meminfo[key] = int(value)
    return meminfo


def kb_to_gib(kb: int) -> float:
    """
    This function converts KB in GB.
    """

    return kb / 1024 / 1024


def kb_to_mib(kb: int) -> float:
    """
    This function converts KB in MB.
    """

    return kb / 1024


def get_size_format(kb: int) -> str:
    """
    This function returns the string the represent size.
    """

    if kb >= 1043334:
        return f"{kb_to_gib(kb):.2f} GB"
    elif kb >= 1019:
        return f"{kb_to_mib(kb):.2f} MB"
    else:
        return f"{kb} KB"


def print_system_memory_usage(
    meminfo: Dict[str, int], color: bool = True
) -> None:
    """
    This function prints the system memory usage.
    """

    total = meminfo["MemTotal"]
    free = meminfo["MemFree"]
    available = meminfo.get("MemAvailable", free)

    sreclaimable = meminfo.get("SReclaimable", 0)
    buffers = meminfo.get("Buffers", 0)
    cached = meminfo.get("Cached", 0)
    shmem = meminfo.get("Shmem", 0)

    buff_cache = buffers + cached + sreclaimable
    used = total - available

    swap_total = meminfo.get("SwapTotal", 0)
    swap_free = meminfo.get("SwapFree", 0)
    swap_used = swap_total - swap_free

    print(f"{'Memory Field':<17}{'Value'}")
    print(f"{'-'*30}")
    print(f"{'Total Memory:':<17}{get_size_format(total)}")
    print_colored_size_value(
        f"{'Used Memory:':<17}{get_size_format(used)}",
        value=used,
        total=total,
        color=color,
    )
    print(f"{'Free Memory:':<17}{get_size_format(free)}")
    print(f"{'Shared Memory:':<17}{get_size_format(shmem)}")
    print(f"{'Buffers/Cache:':<17}{get_size_format(buff_cache)}")
    print(f"{'Available:':<17}{get_size_format(available)}")
    print()
    print(f"{'Swap Field':<17}{'Value'}")
    print(f"{'-'*30}")
    print(f"{'Total Swap:':<17}{get_size_format(swap_total)}")
    print_colored_size_value(
        f"{'Used Swap:':<17}{get_size_format(swap_used)}",
        value=swap_used,
        total=swap_total,
        color=color,
    )
    print(f"{'Free Swap:':<17}{get_size_format(swap_free)}")


def parse_maps(pid: int) -> Iterator[Tuple[int, int]]:
    """
    Yield (start, end) virtual address ranges for a PID
    """

    try:
        with open(f"/proc/{pid}/maps", "r") as f:
            for line in f:
                addr_range = line.split()[0]
                start_str, end_str = addr_range.split("-")
                start = int(start_str, 16)
                end = int(end_str, 16)
                yield start, end
    except FileNotFoundError:
        return None


def get_pfn(pid: int, vaddr: int) -> int:
    """
    Return PFN from /proc/[pid]/pagemap for a virtual address
    """

    offset = (vaddr // PAGE_SIZE) * 8
    try:
        with open(f"/proc/{pid}/pagemap", "rb") as f:
            f.seek(offset)
            data = f.read(8)
            if len(data) < 8:
                return None
            entry = int.from_bytes(data, "little")
            if (entry >> 63) & 1:
                return entry & ((1 << 55) - 1)
            return None
    except Exception:
        return None


def calculate_total_memory_kib(pfns: Set[int]) -> int:
    """
    Return total memory size in KiB from PFN count
    """

    return len(pfns) * (PAGE_SIZE // 1024)


def get_all_pfns(
    executables_statistics: List[MemoryStatistics],
) -> Tuple[Set[int], int]:
    """
    Extract unique PFNs from a list of PIDs

    Return:
        - set of present PFNs
        - total size in KiB of pages with no PFN (i.e. missing from RAM)
    """

    pfns = set()
    missing_pages = 0
    for statistic in executables_statistics:
        for start, end in parse_maps(statistic.pid):
            vaddr = start
            while vaddr < end:
                pfn = get_pfn(statistic.pid, vaddr)
                if pfn is not None:
                    pfns.add(pfn)
                else:
                    missing_pages += 1
                vaddr += PAGE_SIZE
    return pfns, missing_pages * (PAGE_SIZE // 1024)


def get_statistics_by_executable(
    statistics: List[MemoryStatistics],
    calcul_pfns: bool,
) -> Dict[str, ExecutableStatistics]:
    """
    This function groups statistics by executable.
    """

    executables_statistics = defaultdict(list)

    for statistic in statistics:
        executables_statistics[statistic.executable].append(statistic)

    executable_statistics = {}

    for executable, statistics in executables_statistics.items():
        sum_private = sum(x[1] for x in statistics)
        sum_pss = sum(x[4] for x in statistics)
        max_shared = max(statistics, key=lambda x: x[2])
        total = sum_private + max_shared[2]
        if calcul_pfns:
            pfns, missing_pfn_size = get_all_pfns(statistics)
            pfn_size = calculate_total_memory_kib(get_all_pfns(statistics))
        else:
            pfn_size = missing_pfn_size = 0

        executable_statistics[executable] = ExecutableStatistics(
            executable,
            len(statistics),
            sum_private,
            max_shared[2],
            total,
            sum_pss,
            pfn_size,
            missing_pfn_size,
        )

    return executable_statistics


def print_executables(
    statistics: Dict[str, ExecutableStatistics],
    meminfo: Dict[str, int],
    color: bool = True,
    order: str = "pss",
) -> None:
    """
    This function prints memory usages by executable.
    """

    if order not in ("private", "shared", "pss", "total"):
        order = "pss"

    print(
        "Number of process".ljust(20)
        + "Private".ljust(10)
        + "Shared".ljust(10)
        + "Total".ljust(10)
        + "PSS".ljust(8)
        + "From PFNs".ljust(15),
        "Executable",
    )

    for statistics in sorted(
        statistics.values(), key=lambda x: getattr(x, order)
    ):
        print_colored_size_value(
            f"{statistics.number_of_process:<20}{statistics.private:<10}"
            f"{statistics.shared:<10}{statistics.total:<10}{statistics.pss:<8}"
            f"{statistics.pfn_size + statistics.missing_pfn_size:<15}",
            statistics.executable,
            value=statistics.total,
            total=meminfo["MemTotal"],
            color=color,
        )


def parse_args() -> Namespace:
    """
    This function parses the command line arugments.
    """

    parser = ArgumentParser(
        description=(
            "This script prints informations about memory usage on Linux."
        )
    )

    modes = parser.add_mutually_exclusive_group()
    modes.add_argument(
        "-d",
        "--details",
        action="store_true",
        help="Prints memory usage by process",
    )
    modes.add_argument(
        "-s",
        "--system",
        action="store_true",
        help="Prints memory usage on the full system",
    )
    modes.add_argument(
        "-e",
        "--executable",
        action="store_true",
        help="Prints memory usage grouped by executable",
    )
    parser.add_argument(
        "-f",
        "--pfn",
        action="store_true",
        help="Calcul size from PFNs (take a long time)",
    )
    parser.add_argument(
        "-o",
        "--order",
        choices=fields + ["total"],
        default="pss",
        help="Order outputs lines by a specific field",
    )
    parser.add_argument(
        "-c", "--no-color", action="store_true", help="Print without color"
    )

    return parser.parse_args()


def print_colored_size_value(
    *to_print: str,
    value: int = 0,
    total: int = 0,
    color: bool = True,
    **kwargs,
) -> None:
    """
    This function is a special print to manage color.
    """

    if not color or not to_print:
        print(*to_print)
        return None

    if value > total / 2:
        to_print = list(to_print)
        to_print[0] = "\033[31m" + str(to_print[0])
        to_print[-1] = str(to_print[-1]) + "\033[0m"
        print(*to_print, **kwargs)
    elif value > total / 10:
        to_print = list(to_print)
        to_print[0] = "\033[33m" + str(to_print[0])
        to_print[-1] = str(to_print[-1]) + "\033[0m"
        print(*to_print, **kwargs)
    elif value > total / 100:
        to_print = list(to_print)
        to_print[0] = "\033[36m" + str(to_print[0])
        to_print[-1] = str(to_print[-1]) + "\033[0m"
        print(*to_print, **kwargs)
    else:
        to_print = list(to_print)
        to_print[0] = "\033[32m" + str(to_print[0])
        to_print[-1] = str(to_print[-1]) + "\033[0m"
        print(*to_print, **kwargs)


def main() -> int:
    """
    The main function to start the script and print outputs/errors.
    """

    arguments = parse_args()

    if not arguments.system:
        statistics, errors = get_memory_statistics()
    meminfo = parse_meminfo()

    if arguments.details:
        print_details(
            statistics, meminfo, not arguments.no_color, arguments.order
        )
    elif arguments.system:
        print_system_memory_usage(meminfo, not arguments.no_color)
        return 0
    else:
        print_executables(
            get_statistics_by_executable(statistics, arguments.pfn),
            meminfo,
            not arguments.no_color,
            arguments.order,
        )

    for pid in errors:
        print("Error to get statistics for PID:", pid, file=stderr)

    return len(errors)


if __name__ == "__main__":
    exit(main())
