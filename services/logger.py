"""
services/logger.py
Professional logging system for the GeoDraft AI platform.
Tracks events, warnings, and errors internally without exposing raw exceptions to the UI.
"""
import logging
import time

class EngineeringLogger:
    def __init__(self):
        self.logger = logging.getLogger("GeoDraft")
        self.logger.setLevel(logging.DEBUG)
        if not self.logger.handlers:
            ch = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

    def log_processing_time(self, operation, start_time):
        elapsed = time.time() - start_time
        msg = f"{operation} completed in {elapsed:.2f} seconds."
        self.logger.info(msg)
        return msg

    def info(self, msg):
        self.logger.info(msg)
        
    def warning(self, msg):
        self.logger.warning(msg)
        
    def error(self, msg, exc=None):
        if exc:
            self.logger.error(f"{msg}: {str(exc)}")
        else:
            self.logger.error(msg)

logger = EngineeringLogger()
