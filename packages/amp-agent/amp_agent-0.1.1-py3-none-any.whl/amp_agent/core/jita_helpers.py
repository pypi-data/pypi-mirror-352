import json
from typing import Dict, Any, Optional, Union
from datetime import datetime, timedelta, UTC
import re

def _resolve_dynamic_date(date_str: str) -> str:
    """
    Resolve dynamic date strings like 'today+7' to ISO date strings.

    Args:
        date_str: The date string, e.g., 'today+7', '2023-07-05'.

    Returns:
        str: ISO formatted date string (YYYY-MM-DD).
    """
    today = datetime.now(UTC).date()
    match = re.match(r"today([+-]\d+)?", date_str)
    if match:
        offset = int(match.group(1) or 0)
        resolved = today + timedelta(days=offset)
        return resolved.isoformat()
    # Try to parse as date
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date().isoformat()
    except Exception:
        return date_str  # fallback, return as-is

def _process_dates_in_dict(d: Any) -> Any:
    """
    Recursively resolve dynamic date strings in a dict or list.
    """
    if isinstance(d, dict):
        return {k: _process_dates_in_dict(v) for k, v in d.items()}
    elif isinstance(d, list):
        return [_process_dates_in_dict(v) for v in d]
    elif isinstance(d, str) and (d.startswith("today") or re.match(r"\d{4}-\d{2}-\d{2}", d)):
        return _resolve_dynamic_date(d)
    else:
        return d

def build_jita_map(params: Dict[str, Any]) -> str:
    """
    Build a JITA map markdown code block.

    Args:
        params: Dictionary of map parameters.

    Returns:
        str: Markdown code block for the map JITA component.
    """
    payload = _process_dates_in_dict(params)
    return f'```map:{json.dumps(payload, separators=(",", ":"))}```'

def build_jita_calendar(params: Dict[str, Any]) -> str:
    """
    Build a JITA calendar markdown code block, supporting dynamic dates.

    Args:
        params: Dictionary of calendar parameters.

    Returns:
        str: Markdown code block for the calendar JITA component.
    """
    payload = _process_dates_in_dict(params)
    return f'```calendar:{json.dumps(payload, separators=(",", ":"))}```'

def build_jita_selector(params: Dict[str, Any]) -> str:
    """
    Build a JITA selector markdown code block.

    Args:
        params: Dictionary of selector parameters.

    Returns:
        str: Markdown code block for the selector JITA component.
    """
    payload = _process_dates_in_dict(params)
    return f'```selector:{json.dumps(payload, separators=(",", ":"))}```'
