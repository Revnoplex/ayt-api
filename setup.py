from setuptools import setup, find_packages

readme = open("README.md", 'r').read()

requirements = open("requirements.txt", 'r').readlines()

setup(
    name="ayt-api",
    description="An Asynchronous, Object oriented python library for the YouTube api",
    author="Revnoplex",
    author_email="revnoplex.business@protonmail.com",
    version='0.1.0',
    url="https://github.com/Revnoplex/ayt-api",
    license="MIT",
    packages=find_packages(exclude=["tests"]),
    install_requires=requirements,
    tests_require=['pytest~=7.1.2'],
    test_suite='tests',
    python_requires=">=3.7.0"
)
