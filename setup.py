from os.path import join, dirname
from setuptools import setup

LONG_DESCRIPTION = """
Reference implementation of the ERAV data model for citizen science.  ERAV is an extension to EAV with support for maintaining multi-faceted provenance metadata for an entity.
"""


def parse_markdown_readme():
    """
    Convert README.md to RST via pandoc, and load into memory
    (fallback to LONG_DESCRIPTION on failure)
    """
    # Attempt to run pandoc on markdown file
    import subprocess
    try:
        subprocess.call(
            ['pandoc', '-t', 'rst', '-o', 'README.rst', 'README.md']
        )
    except OSError:
        return LONG_DESCRIPTION

    # Attempt to load output
    try:
        readme = open(join(dirname(__file__), 'README.rst'))
    except IOError:
        return LONG_DESCRIPTION
    return readme.read()


setup(
    name='vera',
    version='1.0.0b1',
    author='S. Andrew Sheppard',
    author_email='andrew@wq.io',
    url='https://wq.io/vera',
    license='MIT',
    description=LONG_DESCRIPTION,
    long_description=parse_markdown_readme(),
    packages=[
        'vera',
        'vera.migrations',
    ],
    install_requires=[
        'natural-keys',
        'wq.db>=1.0.0b1',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: JavaScript',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Database :: Database Engines/Servers',
    ],
    test_suite='tests',
    tests_require=[
        'rest-pandas',
        'psycopg2',
    ],
)
