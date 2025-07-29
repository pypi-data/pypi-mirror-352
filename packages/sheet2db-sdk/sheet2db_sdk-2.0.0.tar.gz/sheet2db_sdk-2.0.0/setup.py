from setuptools import setup, find_packages

setup(
    name='sheet2db-sdk',
    version='2.0.0',
    description='A python library allows developers to interact with their Google Sheets via the Sheet2DB platform. It provides full CRUD support along with helper utilities for managing sheets.',
    author='Sheet2DB',
    packages=find_packages(),
    url="https://sheet2db.io",
    author_email="support@sheet2db.com",
    keywords="sheet2db, google sheets, python, sdk",
    project_urls={  # Optional
        "Documentation": "https://sheet2db.io/docs/sdk/python",
    },
    install_requires=[
        'requests'
    ]
)