from setuptools import setup, find_packages
import sys

if sys.version_info < (2, 7) and "install" in str(sys.argv):
    sys.exit('jira-re requires Python >= 2.7 '
             'but the running Python is %s.%s.%s' % sys.version_info[:3])

setup(
    name='jirare',
    version='0.0.1',
    description='A little tool for gathering jira info from the RE project',
    python_requires='>=2.7',
    install_requires=['jira', 'prettytable'],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'jirare=jirare.cli:main',
        ],
    },
)
