import sqlite3
from monitoring import BaseMonitoring
import telegram
import yaml
import os

CREATE_STATIONS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS [urls] (
  [id] INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL ,
  [failcounter] integer,
  [url] text UNIQUE,
  [max_fail_count] INTEGER 
);
"""

CREATE_MONITORING_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS [monitoring] (
  [id] INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
  [server] INTEGER,
  [status_code] INTEGER 
);
"""


def init_db(path='monitoring.sqlite3'):
    db_conn = sqlite3.connect(path)
    db_conn.executescript(CREATE_STATIONS_TABLE_SQL)
    db_conn.executescript(CREATE_MONITORING_TABLE_SQL)
    return db_conn


def main():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.yaml')
    print(path)
    with open(path, 'r', encoding='utf-8') as conf_file:
        config = yaml.load(conf_file, Loader=yaml.FullLoader)
    print(config)
    bot = telegram.Bot(token=config['telegram_api_key'])
    db = init_db(config['db_path']) if 'db_path' in config.keys() else init_db()
    for host in config['hosts']:
        name = host[0]
        print(host[0], host[1]['admins_ids'], host[1]['urls_to_monitoring'])
        admins = host[1]['admins_ids']
        urls = {url[0]: url[1] for url in host[1]['urls_to_monitoring']}
        monitor = BaseMonitoring(name, admins, urls, db, bot)
        monitor.do_monitor_step()
    db.close()


if __name__ == '__main__':
    main()
