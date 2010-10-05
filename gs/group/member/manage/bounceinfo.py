# coding=utf-8
from urllib import quote
from zope.component import createObject
from Products.Five import BrowserView
from Products.XWFCore.XWFUtils import munge_date
from Products.XWFMailingListManager.bounceaudit import SUBSYSTEM
from Products.XWFMailingListManager.bounceaudit import BOUNCE, DISABLE
from Products.GSAuditTrail.utils import marshal_data
from Products.GSGroup.groupInfo import groupInfo_to_anchor
from queries import BounceHistoryQuery

class BounceInfo(BrowserView):

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        userId = request.form.get('userId')
        self.context = context
        self.siteInfo = createObject('groupserver.SiteInfo', context)
        self.groupInfo = createObject('groupserver.GroupInfo', context)
        self.userInfo = \
          createObject('groupserver.UserFromId', context, userId)
        self.label = u'%s\'s Email Addresses' % self.userInfo.name
        self.__bounceHistory = self.__emailAddresses = None
    
    @property
    def emailAddresses(self):
        if self.__emailAddresses == None:
            self.__emailAddresses = self.bounceHistory.keys()
        return self.__emailAddresses
    
    @property
    def bounceHistory(self):
        if self.__bounceHistory == None:
            retval = {}
            query = BounceHistoryQuery(self.context, self.context.zsqlalchemy)
            emailAddresses = self.userInfo.user.get_emailAddresses()
            for email in emailAddresses:
                retval[email] = [ self.munge_event(e) 
                  for e in query.bounce_events(email) ]
            self.__bounceHistory = retval
        return self.__bounceHistory
    
    def munge_event(self, e):
        e = marshal_data(self.context, e)
        event = createObject(SUBSYSTEM, self.context, **e)
        retval = u''
        if (event.code == DISABLE) or ((event.code == BOUNCE) and (event.groupInfo.id == self.groupInfo.id)):
            retval = event.xhtml
        elif (event.code == BOUNCE):
            retval = u'Email delivery failed (%s)' %\
              munge_date(self.context, event.date)
        return retval
        
    