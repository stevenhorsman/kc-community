#!/usr/bin/env python3

#
# Copyright (c) 2025 IBM Corporation
#
# SPDX-License-Identifier: Apache-2.0
#
# Description: Check the list of committers to see if they are still contributing

import argparse
import datetime
from datetime import timedelta
import os

from collections import OrderedDict
from github3 import login
import generate_electorate

def main():
    # Get a token GitHub Personal API token see:
    #   https://blog.github.com/2013-05-16-personal-api-tokens/
    # for more information.
    try:
        personal_token=os.environ['GH_TOKEN']
    except KeyError:
        raise Exception("GH_TOKEN environment variable was not set")

    parser = argparse.ArgumentParser(description='Script to check out committers list')
    parser.add_argument("-end", required=True,help='the end date of the period to examine in format %%d/%%m/%%y.')
    parser.add_argument("-start",  help='the start date of the period to examine in format %%d/%%m/%%y.  If not set will default to' \
    '365 days before the end time')

    args = parser.parse_args()
    end_time = datetime.datetime.strptime(args.end, '%d/%m/%y')
    start_time = end_time - timedelta(days=365)
    if args.start != None:
        start_time = datetime.datetime.strptime(args.start, '%d/%m/%y')

    print("Getting committers from", start_time, " -> ", end_time)

    author_ids = set()
    projects=generate_electorate.find_authors_by_project(start_time, end_time)
    for project in projects:
        for authors in project.values():
            for author in authors:
                author_ids.add(author.id)

    print("Contributors:", author_ids)

    gh = login(token=personal_token)
    org = gh.organization('kata-containers')
    committers = org.team_by_name('kata-containers-committer')
    non_contributors = set()
    contributors = set()
    for member in committers.members():
        if not member.login in author_ids:
            non_contributors.add(member.login)
        else:
            contributors.add(member.login)

    print("Number of committers", committers.members_count, ", contributors:", len(contributors), ", non-contributors:",len(non_contributors))
    print("non-contributors:", sorted(non_contributors))

    maintainers = org.team_by_name('kata-containers-maintainer')
    non_contributors = set()
    contributors = set()
    for member in maintainers.members():
        if not member.login in author_ids:
            non_contributors.add(member.login)
        else:
            contributors.add(member.login)

    print("Number of maintainers", maintainers.members_count, ", contributors:", len(contributors), ", non-contributors:",len(non_contributors))
    print("non-contributors:", sorted(non_contributors))

if __name__ == '__main__':
    main()
