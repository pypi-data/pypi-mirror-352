mywigle is a wrapper for the WiGLE WiFi mapping API
contains ai content
# Installation
To install mywigle for Python 2.x or 3.x just call ``pip install mywigle``<br>
You'll also need to set up an account with WiGLE and retrieve your AP
details to go into the config.py file

# Usage
Using the API wrapper is very much like using the API itself. mywigle ha
four modules, corresponding to the four sections of the WiGLE API v2. Seach section is a module in mywigle and each API endpoint is a function in
that module.

To use the API, first import the section, then call the endpoin
function. So to perform an authenticated GET request against an
endpoint:
```python
from mywigle import network
print(network.geocode(addresscode="London"))
```
This returns a ``dict``, or raises an ``HTTPError`` if something went wrong.
# API documentation
The mywigle API wrapper is fully documented with docstrings which wer
correct as of 11/2/2017, but in case of any disagreement between thes
and the `interactive WiGLE API docs <https://api.wigle.net/swagger>`__
the WiGLE docs take precedence. Please submit any discrepancies a
issues `here <https://github.com/jamiebull1/mywigle/issues>`__

The sections and endpoints available are

- `file <https://api.wigle.net/swagger#/Network_observation_file_upload_and_status.>`_

   - `kml <https://api.wigle.net/swagger#!/Network_observation_file_upload_and_status./getKmlForTransId>`_
   - `transactions <https://api.wigle.net/swagger#!/Network_observation_file_upload_and_status./getTransLogsForUser>`_
   -  `upload <https://api.wigle.net/swagger#!/Network_observation_file_upload_and_status./upload>`_

- `network <https://api.wigle.net/swagger#/Network_search_and_information_tools>`_

   - `comment <https://api.wigle.net/swagger#!/Network_search_and_information_tools/comment>`_
   - `detail <https://api.wigle.net/swagger#!/Network_search_and_information_tools/detail>`_
   - `geocode <https://api.wigle.net/swagger#!/Network_search_and_information_tools/geocode>`_
   - `search <https://api.wigle.net/swagger#!/Network_search_and_information_tools/search>`_

- `stats <https://api.wigle.net/swagger#/Statistics_and_information>`_

   - `countries <https://api.wigle.net/swagger#!/Statistics_and_information/countries>`_
   - `general <https://api.wigle.net/swagger#!/Statistics_and_information/generalStats>`_
   - `group <https://api.wigle.net/swagger#!/Statistics_and_information/groupStats>`_
   - `regions <https://api.wigle.net/swagger#!/Statistics_and_information/countryRegion>`_
   - `site <https://api.wigle.net/swagger#!/Statistics_and_information/siteStats>`_
   - `standings <https://api.wigle.net/swagger#!/Statistics_and_information/stats>`_
   - `user <https://api.wigle.net/swagger#!/Statistics_and_information/userStatistics>`_
- `profile <https://api.wigle.net/swagger#/User_profile_operations>`_
   - `apiToken <https://api.wigle.net/swagger#!/User_profile_operations/apiToken>`_
   - `user <https://api.wigle.net/swagger#!/User_profile_operations/user>`_

# Thanks to ...
- @jamiebull1 ([pygle at PyPi](https://pypi.org/project/pygle/))