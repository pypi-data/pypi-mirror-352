import click
from click_help_colors import HelpColorsCommand

import stf.common.config as common_config
import stf.common.filesystem as common_filesystem
import stf.common.docker as common_docker
import os
import sys
import yaml

sys.path.insert(1, os.getcwd())


@click.command(
    cls=HelpColorsCommand,
    help_headers_color='yellow',
    help_options_color='green',
)
@click.option('-m', '--mode', 'mode', required=False, default="normal", type=click.Choice(['normal', 'debug']))
def init(mode):
    click.secho("Initializing docker for selenium in %s mode" % (mode), fg='blue')

    base_docker_compose_file = "%s/docker-compose.base.yml" % (common_config.get_assets_dir())
    with open(base_docker_compose_file, 'r') as ymlfile:
        docker_compose = yaml.full_load(ymlfile)

        if mode == common_docker.DOCKER_MODE_DEBUG:
            docker_compose['services']['selenium-hub']['environment'].extend([
                'GRID_DEBUG=true',
                'SE_OPTS="-debug"'
            ])

        docker_compose['services']['chrome'] = common_docker.get_chrome_config(mode)
        docker_compose['services']['firefox'] = common_docker.get_firefox_config(mode)

        output_docker_file = "%s/docker-compose.yml" % (os.getcwd())
        with open(output_docker_file, 'w') as file:
            yaml.dump(docker_compose, file, default_flow_style=False, canonical=False, indent=2)
