import logging  # Importing the logging module for logging functionality
from logging.handlers import RotatingFileHandler  # Importing RotatingFileHandler for log file rotation
from datetime import datetime  # Importing datetime for handling timestamps

class CustomRotatingFileHandler(RotatingFileHandler):
    '''A custom file handler class for rotating log files based on size.'''

    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=False):
        '''
        Custom file handler for rotating log files based on size.

        Args:
            filename (str): Name of the log file.
            mode (str, optional): File mode. Defaults to 'a'.
            maxBytes (int, optional): Maximum size of the log file before rotation. Defaults to 0 (no limit).
            backupCount (int, optional): Number of backup files to keep. Defaults to 0 (no backups).
            encoding (str, optional): File encoding. Defaults to None.
            delay (bool, optional): If True, file opening is deferred until the first write. Defaults to False.
        '''
        super().__init__(filename, mode, maxBytes, backupCount, encoding, delay)
        self.last_backup_cnt = 0

    def doRollover(self):
        '''
        Perform log file rollover, closing the current log file and opening a new one.
        '''
        if self.stream:
            self.stream.close()
            self.stream = None
        self.last_backup_cnt += 1
        next_name = f'{self.baseFilename}.{self.last_backup_cnt}'
        self.rotate(self.baseFilename, next_name)
        if not self.delay:
            self.stream = self._open()
# Formatting log messages
log_formatter = logging.Formatter('[%(asctime)s - %(levelname)s] - %(name)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
# Creating a file handler for logging to a file
file_handler = CustomRotatingFileHandler(f'Logs/{datetime.now():%m-%d-%H-%M}.log')
file_handler.setFormatter(log_formatter)
# Creating a stream handler for logging to the console
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(log_formatter)
# Configuring the root logger with both file and stream handlers
logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, stream_handler]
)
# Setting the log level for the pyrogram logger to ERROR to suppress unnecessary messages
logging.getLogger('pyrogram').setLevel(logging.ERROR)

def logger(name: str) -> logging.Logger:
    return logging.getLogger(name)  # Function to create and return a named logger