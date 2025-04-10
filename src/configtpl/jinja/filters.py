def jinja_filter_split_space(input: str) -> list[str]:
    """Splits a multiline string into list of strings where each item is a line"""
    return input.strip().split()
