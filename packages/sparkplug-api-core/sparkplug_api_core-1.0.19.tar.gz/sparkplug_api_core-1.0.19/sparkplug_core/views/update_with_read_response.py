from rest_framework import status
from rest_framework.mixins import UpdateModelMixin
from rest_framework.request import Request
from rest_framework.response import Response


class UpdateWithReadResponse(
    UpdateModelMixin,
):
    """Update a model instance."""

    def update(
        self,
        request: Request,
        *args,  # noqa: ARG002
        **kwargs,
    ) -> Response:
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial,
        )

        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}  # noqa: SLF001

        # Change the action in order to get the available `Read` serializer.
        self.action = "retrieve"
        read_serializer = self.get_serializer_class()(
            instance=serializer.instance,
            context=serializer.context,
        )

        return Response(
            read_serializer.data,
            status=status.HTTP_200_OK,
        )
