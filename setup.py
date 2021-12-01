import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="dswell",
    author="Prince Roshan",
    author_email="princekrroshan01@gmail.com",
    url="https://github.com/Agent-Hellboy/dswell",
    description=(
        "A CLI tool which will run a daemon process in backgroud to delete the file/directory after a specific time period"
    ),
    long_description=read("README.rst"),
    license="MIT",
    py_modules=["dswell"],
    entry_points={"console_scripts": ["dswell = dswell:dswell"]},
    install_requires=["touch", "click", "daemons"],
    include_package_data=True,
)
