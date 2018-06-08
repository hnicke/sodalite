import math
import time
from typing import List, Dict

FACTOR = 1
RESIDUAL_VALUE = 1  # eventually, an old access will have this value
STEEPNESS = 35  # e.g. 50 would make recent accesses much more valuable

_MILLIS_TO_HOURS = 1000 * 60 * 60 * 24


def populate_ratings(entries: List['Entry']):
    dict = normalize(calculate_frecency(entries))
    for entry, rating in dict.items():
        entry.rating = rating


def calculate_frecency(entries: List['Entry']) -> Dict['Entry', int]:
    now = int(time.time() * 1000)
    entries_to_rating = {}
    for entry in entries:
        frecency = sum(value(now - access) for access in entry.access_history)
        entries_to_rating[entry] = frecency
    return entries_to_rating


def normalize(entries: Dict['Entry', int]) -> Dict['Entry', int]:
    """Maps all frecencies in a way that the max frequency equals 1, in a linear fashion"""
    entries_to_ranking = {}
    biggest = max(entries.values())
    if biggest == 0:
        return {entry: 0.5 for (entry, rating) in entries.items()}
    else:
        for entry, frecency in entries.items():
            relative_frecency = frecency / biggest
            entries_to_ranking[entry] = relative_frecency
        return entries_to_ranking


def value(age_millis: int) -> float:
    """
    Maps an age in milliseconds to a value. More recent values have a higher ranking.
    """
    days = age_millis / _MILLIS_TO_HOURS
    # half life of a value should actually depend on the intensity of usage. todo
    rating = 15 / math.e ** (0.06 * (days - STEEPNESS)) + 1
    return rating
