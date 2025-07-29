from setuptools import setup, find_packages

setup(
    name="folder-schema-validator",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'folder-schema-validator=folder_schema_validator.core:main',
        ],
    },
)
