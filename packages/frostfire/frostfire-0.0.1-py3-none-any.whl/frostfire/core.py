from logging.handlers import TimedRotatingFileHandler
import yaml
import requests
import logging
import os

def monitron_heartbeat(monitron_url,script_id,logger):

    if not monitron_url.endswith('/'):
        monitron_url = f'{monitron_url}/'
    url = f"{monitron_url}{script_id}"
    response = requests.get(url=url)
    logger.info(f'Pinged monitron:{response.status_code}')


def get_logger(log_file_dir_path,log_file_prefix):

    log = logging.getLogger()
    log.setLevel(logging.INFO)

    if not log.handlers:
        os.makedirs(log_file_dir_path, exist_ok=True)
        log_file_path = os.path.join(log_file_dir_path, f"{log_file_prefix}.log")

        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(module)s.%(funcName)s | %(message)s'
        )

        file_handler = TimedRotatingFileHandler(
            filename=log_file_path,
            when="midnight",
            interval=1,
            backupCount=0,
            encoding="utf-8",
            utc=False
        )
        file_handler.setFormatter(formatter)

        log.addHandler(file_handler)

    return log

def load_parallax():
    with open(os.getenv('PARALLAX')) as f:
        parallax = yaml.safe_load(f)
    return parallax
