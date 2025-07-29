from datetime import datetime
from typing import List


def is_time_in_ranges(dt: datetime, ranges: List[str]):
    """
    Check if the given datetime is in the given time ranges
    :param dt: datetime to check if it is in the ranges
    :param ranges: a list of time ranges in the format "HH:MM-HH:MM"
    :return:
    """
    for time_range in ranges:
        start_str, end_str = time_range.split('-')
        start_time = datetime.strptime(start_str, "%H:%M").time()
        end_time = datetime.strptime(end_str, "%H:%M").time()

        if start_time <= dt.time() <= end_time:
            return True

    return False
