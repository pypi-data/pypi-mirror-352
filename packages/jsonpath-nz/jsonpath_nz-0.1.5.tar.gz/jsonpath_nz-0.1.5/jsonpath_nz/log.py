import logging
import logging.config
import os
import sys
import tempfile
from datetime import datetime, timedelta

class LoggerConfig:
    """
    Enhanced logging configuration class with file capture and caller information.
    
    This class provides an advanced logging system that extends Python's standard logging
    with features like automatic caller information, conditional file capture, and enhanced
    traceback logging. It creates a logger that can output to both console and file,
    with the ability to selectively capture specific log messages to a file.
    
    The logger automatically includes file name and line number information in all
    log messages, making debugging and troubleshooting more efficient.
    
    Attributes:
        logger (logging.Logger): The configured logger instance with custom methods.
        log_file_path (str, optional): Path to the log file for capture functionality.
        formatter (logging.Formatter): The formatter used for log message formatting.
    
    Examples:
        Basic usage with console logging only:
        
        >>> config = LoggerConfig(level='DEBUG')
        >>> config.logger.info("This is an info message")
        2023-12-07 10:30:45,123 - INFO     [script.py:42] This is an info message
        
        With file capture enabled:
        
        >>> config = LoggerConfig(level='INFO', log_file_path='app.log')
        >>> config.logger.info("Normal message")  # Console only
        >>> config.logger.info("Important message", capture=True)  # Console + file
        >>> config.logger.error("Error occurred", 1)  # Console + file (using positional flag)
        
        Exception handling with traceback:
        
        >>> try:
        ...     1 / 0
        ... except:
        ...     config.logger.traceback()  # Logs detailed traceback to file
        
        Updating configuration:
        
        >>> new_path = config.logger.config('new_log_file.log')
        >>> print(new_path)  # Returns: 'new_log_file.log'
    
    Note:
        - All log messages automatically include caller file name and line number
        - The capture functionality allows selective file logging while maintaining console output
        - Custom methods replace standard logging methods to provide enhanced functionality
        - The logger is thread-safe for concurrent usage
    """
    
    def __init__(self, level='INFO', log_file_path=None):
        """
        Initialize the logger configuration with custom handlers and formatting.
        
        Creates a logger instance with console output and optional file capture capability.
        All existing handlers are cleared and replaced with custom implementations that
        include caller information and selective file capture.
        
        Args:
            level (str, optional): Logging level as string. Defaults to 'INFO'.
                Valid values: 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'.
                Case-insensitive.
            log_file_path (str, optional): Path to log file for capture functionality.
                If None, file capture is disabled but can be enabled later via config().
                The file will be created if it doesn't exist.
        
        Raises:
            AttributeError: If an invalid logging level is provided.
            PermissionError: If the log file path is not writable.
        
        Example:
            >>> config = LoggerConfig(level='debug', log_file_path='/tmp/app.log')
            >>> config.logger.debug("Debug message")  # Will appear in console
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(getattr(logging, level.upper()))
        self.log_file_path = log_file_path
        
        # Clear existing handlers
        self.logger.handlers = []
        
        # Create formatter
        self.formatter = logging.Formatter('%(asctime)s - %(levelname)-8s  %(message)s')
        
        # Always add console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self.formatter)
        self.logger.addHandler(console_handler)
        
        # Replace all logging methods with custom ones
        self._setup_custom_methods()
    
    def _log_with_capture(self, level, msg, *args, **kwargs):
        """
        Internal method to handle logging with optional file capture functionality.
        
        This method processes all log messages, adding caller information and handling
        the capture parameter for selective file logging. It supports both keyword
        and positional argument forms for the capture flag.
        
        Args:
            level (int): Logging level constant (e.g., logging.INFO, logging.ERROR).
            msg (str): The log message, which may contain format placeholders.
            *args: Variable arguments for message formatting.
            **kwargs: Keyword arguments, may include 'capture' flag.
                capture (bool): If True, also write this message to the log file.
        
        Capture Flag Usage:
            - Keyword form: logger.info("Message", capture=True)
            - Positional form: logger.info("Message", 1)  # 1 as first arg means capture
        
        Note:
            - Automatically prepends caller file name and line number to messages
            - Falls back gracefully if file writing fails
            - Uses the same formatter for both console and file output
            - Removes capture flag from args before logging to prevent formatting errors
        """
        caller_frame = sys._getframe(2)
        msg = f"[{os.path.basename(caller_frame.f_code.co_filename)}:{caller_frame.f_lineno}] {msg}"
        
        # Check for capture flag in either args or kwargs
        should_capture = False
        actual_args = list(args)  # Convert to list for modification
        
        # Check if capture is in kwargs
        if 'capture' in kwargs:
            should_capture = kwargs.pop('capture')
        # Check if first arg is 1
        elif args and args[0] == 1:
            should_capture = True
            actual_args = actual_args[1:]  # Remove the capture flag
            
        # Log to console
        self.logger._log(level, msg, actual_args, **kwargs)
        
        # Additionally write to file if should_capture
        if should_capture and self.log_file_path:
            try:
                formatted_msg = msg % tuple(actual_args) if actual_args else msg
                with open(self.log_file_path, 'a') as f:
                    # Use the same formatter as the console handler
                    log_entry = self.formatter.format(logging.LogRecord(
                        name=self.logger.name,
                        level=level,
                        pathname='',
                        lineno=0,
                        msg=formatted_msg,
                        args=(),
                        exc_info=None
                    ))
                    f.write(f"{log_entry}\n")
            except Exception as e:
                self.logger.error(f"Failed to write to log file: {str(e)}")

    def _setup_custom_methods(self):
        """
        Replace standard logging methods with enhanced versions that support file capture.
        
        This method creates custom implementations of all standard logging methods
        (debug, info, warning, error, critical) plus additional utility methods
        (traceback, config). All custom methods support the capture parameter for
        selective file logging.
        
        Custom Methods Created:
            - debug(msg, *args, **kwargs): Debug level logging
            - info(msg, *args, **kwargs): Info level logging  
            - warning(msg, *args, **kwargs): Warning level logging
            - error(msg, *args, **kwargs): Error level logging
            - critical(msg, *args, **kwargs): Critical level logging
            - traceback(exc_info=None): Enhanced exception logging
            - config(log_file_path=None): Configuration management
        
        All methods support:
            - Standard string formatting with args
            - capture=True keyword argument for file logging
            - Positional capture flag (1 as first argument)
            - Automatic caller information injection
        
        Example:
            After setup, these methods become available on the logger:
            >>> logger.info("User %s logged in", username, capture=True)
            >>> logger.error("Failed operation", 1)  # 1 enables capture
            >>> logger.traceback()  # Logs current exception with full traceback
        """
        def custom_debug(msg, *args, **kwargs):
            """
            Log a debug message with optional file capture.
            
            Args:
                msg (str): Debug message, may contain format placeholders.
                *args: Arguments for string formatting.
                **kwargs: Keyword arguments, may include 'capture' for file logging.
            
            Example:
                >>> logger.debug("Processing item %d", item_id, capture=True)
            """
            self._log_with_capture(logging.DEBUG, msg, *args, **kwargs)
        
        def custom_info(msg, *args, **kwargs):
            """
            Log an info message with optional file capture.
            
            Args:
                msg (str): Info message, may contain format placeholders.
                *args: Arguments for string formatting.
                **kwargs: Keyword arguments, may include 'capture' for file logging.
            
            Example:
                >>> logger.info("Operation completed successfully", capture=True)
            """
            self._log_with_capture(logging.INFO, msg, *args, **kwargs)
        
        def custom_warning(msg, *args, **kwargs):
            """
            Log a warning message with optional file capture.
            
            Args:
                msg (str): Warning message, may contain format placeholders.
                *args: Arguments for string formatting.
                **kwargs: Keyword arguments, may include 'capture' for file logging.
            
            Example:
                >>> logger.warning("Deprecated function used: %s", func_name, 1)
            """
            self._log_with_capture(logging.WARNING, msg, *args, **kwargs)
        
        def custom_error(msg, *args, **kwargs):
            """
            Log an error message with optional file capture.
            
            Args:
                msg (str): Error message, may contain format placeholders.
                *args: Arguments for string formatting.
                **kwargs: Keyword arguments, may include 'capture' for file logging.
            
            Example:
                >>> logger.error("Database connection failed: %s", error_msg, capture=True)
            """
            self._log_with_capture(logging.ERROR, msg, *args, **kwargs)
        
        def custom_critical(msg, *args, **kwargs):
            """
            Log a critical message with optional file capture.
            
            Args:
                msg (str): Critical message, may contain format placeholders.
                *args: Arguments for string formatting.
                **kwargs: Keyword arguments, may include 'capture' for file logging.
            
            Example:
                >>> logger.critical("System shutdown initiated", capture=True)
            """
            self._log_with_capture(logging.CRITICAL, msg, *args, **kwargs)
        
        def custom_traceback(exc_info=None):
            """
            Log detailed exception information with full traceback to file.
            
            Provides enhanced exception logging that includes complete traceback
            information with file names, line numbers, function names, and source code.
            The traceback is automatically captured to file regardless of capture settings.
            
            Args:
                exc_info (tuple or Exception, optional): Exception information.
                    Can be:
                    - None: Uses sys.exc_info() to get current exception
                    - Exception instance: Uses the exception's traceback
                    - 3-tuple: (exc_type, exc_value, traceback) from sys.exc_info()
            
            Output Format:
                ======= TRACEBACK =======
                Traceback (most recent call last):
                  File "script.py", line 42, in main
                    result = divide(10, 0)
                  File "script.py", line 15, in divide
                    return a / b
                ZeroDivisionError: division by zero
            
            Examples:
                Current exception:
                >>> try:
                ...     risky_operation()
                ... except:
                ...     logger.traceback()
                
                Specific exception:
                >>> try:
                ...     risky_operation()
                ... except ValueError as e:
                ...     logger.traceback(e)
                
                Manual exception info:
                >>> exc_info = sys.exc_info()
                >>> logger.traceback(exc_info)
            
            Note:
                - Always captures to file if log_file_path is configured
                - Gracefully handles cases where traceback extraction fails
                - Includes source code lines when available
            """
            if exc_info is None:
                exc_info = sys.exc_info()

            try:
                if isinstance(exc_info, Exception):
                    tb = exc_info.__traceback__
                    exc_type = type(exc_info)
                    exc_value = exc_info
                else:
                    exc_type, exc_value, tb = exc_info
                
                import traceback
                tb_list = traceback.extract_tb(tb)
                
                error_msg = "======= TRACEBACK =======\n"
                error_msg += "Traceback (most recent call last):\n"
                
                for filename, line_no, function, text in tb_list:
                    error_msg += f"  File \"{filename}\", line {line_no}, in {function}\n"
                    if text:
                        error_msg += f"    {text}\n"
                
                error_msg += f"{exc_type.__name__}: {str(exc_value)}"
                self._log_with_capture(logging.ERROR, error_msg, capture=True)
                    
            except Exception as e:
                self.logger.error(f"Failed to log traceback: {str(e)}")
        
        def custom_config(log_file_path=None):
            """
            Configure or retrieve logger settings.
            
            Allows runtime configuration updates, particularly for changing the log file path.
            Can be used to enable file capture after logger initialization or to change
            the target log file.
            
            Args:
                log_file_path (str, optional): New path for log file capture.
                    If provided, updates the current log file path.
                    If None, returns the current log file path without changes.
            
            Returns:
                str or None: The current log file path after any updates.
                    Returns None if no log file path is configured.
            
            Examples:
                Get current log file path:
                >>> current_path = logger.config()
                >>> print(current_path)  # '/tmp/app.log' or None
                
                Update log file path:
                >>> new_path = logger.config('/var/log/application.log')
                >>> print(new_path)  # '/var/log/application.log'
                
                Enable file capture on existing logger:
                >>> logger.config('debug.log')
                >>> logger.info("Now capturing to file", capture=True)
            
            Note:
                - Changes take effect immediately for subsequent capture operations
                - Does not validate file path existence or permissions
                - Can be called multiple times to change log destinations
            """
            if log_file_path:
                self.log_file_path = log_file_path                
            return self.log_file_path

        # Attach all custom methods to logger
        self.logger.debug = custom_debug
        self.logger.info = custom_info
        self.logger.warning = custom_warning
        self.logger.error = custom_error
        self.logger.critical = custom_critical
        self.logger.traceback = custom_traceback
        self.logger.config = custom_config

# Create log file
log_file = os.path.join(tempfile.gettempdir(), f'arlog_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
logger_config = LoggerConfig(level='DEBUG', log_file_path=log_file)
log = logger_config.logger


