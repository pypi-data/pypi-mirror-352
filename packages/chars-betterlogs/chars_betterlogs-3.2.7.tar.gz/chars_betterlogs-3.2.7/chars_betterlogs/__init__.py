from .logs import Logging
from . import betterLogs
__all__ = ["Logging", "betterLogs", "getLogFile"]

def getLogFile(logging:Logging) -> str:
    rawXml = open(logging.filename, 'r')
    xml = rawXml.read(); rawXml.close()
    return xml