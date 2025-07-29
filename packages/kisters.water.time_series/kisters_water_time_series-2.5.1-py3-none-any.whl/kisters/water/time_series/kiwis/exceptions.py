class KiWISError(Exception):
    """Exception raised when KiWIS returns an error message"""


class KiWISNoResultsError(Exception):
    """This error is to identify KiWIS queries which produce no results"""


class KiWISDataSourceError(Exception):
    """This error is to mark a likely error due to limit of timestamps to serve from KiWIS"""
