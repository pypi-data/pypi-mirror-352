# Don't touch! This is a keystring substituted in GitHub workflows!
__version__ = "1.2.2-rc.1"
###################################################################

from epx.job import FREDJob, FREDModelConfig, FREDModelConfigSweep, FREDJobResults
from epx.run import FREDRun
from epx.core.models.synthpop import SynthPop
from epx.core.types.common import RunParameters
from epx.attribute import Attribute

# Set default logging handler to avoid "No handler found" warnings.
import logging
from logging import NullHandler

logging.getLogger(__name__).addHandler(NullHandler())
