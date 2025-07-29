import logging

from django.db.models import QuerySet

from .search import SearchView

log = logging.getLogger(__name__)


class SearchWithParentView(
    SearchView,
):
    def get_parent_uuid(self) -> str:
        raise NotImplementedError

    def get_queryset(self) -> QuerySet:
        parent_uuid = self.get_parent_uuid()
        term = self.request.query_params.get("term", "")
        page = int(self.request.query_params.get("page", "1"))
        start, end = self.get_start_end(page)

        self.search_query = self.get_search_query(
            term=term,
            start=start,
            end=end,
            parent_uuid=parent_uuid,
        )

        return self.search_query.to_queryset()
