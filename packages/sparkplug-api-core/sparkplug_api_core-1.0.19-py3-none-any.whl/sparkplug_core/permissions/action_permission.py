import inspect

from django.core.exceptions import ImproperlyConfigured
from rest_framework import permissions
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.viewsets import GenericViewSet


class ActionPermission:
    """
    Set permission class per view action.

    https://github.com/apirobot/django-rest-action-permissions/blob/master/rest_action_permissions/permissions.py.

    The original code's `enough_perms` has been renamed to `super_perms`.

    read_perms = GET, HEAD, OPTIONS
    write_perms = all others
    """

    def has_permission(
        self,
        request: Request,
        view: GenericViewSet,
    ) -> bool:
        perms = self._get_required_permissions(request, view)
        return perms.has_permission(request, view)

    def has_object_permission(
        self,
        request: Request,
        view: GenericViewSet,
        obj,  # noqa: ANN001
    ) -> bool:
        perms = self._get_required_permissions(request, view)
        return perms.has_object_permission(request, view, obj)

    def _get_required_permissions(  # noqa: ANN202
        self,
        request: Request,
        view: GenericViewSet,
    ):
        action = self._get_action(view.action)
        action_perms_attr = f"{action}_perms"
        perms = self._get_permissions_by_attr(action_perms_attr)

        if perms is None:
            if request.method in permissions.SAFE_METHODS:
                read_perms_attr = "read_perms"
                perms = self._get_permissions_by_attr(read_perms_attr)

                if perms is None:
                    self._raise_attr_error(
                        general_attr=read_perms_attr,
                        action_attr=action_perms_attr,
                    )

            else:
                write_perms_attr = "write_perms"
                perms = self._get_permissions_by_attr(write_perms_attr)

                if perms is None:
                    self._raise_attr_error(
                        general_attr=write_perms_attr,
                        action_attr=action_perms_attr,
                    )

        global_perms_attr = "global_perms"
        global_perms = self._get_permissions_by_attr(global_perms_attr)

        if global_perms is not None:
            perms = global_perms & perms

        super_perms_attr = "super_perms"
        super_perms = self._get_permissions_by_attr(super_perms_attr)
        if super_perms is not None:
            perms = super_perms | perms

        return perms()

    def _get_permissions_by_attr(self, attr: str):  # noqa: ANN202
        if not hasattr(self, attr):
            return None
        perms = getattr(self, attr)
        self._validate_permissions(perms=perms, attr=attr)
        return perms

    def _get_action(self, action: str) -> str:
        meta = getattr(self, "Meta", None)
        partial_update_is_update = getattr(
            meta,
            "partial_update_is_update",
            True,
        )

        if action == "partial_update" and partial_update_is_update:
            return "update"

        return action

    def _validate_permissions(
        self,
        perms,  # noqa: ANN001
        attr: str,
    ) -> None:
        if not (
            inspect.isclass(perms) and issubclass(perms, BasePermission)
        ) and not any(
            isinstance(perms, class_)
            for class_ in (
                permissions.OperandHolder,
                permissions.SingleOperandHolder,
            )
        ):
            self._raise_validation_error(attr=attr)

    def _raise_attr_error(
        self,
        action_attr: str,
        general_attr: str,
    ) -> None:
        msg = (
            f"`{self.__class__.__name__}` class must declare `{self.__class__.__name__}.{action_attr}` or "  # noqa: E501
            f"`{self.__class__.__name__}.{general_attr}` attributes"
        )
        raise RuntimeError(
            msg,
        )

    def _raise_validation_error(self, attr: str) -> None:
        msg = (
            f"`{self.__class__.__name__}` class has invalid permission definition in "  # noqa: E501
            f"`{self.__class__.__name__}.{attr}` attribute"
        )
        raise ImproperlyConfigured(
            msg,
        )
