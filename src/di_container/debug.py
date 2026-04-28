def validate(container):
    errors = []

    for key, provider in container._scope.providers.items():
        try:
            container.resolve(*key)
        except Exception as e:
            errors.append((key, e))

    return errors