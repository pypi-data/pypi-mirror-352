import json


def get_bool(value: str) -> bool:
    """
    Try to deserialize `value` to a bool.

    On failure, return None.
    """
    try:
        output = json.loads(value)
        if not isinstance(output, bool):
            output = None
    except (
        TypeError,
        json.JSONDecodeError,
    ):
        output = False

    return output
