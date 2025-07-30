import logging


def setup_logging(log_level=logging.INFO, log_file=None):
    """
    Set up the logging configuration.

    Parameters
    ----------
    log_level : int, optional
        The logging level (e.g., logging.INFO, logging.DEBUG),
        by default logging.INFO.
    log_file : str, optional
        The file to which logs should be written.
        If None, logs will be output to the console, by default None.
    """
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    if log_file:
        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
        )
    else:
        logging.basicConfig(level=log_level, format=log_format)

    # Example usage
    logging.getLogger().info("Logging setup complete.")


# Set up logging when the module is imported
if not logging.getLogger().hasHandlers():
    setup_logging()
