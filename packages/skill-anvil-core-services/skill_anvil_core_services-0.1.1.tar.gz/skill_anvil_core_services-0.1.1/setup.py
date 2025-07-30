from setuptools import setup, find_packages

setup(
    name='skill-anvil-core-services',  
    version='0.1.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django>=3.2',
    ],
    description='Reusable service layer for Django apps',
    author='Fodor Robert Stefan',
    author_email='robifodor1234576@yahoo.com',
    license='MIT',
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python :: 3',
    ],
)
