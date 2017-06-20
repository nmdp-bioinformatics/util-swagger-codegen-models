from github import Github
from github import GithubException

from os import walk

import os
import sys
import argparse


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


def walk_directory(dir):
    template_files = []

    for (dirpath, dirnames, filenames) in walk(dir):
        for f in filenames:
            with open(os.path.join(dirpath, f)) as reader:
                template_files.append(reader.read())

    return template_files


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
                sys.stderr.write('Error processing %s: %s\n', content.path, exc)


def write_swagger_spec_file(directory, swagger_file_name):
    template_files = []
    output_path = os.path.join(output_directory, swagger_file_name)
    definitions_yaml = '%s:\n' % dto_property_name
    paths_yaml = 'paths:\n'
    file_header = ''

    if models_path == None:
        download_directory(repo, sha, 'model_definitions/%s' % directory, template_files)
    else:
        template_files = walk_directory(os.path.join(models_path, directory))

    for str_file in template_files:
        for line in str_file.split('\n'):
            if line and not line.isspace():
                definitions_yaml += '  ' + line + '\n'

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

sys.stdout.write('Begin compiling swagger-spec.yaml')


parser = argparse.ArgumentParser()
parser.add_argument('-u')
parser.add_argument('-p')
parser.add_argument('-b')
parser.add_argument('-o')
parser.add_argument('-s')
parser.add_argument('-t')
parser.add_argument('-d')
parser.add_argument('-m')

args = parser.parse_args()

user_name = args.u
password = args.p
branch = args.b
output_directory = r'%s' % args.o
swagger_paths_directory = r'%s' % args.s
swagger_template_path = r'%s' % args.t
dto_property_name = args.d
models_path = r'%s' % args.m

github = Github(user_name, password)
repository_name = "util-swagger-codegen-models"
organization = github.get_user().get_orgs()[0]
repo = organization.get_repo(repository_name)
sha = get_sha_for_tag(repo, branch)

write_swagger_spec_file('hml', 'swagger-spec.hml.yaml')
write_swagger_spec_file('fhir', 'swagger-spec.fhir.yaml')
