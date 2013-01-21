# coding=utf-8
from zope.cachedescriptors.property import Lazy
from zope.component import adapts
from zope.interface import implements
from zope.formlib import form
from zope.schema import Bool, Choice
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from gs.content.form.radio import radio_widget
from Products.GSGroupMember.interfaces import IGSGroupMembershipStatus
from gs.group.member.manage.interfaces import IGSStatusFormFields,\
    IGSMemberActionsSchema

MAX_POSTING_MEMBERS = 5


class GSStatusFormFields(object):
    adapts(IGSGroupMembershipStatus)
    implements(IGSStatusFormFields)

    def __init__(self, status):
        assert IGSGroupMembershipStatus.providedBy(status), \
          u'%s is not a GSGroupMembershipStatus' % status

        self.status = status
        self.userInfo = status.userInfo
        self.groupInfo = status.groupInfo
        self.siteInfo = status.siteInfo

    # AM: We're unable to get the logged-in user
    #   in this context. Ideally we would grab
    #   the logged-in user and use their status
    #   to determine whether some actions can be
    #   taken, but that's not currently possible.
    #   Further comments below, where relevant.

    @Lazy
    def allFields(self):
        retval = [self.ptnCoach, self.groupAdmin, self.postingMember,
                  self.moderator, self.moderate, self.remove, self.withdraw]
        return retval

    @Lazy
    def validFields(self):
        retval = filter(None, self.allFields)
        return retval

    @Lazy
    def form_fields(self):
        fields = form.Fields(IGSMemberActionsSchema)
        for f in self.validFields:
            fields = form.Fields(fields + form.Fields(f))
            retval = fields.omit('dummy')
        return retval

    @Lazy
    def groupAdmin(self):
        retval = False
        if ((self.status.isSiteAdmin
                or self.status.isNormalMember or self.status.isPtnCoach
                or self.status.isModerator)
            and not (self.status.isGroupAdmin or self.status.isModerated
                or self.status.isOddlyConfigured)):
            t = u'Make %s a Group Administrator' % self.userInfo.name
            retval = Bool(__name__=u'%s-groupAdminAdd' % self.userInfo.id,
                            title=t, description=t, required=False)
        # AM: Admins shouldn't be able to revoke the group-admin
        #   status of other admins of the same or higher rank.
        #elif self.status.isGroupAdmin and self.adminUserStatus.isSiteAdmin:
        elif self.status.isGroupAdmin:
            t = u'Remove the Group Administrator privileges from %s' %\
                self.userInfo.name
            retval = Bool(__name__=u'%s-groupAdminRemove' % self.userInfo.id,
                            title=t, description=t, required=False)
        return retval

    @Lazy
    def ptnCoach(self):
        retval = False
        if (not(self.status.postingIsSpecial)
            and (self.status.isNormalMember or self.status.isSiteAdmin
                or self.status.isGroupAdmin or self.status.isModerator)
            and not (self.status.isPtnCoach or self.status.isModerated
                    or self.status.isOddlyConfigured)):
            ptnCoachTerm = SimpleTerm(True, True,
                  u'Make %s the Participation Coach' % self.userInfo.name)
            ptnCoachVocab = SimpleVocabulary([ptnCoachTerm])
            n = u'%s-ptnCoach' % self.userInfo.id
            retval = form.Fields(Choice(__name__=n, vocabulary=ptnCoachVocab,
                                        required=False),
                                custom_widget=radio_widget)
        return retval

    @Lazy
    def moderator(self):
        retval = False
        if (self.status.groupIsModerated
            and not (self.status.isModerator or self.status.isModerated
                    or self.status.isInvited or self.status.isUnverified
                    or self.status.isOddlyConfigured)):
            t = u'Make %s a Moderator for this group' % self.userInfo.name
            retval = Bool(__name__=u'%s-moderatorAdd' % self.userInfo.id,
                        title=t, description=t, required=False)
        elif self.status.groupIsModerated and self.status.isModerator:
            t = u'Revoke Moderator status from %s' % self.userInfo.name
            retval = Bool(__name__=u'%s-moderatorRemove' % self.userInfo.id,
                        title=t, description=t, required=False)
        return retval

    @Lazy
    def moderate(self):
        retval = False
        if self.status.groupIsModerated and self.status.isNormalMember:
            t = u'Start moderating messages from %s' % self.userInfo.name
            retval = Bool(__name__=u'%s-moderatedAdd' % self.userInfo.id,
                            title=t, description=t, required=False)
        elif self.status.groupIsModerated and self.status.isModerated:
            t = u'Stop moderating messages from %s' % self.userInfo.name
            retval = Bool(__name__=u'%s-moderatedRemove' % self.userInfo.id,
                    title=t, description=t, required=False)
        return retval

    @Lazy
    def postingMember(self):
        retval = False
        if (self.status.postingIsSpecial and
            (self.status.numPostingMembers < MAX_POSTING_MEMBERS)
            and not (self.status.isPostingMember or self.status.isUnverified
                    or self.status.isOddlyConfigured)):
            t = u'Make %s a Posting Member' % self.userInfo.name
            retval = Bool(__name__=u'%s-postingMemberAdd' % self.userInfo.id,
                            title=t, description=t, required=False)
        elif self.status.postingIsSpecial and self.status.isPostingMember:
            n = u'%s-postingMemberRemove' % self.userInfo.id
            t = u'Revoke the Posting Member privileges from %s' % \
                    self.userInfo.name
            retval = Bool(__name__=n, title=t, description=t, required=False)
        return retval

    @Lazy
    def remove(self):
        retval = False
        # AM: Admins shouldn't be able to remove other
        #   admins of the same or higher rank.
        #if not self.status.isSiteAdmin and \
        #  not(self.status.isGroupAdmin and \
        #      self.adminUserStatus.isGroupAdmin):
        if ((not self.status.isSiteAdmin) and (not self.status.isGroupAdmin)
            and (not self.status.isInvited)):
            t = u'Remove %s from the group' % self.userInfo.name
            retval = Bool(__name__=u'%s-remove' % self.userInfo.id,
                            title=t, description=t, required=False)
        return retval

    @Lazy
    def withdraw(self):
        retval = False
        if self.status.isInvited:
            t = u'Withdraw the invitation sent to %s' % self.userInfo.name
            retval = Bool(__name__=u'%s-withdraw' % self.userInfo.id,
                            title=t, description=t, required=False)
        return retval
