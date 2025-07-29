from rest_framework import status
from rest_framework.mixins import CreateModelMixin
from rest_framework.request import Request
from rest_framework.response import Response


class CreateWithReadResponse(
    CreateModelMixin,
):
    """Create a model instance."""

    def create(
        self,
        request: Request,
        *args,  # noqa: ARG002
        **kwargs,  # noqa: ARG002
    ) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        # Change the action in order to get the available `Read` serializer.
        self.action = "retrieve"
        read_serializer = self.get_serializer_class()(
            instance=serializer.instance,
            context=serializer.context,
        )

        return Response(
            read_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )
