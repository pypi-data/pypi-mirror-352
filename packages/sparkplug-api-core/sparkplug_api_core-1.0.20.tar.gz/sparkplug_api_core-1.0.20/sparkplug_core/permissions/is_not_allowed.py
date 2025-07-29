from django.views import View
from rest_framework.permissions import BasePermission
from rest_framework.request import Request


class IsNotAllowed(BasePermission):
    """Reject access to the action."""

    def has_permission(
        self,
        request: Request,  # noqa: ARG002
        view: View,  # noqa: ARG002
    ) -> bool:
        return False

    def has_object_permission(
        self,
        request: Request,  # noqa: ARG002
        view: View,  # noqa: ARG002
        obj,  # noqa: ARG002, ANN001
    ) -> bool:
        return False
