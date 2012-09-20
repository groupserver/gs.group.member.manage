# coding=utf-8
from zope.cachedescriptors.property import Lazy
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from gs.group.base.form import GroupForm
from manager import GSGroupMemberManager


class GSManageGroupMembersForm(GroupForm):
    pageTemplateFileName = 'browser/templates/manage_members.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)

    def __init__(self, context, request):
        GroupForm.__init__(self, context, request)
        self.groupName = self.groupInfo.name
        self.label = u'Manage the Members of %s' % self.groupName
        self.showOnly = request.form.get('showOnly', '')
        self.page = request.form.get('page', '1')

    @Lazy
    def form_fields(self):
        if (not(self.memberManager.postingIsSpecial)
                and not('form.ptnCoachRemove' in self.request.form)
                and not(self.groupInfo.ptn_coach)):
            self.request.form['form.ptnCoachRemove'] = u'True'
        if self.showOnly or not(self.memberManager.membersToShow):
            retval = self.memberManager.form_fields.omit('ptnCoachRemove')
        else:
            retval = self.memberManager.form_fields
        return retval

    def setUpWidgets(self, ignore_request=False, data={}):
        self.adapters = {}
        self.widgets = form.setUpWidgets(
            self.form_fields, self.prefix, self.context,
            self.request, form=self, data=data,
            ignore_request=ignore_request)
        for widget in self.widgets:
            widget._displayItemForMissingValue = False
        assert self.widgets

    @form.action(label=u'Change', failure='handle_change_action_failure')
    def handle_change(self, action, data):
        self.status = self.memberManager.make_changes(data)
        # Reset the form_fields cache so that the
        # page reloads with the updated widgets
        self.__form_fields = None

    def handle_change_action_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = u'<p>There is an error:</p>'
        else:
            self.status = u'<p>There are errors:</p>'

    @Lazy
    def memberManager(self):
        retval = GSGroupMemberManager(self.groupInfo.groupObj,
                                        self.page, self.showOnly)
        return retval
