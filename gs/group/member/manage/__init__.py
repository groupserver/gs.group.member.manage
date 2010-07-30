import memberStatusActionsContentProvider

from zope.tales.tales import RegistrationError
from zope.contentprovider import tales
try:
    from zope.browserpage import metaconfigure
except ImportError:
    from zope.app.pagetemplate import metaconfigure
try:
    metaconfigure.registerType('provider', 
      tales.TALESProviderExpression)
except RegistrationError:
    # Almost certainly registered somewhere else
    pass
