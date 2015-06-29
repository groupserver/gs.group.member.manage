Changelog
=========

2.8.3 (2015-06-30)
------------------

* Sorting the list of members on the *Manage many members* page
* Changing the definition of *many*
* Removing a boundary-error in the batching code
* Dealing with the removal of odd-members better

2.8.2 (2015-06-15)
------------------

* Following the change of the leave-code to
  `gs.group.member.leave.base`_

.. _gs.group.member.leave.base:
   https://github.com/groupserver/gs.group.member.leave.base

2.8.1 (2014-11-10)
------------------

* Showing the posting-member related functionality when the
  announcement-group is only marked with the marker-interface
* Renaming all reStructuredText files as such, and pointing to
  GitHub_ as the primary repository

.. _GitHub: https://github.com/groupserver/gs.group.member.manage

2.8.0 (2014-06-26)
------------------

* Added the *Manage many members* page, closing `Issue 236`_, and
  `Bug 398`_

.. _Issue 236: https://redmine.iopen.net/issues/236
.. _Bug 698: https://redmine.iopen.net/issues/698

2.7.2 (2014-06-11)
------------------

* Following the renaming of ``gs.content.form`` to
  ``gs.content.form.base``

2.7.1 (2014-01-29)
------------------

* Adding a product dependency on ``gs.group.member.invite.resend``
* Renaming *managers* to *administrators*, closing `Bug 4054`_

.. _Bug 4054: https://redmine.iopen.net/issues/4054

2.7.0 (2013-11-15)
------------------

* Major refactor of the JavaScript
* Fixing some URIs, closing `Bug 4022`_

.. _Bug 4022: https://redmine.iopen.net/issues/4022

2.6.2 (2013-09-06)
------------------

* Split the *Admin* link viewlet in two

2.6.1 (2013-08-09)
------------------

* Updated the license and copyright

2.6.0 (2013-06-16)
------------------

* Added categorical member management links to the *Admin* tab

2.5.0 (2013-03-20)
------------------

* Following the split of ``gs.group.member.base``,
  ``gs.group.member.info``, and ``gs.group.member.viewlet``
* Further code cleanup
* Updating the dependencies of the product

2.4.1 (2013-01-22)
------------------

* Code cleanup
* Updating the *Admin* links so they are relative to the base of
  the site

2.4.0 (2012-09-20)
------------------

* Refactor of the code for PEP-8
* Dropping the context menu from the *Manage members* form
* Following the bounce information to ``gs.group.member.bounce``

2.3.3 (2012-06-22)
------------------

* Update to SQLAlchemy

2.3.2 (2012-05-15)
-------------------

* Refactor for ``gs.group.member.invite.base``

2.3.1 (2011-05-19)
------------------

* Added the *Manage members* links to the *Admin* tab on the
  group page

2.3.0 (2011-01-26)
------------------

* Refactor for ``gs.profile.email.base``

2.2.1 (2010-12-09)
------------------

* Moving the page-specific styles to the global stylesheet
* Tweaks to the navigation links on the Manage Members page
* Using the new form-message content provider

2.2.0 (2010-10-23)
------------------

* Added links to the filtered view of the page
* Improved the wording
* Fix Zope 2.10 acquisition issues
* Correcting a coding error with the participation coach
* Following the radio-button to its new home

2.1.0 (2010-09-24)
------------------

* Added batching
* Formatting improvements
* Linking to more pages

2.0.1 (2010-09-08)
------------------

* Improving the moderation interlock
* Handle multiple user identifiers
* Performance improvements
* Fixing some errors

2.0.0 (2010-08-06)
------------------

* New product created
* Code moved from ``Products.GSGroupMember``

..  LocalWords:  Changelog
