class HMException(Exception):
    """
    Base exception for all exceptions pyhomeamtic will raise.
    """


class HMRpcException(HMException):
    """
    Exception for errors while communicating via XML-RPC.
    """
