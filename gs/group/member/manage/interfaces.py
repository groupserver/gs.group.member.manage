# -*- coding: utf-8 -*-
"""Interfaces for the member-management pages."""
from zope.interface import Attribute
from zope.interface.interface import Interface
from zope.schema import List, Text, Bool, Choice
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary


class IGSManageGroupMembersForm(Interface):
    groupInfo = Attribute("""A groupInfo instance""")
    siteInfo = Attribute("""A siteInfo instance""")
    memberManager = Attribute("""A GSGroupMemberManager instance""")
    form_fields = Attribute("""The fields to be displayed in a form""")


class IGSManageMembersForm(Interface):
    """ One user-independent field."""
    ptnCoachRemove = Choice(vocabulary=SimpleVocabulary([SimpleTerm(True,
        True, u'No participation coach')]),
      required=False)


class IGSGroupMemberManager(Interface):
    groupInfo = Attribute("""A groupInfo instance""")
    siteInfo = Attribute("""A siteInfo instance""")
    membersInfo = Attribute("""A GSGroupMembersInfo instance""")
    memberStatusActions = \
        Attribute("A list of GSMemberStatusActions instances")
    form_fields = Attribute("""The fields to be displayed in a form""")


class IGSMemberStatusActions(Interface):
    userInfo = Attribute("""A userInfo instance""")
    groupInfo = Attribute("""A groupInfo instance""")
    siteInfo = Attribute("""A siteInfo instance""")
    status = Attribute("""A GSGroupMembershipStatus instance""")
    form_fields = Attribute("""The fields to be displayed in a """
      """form to change the membership status of this user""")


class IGSMemberStatusActionsContentProvider(Interface):
    """The content provider for the actions available to change """
    """a group member's status within the group"""
    statusActions = List(title=u'Instances',
      description=u'GSMemberStatusActions instances',
      required=True)
    widgets = List(title=u'Widgets',
      description=u'Form Widgets',
      required=True)
    pageTemplateFileName = Text(title=u"Page Template File Name",
      description=u'The name of the ZPT file that is used to render the '
        u'group member\'s status and the appropriate form widgets.',
      required=False,
      default=u"browser/templates/statusActionsContentProvider.pt")


class IGSStatusFormFields(Interface):
    """ An adapter to take a member's status within a group, and
        give us the appropriate form_fields to alter the status,
        also depending on the status of the logged-in administrator.
    """
    status = Attribute("""A GSGroupMembershipStatus instance""")
    userInfo = Attribute("""A userInfo instance""")
    groupInfo = Attribute("""A groupInfo instance""")
    siteInfo = Attribute("""A siteInfo instance""")
    adminUserInfo = Attribute("A userInfo instance for the logged-in "
                                "administrator")
    adminUserStatus = Attribute("A GSGroupMembershipStatus instance for the "
                                "logged-in administrator")
    form_fields = Attribute("The fields to be displayed in a form to change "
                            "the membership status of this user")
    groupAdmin = Bool(title=u'Make fn a Group Administrator (or Unmake)',
      description=u'Make fn a Group Administrator (or Unmake)',
      required=False)
    ptnCoach = Bool(title=u'Make fn the Participation Coach (or Unmake)',
      description=u'Make fn the Participation Coach (or Unmake)',
      required=False)
    moderator = Bool(title=u'Make fn a Moderator (or Unmake)',
      description=u'Make fn a Moderator (or Unmake)',
      required=False)
    moderate = Bool(title=u'Moderate fn (or Unmoderate)',
      description=u'Moderate fn (or Unmoderate)',
      required=False)
    postingMember = Bool(title=u'Make fn a Posting Member (or Unmake)',
      description=u'Make fn a Posting Member (or Unmake)',
      required=False)
    remove = Bool(title=u'Remove fn from the Group',
      description=u'Remove fn from the Group',
      required=False)


class IGSMemberActionsSchema(Interface):
    """ Dummy interface to get the schema started."""
    dummy = Bool(title=u'Dummy',
      description=u'Is this a dummy value?',
      required=False)
