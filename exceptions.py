#creating ParseWikiError as superclass for all other parsing related errors

class ParseWikiError(Exception):
    """
    Base exception class for parsing wikipedia errors
    """
    pass

class TopicNotFoundError(ParseWikiError):
    def __init__(self, message, topic):
        self.message = message,
        self.topic = topic

class HTMLParsingError(ParseWikiError):
    def __init__(self, message, topic):
        self.message = message,
        self.topic = topic