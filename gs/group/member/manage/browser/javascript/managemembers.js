'use strict';
// Interlocks on the manage members form.
//
// Copyright © 2010, 2013, 2016 OnlineGroups.net and Contributors.
// All Rights Reserved.
//
// This software is subject to the provisions of the Zope Public License,
// Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
// THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
// WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
// WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
// FOR A PARTICULAR PURPOSE.
//
jQuery.noConflict();

function GSManageMembers() {
    //
    // Private methods
    //
    function ptnCoachChange() {
        var updatedWidget = null, allRelatedWidgets = null, checkedValue = null;
        updatedWidget = jQuery(this);
        allRelatedWidgets = jQuery('.ptnCoach :radio');
        checkedValue = updatedWidget.prop('checked');

        if (checkedValue == true) {
            // If we select a Ptn Coach button, deselect all others
            for (i = 0; i < allRelatedWidgets.length; i = i + 1) {
                jQuery(allRelatedWidgets[i]).prop('checked', false);
            }
            // Then re-select the one that changed
            updatedWidget.prop('checked', true);
        }
    } // ptnCoachChange

    function removeMemberChange() {
        var updatedWidget = null, memberId = null, allRelatedWidgets = null,
            checkedValue = null;
        updatedWidget = jQuery(this);
        memberId = updatedWidget.attr('id').split('-')[0].split('.')[1];
        allRelatedWidgets = jQuery('#' + memberId + '-actions input');
        checkedValue = updatedWidget.prop('checked');

        if (checkedValue == true) {
            // If we select the remove button, deselect and
            // disable all other options for this member
            for (i = 0; i < allRelatedWidgets.length; i = i + 1) {
                jQuery(allRelatedWidgets[i])
                    .prop('checked', false)
                    .attr('disabled', 'disabled');
            }
            // Then re-select and re-enable the one that changed
            updatedWidget.removeAttr('disabled').prop('checked', true);
        } else {
            // If we deselect the remove button, re-enable all
            // other options for this member
            for (i = 0; i < allRelatedWidgets.length; i = i + 1) {
                jQuery(allRelatedWidgets[i]).removeAttr('disabled');
            }
        }
    } // removeMemberChange

    function moderationChange() {
        var updatedWidget = null, memberId = null, moderationAction = null,
            checkedValue = null, allRelatedWidgets = null;
        updatedWidget = jQuery(this);
        memberId = updatedWidget.attr('id').split('-')[0].split('.')[1];
        moderationAction = updatedWidget.attr('id').split('-')[1];
        checkedValue = updatedWidget.prop('checked');


        if (moderationAction == 'moderatorAdd') {
            allRelatedWidgets = jQuery('#form\\.' + memberId + '-moderatedAdd');
        } else {
            ptnCoachInputName = memberId + '-ptnCoach';
            allRelatedWidgets = [
                jQuery('#form\\.' + memberId + '-moderatorAdd'),
                jQuery('#form\\.' + memberId + '-groupAdminAdd'),
                jQuery('#form\\.' + memberId + '-postingMemberAdd'),
                jQuery('input[name="form\\.' + ptnCoachInputName + '"]')];
        }

        if (checkedValue == true) {
            // If we select the one Moderation checkbox, deselect and
            // disable the other for this member
            for (i = 0; i < allRelatedWidgets.length; i = i + 1) {
                jQuery(allRelatedWidgets[i])
                    .prop('checked', false)
                    .attr('disabled', 'disabled');
            }
            // Then re-select and re-enable the one that changed
            updatedWidget.removeAttr('disabled').prop('checked', true);
        } else {
            // If we deselect the Moderation checkbox, re-enable
            // the other option
            for (i = 0; i < allRelatedWidgets.length; i = i + 1) {
                jQuery(allRelatedWidgets[i]).removeAttr('disabled');
            }
        }
    } // moderationChange

    //
    // Public methods and properties
    //
    return {
        init: function() {
            jQuery('.ptnCoach :radio').change(ptnCoachChange);
            jQuery('.remove :checkbox').change(removeMemberChange);
            jQuery('.moderatorAdd :checkbox').change(moderationChange);
            jQuery('.moderatedAdd :checkbox').change(moderationChange);
        }
    };
} // GSManageMembers

jQuery(window).load(function() {
    var gsmm = null;
    gsmm = GSManageMembers();
    gsmm.init();
});
