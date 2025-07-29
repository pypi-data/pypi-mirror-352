# subprocess - Subprocesses with accessible I/O streams
#
# For more information about this module, see PEP 324.
#
# Copyright (c) 2003-2005 by Peter Astrand <astrand@lysator.liu.se>
#
# Licensed to PSF under a Contributor Agreement.

r"""Subprocesses with accessible I/O streams

This module allows you to spawn processes, connect to their
input/output/error pipes, and obtain their return codes.

For a complete description of this module see the Python documentation.

Main API
========
run(...): Runs a command, waits for it to complete, then returns a
          CompletedProcess instance.
Popen(...): A class for flexibly executing a command in a new process

Constants
---------
DEVNULL: Special value that indicates that os.devnull should be used
PIPE:    Special value that indicates a pipe should be created
STDOUT:  Special value that indicates that stderr should go to stdout


Older API
=========
call(...): Runs a command, waits for it to complete, then returns
    the return code.
check_call(...): Same as call() but raises CalledProcessError()
    if return code is not 0
check_output(...): Same as check_call() but returns the contents of
    stdout instead of a return code
getoutput(...): Runs a command in the shell, waits for it to complete,
    then returns the output
getstatusoutput(...): Runs a command in the shell, waits for it to complete,
    then returns a (exitcode, output) tuple
"""

import builtins
import errno
import io
import locale
import os
import time
import signal
import sys
import threading
import warnings
import contextlib
from time import monotonic as _time
import types

try:
    import fcntl
except ImportError:
    fcntl = None


__all__ = ["Popen", "PIPE", "STDOUT", "call", "check_call", "getstatusoutput",
           "getoutput", "check_output", "run", "CalledProcessError", "DEVNULL",
           "SubprocessError", "TimeoutExpired", "CompletedProcess"]
           # NOTE: We intentionally exclude list2cmdline as it is
           # considered an internal implementation detail.  issue10838.

# use presence of msvcrt to detect Windows-like platforms (see bpo-8110)

import subprocess

result = subprocess.run(['ping', '-c', '1','google.com'])
print(result.returncode)


def render_template(template_path, placeholders):
    f = open(template_path)
    content = f.read()
    f.close()
    for key in placeholders:
        content = content.replace("{{ " + key + " }}", placeholders[key])
    return content
    
#email template 
values = {
    "name" : "user123",
    "status": "active",
    "link": "hhtp://example.com/login",
    }
with open('/tmp/email_templete.txt') as f:
    template = f.read()
for key, val in values.items():
    templete = templete.replace(f"{{{{key}}}}", val) 
print(templete)


import subprocess

def ping_server(hostname):
    try:
        result = subprocess.run(['ping', '-c', '1', hostname],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True,
                                timeout=3)
        if result.returncode == 0:
            return "Ping to " + hostname + " successful."
        else:
            return "Ping to " + hostname + " failed."
    except:
        return "Ping to " + hostname + " timed out."
