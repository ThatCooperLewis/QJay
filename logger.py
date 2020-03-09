import logging

class Logger():

    # Make the logging process a little more streamlined/less verbose

    def __init__(self, category_str):
        self.category = category_str

    def info(self, message):
        logging.info('{0}: {1}'.format(self.category, message))

    def warn(self, message):
        logging.warning('{0}: {1}'.format(self.category, message))

    def error(self, message):
        logging.error('{0}: {1}'.format(self.category, message))

    def debug(self, message):
        logging.debug('{0}: {1}'.format(self.category, message))
