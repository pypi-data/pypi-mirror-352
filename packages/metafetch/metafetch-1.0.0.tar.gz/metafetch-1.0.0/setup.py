
from setuptools import setup, find_packages
import os

def read_readme():
    with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as f:
        return f.read()

def read_requirements():
    with open('requirements.txt') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='metafetch',
    version='1.0.0',
    description='A beautiful, fast, and comprehensive system information tool',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    author='Ujjawal Singh / @volksgeistt',
    author_email='unrealvolksgeist@gmail.com',
    url='https://github.com/volksgeistt/metafetch',
    license='MIT',
    py_modules=['metafetch'],
    install_requires=read_requirements(),
    entry_points={
        'console_scripts': [
            'metafetch=metafetch:main',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],
    keywords='system information neofetch system-info cli terminal',
    python_requires='>=3.6',
    project_urls={
        'Bug Reports': 'https://github.com/volksgeistt/metafetch/issues',
        'Source': 'https://github.com/volksgeistt/metafetch',
        'Documentation': 'https://github.com/volksgeistt/metafetch/blob/main/README.md',
    },
)