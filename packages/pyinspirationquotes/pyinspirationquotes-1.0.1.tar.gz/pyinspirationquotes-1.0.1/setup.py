from setuptools import setup, find_packages
import pathlib

# Read the README.md file for the long_description
here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name='pyinspirationquotes',
    version='1.0.1',
    author='Akanksha Soni',
    author_email='aakankshasoni024@gmail.com',
    description='A simple and fun Python package that provides random inspirational quotes.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/akankshasoni024/pyinspirationquotes',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'pyinspirationquotes=pyinspirationquotes.main:get_inspiration',
        ],
    },
    package_data={
        'pyinspirationquotes': ['quotes.txt'],
    },
    include_package_data=True,
    install_requires=[],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Utilities',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
