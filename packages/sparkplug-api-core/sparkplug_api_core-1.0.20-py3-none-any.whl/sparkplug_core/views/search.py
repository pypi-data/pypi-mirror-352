import logging

from decouple import config
from django.db.models import QuerySet
from django_elasticsearch_dsl.search import Search
from rest_framework.viewsets import ReadOnlyModelViewSet

from ..pagination import SearchPagination
from . import LogQueryCount

log = logging.getLogger(__name__)


class SearchView(
    LogQueryCount,
    ReadOnlyModelViewSet,
):
    lookup_field = "uuid"
    pagination_class = SearchPagination

    search_query = None
    log_field = "title"

    def get_start_end(
        self,
        page: int,
    ) -> tuple[int, int]:
        start = (page - 1) * SearchPagination.page_size
        end = start + SearchPagination.page_size - 1
        return (start, end)

    def get_search_query(self, **kwargs) -> Search:
        raise NotImplementedError

    def get_queryset(self) -> QuerySet:
        term = self.request.query_params.get("term", "")
        page = int(self.request.query_params.get("page", "1"))
        start, end = self.get_start_end(page)

        self.search_query = self.get_search_query(
            term=term,
            start=start,
            end=end,
        )

        self.log_scores(self.search_query)

        return self.search_query.to_queryset()

    def log_scores(self, search_query: Search) -> None:
        log_level = config("API_LOG_LEVEL", default="INFO")

        if log_level != "DEBUG":
            return

        # For debugging purposes only
        for hit in search_query:
            msg = f"{hit.meta.score} - {getattr(hit, self.log_field, None)}"

            log.debug(msg)

    def paginate_queryset(self, queryset: QuerySet) -> QuerySet | None:
        if self.paginator is None:
            return None

        self.paginator.set_search_query(self.search_query)

        return self.paginator.paginate_queryset(
            queryset,
            self.request,
            view=self,
        )
