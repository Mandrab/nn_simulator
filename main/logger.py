import logging
import sys

__FORMAT = '[%(asctime)s %(levelname)s]\t %(message)s'

# define default logging level as INFO and following a standard format
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=__FORMAT)
logger = logging.getLogger('nanowire-network-simulator-lib')
