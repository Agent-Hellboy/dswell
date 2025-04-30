import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from .logger import logger

PENDING_FILE = Path.home() / ".dswell" / "pending.json"


def ensure_pending_file() -> None:
    """Ensure the pending.json file exists and has valid content."""
    PENDING_FILE.parent.mkdir(exist_ok=True)

    try:
        if PENDING_FILE.exists():
            with open(PENDING_FILE, "r") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return  # File exists and contains valid dictionary
                logger.warning("pending.json contains invalid data, resetting")
    except Exception as e:
        logger.warning(f"Error reading pending.json: {e}, resetting file")

    # Create new file with empty dictionary
    with open(PENDING_FILE, "w") as f:
        json.dump({}, f, indent=2)


def add_pending(path: str, deletion_time: int) -> None:
    """Add a new pending deletion.

    Args:
        path: Path to the file/directory to be deleted
        deletion_time: Time in seconds until deletion
    """
    ensure_pending_file()
    try:
        with open(PENDING_FILE, "r") as f:
            data = json.load(f)

        data[path] = {
            "created_at": datetime.now().isoformat(),
            "deletion_time": deletion_time,
            "scheduled_deletion": (datetime.now().timestamp() + deletion_time),
        }

        with open(PENDING_FILE, "w") as f:
            json.dump(data, f, indent=2)

        logger.debug(f"Added pending deletion for {path}")
    except Exception as e:
        logger.error(f"Failed to add pending deletion: {e}")


def remove_pending(path: str) -> None:
    """Remove a pending deletion.

    Args:
        path: Path to remove from pending deletions
    """
    if not PENDING_FILE.exists():
        return

    try:
        with open(PENDING_FILE, "r") as f:
            data = json.load(f)

        if path in data:
            del data[path]
            with open(PENDING_FILE, "w") as f:
                json.dump(data, f, indent=2)
            logger.debug(f"Removed pending deletion for {path}")
    except Exception as e:
        logger.error(f"Failed to remove pending deletion: {e}")


def get_pending_deletions() -> List[Dict]:
    """Get all pending deletions with time remaining.

    Returns:
        List of dictionaries containing pending deletion information
    """
    ensure_pending_file()

    try:
        with open(PENDING_FILE, "r") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            logger.error("Invalid pending.json format: expected dictionary")
            return []

        current_time = datetime.now().timestamp()
        pending = []

        for path, info in data.items():
            if not isinstance(info, dict):
                continue

            scheduled_time = info.get("scheduled_deletion")
            if not scheduled_time:
                continue

            time_left = scheduled_time - current_time
            if time_left > 0:
                pending.append(
                    {
                        "path": path,
                        "created_at": info.get("created_at", ""),
                        "time_left": int(time_left),
                    }
                )

        return sorted(pending, key=lambda x: x["time_left"])
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in pending.json: {e}")
        return []
    except Exception as e:
        logger.error(f"Failed to get pending deletions: {e}")
        return []
