from setuptools import setup, find_packages

with open("README.md", 'r') as readme_file:
    readme = readme_file.read()
    readme_file.close()

with open("requirements.txt", 'r') as requirements_file:
    requirements = requirements_file.readlines()
    requirements_file.close()

setup(
    name="ayt-api",
    description="An Asynchronous, Object oriented python library for the YouTube api",
    long_description_content_type="text/markdown",
    long_description=readme,
    author="Revnoplex",
    author_email="revnoplex.business@protonmail.com",
    version="0.1.0r1",
    url="https://github.com/Revnoplex/ayt-api",
    license="MIT",
    packages=find_packages(exclude=["tests"]),
    install_requires=requirements,
    setup_requires=["wheel"],
    tests_require=['pytest~=7.1.2'],
    test_suite='tests',
    python_requires=">=3.7.0",
)
