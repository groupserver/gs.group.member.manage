# -*- coding: utf-8 -*-
from zope.cachedescriptors.property import Lazy
from zope.component import adapts
from zope.interface import implements
from Products.CustomUserFolder.interfaces import IGSUserInfo
from Products.GSGroupMember.interfaces import IGSGroupMembersInfo
from Products.GSGroupMember.groupmembershipstatus import \
    GSGroupMembershipStatus
from statusformfields import GSStatusFormFields
from interfaces import IGSMemberStatusActions


class GSMemberStatusActions(object):
    adapts(IGSUserInfo, IGSGroupMembersInfo)
    implements(IGSMemberStatusActions)

    def __init__(self, userInfo, membersInfo):
        assert IGSUserInfo.providedBy(userInfo),\
          u'%s is not a GSUserInfo' % userInfo
        assert IGSGroupMembersInfo.providedBy(membersInfo), \
          u'%s is not a GSGroupMembersInfo' % membersInfo

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
