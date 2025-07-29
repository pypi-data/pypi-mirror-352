from sparkplug_core.pagination import SearchPagination


def get_pagination_start_end(page: int) -> tuple[int, int]:
    """
    Return the start and end indices for pagination based on the given page.
    """
    start = (page - 1) * SearchPagination.page_size
    end = start + SearchPagination.page_size - 1
    return (start, end)
