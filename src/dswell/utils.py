import re

## ================================Time Parsing================================
## TODO: Add support for more time units like days, weeks, months, years, etc.


def parse_time(time_str: str) -> int:
    """
    Parse time string in format like '1h3m2s', '1h', '30m', etc. into seconds.

    Args:
        time_str: Time string in format like '1h3m2s', '1h', '30m', etc.

    Returns:
        int: Total time in seconds

    Raises:
        ValueError: If time string format is invalid
    """
    if not time_str:
        raise ValueError("Time string cannot be empty")

    # Regular expression to match time components
    pattern = r"^(?:(?P<hours>\d+)h)?(?:(?P<minutes>\d+)m)?(?:(?P<seconds>\d+)s)?$"
    match = re.match(pattern, time_str.lower())

    if not match:
        raise ValueError(
            "Invalid time format. Use format like '1h3m2s', '1h', '30m', etc."
        )

    # Extract components
    hours = int(match.group("hours") or 0)
    minutes = int(match.group("minutes") or 0)
    seconds = int(match.group("seconds") or 0)

    # Convert to total seconds
    total_seconds = (hours * 3600) + (minutes * 60) + seconds

    if total_seconds == 0:
        raise ValueError("Time must be greater than 0")

    return total_seconds


def format_time(seconds: int) -> str:
    """
    Format seconds into human-readable time string.

    Args:
        seconds: Time in seconds

    Returns:
        str: Formatted time string like '1h3m2s'
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:  # Include seconds if it's the only component
        parts.append(f"{seconds}s")

    return "".join(parts)


## ================================Time Parsing================================
