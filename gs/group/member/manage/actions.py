# coding=utf-8
from zope.component import createObject, adapts
from zope.interface import implements
from Products.CustomUserFolder.interfaces import IGSUserInfo
from Products.GSContent.interfaces import IGSSiteInfo
from Products.GSGroup.interfaces import IGSGroupInfo
from Products.GSGroupMember.groupmembershipstatus import GSGroupMembershipStatus
from gs.group.member.manage.statusformfields import GSStatusFormFields
from gs.group.member.manage.interfaces import IGSMemberStatusActions

class GSMemberStatusActions(object):
    adapts(IGSUserInfo, IGSGroupInfo, IGSSiteInfo)
    implements(IGSMemberStatusActions)

    def __init__(self, userInfo, groupInfo, siteInfo):
        assert IGSUserInfo.providedBy(userInfo),\
          u'%s is not a GSUserInfo' % userInfo
        assert IGSGroupInfo.providedBy(groupInfo),\
          u'%s is not a GSGroupInfo' % groupInfo
        assert IGSSiteInfo.providedBy(siteInfo),\
          u'%s is not a GSSiteInfo' % siteInfo
        
        self.userInfo = userInfo
        self.groupInfo = groupInfo
        self.siteInfo = siteInfo
    
        self.__status = None
        self.__form_fields = None
    
    @property
    def status(self):
        if self.__status == None:
            self.__status = \
              GSGroupMembershipStatus(self.userInfo, 
                self.groupInfo, self.siteInfo)
        return self.__status
    
    @property
    def form_fields(self):
        if self.__form_fields == None:
            self.__form_fields =\
              GSStatusFormFields(self.status).form_fields
        return self.__form_fields
    
    