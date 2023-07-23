from celery import shared_task
from datetime import datetime
from importlib import import_module


@shared_task
def parse_news(parser_classes: list[str], last_timestamp: datetime):
    module = import_module('api.parsers')
    for pc in parser_classes:
        c = getattr(module, pc)
        parser = c(last_timestamp)
        parser.parse()
    return {'result': 'success'}
