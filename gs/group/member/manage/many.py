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
try:
    from urllib.parse import quote  # Python 3
except ImportError:
    from urllib import quote  # Python 2  # lint:ok
from zope.cachedescriptors.property import Lazy
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from gs.content.form.base import multi_check_box_widget
from gs.core import to_ascii
from gs.group.base import GroupForm
from .interfaces import IGSManageManyMembers


class ManageManyMembers(GroupForm):
    '''The *Manage Members* page is slow when there are many members. This
page provides a nice list of members that can be selected and then managed.'''
    pageTemplateFileName = 'browser/templates/manage_many_members.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)

    def __init__(self, context, request):
        super(ManageManyMembers, self).__init__(context, request)

    @Lazy
    def form_fields(self):
        retval = form.Fields(IGSManageManyMembers, render_context=False)
        retval['members'].custom_widget = multi_check_box_widget
        return retval

    @form.action(label='Manage', name='manage',
                 failure='handle_manage_action_failure')
    def handle_manage(self, action, data):
        self.status = 'Should manage {0}'.format(data['members'])
        membersToManage = quote(' '.join(data['members']))
        u = '{0}/managemembers.html?showOnly={1}'
        uri = to_ascii(u.format(self.groupInfo.relative_url(), membersToManage))
        return self.request.RESPONSE.redirect(uri)

    def handle_manage_action_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = '<p>There is an error:</p>'
        else:
            self.status = '<p>There are errors:</p>'
