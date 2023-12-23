import os
from alembic import command
from alembic.config import Config


def migrate_database_tables() -> None:
    """Alembic default behaviour is searching for env.py file in ./env.py path.
    Currently there is no configuration to set absolute path for env.py in alembic.
    Workaround is to change current directory to ./migrations which is env.py parent directory
    """

    initial_directory = os.getcwd()

    print(initial_directory)

    os.chdir("./app/migrations")

    alembic_cfg = Config("./alembic.ini")
    command.upgrade(alembic_cfg, "head")

    os.chdir(initial_directory)
