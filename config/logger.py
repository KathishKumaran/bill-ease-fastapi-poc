import socket
import logging

log_level = logging.INFO  # Set the log level as needed

# log_format = '{"level":"%(levelname)s","time":"%(asctime)s","pid":%(process)d,"hostname":"%(hostname)s","name":"FastAPI Python Server","msg":"%(message)s"}'
log_format = '{"level":"%(levelname)s","time":"%(asctime)s","name":"FastAPI Python Server","msg":"%(message)s"}'

date_format = "%a %b %d %Y %H:%M:%S %Z%z"  # Adjust the date format as needed

logging.basicConfig(level=log_level, format=log_format, datefmt=date_format)

logger = logging.getLogger(__name__)

# Get the hostname
hostname = socket.gethostname()
# Set the hostname in the logger's extra context
logger = logging.LoggerAdapter(logger, {"hostname": hostname})
