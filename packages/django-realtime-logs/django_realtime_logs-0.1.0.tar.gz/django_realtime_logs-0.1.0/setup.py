from setuptools import setup, find_packages # type: ignore

setup(
    name='django-realtime-logs',
    version='0.1.0',
    description='Realtime log viewer for Django using Channels',
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
