# telegram_http_server_monitoring
A simple application for monitoring many HTTP services in telegram. 

Supported only python 3.4+

First, install a requriments libraies:

`pip install -r requriments.txt`


Example of configuration file in _config.yaml_example_

Sections in **config.yaml**:

**hosts** contains description of monitoring hosts. Firts value contains name of service.
**admin_ids** contains all telegram ids for messages about current host

**urls_to_monitoring** contains pairs  all urls for monitoring current host and timeout 

**db_path** contains path for sqlite database. Created automatic after main.py start. Recomendet value is full path in filesystem

**telegram_api_key** contains API key bot from BotFather


For start monitoring run main.py from any scheduler on every minute.

Example for linux crontab line:

`* * * * * username python3 /path/to/main.py `