import os
import json
import logging

logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO").upper())


class Formatter:
    """
    Formats results before publishing them to or after receiving them after
    subscribing to MQTT. This base formatter does not change the input or
    output, but establishes an API for other formatters, such as JSONFormatter
    or other, user-defined, formatters.
    """
    def pack(self, x):
        """
        Returns the input unchanged.
        """
        return x

    def unpack(self, x):
        """
        Returns the input unchanged.
        """
        return x


class JSONFormatter(Formatter):
    """
    Formats results as JSON before publishing them to or after receiving them
    after subscribing to MQTT.

    Malformed input is returned unprocessed.
    """
    def pack(self, x):
        """
        Returns the input as a JSON string.

        Malformed input is returned unprocessed.
        """
        try:
            return json.dumps(x)
        except:
            return x
    
    def unpack(self, x):
        """
        Returns the json-formatted input as an object.

        Malformed input is returned unprocessed.
        """
        try:
            return json.loads(x)
        except:
            return x

