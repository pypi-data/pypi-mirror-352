CACHE_WORKDAY_DATA = False

DEFAULT_CHROME_PORT = 9222


VERBOSE = False


def set_verbose(verbose: bool):
    """Set the verbosity level for logging."""
    global VERBOSE
    VERBOSE = verbose


def get_verbose():
    """Get the current verbosity level."""
    return VERBOSE
