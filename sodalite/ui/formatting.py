UNITS = ['B', 'KB', 'MB', 'GB', 'TB']


def format_size(size: int):
    """
    Converts a file size into human readable format
    :param size: size in bytes
    """
    for unit in UNITS[:-1]:
        if size <= 1024:
            return f"{round(size, 1)}{unit}"
        else:
            size /= 1024
    return f"{round(size, 2)}{UNITS[-1]}"
