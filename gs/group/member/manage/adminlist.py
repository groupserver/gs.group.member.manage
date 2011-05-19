# coding=utf-8
from zope.component import createObject
from zope.cachedescriptors.property import Lazy
from gs.group.member.base.viewlet import GroupAdminViewlet

class MembersListViewlet(GroupAdminViewlet):
    
    @Lazy
    def memberCount(self):
        acl_users = self.context.acl_users
        assert acl_users, 'Aquisition bites'
        userGroupId = '%s_member' % self.groupInfo.id
        userGroup = acl_users.getGroupById(userGroupId)
        retval = len(userGroup.getUsers())
        return retval

    @Lazy
    def isModerated(self):
        mailingListInfo = createObject('groupserver.MailingListInfo', 
                                               self.context)
        retval = mailingListInfo.is_moderated
        return retval

