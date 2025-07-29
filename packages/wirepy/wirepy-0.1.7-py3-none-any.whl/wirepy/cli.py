# wirepy/cli.py

import click
from wirepy.scaffold import create_project, make_file
from wirepy.migrations import run_migrate, run_upgrade

@click.group()
def cli():
    """wirepy CLI - Scaffold Laravel-style FastAPI projects"""
    pass

@cli.command()
@click.argument('name')
def new(name):
    """Create a new wirepy project."""
    create_project(name)

@cli.command()
@click.argument('name')
def make_controller(name):
    """Create a new controller"""
    make_file('controller', name)

@cli.command()
@click.argument('name')
def make_model(name):
    """Create a new model"""
    make_file('model', name)

@cli.command()
@click.argument('name')
def make_service(name):
    """Create a new service"""
    make_file('service', name)

@cli.command()
@click.argument('name')
def make_route(name):
    """Create a new route"""
    make_file('route', name)

@cli.command()
@click.argument('name')
def make_schema(name):
    """Create a new schema"""
    make_file('schema', name)

@cli.command()
def migrate():
    """Generate alembic migration"""
    run_migrate()

@cli.command()
def upgrade():
    """Apply alembic migration"""
    run_upgrade()
