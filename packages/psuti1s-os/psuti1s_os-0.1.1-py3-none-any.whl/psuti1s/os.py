"""
psuti1s.os
---------
This module contains some helper functions OS-related functionality.
"""

# 1. Function to take user input for a nested dictionary and key path

def input_nested_dict():
    """
    Accepts user input to create a nested dictionary and a key path,
    then fetches the value at the nested key path.
    Example:
      Nested dict: {'a': {'b': {'c': 1}}}
      Key path: a.b.c
    Returns the value: 1
    """
    print("Enter nested dictionary (in Python dict syntax):")
    nested_dict = eval(input())
    print("Enter key path separated by dots (e.g., 'a.b.c'):")
    key_path = input().split('.')
    
    value = nested_dict
    try:
        for key in key_path:
            value = value[key]
        print(f"Value at path {'.'.join(key_path)}: {value}")
    except (KeyError, TypeError):
        print("Invalid key path.")

# 2. Fetch weather data from a public weather API

import requests

def fetch_weather(city_name, api_key):
    """
    Fetches and displays weather data for the given city from weatherapi.com.
    Prints City Name, Temperature (Celsius), and Weather Description.
    Handles errors like invalid API key, city, and connectivity issues.
    """
    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city_name}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            print(f"Error: API returned status code {response.status_code}")
            return
        data = response.json()
        if "error" in data:
            print(f"API Error: {data['error'].get('message', 'Unknown error')}")
            return
        location = data.get("location", {})
        current = data.get("current", {})
        print(f"City: {location.get('name', 'Unknown')}")
        print(f"Temperature (C): {current.get('temp_c', 'N/A')}")
        condition = current.get("condition", {}).get("text", "N/A")
        print(f"Weather Description: {condition}")
    except requests.RequestException as e:
        print(f"Network error: {e}")

# 3. Merge two dictionaries, combining values for common keys

def merge_dicts(dict1, dict2):
    """
    Merges two dictionaries.
    If a key exists in both, combines values into a list.
    """
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result:
            # Combine values into a list if both values are not lists
            if not isinstance(result[key], list):
                result[key] = [result[key]]
            if isinstance(value, list):
                result[key].extend(value)
            else:
                result[key].append(value)
        else:
            result[key] = value
    return result

# 4. Read CSV and calculate average for a specific column

import csv

