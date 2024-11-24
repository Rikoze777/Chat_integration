def parse_sql(file_content: str) -> list:
    """
    Парсит SQL-файл, возвращая список запросов.
    """
    queries = file_content.strip().split(";")
    result = [query.strip() for query in queries if query.strip()]
    return str(result)

