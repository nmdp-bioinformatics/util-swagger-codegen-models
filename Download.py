from os import walk

import os
import sys
import argparse


def walk_directory(dir):
    template_files = []

    for (dirpath, dirnames, filenames) in walk(dir):
        for f in filenames:
            with open(os.path.join(dirpath, f)) as reader:
                template_files.append(reader.read())

    return template_files


def write_swagger_spec_file(directory, swagger_file_name):
    output_path = os.path.join(output_directory, swagger_file_name)
    definitions_yaml = '%s:\n' % dto_property_name
    paths_yaml = 'paths:\n'
    file_header = ''
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
parser.add_argument('-o')
parser.add_argument('-s')
parser.add_argument('-t')
parser.add_argument('-d')
parser.add_argument('-m')
parser.add_argument('-p')

args = parser.parse_args()

output_directory = r'%s' % args.o
swagger_paths_directory = r'%s' % args.s
swagger_template_path = r'%s' % args.t
dto_property_name = args.d
models_path = r'%s' % args.m
packages = args.p.split(',')

for package in packages:
    if package and not package.isspace():
        write_swagger_spec_file(package, 'swagger-sepc.%s.yaml' % package)
