import io
import os
import json
import requests
import logging
from multiprocessing import Pool, cpu_count
from multiprocessing.dummy import Pool as ThreadPool

import config

from uniresto.util.mplog import MultiProcessingLog
import uniscrapers

mplog = MultiProcessingLog(config.LOG_FILENAME, 'a', 0, 0)
mplog.setFormatter(logging.Formatter(config.LOG_FORMAT))
logging.basicConfig(level=logging.WARNING)  # TODO: logging.WARNING
logging.getLogger().addHandler(mplog)


_instances = {}


def find_scrapers():
    """Returns a list of Scraper subclass instances
    """
    plugins = []
    for class_name in uniscrapers.__all__:
        cls = getattr(uniscrapers, class_name)
        # Only instantiate each plugin class once.
        if class_name not in _instances:
            _instances[class_name] = cls()
        plugins.append(_instances[class_name])
    return plugins


def dump(data, filename):
    # TODO: remove filename param when we are exporting to server
    # This JSON writing business is temporary, until the server is ready
    with io.open(os.path.join('.', filename), 'w', encoding='utf8') as f:
        f.write(unicode(json.dumps(data, ensure_ascii=False)))

    # TODO: wait for the server to be ready for us
    # r = requests.post(config.SERVER_URL,
    #                   json=data,
    #                   params={'passPhrase': config.SERVER_AUTH_TOKEN})
    # logging.info(r)


def run_scraper(scraper):
    """ Runs the Scraper to get the data and dump it somewhere (db, json, ...)
    """
    def get_data_and_dump((url, lang)):
        try:
            data = scraper.get_data(url, lang)
            if not data:
                raise Exception('lege data')
            # TODO: remove filename param
            dump(data, scraper.name + '_' + lang + '.json')
        except Exception as exc:
            # TODO: proper exception handling, not this catch-all crap
            # TODO: reschedule this scraper
            logging.exception(exc)

    scraper.log = logging
    pool = ThreadPool()
    pool.map(get_data_and_dump, scraper.remotes)


def main():
    logging.info("Start scraping")

    pool = Pool(cpu_count() // 2)
    pool.map(run_scraper, find_scrapers())

    logging.info("Finish scraping")


if __name__ == '__main__':
    main()
