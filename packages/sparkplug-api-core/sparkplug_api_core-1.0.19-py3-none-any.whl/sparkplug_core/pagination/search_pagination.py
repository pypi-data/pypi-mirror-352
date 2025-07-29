from django.core.paginator import InvalidPage
from django.db.models import QuerySet
from django.views import View
from django_elasticsearch_dsl.search import Search
from rest_framework.exceptions import NotFound
from rest_framework.request import Request

from .default_pagination import DefaultPagination
from .search_paginator import SearchPaginator


class SearchPagination(
    DefaultPagination,
):
    django_paginator_class = SearchPaginator

    search_query: Search | None = None

    def paginate_queryset(
        self,
        queryset: QuerySet,
        request: Request,
        view: View | None = None,  # noqa: ARG002
    ) -> list | None:
        """
        Paginate a queryset if required.

        Either returning a page object, or `None` if pagination is not
        configured for this view.
        """
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        paginator = self.django_paginator_class(queryset, page_size)

        # Inject the search_query
        paginator.set_search_query(self.search_query)

        page_number = request.query_params.get(self.page_query_param, 1)
        if page_number in self.last_page_strings:
            page_number = paginator.num_pages

        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            msg = self.invalid_page_message.format(
                page_number=page_number,
                message=str(exc),
            )
            raise NotFound(msg) from None

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request
        return list(self.page) if self.page else []

    def set_search_query(self, instance: Search) -> None:
        self.search_query = instance
