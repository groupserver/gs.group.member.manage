# -*- coding: utf-8 -*-
############################################################################
#
# Copyright © 2014, 2016 OnlineGroups.net and Contributors.
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
from gs.group.type.announcement.interfaces import IGSAnnouncementGroup
from Products.GSGroupMember.groupmembershipstatus import \
    GSGroupMembershipStatus
from .statusformfields import GSStatusFormFields


class GSMemberStatusActions(object):
    def __init__(self, userInfo, membersInfo):
        self.userInfo = userInfo
        self.membersInfo = membersInfo

    @Lazy
    def status(self):
        retval = GSGroupMembershipStatusHack(self.userInfo,
                                             self.membersInfo)
        return retval

    @Lazy
    def form_fields(self):
        retval = GSStatusFormFields(self.status).form_fields
        return retval


class GSGroupMembershipStatusHack(GSGroupMembershipStatus):

    def __init__(self, ui, msi):
        super(GSGroupMembershipStatusHack, self).__init__(ui, msi)
        pis = ((IGSAnnouncementGroup.providedBy(msi.group))
               or (msi.groupInfo.group_type == 'announcement'))
        self.__dict__['postingIsSpecial'] = pis
