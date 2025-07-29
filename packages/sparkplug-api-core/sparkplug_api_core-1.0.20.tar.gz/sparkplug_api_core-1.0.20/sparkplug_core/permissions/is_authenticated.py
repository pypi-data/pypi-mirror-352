from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView
from rules import test_rule


class IsAuthenticated(BasePermission):
    def has_permission(
        self,
        request: Request,
        view: APIView,  # noqa: ARG002
    ) -> bool:
        return test_rule("is_authenticated", request.user)
