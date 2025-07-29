from django.db.models import QuerySet


class ActionQueryset:
    def get_queryset(self) -> QuerySet:
        action_queryset = f"get_{self.action}_queryset"

        method = getattr(self, action_queryset, None)
        if method:
            return method()

        # Fallback to detail/list queryset if no action queryset defined
        if self._is_detail_request():
            return self.get_detail_queryset()

        return self.get_list_queryset()

    def get_detail_queryset(self) -> QuerySet:
        return self.model.objects.all()

    def _is_detail_request(self) -> bool:
        # https://github.com/chibisov/drf-extensions/blob/master/rest_framework_extensions/mixins.py
        if hasattr(self, "lookup_url_kwarg"):
            lookup = self.lookup_url_kwarg or self.lookup_field

        return lookup and lookup in self.kwargs
