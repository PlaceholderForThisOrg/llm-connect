import logging

from llm_connect.configs.app import APP

# 1. Create the logger
logger = logging.getLogger(APP)

# 2. Set the debug level
logger.setLevel(logging.DEBUG)

# 3. Create a handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# 4. Set up the formatter of the handler
formatter = logging.Formatter("🐛🐛🐛🐛 %(asctime)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

logger.debug("Debug log working!")