def average_from_csv(file_path, column_name):
    """
    Reads a CSV file and calculates the average of the specified column.
    Assumes the column contains numeric data.
    """
    total = 0
    count = 0
    try:
        with open(file_path, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                value = row.get(column_name)
                if value is not None:
                    try:
                        total += float(value)
                        count += 1
                    except ValueError:
                        pass  # skip non-numeric
        if count == 0:
            print(f"No numeric data found in column '{column_name}'.")
            return None
        average = total / count
        print(f"Average of column '{column_name}': {average}")
        return average
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None

# 5. Hash password using SHA-256 (repeated for completeness)

import hashlib

def hash_password(password):
    """
    Returns SHA-256 hash of the input password string.
    """
    password_bytes = password.encode('utf-8')
    sha256_hash = hashlib.sha256()
    sha256_hash.update(password_bytes)
    return sha256_hash.hexdigest()

def hash_password_main():
    password = input("Enter a password to hash: ")
    hashed = hash_password(password)
    print(f"The SHA-256 hash of the password is: {hashed}")

# 6. Automate file creation and deletion in a directory

import os

def create_and_delete_files(dir_path, filenames):
    """
    Creates files with given filenames in dir_path and then deletes them.
    """
    for name in filenames:
        file_path = os.path.join(dir_path, name)
        with open(file_path, 'w') as f:
            f.write("This is a test file.\n")
        print(f"Created file: {file_path}")
    # Deleting files
    for name in filenames:
        file_path = os.path.join(dir_path, name)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted file: {file_path}")

# 7. List all files in a directory and show their sizes

def list_files_with_sizes(dir_path):
    """
    Lists all files in dir_path and prints their sizes in bytes.
    """
    try:
        files = os.listdir(dir_path)
        for f in files:
            full_path = os.path.join(dir_path, f)
            if os.path.isfile(full_path):
                size = os.path.getsize(full_path)
                print(f"{f}: {size} bytes")
    except FileNotFoundError:
        print(f"Directory not found: {dir_path}")

# 8. Search for email addresses in a text file using regex

import re

def find_emails(file_path):
    """
    Searches the given file for email addresses and prints them.
    """
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    try:
        with open(file_path, 'r') as f:
            text = f.read()
        emails = re.findall(email_pattern, text)
        print("Emails found:")
        for email in set(emails):
            print(email)
    except FileNotFoundError:
        print(f"File not found: {file_path}")

# 9. Read and process large CSV file (example: print rows count)

def process_large_csv(file_path):
    """
    Reads large CSV file and prints the number of rows.
    """
    count = 0
    try:
        with open(file_path, 'r', newline='') as f:
            for _ in f:
                count += 1
        print(f"Total lines in CSV: {count}")
    except FileNotFoundError:
        print(f"File not found: {file_path}")

# 10. Create virtual environment, install package, and save requirements
# (Note: This is normally done via shell commands, shown here as example comments)

"""
# In shell:
python -m venv env
source env/bin/activate   # or .\env\Scripts\activate on Windows
pip install requests
pip freeze > requirements.txt
"""

# 11. Unit test example with unittest framework

import unittest

def add(a, b):
    return a + b

class TestAddFunction(unittest.TestCase):
    def test_add_positive(self):
        self.assertEqual(add(2, 3), 5)
    def test_add_negative(self):
        self.assertEqual(add(-1, -1), -2)
    def test_add_zero(self):
        self.assertEqual(add(0, 0), 0)

# 12. Mock example in unit test (simulate a function)

from unittest.mock import patch

def fetch_data():
    # Simulate fetching data (e.g., from network)
    return "real data"

class TestFetchData(unittest.TestCase):
    @patch('__main__.fetch_data')
    def test_fetch_mocked(self, mock_fetch):
        mock_fetch.return_value = "mocked data"
        result = fetch_data()
        self.assertEqual(result, "mocked data")

# --- Important Questions ---

# 1. Extract WARNING lines from /tmp/app.log and save to /tmp/warnings.txt

def extract_warnings(input_file="/tmp/app.log", output_file="/tmp/warnings.txt"):
    try:
        with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
            for line in infile:
                if "WARNING" in line:
                    outfile.write(line)
        print(f"Warnings extracted to {output_file}")
    except FileNotFoundError:
        print(f"File not found: {input_file}")

# 2. Parse /tmp/config.ini and extract host and user from [DATABASE]

import configparser

def read_database_config(file_path="/tmp/config.ini"):
    config = configparser.ConfigParser()
    try:
        config.read(file_path)
        host = config.get('DATABASE', 'host')
        user = config.get('DATABASE', 'user')
        print(f"Database host: {host}")
        print(f"Database user: {user}")
    except Exception as e:
        print(f"Error reading config: {e}")

# 3. Check /tmp/report.csv existence, print first 5 lines or message

def print_report_head(file_path="/tmp/report.csv", lines=5):
    try:
        with open(file_path, 'r') as f:
            for i, line in enumerate(f):
                if i >= lines:
                    break
                print(line.strip())
    except FileNotFoundError:
        print(f"File not found: {file_path}")

# 4. Check CPU utilization and print warning if > 80% (requires psutil)

import psutil

def check_cpu_utilization(threshold=80):
    cpu_percent = psutil.cpu_percent(interval=1)
    print(f"CPU Utilization: {cpu_percent}%")
    if cpu_percent > threshold:
        print("High CPU utilization detected!")

# 5. Ping servers from /tmp/servers.txt and print result

import subprocess

def ping_servers(file_path="/tmp/servers.txt"):
    try:
        with open(file_path, 'r') as f:
            servers = [line.strip() for line in f if line.strip()]
        for server in servers:
            # ping once, timeout 1 sec
            try:
                result = subprocess.run(
                    ['ping', '-c', '1', '-W', '1', server],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                if result.returncode == 0:
                    print(f"Ping successful: {server}")
                else:
                    print(f"Ping failed: {server}")
            except Exception as e:
                print(f"Error pinging {server}: {e}")
    except FileNotFoundError:
        print(f"File not found: {file_path}")

# 6. Extract unique timestamps from /tmp/access.log and print list

def extract_unique_timestamps(file_path="/tmp/access.log"):
    timestamps = set()
    try:
        with open(file_path, 'r') as f:
            for line in f:
                parts = line.split()
                if parts:
                    timestamps.add(parts[0])  # assuming timestamp is first word
        print("Unique timestamps found:")
        print(sorted(timestamps))
    except FileNotFoundError:
        print(f"File not found: {file_path}")

# 7. Parse JSON user data and print names of users older than 28

import json

def users_older_than_28(file_path="/tmp/user_data.json"):
    try:
        with open(file_path, 'r') as f:
            users = json.load(f)
        names = [user['name'] for user in users if user.get('age', 0) > 28]
        print("Users older than 28:")
        for name in names:
            print(name)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading JSON: {e}")

# 8. Check free disk space on /tmp and warn if less than 1GB

import shutil

def check_disk_space(path="/tmp", threshold_gb=1):
    total, used, free = shutil.disk_usage(path)
    free_gb = free / (1024 ** 3)
    print(f"Free disk space on {path}: {free_gb:.2f} GB")
    if free_gb < threshold_gb:
        print(f"Low disk space on {path}!")

# 9. Replace placeholders in email template from dictionary

def fill_email_template(template_path="/tmp/email_template.txt", values=None):
    if values is None:
        values = {"name": "User123", "status": "Active", "link": "https://example.com/login"}
    try:
        with open(template_path, 'r') as f:
            template = f.read()
        for key, val in values.items():
            placeholder = f"{{{{{key}}}}}"  # e.g. {{name}}
            template = template.replace(placeholder, val)
        print("Filled email template:")
        print(template)
    except FileNotFoundError:
        print(f"File not found: {template_path}")

# 10. Count occurrences of "Failed" in /tmp/security.log (case-insensitive)

def count_failed_occurrences(file_path="/tmp/security.log"):
    count = 0
    try:
        with open(file_path, 'r') as f:
            for line in f:
                count += line.lower().count("failed")
        print(f"Occurrences of 'Failed': {count}")
    except FileNotFoundError:
        print(f"File not found: {file_path}")

# If running as main, you can test functions here (optional)
if __name__ == "__main__":
    print("Run individual functions as needed for testing.")

import os

def list_files(path):
    """List all files in the given directory."""
    return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

def get_file_size(filepath):
    """Return the size of a file in bytes."""
    return os.path.getsize(filepath)
