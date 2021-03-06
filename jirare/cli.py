#!/usr/bin/env python

from jira import JIRA
from datetime import date
from collections import Counter
import argparse
import os


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--release', action='store', dest='release')
    parser.add_argument('-i', '--issue', action='store', dest='issue')
    parser.add_argument('-pd', '--plan-date', action='store', dest='plan')
    parser.add_argument('-p', '--project', action='store', dest='project',
                        default='RE')
    parser.add_argument('-d', '--debug', action='store_true', dest='debug')
    parser.add_argument('-ppp', action='store_true', dest='ppp')
    parser.add_argument('--user', default=os.environ.get('JIRA_USER', None))
    parser.add_argument('--passwd', default=os.environ.get('JIRA_PASS', None))

    args = parser.parse_args()
    return args


def get_release():
    if args.release:
        release = args.release
    else:
        t = date.today()
        if t.month == 12:
            month = 1
            year = t.year + 1
        else:
            year = t.year
            month = t.month + 1
        release = "RE-%d.%02d" % (year, month)
    return release


def get_jira_fieldname(field):
    fields = jira.fields()
    for i in fields:
        if i['name'] == field:
            return i['key']


def get_epic_link(issue, epic_link_fieldname):
    iss = jira.issue(issue)
    return iss.raw['fields'][epic_link_fieldname]


def get_plan_date():
    if args.plan:
        return args.plan
    else:
        t = date.today()
        return t.strftime("%Y-%m-01")


def check_fixversion_exists(project, fixversion, jira):
    fixversions = [version.name for version in jira.project_versions(project)]
    if fixversion not in fixversions:
        print('Warning: Release %s was not found in project %s '
              % (CURRENT_RELEASE, PROJECT))
        exit(1)


def get_issue_fixversions(issue):
    fixVersions = []
    for fixVersion in issue.fields.fixVersions:
        fixVersions.append(fixVersion.name)

    return fixVersions


def print_issues_summary(issues):
    from prettytable import PrettyTable
    t = PrettyTable([
        'Type',
        'fix',
        'Status',
        'Resolution',
        'Key',
        'Epic',
        'Description'])

    t.align = 'l'
    epic_link_fieldname = get_jira_fieldname('Epic Link')

    for issue in issues:
        epic_link = get_epic_link(issue, epic_link_fieldname)

        if issue.fields.status.name == 'Needs Review (doing)':
            status = 'Review'
        else:
            status = issue.fields.status.name

        if len(issue.fields.summary) > 55:
            summary = (issue.fields.summary[:55] + '..')
        else:
            summary = issue.fields.summary

        fixVersions = ','.join(get_issue_fixversions(issue))

        try:
            resolution = issue.fields.resolution.name
        except AttributeError:
            resolution = 'Unresolved'

        t.add_row([issue.fields.issuetype.name,
                   fixVersions,
                   status,
                   resolution,
                   issue.key,
                   epic_link,
                   summary])
    print(t)


def open_link(link):
    import webbrowser
    webbrowser.open(link)


def open_issue(issue):
    link = 'https://rpc-openstack.atlassian.net/browse/%s' % issue
    open_link(link)


def ppp_report():
    print('- Release %s' % CURRENT_RELEASE)
    print('  - %s total issues, %s completed, %s in progress, %s backlog'
          % (len(total_items_in_release),
             len(completed_items),
             remaining,
             backlog))
    print('  - %s additional non-release items completed '
          '(re-related or non-release themed bugs)'
          % len(non_release_items))
    if DEBUG:
        open_link('https://rpc-openstack.atlassian.net/issues/?filter=14161')
    last_seven_days = jira.search_issues('filter=14161')
#        '(project = re OR labels = re-related) '
#        'AND type in (bug, task, sub-task) '
#        'AND resolutiondate >= -7d '
#        'AND resolution not in ("Won\'t Fix", "Won\'t Do", Duplicate) '
#        'ORDER BY resolutiondate ASC'
#   )
    total = len(last_seven_days)
    print('\n%d issues completed in the last seven days:\n' % total)
    print_issues_summary(last_seven_days)
    print('Remaining release items:\t\t\t %s (%s)'
          % (len(remaining_items), status_string))
    if DEBUG:
        print_issues_summary(remaining_items)


def normal_report():
    print('Planning Date: %s' % PLAN_DATE)
    print('Current Release: %s' % CURRENT_RELEASE)
    print('Total (non-epic) items in release:\t\t %s'
          % len(total_items_in_release))
    print
    print('Initial release items in planning:\t\t %s' % len(initial_items))
    if DEBUG: print_issues_summary(initial_items)
    print('Additional release items since planning:\t %s' % len(addl_items))
    if DEBUG: print_issues_summary(addl_items)
    print
    print('Completed release items:\t\t\t %s' % len(completed_items))
    if DEBUG: print_issues_summary(completed_items)
    print('Remaining release items:\t\t\t %s (%s)'
          % (len(remaining_items), status_string))
    if DEBUG: print_issues_summary(remaining_items)
    print
    print('Completed non-release items:\t\t\t %s' % len(non_release_items))
    if DEBUG: print_issues_summary(non_release_items)
    print
    print('Total items completed in release period:\t %s'
          % (len(completed_items) + len(non_release_items)))


args = get_args()

USER = args.user
PASS = args.passwd
PLAN_DATE = get_plan_date()
CURRENT_RELEASE = get_release()
PROJECT = args.project
DEBUG = args.debug

jira = JIRA('https://rpc-openstack.atlassian.net', basic_auth=(USER, PASS))

initial_items = jira.search_issues(
    'fixVersion = %s '
    'AND  created <= %s '
    'AND type in (bug,task) '
    % (CURRENT_RELEASE, PLAN_DATE))

addl_items = jira.search_issues(
    'fixVersion = %s '
    'AND created > %s '
    'AND type in (bug,task) '
    % (CURRENT_RELEASE, PLAN_DATE))

total_items_in_release = initial_items + addl_items

completed_items = jira.search_issues(
    'fixVersion = %s '
    'AND type in (bug,task) '
    'AND StatusCategory = Done '
    'ORDER BY resolution ASC '
    % CURRENT_RELEASE)

remaining_items = jira.search_issues(
    'fixVersion = %s '
    'AND type in (bug,task) '
    'AND status != Finished '
    'ORDER BY STATUS ASC '
    % CURRENT_RELEASE)

non_release_items = jira.search_issues(
    '('
    '(Project = %s AND (fixVersion != %s OR fixVersion = null)) '
    'OR (labels = re-related) '
    ')'
    'AND type in (bug, task, sub-task) '
    'AND resolutiondate >= %s '
    'AND StatusCategory = Done '
    'AND resolution = "Done"'
    'ORDER BY resolved ASC'
    % (PROJECT, CURRENT_RELEASE, PLAN_DATE))

remaining_statuses = [a.fields.status.name for a in remaining_items]
status_count = Counter(remaining_statuses)
backlog = status_count['Backlog']
remaining = sum(status_count.values()) - backlog
status_string = ', '.join([k + ': ' + str(v) for k, v in status_count.items()])

######################
#        main        #
######################


def main():

    if args.issue:
        open_issue(args.issue)
        exit(0)

    print('Querying project %s for issues in release %s...'
          % (PROJECT, CURRENT_RELEASE))

    check_fixversion_exists(PROJECT, CURRENT_RELEASE, jira)

    if args.ppp:
        ppp_report()

    else:
        normal_report()


if __name__ == "__main__":
    main()
