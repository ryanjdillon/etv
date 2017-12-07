'''This CLI provides commands for running the Etv app, as well as generating a sample dataset
'''
import click

class Config(dict):
    def __init__(self, *args, **kwargs):
        import etv
        import os

        self.config = os.path.join(click.get_app_dir('etv'), 'config.yml')
        self.module = os.path.split(os.path.abspath(etv.__file__))[0]

        super(Config, self).__init__(*args, **kwargs)

    def load(self):
        '''Load YAML configuration from default system config location'''
        import yamlord
        try:
            self.update(yamlord.read_yaml(self.config))
        except Exception as e:
            click.echo(e)

    def save(self):
        '''Save YAML configuration from default system config location'''
        import yamlord
        self.config.ensure()
        yamlord.write_yaml(self, self.config)


pass_config = click.make_pass_decorator(Config, ensure=True)

@click.group()
@click.argument('json', type=click.Path(exists=True))
@pass_config
def main(config, json):
    config.load
    config['json'] = json


@main.command()
@pass_config
@click.option('-nt', default=32)
@click.option('-nd', default=2)
def create_sample_data(config, nt, nd):
    from ..utils.example import sample_data

    sample_data(path_json=config['json'], n_timesteps=nt, n_depths=nd)


@main.command()
@pass_config
@click.argument('command')
@click.argument('subcommand', default=None, required=False, nargs=-1)
def manage(config, command, subcommand):
    '''Run the Etv manage.py module with the given cmd

    `PATH_JSON` is made available to Django by setting it as an environment
    variable for the current process and it's subprocesses

    Example
    -------
    etv <path_json> manage migrate
    etv <path_json> manage runserver
    '''
    import os
    from subprocess import Popen
    import sys

    os.environ['PATH_JSON'] = config['json']

    cmd = ['python3', os.path.join(config.module, 'manage.py'), command]
    if subcommand:
        cmd.extend(list(subcommand))

    Popen(cmd, stdout=sys.stdout, stderr=sys.stderr).communicate()


if __name__ == '__main__':
    main()
