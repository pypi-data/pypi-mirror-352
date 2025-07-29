from django.db.models import Case, When


def preserve_order(uuids: list[str]) -> Case:
    # taken from django_elasticsearch_dsl to_queryset() method
    # https://github.com/django-es/django-elasticsearch-dsl/blob/master/django_elasticsearch_dsl/search.py#L34
    return Case(
        *[When(uuid=uuid, then=pos) for pos, uuid in enumerate(uuids)],
    )
