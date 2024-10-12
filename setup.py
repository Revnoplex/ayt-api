from setuptools import setup, find_packages
import codecs
import os.path

with open("README.md", 'r') as readme_file:
    readme = readme_file.read()
    readme_file.close()

with open("requirements.txt", 'r') as requirements_file:
    requirements = requirements_file.read().splitlines()
    requirements_file.close()


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


setup(
    name="ayt-api",
    description="A basic, asynchronous, object-oriented YouTube API wrapper written in Python.",
    long_description_content_type="text/markdown",
    long_description=readme,
    author="Revnoplex",
    author_email="revnoplex.business@protonmail.com",
    version=get_version("ayt_api/__init__.py"),
    url="https://github.com/Revnoplex/ayt-api",
    license="MIT",
    packages=find_packages(exclude=["tests", "experiments"]),
    install_requires=requirements,
    setup_requires=["wheel"],
    tests_require=['pytest>=7.1.2'],
    test_suite='tests',
    python_requires=">=3.8.0",
)
