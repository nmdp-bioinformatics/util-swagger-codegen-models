from github import Github
from github import GithubException

from sys import argv

from os import walk

import os
import sys


def get_sha_for_tag(repository, tag):
    branches = repository.get_branches()
    matched_branches = [match for match in branches if match.name == tag]
    if matched_branches:
        return matched_branches[0].commit.sha

    tags = repository.get_tags()
    matched_tags = [match for match in tags if match.name == tag]
    if not matched_tags:
        raise ValueError('No Tag or Branch exists with that name')

    return matched_tags[0].commit.sha


def download_directory(repository, sha, server_path, template_files):
    contents = repository.get_dir_contents(server_path, ref=sha)

    for content in contents:

        if content.type == 'dir':
            download_directory(repository, sha, content.path, template_files)
        else:
            try:
                path = content.path
                file_name, file_extension = os.path.splitext(path)

                if file_extension == '.yaml':
                    sys.stdout.write("Processing %s" % content.path)

                    file_content = repository.get_contents(path, ref=sha)
                    file_data = file_content.decoded_content
                    template_files.append(file_data)
            except (GithubException, IOError) as exc:
                sys.stderr.write('Error processing %s: %s', content.path, exc)


def write_swagger_spec_file(directory, swagger_file_name, repo, sha, output_directory, swagger_template_path, swagger_paths_directory, dto_property_name, models_path):
    template_files = []
    output_path = os.path.join(output_directory, swagger_file_name)
    definitions_yaml = '%s:\n' % dto_property_name
    paths_yaml = 'paths:\n'
    file_header = ''

    if models_path == None:
        download_directory(repo, sha, 'model_definitions/%s' % directory, template_files)
        for str_file in template_files:
            for line in str_file.split('\n'):
                if line and not line.isspace():
                    definitions_yaml += '  ' + line + '\n'
    else:
        with open(os.path.join(models_path, '%.txt' % directory)) as model_reader:
            definitions_yaml = model_reader.read()

    definitions_yaml += '\n\r'

    with open(swagger_template_path, 'r') as reader:
        swagger_template = reader.read()

    for line in swagger_template.split('\n'):
        if line and not line.isspace():
            file_header += line + '\n'

    for (dirpath, dirnames, filenames) in walk(os.path.join(swagger_paths_directory, directory)):
        for f in filenames:
            with open(os.path.join(dirpath, f)) as path_reader:
                path = path_reader.read()

                for line in path.split('\n'):
                    if line and not line.isspace():
                        paths_yaml += '  ' + line + '\n'

    with open(output_path, 'w') as writer:
        writer.write(swagger_template + '\n')
        writer.write(paths_yaml + '\n')
        writer.write(definitions_yaml + '\n')

    sys.stdout.write('Successfully created %s\n' % swagger_file_name)

# user_name = raw_input("Github username? ")
# password = raw_input("Github password? ")
# branch = raw_input("Branch to download? ")

sys.stdout.write('Begin compiling swagger-spec.yaml')

user_name = argv[1]
password = argv[2]
branch = argv[3]
output_directory = r'%s' % argv[4]
swagger_paths_directory = r'%s' % argv[5]
swagger_template_path = r'%s' % argv[6]
dto_property_name = argv[7]
models_path = None

if len(argv) >= 9:
    models_path = r'%s' % argv[8]

github = Github(user_name, password)
repository_name = "util-swagger-codegen-models"
organization = github.get_user().get_orgs()[0]
repo = organization.get_repo(repository_name)
sha = get_sha_for_tag(repo, branch)


write_swagger_spec_file('hml', 'swagger-spec.hml.yaml', repo, sha, output_directory, swagger_template_path, swagger_paths_directory, dto_property_name, models_path)
write_swagger_spec_file('fhir', 'swagger-spec.fhir.yaml', repo, sha, output_directory, swagger_template_path, swagger_paths_directory, dto_property_name, models_path)
