# coding=utf-8
from urllib import quote
from zope.component import createObject
from Products.Five import BrowserView

class BounceInfo(BrowserView):

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        userId = request.form.get('userId')
        self.siteInfo = createObject('groupserver.SiteInfo', context)
        self.groupInfo = createObject('groupserver.GroupInfo', context)
        self.userInfo = createObject('groupserver.UserFromId', 
                                     context, userId)

    