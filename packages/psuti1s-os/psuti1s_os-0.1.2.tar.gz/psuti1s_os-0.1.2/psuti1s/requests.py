#   __
#  /__)  _  _     _   _ _/   _
# / (   (- (/ (/ (- _)  /  _)
#          /

"""
Requests HTTP Library
~~~~~~~~~~~~~~~~~~~~~

Requests is an HTTP library, written in Python, for human beings.
Basic GET usage:

   >>> import requests
   >>> r = requests.get('https://www.python.org')
   >>> r.status_code
   200
   >>> b'Python is a programming language' in r.content
   True

... or POST:

   >>> payload = dict(key1='value1', key2='value2')
   >>> r = requests.post('https://httpbin.org/post', data=payload)
   >>> print(r.text)
   {
     ...
     "form": {
       "key1": "value1",
       "key2": "value2"
     },
     ...
   }

The other HTTP methods are supported - see `requests.api`. Full documentation
is at <https://requests.readthedocs.io>.

:copyright: (c) 2017 by Kenneth Reitz.
:license: Apache 2.0, see LICENSE for more details.
"""

import warnings

import urllib3

from .exceptions import RequestsDependencyWarning

try:
    from charset_normalizer import __version__ as charset_normalizer_version
except ImportError:
    charset_normalizer_version = None



import requests

def get_weather(city, api_key):
    url = "http://api.weatherapi.com/v1/current.json"
    params = {'key': api_key, 'q': city}
    try:
        response = requests.get(url, params=params)
        data = response.json()
        city_name = data['location']['name']
        temp_c = data['current']['temp_c']
        desc = data['current']['condition']['text']
        return {"City": city_name, "Temperature": temp_c, "Description": desc}
    except:
        return "Error fetching weather data"


import requests
url = "http://httpbin.org"
res = requests.get(url)
if res.status_code == 200:
    print("Site is UP")
    print("API Response:")
    print(res.text)
else:
    print("Site is DOWN")

    

from selenium import webdriver

driver = webdriver.Chrome()  # Make sure chromedriver is installed and in PATH
driver.get("https://www.python.org")

print(driver.title)  # Print the page title

driver.quit()