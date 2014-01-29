# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright © 2014 OnlineGroups.net and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
from __future__ import absolute_import, unicode_literals
from zope.cachedescriptors.property import Lazy
from zope.component import createObject
from Products.XWFCore.XWFUtils import munge_date
from Products.GSAuditTrail.utils import marshal_data
from gs.group.base import GroupPage
from gs.profile.email.base.emailuser import EmailUser
from gs.group.member.bounce.audit import SUBSYSTEM, BOUNCE, DISABLE
from .queries import BounceHistoryQuery


class BounceInfo(GroupPage):

    def __init__(self, group, request):
        super(BounceInfo, self).__init__(group, request)
        self.label = '%s\'s Email Addresses' % self.userInfo.name

    @Lazy
    def userInfo(self):
        userId = self.request.form.get('userId')
        retval = createObject('groupserver.UserFromId', self.context, userId)
        return retval

    @Lazy
    def emailAddresses(self):
        retval = list(self.bounceHistory.keys())
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
        retval = ''
        if (event.code == DISABLE):
            retval = event.xhtml
        elif (event.code == BOUNCE):
            retval = 'Email delivery failed (%s)' %\
              munge_date(self.context, event.date)
        return retval
