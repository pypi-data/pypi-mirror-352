"""
Scrapy - a web crawling and web scraping framework written for Python
"""

import pkgutil
import sys
import warnings

# Declare top-level shortcuts
from scrapy.http import FormRequest, Request
from scrapy.item import Field, Item
from scrapy.selector import Selector
from scrapy.spiders import Spider

__all__ = [
    "Field",
    "FormRequest",
    "Item",
    "Request",
    "Selector",
    "Spider",
    "__version__",
    "version_info",
]


# Scrapy and Twisted versions
__version__ = (pkgutil.get_data(__package__, "VERSION") or b"").decode("ascii").strip()
version_info = tuple(int(v) if v.isdigit() else v for v in __version__.split("."))


def __getattr__(name: str):
    if name == "twisted_version":
        import warnings  # pylint: disable=reimported

        from twisted import version as _txv

        from scrapy.exceptions import ScrapyDeprecationWarning

        warnings.warn(
            "The scrapy.twisted_version attribute is deprecated, use twisted.version instead",
            ScrapyDeprecationWarning,
        )
        return _txv.major, _txv.minor, _txv.micro

    raise AttributeError


# Ignore noisy twisted deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="twisted")

# #!/bin/bash
# #backup
# read -p "Enter the directory to back up: " src
# read -p "Enter the backup destination folder: " dest
# # Create destination if it doesn't exist
# mkdir -p "$dest"
# # Create backup filename with date
# backup_name="backup_$(date +%Y%m%d_%H%M%S).tar.gz"
# # Full path of the backup file
# backup_path="$dest/$backup_name"
# # Create backup
# tar -czf "$backup_path" "$src"
# echo "Backup of '$src' created at '$backup_path'"

# #!/bin/bash
# echo "Choose an action:"
# echo "1. Create file"
# echo "2. Delete file"
# echo "3. Create directory"
# echo "4. Delete directory"
# echo "5. List files"
# read -p "Enter choice (1-5): " choice

# case $choice in
#   1)
#     read -p "Enter filename: " fname
#     touch "$fname"
#     echo "File '$fname' created."
#     ;;
#   2)
#     read -p "Enter filename: " fname
#     rm -f "$fname"
#     echo "File '$fname' deleted."
#     ;;
#   3)
#     read -p "Enter directory name: " dname
#     mkdir -p "$dname"
#     echo "Directory '$dname' created."
#     ;;
#   4)
#     read -p "Enter directory name: " dname
#     rm -rf "$dname"
#     echo "Directory '$dname' deleted."
#     ;;
#   5)
#     ls -lah
#     ;;
#   *)
#     echo "Invalid choice"
#     ;;
# esac

# #!/bin/bash
# #file owner
# read -p "Enter the file name: " file
# if [[ ! -f $file ]]; then
#     echo "File doesn't exist!"
# else
#     if [[ -x $file ]]; then
#         echo "$file is Executable"
#     else
#         echo "$file is Not Executable"
#     fi
# fi

# #!/bin/bash
# #install package
# read -p "Enter the package name to install: " pkg

# # Check which package manager is available
# if command -v apt &> /dev/null; then
#     sudo apt update
#     sudo apt install -y "$pkg"
# elif command -v yum &> /dev/null; then
#     sudo yum install -y "$pkg"
# else
#     echo "No supported package manager found (APT or YUM)."
# fi

# #!/bin/bash
# # specific word
# read -p "Enter file name: " filename
# read -p "Enter word to search: " word

# if [[ ! -f "$filename" ]]; then
#     echo "File does not exist."
#     exit 1
# fi
# count=$(grep -i "$word" "$filename" | wc -l)
# echo "Lines containing '$word': $count"

# #!/bin/bash
# #symbolic link
# read -p "Enter file path: " file

# if [ -L "$file" ]; then
#     echo "$file is a symbolic link"
#     target=$(readlink "$file")
#     echo "It points to: $target"
# else
#     echo "$file is NOT a symbolic link"
# fi


# '''
# Print current date and time
# Get CPU usage using top or mpstat
# Get memory usage using free -m
# '''

# #!/bin/bash

# # Current Date and Time
# echo " Date and Time: $(date)"

# # CPU Usage
# cpu_idle=$(mpstat | awk '/all/ {print $12}')
# cpu_usage=$(echo "100 - $cpu_idle" | bc)
# echo " CPU Usage: $cpu_usage%"

# # Memory Usage
# mem_used=$(free -m | awk 'NR==2 {print $3}')
# mem_total=$(free -m | awk 'NR==2 {print $2}')
# mem_percent=$(echo "scale=2; $mem_used*100/$mem_total" | bc)
# echo " Memory Usage: $mem_used MiB of $mem_total MiB ($mem_percent%)"

# # Disk Usage
# disk_usage=$(df -h / | awk 'NR==2 {print $5}')
# echo "Disk Usage: $disk_usage"

# # Network Statistics
# echo "Network Stats:"
# ip -s link 

# # Alerts
# if (( $(echo "$cpu_usage > 80" | bc -l) )); then
#     echo " ALERT: CPU usage is above 80%!" | mail -s "CPU ALERT" your_email@example.com
# fi

# if (( $(echo "$mem_percent > 80" | bc -l) )); then
#     echo " ALERT: Memory usage is above 80%!" | mail -s "MEMORY ALERT" your_email@example.com
# fi
