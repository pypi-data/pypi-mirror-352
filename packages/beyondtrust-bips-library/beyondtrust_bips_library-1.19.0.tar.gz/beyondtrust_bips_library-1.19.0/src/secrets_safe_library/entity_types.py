"""Entity Types module, all the logic to manage entity types from PS API"""

import logging

from secrets_safe_library.authentication import Authentication
from secrets_safe_library.core import APIObject


class EntityType(APIObject):

    def __init__(self, authentication: Authentication, logger: logging.Logger = None):
        super().__init__(authentication, logger, endpoint="/entitytypes")
