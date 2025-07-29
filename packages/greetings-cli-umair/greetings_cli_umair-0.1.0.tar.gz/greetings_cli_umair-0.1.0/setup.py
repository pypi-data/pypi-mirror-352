from setuptools import setup, find_packages

setup(
    name='greetings-cli-umair',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'click',
    ],
    entry_points={
        'console_scripts': [
            'mycli = mycli.cli:hello',
        ],
    },
    author='Umair Ahmed Imran',
    description='A simple CLI app using Click(Testing).',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
)

