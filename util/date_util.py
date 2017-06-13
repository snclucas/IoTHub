from dateutil.parser import parse
from dateutil.relativedelta import *
from datetime import *


def parse_date(date_string):
    return parse(date_string)


def __check_date__(date_string):
    try:
        parse_date(date_string)
        return True
    except ValueError:
        return False


def get_date_delta(date1, date2):
    if __check_date__(date1) and __check_date__(date2):
        return relativedelta(date1, date2)
    else:
        return None


def get_now():
    return datetime.now()
