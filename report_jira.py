#!/usr/bin/env python

from jira import JIRA
from datetime import date

USER = '<your_jira_user>'
PASS = '<your_jira_password>'
PLAN_DATE='2017-10-03'
CURRENT_RELEASE = 'RE-2017.11'

jira = JIRA('https://rpc-openstack.atlassian.net', basic_auth=(USER,PASS))

initial_items = len(jira.search_issues('fixVersion = %s and created <= 2017-10-03 and type in (bug,task)' % CURRENT_RELEASE))
addl_items = len(jira.search_issues('fixVersion = %s and created > 2017-10-03 and type in (bug,task)' % CURRENT_RELEASE))
total_items_in_release = initial_items + addl_items

completed_items = len(jira.search_issues('fixVersion = %s and type in (bug,task) and status = Finished' % CURRENT_RELEASE))
remaining_items = len(jira.search_issues('fixVersion = %s and type in (bug,task) and status != Finished' % CURRENT_RELEASE))

non_release_items = len(jira.search_issues('labels in (re-related) AND resolved >= 2017-10-01 and Status in (Finished, Done) ORDER BY created ASC'))

JUST = 20

print 'Date: %s' % str(date.today())
print 'Current Release: %s' % CURRENT_RELEASE

print 'Initial items committed to for release: %s' % initial_items
print 'Additional items for release created since planning: %s' % addl_items
print 'Total items in release: %s'  % total_items_in_release

print 'Completed items in release: %s'  % completed_items
print 'Remaining items in release: %s'  % remaining_items

print 'Additional re-related items completed this month: %s' % non_release_items

print 'Total items completed in release period: %s' % (completed_items + non_release_items)


