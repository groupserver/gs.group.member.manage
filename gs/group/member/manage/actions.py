# -*- coding: utf-8 -*-
############################################################################
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
############################################################################
from __future__ import absolute_import, unicode_literals
from zope.cachedescriptors.property import Lazy
from zope.component import adapts
from zope.interface import implements
from Products.CustomUserFolder.interfaces import IGSUserInfo
from Products.GSGroupMember.interfaces import IGSGroupMembersInfo
from Products.GSGroupMember.groupmembershipstatus import \
    GSGroupMembershipStatus
from .statusformfields import GSStatusFormFields
from .interfaces import IGSMemberStatusActions


class GSMemberStatusActions(object):
    adapts(IGSUserInfo, IGSGroupMembersInfo)
    implements(IGSMemberStatusActions)

    def __init__(self, userInfo, membersInfo):
        if not(IGSUserInfo.providedBy(userInfo)):
            m = '{0} is not a GSUserInfo'.format(userInfo)
            raise TypeError(m)
        if not(IGSGroupMembersInfo.providedBy(membersInfo)):
            m = '{0} is not a GSGroupMembersInfo'.format(membersInfo)
            raise TypeError(m)

        self.userInfo = userInfo
        self.membersInfo = membersInfo

    @Lazy
    def status(self):
        retval = GSGroupMembershipStatus(self.userInfo, self.membersInfo)
        return retval

    @Lazy
    def form_fields(self):
        retval = GSStatusFormFields(self.status).form_fields
        return retval
