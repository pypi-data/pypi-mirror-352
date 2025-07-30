from setuptools import setup, find_namespace_packages

setup(
    name='brynq_sdk_hr2day',
    version='1.0.0',
    description='BrynQ SDK for the HR2Day platform',
    long_description='BrynQ SDK for the HR2Day platform',
    author='BrynQ',
    author_email='support@brynq.com',
    packages=find_namespace_packages(include=['brynq_sdk*']),
    license='BrynQ License',
    install_requires=[
        'brynq-sdk-brynq>=4,<5',
        'requests>=2,<=3'
    ],
    zip_safe=False,
) 