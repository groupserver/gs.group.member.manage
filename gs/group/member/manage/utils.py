# coding=utf-8
from zope.component import createObject
from Products.GSGroup.mailinglistinfo import GSMailingListInfo
from gs.group.member.manage.audit import StatusAuditor, GAIN, LOSE
from gs.group.member.manage.statusformfields import MAX_POSTING_MEMBERS
from gs.group.member.invite.base.queries import InvitationQuery
from gs.group.member.invite.base.audit import Auditor, WITHDRAW_INVITATION


def addAdmin(groupInfo, userInfo):
    roles = list(groupInfo.groupObj.get_local_roles_for_userid(userInfo.id))
    assert 'GroupAdmin' not in roles, '%s (%s) was marked for becoming '\
      'a GroupAdmin in %s (%s), but is one already.' % \
       (userInfo.name, userInfo.id, groupInfo.name, groupInfo.id)
    groupInfo.groupObj.manage_addLocalRoles(userInfo.id, ['GroupAdmin'])
    auditor = StatusAuditor(groupInfo.groupObj, userInfo)
    auditor.info(GAIN, 'Group Administrator')
    retval = 'became a Group Administrator'
    return retval


def removeAdmin(groupInfo, userInfo):
    roles = list(groupInfo.groupObj.get_local_roles_for_userid(userInfo.id))
    assert 'GroupAdmin' in roles, '%s (%s) was marked for removal '\
      'as a GroupAdmin in %s (%s), but does not have the role.' % \
       (userInfo.name, userInfo.id, groupInfo.name, groupInfo.id)
    roles.remove('GroupAdmin')
    if roles:
        groupInfo.groupObj.manage_setLocalRoles(userInfo.id, roles)
    else:
        groupInfo.groupObj.manage_delLocalRoles([userInfo.id])
    auditor = StatusAuditor(groupInfo.groupObj, userInfo)
    auditor.info(LOSE, 'Group Administrator')
    retval = 'no longer a Group Administrator'
    return retval


def addModerator(groupInfo, userInfo):
    listInfo = GSMailingListInfo(groupInfo.groupObj)
    moderatorIds = [m.id for m in listInfo.moderators]
    assert userInfo.id not in moderatorIds, '%s (%s) was marked for addition '\
      'as a moderator in %s (%s), but is already a moderator.' % \
       (userInfo.name, userInfo.id, groupInfo.name, groupInfo.id)
    moderatorIds.append(userInfo.id)
    groupList = listInfo.mlist
    if groupList.hasProperty('moderator_members'):
        groupList.manage_changeProperties(moderator_members=moderatorIds)
    else:
        groupList.manage_addProperty('moderator_members', moderatorIds,
                                        'lines')
    auditor = StatusAuditor(groupInfo.groupObj, userInfo)
    auditor.info(GAIN, 'Moderator')
    retval = 'became a Moderator'
    return retval


def removeModerator(groupInfo, userInfo):
    listInfo = GSMailingListInfo(groupInfo.groupObj)
    moderatorIds = [m.id for m in listInfo.moderators]
    assert userInfo.id in moderatorIds, '%s (%s) was marked for removal '\
      'as a moderator in %s (%s), but is not listed as a moderator.' % \
       (userInfo.name, userInfo.id, groupInfo.name, groupInfo.id)
    moderatorIds.remove(userInfo.id)
    groupList = listInfo.mlist
    if groupList.hasProperty('moderator_members'):
        groupList.manage_changeProperties(moderator_members=moderatorIds)
    else:
        groupList.manage_addProperty('moderator_members', moderatorIds,
                                    'lines')
    auditor = StatusAuditor(groupInfo.groupObj, userInfo)
    auditor.info(LOSE, 'Moderator')
    retval = 'no longer a Moderator'
    return retval


def moderate(groupInfo, userInfo):
    listInfo = GSMailingListInfo(groupInfo.groupObj)
    moderatedIds = [m.id for m in listInfo.moderatees]
    assert userInfo.id not in moderatedIds, '%s (%s) was marked for '\
      'moderation in %s (%s), but is already moderated.' % \
       (userInfo.name, userInfo.id, groupInfo.name, groupInfo.id)
    moderatedIds.append(userInfo.id)
    groupList = listInfo.mlist
    if groupList.hasProperty('moderated_members'):
        groupList.manage_changeProperties(moderated_members=moderatedIds)
    else:
        groupList.manage_addProperty('moderated_members', moderatedIds,
                                        'lines')
    auditor = StatusAuditor(groupInfo.groupObj, userInfo)
    auditor.info(GAIN, 'Moderated')
    retval = 'became Moderated'
    return retval


