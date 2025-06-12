import os
import sys
from sys import stderr

from github import Github
from github.Commit import Commit
from github.PaginatedList import PaginatedList


def has_commits(commits: "PaginatedList[Commit]") -> bool:
    # totalCount is borked, len(list(...)) eats too many API calls
    try:
        commits[0]
        return True
    except IndexError:
        return False


def main() -> None:
    token = os.environ.get("GITHUB_TOKEN", None)
    if token is None:
        print("environment variable GITHUB_TOKEN not set", file=sys.stderr)
        sys.exit(1)

    gh = Github(
        os.environ["GITHUB_TOKEN"],
        user_agent="nixpkgs-inactive-committers",
        per_page=100,
        timeout=90,
        retry=5,
    )
    print(gh.get_rate_limit(), file=stderr)
    org = gh.get_organization("nixos")
    nixpkgs = org.get_repo("nixpkgs")

    committers = org.get_team_by_slug("nixpkgs-committers").get_members()
    sorted_committers = sorted(list(committers), key=lambda c: c.login.lower())

    for member in sorted_committers:
        # Check whether the user used their commit access in the past year
        # https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#list-repository-activities
        url_parameters = dict()
        url_parameters["actor"] = member.login
        url_parameters["time_period"] = "year"
        _, data = nixpkgs.requester.requestJsonAndCheck("GET", f"{nixpkgs.url}/activity", parameters=url_parameters)

        if len(data) == 0:
            print(f"{member.login:<20}: No activity requiring commit access within the past year")

if __name__ == "main":
    main()
