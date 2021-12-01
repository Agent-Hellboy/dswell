import logging
import os
from pathlib import Path
import time

import click
import touch
from daemons.prefab import run


class DswellDaemon(run.RunDaemon):
    """A daemon to perform backgroud action like deletion of file after required period."""

    def __init__(self, rtime, name, pidfile):
        super().__init__(pidfile=pidfile)
        self.rtime = rtime
        self.name = name

    def run(self):
        time.sleep(self.rtime)
        if os.path.isfile(self.name):
            os.remove(self.name)
        else:
            os.rmdir(self.name)


@click.command()
@click.option(
    "--dir",
    default=False,
    help="Set this if you want to test multiple thing inside a directory",
)
@click.option("--name", help="Name of the file or package", required=True)
@click.option(
    "--time", type=int, help="time till file will be deleted(in seconds)", required=True
)
def dswell(dir: bool, name: str, time: int) -> None:
    dswell_path = os.path.join(Path.home(), ".dswell")
    if not os.path.isdir(dswell_path):
        os.mkdir(dswell_path)
    config_file = os.path.join(dswell_path, "daemon.log")
    logging.basicConfig(filename=config_file, level=logging.DEBUG)
    pidfile = os.path.join(dswell_path, "daemon.pid")
    if dir:
        os.mkdir(name)
        name = os.path.join(os.getcwd(), name)
        d = DswellDaemon(time, name, pidfile=pidfile)
        d.start()
    else:
        touch.touch(name)
        name = os.path.join(os.getcwd(), name)
        d = DswellDaemon(time, name, pidfile=pidfile)
        d.start()


if __name__ == "__main__":
    dswell()
