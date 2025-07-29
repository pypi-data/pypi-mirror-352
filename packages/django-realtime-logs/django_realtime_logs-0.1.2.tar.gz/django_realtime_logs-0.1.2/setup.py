import pathlib
from setuptools import setup, find_packages # type: ignore

# Get the long description from README.md
HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name='django-realtime-logs',
    version='0.1.2',
    description='Realtime log viewer for Django using Channels',
    long_description=README,
    long_description_content_type='text/markdown',
    author='Pranav Dixit',
    author_email='pranavdixit20@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django>=3.2',
        'channels>=3.0',
    ],
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
