"""Validated partial edits for the native full-object equalizer endpoint."""
from copy import deepcopy
import math

FIELDS = {'bass', 'treble', 'loudness', 'night'}
REQUIRED = {'version', 'bass', 'treble', 'loudness', 'night', 'roomOn', 'room'}

def eq_matches(left, right):
    # The firmware serializes an unused filter list as null before the first
    # write, then [] after validation. They represent the same saved EQ.
    return {**left, 'room': left.get('room') or []} == {**right, 'room': right.get('room') or []}

def eq_payload(current, key, value):
    if not REQUIRED <= current.keys():
        raise ValueError('Equalizer settings are incomplete')
    if key not in FIELDS:
        raise ValueError('Unsupported equalizer control')
    if key in ('bass', 'treble'):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not -12 <= value <= 12 or value != int(value):
            raise ValueError('Use a whole number from -12 to 12 dB')
        value = int(value)
    elif not isinstance(value, bool):
        raise ValueError('Equalizer switch requires true or false')
    result = deepcopy(current)
    result[key] = value
    return result
