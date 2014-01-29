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
import os
from setuptools import setup, find_packages
from version import get_version

version = get_version()

setup(name='gs.group.member.manage',
    version=version,
    description="The admin pages related to member management",
    long_description=open("README.txt").read() + "\n" +
                    open(os.path.join("docs", "HISTORY.txt")).read(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        "Environment :: Web Environment",
        "Framework :: Zope2",
        "Intended Audience :: Developers",
        'License :: OSI Approved :: Zope Public License',
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux"
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='user, group, member, group member, manage, remove, role',
    author='Alice Murphy',
    author_email='alice@onlinegroups.net',
    url='http://groupserver.org',
    license='ZPL 2.1',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['gs', 'gs.group', 'gs.group.member'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'pytz',
        'sqlalchemy',
        'zope.browserpage',
        'zope.browserresource',
        'zope.cachedescriptors',
        'zope.component',
        'zope.contentprovider',
        'zope.formlib',
        'zope.interface',
        'zope.publisher',
        'zope.schema',
        'zope.tal',
        'zope.tales',
        'zope.viewlet',
        'gs.content.form',
        'gs.content.layout',
        'gs.database',
        'gs.group.base',
        'gs.group.member.bounce',
        'gs.group.member.info',
        'gs.group.member.invite',
        'gs.group.member.leave',
        'gs.group.member.viewlet',
        'gs.profile.email.base',
        'Products.CustomUserFolder',
        'Products.GSAuditTrail',
        'Products.GSGroupMember',
        'Products.XWFCore',
    ],
    entry_points="""
    # -*- Entry points: -*-
    """,
)
