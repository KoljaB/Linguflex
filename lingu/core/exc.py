import traceback
from .log import log


def exc(exception):
    """Log and re-raise an exception with its traceback.

    Args:
        exception (Exception): The exception to be logged and re-raised.

    Raises:
        exception: Re-raises the passed exception after logging.

    """
    # Format the traceback as a string
    tb_str = traceback.format_exc()

    # Logging the exception and its traceback
    log.hgh(f"Exception: {str(exception)}")
    log.hgh("Traceback:")
    log.hgh(f"  {tb_str}")

    # Re-raise the exception
    raise exception
