from setuptools import setup, find_packages

with open('requirements.txt') as f:
    install_requires = f.read().splitlines()

setup(
    name='fastapi-filter',
    version='0.0.1',
    packages=find_packages(where='src', include=['fastapi_filter']),
    package_dir={'': 'src'},
    install_requires=install_requires,
    author='Aleksandr Andrukhov',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
)
