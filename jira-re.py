#!/usr/bin/env python

from jira import JIRA
from datetime import date
from collections import Counter
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('-r', '--release', action='store', dest='release')
parser.add_argument('-pd', '--plan-date', action='store', dest='plan')
parser.add_argument('-p', '--project', action='store', dest='project')
parser.add_argument('-d', '--debug', action='store_true', dest='debug')

args = parser.parse_args()


USER = '<your_jira_user>'
PASS = '<your_jira_password>'
PLAN_DATE = args.plan if args.plan else '2017-11-01'
CURRENT_RELEASE = args.release if args.release else 'RE-2017.12'
PROJECT = args.project if args.project else 'RE'
DEBUG = args.debug


# check if fixversion actually exists
def check_fixversion_exists(project, fixversion):
    fixversions = [version.name for version in jira.project_versions(project)]
    if fixversion not in fixversions:
        print 'Warning: Release %s was not found in project %s ' \
            % (CURRENT_RELEASE, PROJECT)
        exit(1)


def print_issue_summary(issue):
    print issue.key + '\t: ' + issue.fields.summary


def print_issues_summary(issues):
    for issue in issues:
        print_issue_summary(issue)
    print


# main
jira = JIRA('https://rpc-openstack.atlassian.net', basic_auth=(USER, PASS))
print 'Querying project %s for issues in release %s...' \
    % (PROJECT, CURRENT_RELEASE)

check_fixversion_exists(PROJECT, CURRENT_RELEASE)

initial_items = jira.search_issues(
    'fixVersion = %s and created <= %s and type in (bug,task)'
    % (CURRENT_RELEASE, PLAN_DATE))
addl_items = jira.search_issues(
    'fixVersion = %s and created > %s and type in (bug,task)'
    % (CURRENT_RELEASE, PLAN_DATE))
total_items_in_release = initial_items + addl_items
completed_items = jira.search_issues(
    'fixVersion = %s and type in (bug,task) and status = Finished'
    % CURRENT_RELEASE)
remaining_items = jira.search_issues(
    'fixVersion = %s and type in (bug,task) and status != Finished'
    % CURRENT_RELEASE)
non_release_items = jira.search_issues(
    'labels in (re-related) AND resolved >= %s '
    'and Status in (Finished, Done) ORDER BY created ASC'
    % PLAN_DATE)

remaining_statuses = [a.fields.status.name for a in remaining_items]
status_count = Counter(remaining_statuses)
status_string = ', '.join([k + ': ' + str(v) for k, v in status_count.items()])

print 'Date: %s' % str(date.today())
print 'Planning Date: %s' % PLAN_DATE
print 'Current Release: %s' % CURRENT_RELEASE
print 'Total items in release:\t\t\t\t %s' % len(total_items_in_release)
print
print 'Initial release items in planning:\t\t %s' % len(initial_items)
if DEBUG: print_issues_summary(initial_items)
print 'Additional release items since planning:\t %s' % len(addl_items)
if DEBUG: print_issues_summary(addl_items)
print
print 'Completed release items:\t\t\t %s' % len(completed_items)
if DEBUG: print_issues_summary(completed_items)
print 'Remaining release items:\t\t\t %s (%s)' \
    % (len(remaining_items), status_string)
if DEBUG: print_issues_summary(remaining_items)
print
print 'Completed non-release items:\t\t\t %s' % len(non_release_items)
if DEBUG: print_issues_summary(non_release_items)
print
print 'Total items completed in release period:\t %s' \
    % (len(completed_items) + len(non_release_items))
