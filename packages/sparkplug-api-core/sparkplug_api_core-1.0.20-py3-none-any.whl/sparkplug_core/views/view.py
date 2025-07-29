from . import (
    ActionQueryset,
    ActionSerializer,
    CreateWithReadResponse,
    LogQueryCount,
    UpdateWithReadResponse,
)


class BaseView(
    LogQueryCount,
    ActionQueryset,
    ActionSerializer,
):
    lookup_field = "uuid"


class CreateView(
    CreateWithReadResponse,
    BaseView,
):
    pass


class UpdateView(
    UpdateWithReadResponse,
    BaseView,
):
    pass


class CreateUpdateView(
    CreateView,
    UpdateView,
):
    pass
