# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
MANY = 48
#lint:disable
from . import memberStatusActionsContentProvider
#lint:enable
from zope.browserpage import metaconfigure
from zope.tales.tales import RegistrationError
from zope.contentprovider import tales
try:
    metaconfigure.registerType('provider', tales.TALESProviderExpression)
except RegistrationError:
    # Almost certainly registered somewhere else
    pass