def unmoderate(groupInfo, userInfo):
    listInfo = GSMailingListInfo(groupInfo.groupObj)
    moderatedIds = [m.id for m in listInfo.moderatees]
    assert userInfo.id in moderatedIds, '%s (%s) was marked to be '\
        'unmoderated in %s (%s), but is not listed as a moderated member.' %\
       (userInfo.name, userInfo.id, groupInfo.name, groupInfo.id)
    moderatedIds.remove(userInfo.id)
    groupList = listInfo.mlist
    if groupList.hasProperty('moderated_members'):
        groupList.manage_changeProperties(moderated_members=moderatedIds)
    else:
        groupList.manage_addProperty('moderated_members', moderatedIds,
                                        'lines')
    auditor = StatusAuditor(groupInfo.groupObj, userInfo)
    auditor.info(LOSE, 'Moderated')
    retval = 'no longer Moderated'
    return retval


def addPostingMember(groupInfo, userInfo):
    listInfo = GSMailingListInfo(groupInfo.groupObj)
    postingMemberIds = [m.id for m in listInfo.posting_members]
    assert userInfo.id not in postingMemberIds, '%s (%s) was marked to '\
        'become a posting member in %s (%s), but is already a posting '\
        'member.' % (userInfo.name, userInfo.id, groupInfo.name, groupInfo.id)
    numPostingMembers = len(postingMemberIds)
    if numPostingMembers >= MAX_POSTING_MEMBERS:
        retval = 'not become a posting member, as the number of '\
        'posting members was already at the maximum (%d)' % MAX_POSTING_MEMBERS
    else:
        postingMemberIds.append(userInfo.id)
        groupList = listInfo.mlist
        if groupList.hasProperty('posting_members'):
            groupList.manage_changeProperties(posting_members=postingMemberIds)
        else:
            groupList.manage_addProperty('posting_members', postingMemberIds,
                                            'lines')
        auditor = StatusAuditor(groupInfo.groupObj, userInfo)
        auditor.info(GAIN, 'Posting Member')
        retval = 'became a Posting Member'
    return retval


def removePostingMember(groupInfo, userInfo):
    listInfo = GSMailingListInfo(groupInfo.groupObj)
    postingMemberIds = [m.id for m in listInfo.posting_members]
    assert userInfo.id in postingMemberIds, '%s (%s) was marked for removal '\
        'as a posting member in %s (%s), but is not a posting member.' %\
        (userInfo.name, userInfo.id, groupInfo.name, groupInfo.id)
    postingMemberIds.remove(userInfo.id)
    groupList = listInfo.mlist
    if groupList.hasProperty('posting_members'):
        groupList.manage_changeProperties(posting_members=postingMemberIds)
    else:
        groupList.manage_addProperty('posting_members', postingMemberIds,
                                        'lines')
    auditor = StatusAuditor(groupInfo.groupObj, userInfo)
    auditor.info(LOSE, 'Posting Member')
    retval = 'no longer a Posting Member'
    return retval


def addPtnCoach(groupInfo, userInfo):
    removePtnCoach(groupInfo)
    group = groupInfo.groupObj
    if group.hasProperty('ptn_coach_id'):
        group.manage_changeProperties(ptn_coach_id=userInfo.id)
    else:
        group.manage_addProperty('ptn_coach_id', userInfo.id, 'string')
    listInfo = GSMailingListInfo(group)
    if listInfo.mlist.hasProperty('ptn_coach_id'):
        listInfo.mlist.manage_changeProperties(ptn_coach_id=userInfo.id)
    else:
        listInfo.mlist.manage_addProperty('ptn_coach_id', userInfo.id,
                                            'string')
    auditor = StatusAuditor(groupInfo.groupObj, userInfo)
    auditor.info(GAIN, 'Participation Coach')
    retval = 'became the Participation Coach'
    return retval


def removePtnCoach(groupInfo):
    retval = ('', None)
    group = groupInfo.groupObj
    oldPtnCoach = groupInfo.ptn_coach
    if group.hasProperty('ptn_coach_id'):
        group.manage_changeProperties(ptn_coach_id='')
    listInfo = GSMailingListInfo(group)
    if listInfo.mlist.hasProperty('ptn_coach_id'):
        listInfo.mlist.manage_changeProperties(ptn_coach_id='')
    if oldPtnCoach:
        auditor = StatusAuditor(group, oldPtnCoach)
        auditor.info(LOSE, 'Participation Coach')
        retval = ('no longer the Participation Coach', oldPtnCoach.id)
    assert len(retval) == 2
    assert type(retval[0]) == str
    assert ((retval[1] is None) or (type(retval[1]) == str))
    return retval


def withdrawInvitation(groupInfo, userInfo):
    adminInfo = createObject('groupserver.LoggedInUser', groupInfo.groupObj)
    query = InvitationQuery()
    siteInfo = groupInfo.siteInfo
    query.withdraw_invitation(siteInfo.id, groupInfo.id, userInfo.id,
                                adminInfo.id)
    auditor = Auditor(siteInfo, groupInfo, adminInfo, userInfo)
    auditor.info(WITHDRAW_INVITATION)
    retval = 'no longer has an invitation to join the group'
    return retval
