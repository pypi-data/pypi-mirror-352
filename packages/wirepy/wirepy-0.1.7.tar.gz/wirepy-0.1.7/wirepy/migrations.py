# wirepy/migrations.py

import subprocess

def run_migrate():
    subprocess.run(["alembic", "revision", "--autogenerate", "-m", "auto"])

def run_upgrade():
    subprocess.run(["alembic", "upgrade", "head"])
