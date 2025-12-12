import logging


def configure_logging(log_level=logging.INFO) -> logging.Logger:
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    