import os
import shutil
import sys

import click

from biolib import utils  # Import like this to let BASE_URL_IS_PUBLIC_BIOLIB be set correctly
from biolib._internal.add_copilot_prompts import add_copilot_prompts
from biolib._internal.templates import templates
from biolib.utils import BIOLIB_PACKAGE_VERSION


@click.command(help='Initialize a BioLib project', hidden=True)
def init() -> None:
    cwd = os.getcwd()

    app_uri = input('What URI do you want to create the application under? (leave blank to skip): ')
    app_name = app_uri.split('/')[-1] if app_uri else None
    if not app_uri:
        print(
            'Remember to set the app URI in the .biolib/config.yml file later, '
            'and docker image name in the .biolib/config.yml and .github/workflows/biolib.yml files.'
        )
    copilot_input = input('Do you want to include Copilot style prompts? [y/N]: ')
    include_copilot_style = copilot_input.lower() == 'y'

    template_dir = templates.init_template()
    conflicting_files = []

    try:
        # First pass: check for conflicts
        for root, dirs, filenames in os.walk(template_dir):
            dirs[:] = [d for d in dirs if '__pycache__' not in d]
            relative_dir = os.path.relpath(root, template_dir)
            destination_dir = cwd if relative_dir == '.' else os.path.join(cwd, relative_dir)
            for filename in filenames:
                source_file = os.path.join(root, filename)
                destination_file = os.path.join(destination_dir, filename)
                if os.path.exists(destination_file):
                    with open(source_file, 'rb') as fsrc, open(destination_file, 'rb') as fdest:
                        if fsrc.read() != fdest.read():
                            conflicting_files.append(os.path.relpath(destination_file, cwd))
        if conflicting_files:
            print('The following files were not overwritten. Use --force to override them:', file=sys.stderr)
            for conflicting_file in conflicting_files:
                print(f'  {conflicting_file}', file=sys.stderr)
            exit(1)

        replace_app_uri = app_uri if app_uri else 'PUT_APP_URI_HERE'

        # Second pass: copy files (only if no conflicts)
        for root, dirs, filenames in os.walk(template_dir):
            dirs[:] = [d for d in dirs if '__pycache__' not in d]
            relative_dir = os.path.relpath(root, template_dir)
            destination_dir = os.path.join(cwd, relative_dir)
            os.makedirs(destination_dir, exist_ok=True)

            for filename in filenames:
                if utils.BASE_URL_IS_PUBLIC_BIOLIB and filename == 'biolib.yml':
                    continue

                source_file = os.path.join(root, filename)
                destination_file = os.path.join(destination_dir, filename)

                if not os.path.exists(destination_file):
                    try:
                        with open(source_file) as f:
                            content = f.read()

                        new_content = content.replace('BIOLIB_REPLACE_PYBIOLIB_VERSION', BIOLIB_PACKAGE_VERSION)
                        new_content = new_content.replace('BIOLIB_REPLACE_APP_URI', replace_app_uri)
                        new_content = new_content.replace(
                            'BIOLIB_REPLACE_DOCKER_TAG',
                            app_name if app_name else 'PUT_DOCKER_TAG_HERE',
                        )

                        with open(destination_file, 'w') as f:
                            f.write(new_content)
                    except UnicodeDecodeError:
                        shutil.copy2(source_file, destination_file)

        readme_path = os.path.join(cwd, 'README.md')
        if not os.path.exists(readme_path) and app_name:
            with open(readme_path, 'w') as readme_file:
                readme_file.write(f'# {app_name}\n')

        add_copilot_prompts(force=False, style=include_copilot_style, silent=True)

    except KeyboardInterrupt:
        print('\nInit command cancelled.', file=sys.stderr)
        exit(1)
