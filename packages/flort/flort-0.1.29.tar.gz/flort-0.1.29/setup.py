from setuptools import setup, find_packages
from pathlib import Path

def get_version():
    """Get version from VERSION file."""
    version_file = Path(__file__).parent / "VERSION"
    if version_file.exists():
        return version_file.read_text().strip()
    return "2.0.0"

def get_long_description():
    """Get long description from README.md."""
    readme_file = Path(__file__).parent / "README.md"
    if readme_file.exists():
        return readme_file.read_text(encoding='utf-8')
    return "File Concatenation and Project Overview Tool"

setup(
    name='flort',
    version=get_version(),
    packages=find_packages(),
    
    # Include package data (assets, icons, etc.)
    package_data={
        'flort': [
            'assets/*.png',
            'assets/*.svg', 
            'assets/*.ico',
            'assets/logo.*',
        ],
    },
    include_package_data=True,
    
    # Entry points
    entry_points={
        'console_scripts': [
            'flort = flort.wrapper:main'
        ]
    },
    
    # Dependencies
    install_requires=[
        'windows-curses;platform_system=="Windows"',
    ],
    
    # Optional dependencies
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
            'mkdocs-material>=9.0',
        ],
        'docs': [
            'mkdocs-material>=9.0',
            'mkdocs-minify-plugin>=0.7',
            'mkdocstrings[python]>=0.20',
        ],
    },

    # Metadata
    author='Chris Watkins',
    author_email='chris@watkinslabs.com',
    description='File Concatenation and Project Overview Tool for LLM preparation',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    
    # URLs and links
    url='https://github.com/watkinlabs/flort',
    project_urls={
        'Homepage': 'https://github.com/watkinslabs/flort',
        'Documentation': 'https://watkinslabs.github.io/flort',
        'Repository': 'https://github.com/watkinslabs/flort.git',
        'Bug Tracker': 'https://github.com/watkinslabs/flort/issues',
        'Discussions': 'https://github.com/watkinslabs/flort/discussions',
        'Changelog': 'https://github.com/watkinslabs/flort/blob/main/CHANGELOG.md',
        'Logo': 'https://raw.githubusercontent.com/watkinslabs/flort/main/assets/flort-logo.png',
    },
    
    # Classification
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Console :: Curses',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Topic :: Documentation',
        'Topic :: Software Development :: Documentation',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Archiving',
        'Topic :: Text Processing',
        'Topic :: Utilities',
    ],
    
    keywords='file concatenation, project overview, LLM preparation, code analysis, documentation',
    
    # Python version requirement
    python_requires='>=3.6',
    
    # License
    license='BSD-3-Clause',
    
    # Additional files to include
    zip_safe=False,
)