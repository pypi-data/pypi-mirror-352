import re
from datetime import datetime, timedelta


def parse_time_regex(fmt: str, base_time: datetime = None) -> str:
    """
    Replaces {%...} blocks in the input string with time values.

    Rules:
    1. Only content inside {...} is parsed.
    2. Within {...}, only tokens that:
       - start with '%'
       - end with one of [Y, m, d, H, i]
       are treated as time expressions.
    3. Time tokens support offset and rounding:
       - %+nX, %-nX  : add/subtract n units (X = Y/m/d/H/i)
       - %/nX        : floor to nearest n step
       - %+n/stepX   : shift by n and floor by step
    4. All other characters (including before % or invalid tokens) are treated as plain text.
    5. Returns the original string with {%...} blocks replaced by evaluated values.
    """
    if base_time is None:
        base_time = datetime.now()

    def replacer(match):
        expr = match.group(1)
        result = ''
        cursor = 0

        # Match only valid time tokens: starts with %, ends in Y/m/d/H/i
        token_pattern = re.compile(r'%([+-]?\d+)?(?:/(\d+))?([YmdHi])')

        for m in token_pattern.finditer(expr):
            start, end = m.span()

            # Add text before this token as literal
            if cursor < start:
                result += expr[cursor:start]

            offset = int(m.group(1)) if m.group(1) else 0
            step = int(m.group(2)) if m.group(2) else 1
            symbol = m.group(3)

            dt = base_time
            if symbol == 'Y':
                value = dt.year + offset
            elif symbol == 'm':
                year = dt.year
                month = dt.month + offset
                while month <= 0:
                    month += 12
                    year -= 1
                while month > 12:
                    month -= 12
                    year += 1
                value = month
            elif symbol == 'd':
                dt += timedelta(days=offset)
                value = dt.day
            elif symbol == 'H':
                dt += timedelta(hours=offset)
                value = dt.hour
            elif symbol == 'i':
                dt += timedelta(minutes=offset)
                value = dt.minute
            else:
                continue

            norm = (value // step) * step
            width = 4 if symbol == 'Y' else 2
            result += f'{norm:0{width}d}'

            cursor = end

        # Add remaining literal after last token
        if cursor < len(expr):
            result += expr[cursor:]

        return result

    return re.sub(r'\{(.*?)\}', replacer, fmt)


def parse_period(s: str) -> int:
    """
    Converts a duration string to seconds.

    Rules:
    1. Supports suffixes: d (days), h (hours), m (minutes), s (seconds)
    2. If no suffix, assumes seconds
    3. Invalid input returns -1

    Examples:
        "5m" → 300
        "2h" → 7200
        "10" → 10
        "3d" → 259200
        "abc" → -1
    """
    if not s:
        return -1

    unit = s[-1]

    if unit.isdigit():
        return int(s)

    try:
        value = int(s[:-1])
    except ValueError:
        return -1

    if unit == 'd':
        return value * 86400
    elif unit == 'h':
        return value * 3600
    elif unit == 'm':
        return value * 60
    elif unit == 's':
        return value
    else:
        return -1

# Example usage
if __name__ == "__main__":
    #f = "PM10_{%Y%m%dT%-1/6H:%-10/5i}.txt"
    f = "{%Y%m%d%H%-5i}"
    print(parse_time_regex(f))
    print (parse_period("2m"))
