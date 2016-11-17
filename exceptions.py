"""
holds some custom execptions
"""

class NoRedirectException(Exception):
    """
    unable to follow a redirect from dx.doi.org
    """
    pass

class NoContentInIndexException(Exception):
    """
    an es index is empty
    """
    pass
