#!/usr/bin/env python3

import json
import os
import re
import requests
import git

GITHUB_TOKEN = os.environ['TRUSTPILOT_GITHUB_TOKEN']
TRELLO_API_KEY = os.environ['TRELLO_API_KEY']
TRELLO_TOKEN = os.environ['TRELLO_TOKEN']
TRELLO_INVITATIONS_REVIEW_LIST_ID = os.environ['TRELLO_INVITATIONS_REVIEW_LIST_ID']


def main():
    new_version = "1.0.21"

    run_for_all([
        "InvitationsModel",
        # "InvitationsModelTrustpilotMongo",
        # "InvitationsModelTrustpilotLegacyMongo",
    ], new_version)


def run_for_all(packages, new_version):
    for package in packages:
        search_result = search_library_consumers(package)

        if not search_result:
            print("No results for " + package +
                  "+in:file+extension:csproj+org:trustpilot+-filename:InvitationsModel.csproj")
            return

        projects = parse_search_results(search_result)
        update_package_in_projects(projects, package, new_version)


def search_library_consumers(package_name):
    search = "https://api.github.com/search/code?q=" + package_name + \
        "+in:file+extension:csproj+org:trustpilot+-filename:InvitationsModel.csproj"
    return github("GET", search).json()["items"]


def parse_search_results(search_items):
    parsed = {}
    for item in search_items:
        repo = item["repository"]["id"]
        # The same repo could show up in the search results more than once
        if not repo in parsed:
            repo_url = "https://api.github.com/repos/" + \
                item["repository"]["full_name"]
            repo_info = github("GET", repo_url).json()

            if repo_info['archived']:
                print("Skipping Project " +
                      item["repository"]["name"] + ": Project archived.")
                continue

            if not repo_info['permissions']['push']:
                print("Skipping Project " +
                      item["repository"]["name"] + ": No write access.")
                continue

            parsed[repo] = {
                "full_name": item["repository"]["full_name"],
                "name": item["repository"]["name"],
                "project": item["path"]
            }

            # Temp, return after first item is parsed
            print(parsed)
            return parsed

    return parsed


def update_package_in_projects(projects, package_name, new_version):
    print("Processing projects for package '" + package_name + "'")

    for project_id in projects:
        project = projects[project_id]
        print("Processing '" + project["name"] + "'")

        title = project["name"] + \
            ": TEST USING GITHUB ACTIONS"

        print("Creating trello card")
        create_trello_card(title)

        repo_location = "/tmp/" + project["name"]
        project_file_location = repo_location + "/" + project["project"]
        repo = git.Repo.clone_from(
            "https://" + GITHUB_TOKEN + "@github.com/" + project["full_name"] + ".git", repo_location)

        project_file_content = load_project_file_content(project_file_location)

        if not file_includes_package(project_file_content, package_name):
            print("Skipping, no package found for updating")
            continue

        if not project_type_is_core(project_file_content):
            print("Can't update version automatically, skipping")
            continue

        print("Updating version in project")
        updated_content = update_package_version(
            project_file_content, package_name, new_version)
        save_file_update(project_file_location, updated_content)

        print("Committing and pushing changes")
        try:
            commit_and_push(repo, normalize_name(
                title), package_name, new_version)
        except:
            print("Committing and pushing changes FAILED")

        # We rely on the github-pullrequestcreator to create a pull request
        # and github-trello bridge to attach it to the trello card


def create_trello_card(title):
    requests.request("POST", "https://api.trello.com/1/cards", params={
        "idList": TRELLO_INVITATIONS_REVIEW_LIST_ID,
        "name": title,
        "desc": ("This card and attached pull request was created automatically. "
                 "This was done using github actions, asking Andreas for more info......"),
        "key": TRELLO_API_KEY,
        "token": TRELLO_TOKEN,
    })


def commit_and_push(repo, branch_name, package_name, new_version):
    repo.config_writer().set_value(
        "user", "name", "Trustpilot Invitations Robot User").release()
    repo.config_writer().set_value("user", "email",
                                   "spe+trustpilot-invitations-robot-user@trustpilot.com").release()
    repo.git.checkout(b=branch_name)
    repo.git.commit("-am", "Updated " + package_name +
                    " to version " + new_version)
    repo.git.push("origin", branch_name)


def save_file_update(project_file_location, updated_content):
    with open(project_file_location, "w") as f:
        f.write(updated_content)


def update_package_version(project_file_content, package_name, new_version):
    package_line_regex = r"(.*\"Trustpilot." + \
        package_name + "\".*\")(.*)(\".*>)"
    replacer = r"\g<1>"+new_version+"\g<3>"
    return re.sub(package_line_regex, replacer, project_file_content)


def load_project_file_content(file_location):
    with open(file_location, "r") as f:
        return f.read()


def file_includes_package(project_file_content, package_name):
    return project_file_content.find("Include=\"Trustpilot." + package_name + "\"") >= 0


def project_type_is_core(project_file_content):
    # Only new .net core style projects use "PackageReference"
    return project_file_content.find("<PackageReference") >= 0


def github(method, url, params=None):
    return requests.request(method, url, json=params, headers={
        "Authorization": "token " + GITHUB_TOKEN,
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
    })


def normalize_name(name):
    name = name.lower()
    name = re.sub(r'[^a-z0-9]', ' ', name)
    name = re.sub(r'\s+', '-', name)
    name = name.strip('-')
    return name


if __name__ == "__main__":
    main()
