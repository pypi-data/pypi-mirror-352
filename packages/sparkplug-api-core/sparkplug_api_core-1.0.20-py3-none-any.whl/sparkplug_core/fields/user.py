from django.contrib.auth import get_user_model
from rest_framework.serializers import SlugRelatedField


class UserUuidField(SlugRelatedField):
    def __init__(self, **kwargs) -> None:
        User = get_user_model()  # noqa: N806
        kwargs.setdefault("queryset", User.objects.all())
        kwargs.setdefault("slug_field", "uuid")
        kwargs.setdefault("source", "user")
        super().__init__(**kwargs)
