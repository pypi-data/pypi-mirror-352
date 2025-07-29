class ActionSerializer:
    def get_serializer_class(self):  # noqa: ANN201
        action_serializer_name = f"{self.action}_serializer_class"

        cls = getattr(self, action_serializer_name, None)

        if cls is not None:
            return cls

        write_actions = [
            "create",
            "update",
            "partial_update",
            "destroy",
        ]

        if self.action in write_actions:
            cls = getattr(self, "write_serializer_class", None)
        else:
            cls = getattr(self, "read_serializer_class", None)

        if cls is not None:
            return cls

        return self.serializer_class
