import click
from click_help_colors import HelpColorsCommand

import stf.common.config as common_config
import stf.common.filesystem as common_filesystem
import stf.common.docker as common_docker
import os
import sys
import shutil

sys.path.insert(1, os.getcwd())


@click.command(
    cls=HelpColorsCommand,
    help_headers_color='yellow',
    help_options_color='green',
)
def init():
    click.secho("Initializing project config...", fg='blue')

    base_project_config_file = "%s/config.base.yml" % (common_config.get_assets_dir())
    target = "%s/config.yml" % os.getcwd()

    shutil.copyfile(base_project_config_file, target)

    click.secho("Initializing project xpath file...", fg='blue')

    base_project_xpath_file = "%s/xpath.yml" % (common_config.get_assets_dir())
    target_xpath = "%s/xpath.yml" % os.getcwd()

    shutil.copyfile(base_project_xpath_file, target_xpath)

    click.secho("Generating gitignore file...", fg='blue')

    base_gitignore_file = "%s/gitignore.base" % (common_config.get_assets_dir())
    target_gitignore = "%s/.gitignore" % os.getcwd()

    shutil.copyfile(base_gitignore_file, target_gitignore)