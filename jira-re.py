#!/usr/bin/env python

from jira import JIRA
from datetime import date
from collections import Counter
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('-r', '--release', action='store', dest='release')
parser.add_argument('-p', '--plan-date', action='store', dest='plan')
args = parser.parse_args()


USER = '<your_jira_user>'
PASS = '<your_jira_password>'
PLAN_DATE = args.plan if args.plan else '2017-10-03'
CURRENT_RELEASE = args.release if args.release else 'RE-2017.11'

jira = JIRA('https://rpc-openstack.atlassian.net', basic_auth=(USER,PASS))

initial_items = jira.search_issues('fixVersion = %s and created <= 2017-10-03 and type in (bug,task)' % CURRENT_RELEASE)
addl_items = jira.search_issues('fixVersion = %s and created > 2017-10-03 and type in (bug,task)' % CURRENT_RELEASE)
total_items_in_release = initial_items + addl_items

completed_items = jira.search_issues('fixVersion = %s and type in (bug,task) and status = Finished' % CURRENT_RELEASE)
remaining_items = jira.search_issues('fixVersion = %s and type in (bug,task) and status != Finished' % CURRENT_RELEASE)

non_release_items = jira.search_issues('labels in (re-related) AND resolved >= 2017-10-01 and Status in (Finished, Done) ORDER BY created ASC')

remaining_statuses = [a.fields.status.name for a in remaining_items]
status_count = Counter(remaining_statuses)
status_string = ', '.join([k+': '+str(v) for k,v in status_count.items()])

print 'Date: %s' % str(date.today())
print 'Planning Date: %s' % PLAN_DATE
print 'Current Release: %s' % CURRENT_RELEASE
print 'Total items in release:\t\t\t\t\t %s'  % len(total_items_in_release)
print
print 'Initial release items in planning:\t\t\t %s' % len(initial_items)
print 'Additional release items since planning:\t\t %s' % len(addl_items)
print
print 'Completed release items :\t\t\t\t %s'  % len(completed_items)
print 'Remaining release items :\t\t\t\t %s (%s)'  % (len(remaining_items), status_string)
print
print 'Completed non-release items:\t\t\t\t %s' % len(non_release_items)
print
print 'Total items completed in release period:\t\t %s' % (len(completed_items) + len(non_release_items))


