"""
Setup configuration for FabricEase library
Author: Abdulrafiu Izuafa
"""

from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "FabricEase - A Simple Python Library for Microsoft Fabric SQL Database Connections"

# Read requirements
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(req_path):
        with open(req_path, 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return [
        'pyodbc>=4.0.34',
        'azure-identity>=1.12.0',
        'python-dotenv>=0.19.0'
    ]

setup(
    name="fabricease",
    version="0.1.0",
    author="Abdulrafiu Izuafa",
    author_email="abdulrafiu@azurelearnai.org",
    description="A Simple Python Library for Microsoft Fabric SQL Database Connections",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Ramseyxlil/fabrisqldb_python_library",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Environment :: Console",
        "Framework :: Jupyter",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
            'black>=21.0',
            'flake8>=3.8',
            'mypy>=0.812',
            'build>=0.7.0',
            'twine>=4.0.0'
        ],
        'test': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
            'pytest-mock>=3.6.0'
        ]
    },
    keywords="microsoft-fabric sql-database azure authentication pyodbc database-connection",
    project_urls={
        "Bug Reports": "https://github.com/Ramseyxlil/fabrisqldb_python_library/issues",
        "Source": "https://github.com/Ramseyxlil/fabrisqldb_python_library",
        "Documentation": "https://github.com/Ramseyxlil/fabrisqldb_python_library#readme",
        "Repository": "https://github.com/Ramseyxlil/fabrisqldb_python_library.git",
        "Changelog": "https://github.com/Ramseyxlil/fabrisqldb_python_library/releases",
    },
    entry_points={
        'console_scripts': [
            'fabricease-init=fabricease.utils:create_env_template',
        ],
    },
    package_data={
        'fabricease': ['*.md', '*.txt'],
    },
    include_package_data=True,
    zip_safe=False,
    license="MIT",
    platforms=["any"],
)