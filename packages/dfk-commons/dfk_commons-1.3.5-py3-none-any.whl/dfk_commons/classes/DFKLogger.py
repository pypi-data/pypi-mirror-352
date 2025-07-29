import logging

class DFKLogger:
    def __init__ (self, logger: logging.Logger):
        self.logger = logger
        self.hadErrors = False
    
    def info(self, message):
        self.logger.info(message)
    
    def error(self, message):
        self.logger.error(message)
        self.hadErrors = True