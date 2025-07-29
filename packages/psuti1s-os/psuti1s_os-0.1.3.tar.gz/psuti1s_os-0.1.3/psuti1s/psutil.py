import sys
from _typeshed import Incomplete
from collections.abc import Callable, Iterable, Iterator
from contextlib import AbstractContextManager
from typing import Any, Literal, overload
from typing_extensions import Self, TypeAlias, deprecated

from psutil._common import (
    AIX as AIX,
    BSD as BSD,
    CONN_CLOSE as CONN_CLOSE,
    CONN_CLOSE_WAIT as CONN_CLOSE_WAIT,
    CONN_CLOSING as CONN_CLOSING,
    CONN_ESTABLISHED as CONN_ESTABLISHED,
    CONN_FIN_WAIT1 as CONN_FIN_WAIT1,
    CONN_FIN_WAIT2 as CONN_FIN_WAIT2,
    CONN_LAST_ACK as CONN_LAST_ACK,
    CONN_LISTEN as CONN_LISTEN,
    CONN_NONE as CONN_NONE,
    CONN_SYN_RECV as CONN_SYN_RECV,
    CONN_SYN_SENT as CONN_SYN_SENT,
    CONN_TIME_WAIT as CONN_TIME_WAIT,
    FREEBSD as FREEBSD,
    LINUX as LINUX,
    MACOS as MACOS,
    NETBSD as NETBSD,
    NIC_DUPLEX_FULL as NIC_DUPLEX_FULL,
    NIC_DUPLEX_HALF as NIC_DUPLEX_HALF,
    NIC_DUPLEX_UNKNOWN as NIC_DUPLEX_UNKNOWN,
    OPENBSD as OPENBSD,
    OSX as OSX,
    POSIX as POSIX,
    POWER_TIME_UNKNOWN as POWER_TIME_UNKNOWN,
    POWER_TIME_UNLIMITED as POWER_TIME_UNLIMITED,
    STATUS_DEAD as STATUS_DEAD,
    STATUS_DISK_SLEEP as STATUS_DISK_SLEEP,
    STATUS_IDLE as STATUS_IDLE,
    STATUS_LOCKED as STATUS_LOCKED,
    STATUS_PARKED as STATUS_PARKED,
    STATUS_RUNNING as STATUS_RUNNING,
    STATUS_SLEEPING as STATUS_SLEEPING,
    STATUS_STOPPED as STATUS_STOPPED,
    STATUS_TRACING_STOP as STATUS_TRACING_STOP,
    STATUS_WAITING as STATUS_WAITING,
    STATUS_WAKING as STATUS_WAKING,
    STATUS_ZOMBIE as STATUS_ZOMBIE,
    SUNOS as SUNOS,
    WINDOWS as WINDOWS,
    AccessDenied as AccessDenied,
    Error as Error,
    NoSuchProcess as NoSuchProcess,
    TimeoutExpired as TimeoutExpired,
    ZombieProcess as ZombieProcess,
    pconn,
    pcputimes,
    pctxsw,
    pgids,
    pionice,
    popenfile,
    pthread,
    puids,
    sconn,
    scpufreq,
    scpustats,
    sdiskio,
    sdiskpart,
    sdiskusage,
    sfan,
    shwtemp,
    snetio,
    snicaddr,
    snicstats,
    sswap,
    suser,
)
_Status: TypeAlias = Literal[
    "running",
    "sleeping",
    "disk-sleep",
    "stopped",
    "tracing-stop",
    "zombie",
    "dead",
    "wake-kill",
    "waking",
    "idle",
    "locked",
    "waiting",
    "suspended",
    "parked",
]

import psutil  

def check_cpu():
    cpu = psutil.cpu_percent(interval=1) 
    if cpu > 80:
        print("alert!  (" + str(cpu) + "%)")
    else:
        print("less consumption (" + str(cpu) + "%)")

def check_disk():
    disk = psutil.disk_usage("/") 
    free = disk.free / (1024 * 1024 * 1024)  # Turn bytes into GB
    if free < 1:
        print("space left only " + str(round(free, 2)) + " GB.")
    else:
        print("Disk space is good: " + str(round(free, 2)) + " GB free.")

# Run the checks
check_cpu()
check_disk()
