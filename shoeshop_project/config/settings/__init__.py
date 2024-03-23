from .base import *


if os.getenv('PROJECT_MODE') == 'prod':
   from .prod import *
else:
   from .dev import *
