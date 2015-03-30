import datetime
import requests


class UniScraper(object):

    def __init__(self):
        self.name = 'UniScraper'
        self.remotes = []
        self.log = None

    def get_data(self, resto):
        raise NotImplementedError("Implement get_data")

    def curl(self, url):
        return requests.get(url)

    def clean_string(self, string):
        return string.replace(u'\xa0', u' ').strip()

    def format_date(self, date):
        """ Returns the date object formatted as the server expects it
        """
        if not isinstance(date, datetime.date):
            raise ValueError("date is expected to be a date")

        return date.strftime('%m/%d/%Y')
