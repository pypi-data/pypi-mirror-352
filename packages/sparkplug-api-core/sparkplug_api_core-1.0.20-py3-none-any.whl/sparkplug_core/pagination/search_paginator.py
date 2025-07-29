from django.core.paginator import (
    Page,
    Paginator,
)
from django.utils.functional import cached_property
from django_elasticsearch_dsl.search import Search


class SearchPaginator(
    Paginator,
):
    search_query: Search | None = None

    @cached_property
    def count(self) -> int:
        if not self.search_query:
            return 0

        return self.search_query.count()

    def page(self, number: int) -> Page:
        # This is overridden to prevent any slicing of the object_list.
        # Elasticsearch has returned the sliced data already.
        number = self.validate_number(number)
        return Page(self.object_list, number, self)

    def set_search_query(self, instance: Search) -> None:
        self.search_query = instance
