def construct_url(base_url: str, endpoint: str) -> str:
    """
    Конструирует полный URL из базового URL и эндпоинта.
    :param base_url: Базовый URL.
    :param endpoint: Эндпоинт.
    :return: Полный URL.
    """
    return f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
