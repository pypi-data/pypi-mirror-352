import urllib.parse


def get_query_param(url: str, param: str) -> str | None:
    """Extract the query parameter value from a URL string."""
    try:
        parsed_url = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed_url.query)

        if value := query_params.get(param):
            # Return the first param value
            return value[0]
    except Exception:  # noqa: BLE001, S110
        pass

    return None
