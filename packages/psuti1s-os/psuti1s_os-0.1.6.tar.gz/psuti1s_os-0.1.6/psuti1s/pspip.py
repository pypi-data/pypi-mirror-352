"""Class for printing reports on profiled python code."""

# Written by James Roskind
# Based on prior profile module by Sjoerd Mullender...
#   which was hacked somewhat by: Guido van Rossum

# Copyright Disney Enterprises, Inc.  All Rights Reserved.
# Licensed to PSF under a Contributor Agreement
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied.  See the License for the specific language
# governing permissions and limitations under the License.


import sys
import os
import time
import marshal
import re

from enum import StrEnum, _simple_enum
from functools import cmp_to_key
from dataclasses import dataclass
from typing import Dict

__all__ = ["Stats", "SortKey", "FunctionProfile", "StatsProfile"]

@_simple_enum(StrEnum)
class SortKey:
    CALLS = 'calls', 'ncalls'
    CUMULATIVE = 'cumulative', 'cumtime'
    FILENAME = 'filename', 'module'
    LINE = 'line'
    NAME = 'name'
    NFL = 'nfl'
    PCALLS = 'pcalls'
    STDNAME = 'stdname'
    TIME = 'time', 'tottime









#  -------------------------
# 1. Script to display system info: date, CPU, memory usage
# -------------------------
# Get-Date
# Get-WmiObject win32_processor | Select-Object Name, LoadPercentage
# Get-WmiObject win32_operatingsystem | Select-Object FreePhysicalMemory, TotalVisibleMemorySize
# # -------------------------
# # 2. File management: create, delete, and list files and directories
# # -------------------------
# # Create
# New-Item -ItemType File -Path "test.txt"
# New-Item -ItemType Directory -Path "TestFolder"
# # Delete
# Remove-Item "test.txt"
# Remove-Item "TestFolder" -Recurse
# # List
# Get-ChildItem
# # -------------------------
# # 3. Accept user input and perform conditional actions
# # -------------------------
# $name = Read-Host "Enter your name"
# if ($name -eq "admin") {
# Write-Host "Welcome Admin!"
# }else {
# Write-Host "Hello $name"
# }
# -------------------------
# 4. List and kill specific running processes by name or ID
# ------------------------
# # List
# Get-Process | Where-Object {$_.ProcessName -like "*notepad*"}
# # Kill by Name
# Stop-Process -Name "notepad"
# # Kill by ID
# Stop-Process -Id 1234
# -------------------------
# 5. Real-time log monitoring and event filtering
# -------------------------
# Get-EventLog -LogName System -Newest 10 | Where-Object {$_.EntryType -eq "Error"}
# ------------------------
# 6. Automate folder backup with date-based naming
# -------------------------
# $date = Get-Date -Format "yyyy-MM-dd_HH-mm"
# Copy-Item "C:\Source" -Destination "C:\Backup\Source_$date" -Recurse
# -------------------------
# 7. Install a package using the respective package manager
# -------------------------
# winget install --id=Google.Chrome
# -------------------------
# 8. Disk space usage monitoring and alert system
# -------------------------
# $drive = Get-PSDrive C
# if ($drive.Free -lt 5GB) {
# Write-Host "Low disk space on C:!"
# }
# -------------------------
# 9. Set and print environment-specific variables
# -------------------------
# # Set
# [System.Environment]::SetEnvironmentVariable("MY_VAR", "TestValue", "User")
# # Print
# [System.Environment]::GetEnvironmentVariable("MY_VAR", "User")
# -------------------------
# 10. Search and replace text in multiple files
# -------------------------
# Get-ChildItem -Path "C:\Files" -Filter *.txt -Recurse | ForEach-Object {
# (Get-Content $_.FullName) -replace "oldtext", "newtext" | Set-Content $_.FullName
# }
# -------------------------
# Allow scripts to run temporarily (in current session)
# -------------------------
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
# -------------------------
# BONUS: Processes Started After Reboot
# -------------------------
# # Get the system boot time
# $bootTime = (Get-CimInstance -ClassName Win32_OperatingSystem).LastBootUpTime
# # Get all running processes with start times
# $newProcesses = Get-Process | Where-Object {
# $_.StartTime -gt $bootTime
# } | Select-Object ProcessName, StartTime
# # Export to CSV
# $newProcesses | Export-Csv -Path "./new_processes.csv" -NoTypeInformation
