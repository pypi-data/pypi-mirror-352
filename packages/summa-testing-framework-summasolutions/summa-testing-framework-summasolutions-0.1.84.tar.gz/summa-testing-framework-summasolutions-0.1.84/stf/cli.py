import click
from click_help_colors import HelpColorsGroup
import os
import sys

sys.path.append(os.getcwd())

from stf.command import config as config_commands
from stf.command import grid as grid_commands
from stf.command import suite as suite_commands


@click.group(
    cls=HelpColorsGroup,
    help_headers_color='yellow',
    help_options_color='green',
)
@click.version_option()
def cli():
    pass


cli.add_command(config_commands.init, 'config:init')
cli.add_command(grid_commands.init, 'grid:init')
cli.add_command(suite_commands.create, 'suite:create')
cli.add_command(suite_commands.run, 'suite:run')
