from requests import head


class BaseMonitoring(object):

    def __init__(self, name, admins_ids, urls_to_monitor,
                 sqlite_db_cursor, bot):
        #urls_to_monitor = {k[0]: k[1] for k in urls_to_monitor}
        self.telegram_ids = admins_ids
        self.urls_to_monitor = urls_to_monitor
        self.sqlite_db_cursor = sqlite_db_cursor
        self.bot = bot
        self.name = name
        existing_urls = self.sqlite_db_cursor.execute("SELECT url from urls").fetchall()
        existing_urls = set(url[0] for url in existing_urls)
        print(f'Exiting: {existing_urls}\n')
        needed_urls = set(urls_to_monitor.keys()) - existing_urls
        print(f'Needed: {needed_urls}\n')
        if needed_urls:
            values = ','.join([f"('{url}', 0, {urls_to_monitor[url]})" for url in needed_urls])
            sql = f"INSERT INTO [urls] (url, failcounter, max_fail_count)  values {values}"
            self.sqlite_db_cursor.executescript(sql)
            msg = f'{name}: \n' + '\n'.join([f'Monitoring is running for url {url} with '
                                                f'timeout {urls_to_monitor[url]} '
                                             f'minutes' for url in needed_urls])
            for chat_id in admins_ids:
                bot.send_message(chat_id=chat_id, text=msg)

    def send_message(self, message):
        for telegram_id in self.telegram_ids:
            self.bot.send_message(chat_id=telegram_id, text=message)

    def do_monitor_step(self):
        print(f'HOST {self.name}!')
        for resource in self.urls_to_monitor:
            fails = self.sqlite_db_cursor.execute(f"SELECT failcounter, max_fail_count "
                                                  f"from [urls] where url = '{resource}';").fetchone()
            fail_counter = fails[0]
            max_count = fails[1]
            error = False
            try:
                response = head(resource, verify=False)
            except IOError as err:
                response = {}
                reason = err.__str__
                error_msg = f'{self.name}: Cant connect to {resource}. Reason: {reason}'
                error = True
            if hasattr(response, 'status_code'):
                if response.status_code != 200:
                    error_msg = f'{self.name}: Resource {resource} have status {response.status_code}'
                    error = True
                else:
                    self.sqlite_db_cursor.executescript(
                        f"update [urls] set failcounter = 0 where  url = '{resource}';")
                    if fail_counter >= max_count:
                        self.send_message(f'Resource {resource} is UP after {fail_counter} minutes!')
            if error:
                self.sqlite_db_cursor.executescript(
                    f"update [urls] set failcounter = {fail_counter + 1} where  url = '{resource}';")
                if fail_counter == max_count:
                    self.send_message(error_msg)

