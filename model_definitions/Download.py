from github import Github
from github import GithubException

import StringIO

def get_sha_for_tag(repository, tag):
    branches = repository.get_branches()
    matched_branches = [match for match in branches if match.name == tag]
    if matched_branches:
        return matched_branches[0].commit.sha

    tags = repository.get_tags()
    matched_tags = [match for match in tags if match.name == tag]
    if not matched_tags:
        raise ValueError('No Tag or Branch exists with tha'
                         't name')
    return matched_tags[0].commit.sha


def download_directory(repository, sha, server_path, template_files):
    contents = repository.get_dir_contents(server_path, ref=sha)

    for content in contents:

        if content.type == 'dir':
            download_directory(repository, sha, content.path, template_files)
        else:
            try:
                print "Processing %s" % content.path
                path = content.path
                file_content = repository.get_contents(path, ref=sha)
                file_data = file_content.decoded_content
                template_files.append(file_data)
            except (GithubException, IOError) as exc:
                print('Error processing %s: %s', content.path, exc)

user_name = raw_input("Github username? ")
password = raw_input("Github password? ")
github = Github(user_name, password)
repository_name = "util-swagger-codegen-models"
organization = github.get_user().get_orgs()[0]
repo = organization.get_repo(repository_name)
branch = raw_input("Branch to download? ")
sha = get_sha_for_tag(repo, branch)
template_files = []
download_directory(repo, sha, 'model_definitions', template_files)
definitions_yaml = ''

print 'Composing swagger-spec.yaml with ' + str(len(template_files)) + ' models.'

for str_file in template_files:
    definitions_yaml = definitions_yaml + str_file

print 'swagger-spec.yaml definitions view:\n' + definitions_yaml