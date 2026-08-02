from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.logging.formatters.datadog import (
    DatadogLogFormatter,
)


logger = Logger(logger_formatter=DatadogLogFormatter())
