# coding=utf-8
from zope.cachedescriptors.property import Lazy
from zope.component import createObject
from Products.XWFCore.XWFUtils import munge_date
from gs.group.member.bounce.audit import SUBSYSTEM, BOUNCE, DISABLE
from Products.GSAuditTrail.utils import marshal_data
from gs.group.base.page import GroupPage
from gs.profile.email.base.emailuser import EmailUser
from queries import BounceHistoryQuery


class BounceInfo(GroupPage):

    def __init__(self, context, request):
        GroupPage.__init__(self, context, request)
        self.label = u'%s\'s Email Addresses' % self.userInfo.name

    @Lazy
    def userInfo(self):
        userId = self.request.form.get('userId')
        retval = createObject('groupserver.UserFromId', self.context, userId)
        return retval

    @Lazy
    def emailAddresses(self):
        retval = self.bounceHistory.keys()
        return retval

    @Lazy
    def bounceHistory(self):
        retval = {}
        query = BounceHistoryQuery(self.context)
        eu = EmailUser(self.context, self.userInfo)
        emailAddresses = eu.get_addresses()
        for email in emailAddresses:
            retval[email] = [self.munge_event(e)
              for e in query.bounce_events(email)]
        return retval

    def munge_event(self, e):
        e = marshal_data(self.context, e, siteInfo=self.siteInfo,
                         groupInfo=self.groupInfo)
        event = createObject(SUBSYSTEM, self.context, **e)
        retval = u''
        if (event.code == DISABLE):
            retval = event.xhtml
        elif (event.code == BOUNCE):
            retval = u'Email delivery failed (%s)' %\
              munge_date(self.context, event.date)
        return retval
