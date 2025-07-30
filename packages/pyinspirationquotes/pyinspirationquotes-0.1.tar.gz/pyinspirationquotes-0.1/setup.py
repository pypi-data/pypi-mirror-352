from setuptools import setup, find_packages

setup(
    name='pyinspirationquotes',
    version='0.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'pyinspirationalquotes=pyinspirationalquotes.main:get_quote',
        ],
    },
    package_data={
        'pyinspirationalquotes': ['quotes.txt'],
    },
    include_package_data=True,
    install_requires=[],
)
