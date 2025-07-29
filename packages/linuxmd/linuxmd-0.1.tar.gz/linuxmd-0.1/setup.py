from setuptools import setup, find_packages

setup(
    name='linuxmd',
    version='0.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'ls=linuxmd.cli:ls',
            'rm=linuxmd.cli:rm',
            'cat=linuxmd.cli:cat',
            'echo=linuxmd.cli:echo',
            'mkdir=linuxmd.cli:mkdir',
            'touch=linuxmd.cli:touch',
            'pwd=linuxmd.cli:pwd',
            'whoami=linuxmd.cli:whoami',
            'clear=linuxmd.cli:clear',
        ],
    },
    description='Linux command-line utilities for Windows',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Martin V.',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
    ],
    python_requires='>=3.6',
)
