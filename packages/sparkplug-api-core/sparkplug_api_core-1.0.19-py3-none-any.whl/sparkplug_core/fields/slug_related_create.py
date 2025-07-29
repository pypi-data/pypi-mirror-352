from rest_framework import serializers


# https://stackoverflow.com/a/28011896/2407209
class SlugRelatedCreate(
    serializers.SlugRelatedField,
):
    def to_internal_value(self, data: dict):  # noqa: ANN201
        try:
            return self.get_queryset().get_or_create(
                **{self.slug_field: data},
            )[0]

        except (TypeError, ValueError):
            self.fail("invalid")
