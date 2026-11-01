class DomainError(Exception):
    """Базовый тип ошибки."""
    status_code: int = 400
    error_code: str = "domain_error"

    def __init__(self, detail: str = None):
        self.detail = detail
        super().__init__(detail)
