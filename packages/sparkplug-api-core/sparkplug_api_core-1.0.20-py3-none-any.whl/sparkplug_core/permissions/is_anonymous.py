from django.views import View
from rest_framework.permissions import BasePermission
from rest_framework.request import Request


class IsAnonymous(BasePermission):
    """Allows access only to anonymous users only."""

    def has_permission(
        self,
        request: Request,
        view: View,  # noqa: ARG002
    ) -> bool:
        user = request.user

        if not user:
            return False

        return not user.is_authenticated
