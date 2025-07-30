from setuptools import setup, find_namespace_packages

setup(
    name='brynq_sdk_task_scheduler',
    version='4.0.1',
    description='Code to execute tasks in BrynQ.com with the task scheduler',
    long_description='Code to execute tasks in the BrynQ.com platform with the task scheduler',
    author='BrynQ',
    author_email='support@brynq.com',
    packages=find_namespace_packages(include=['brynq_sdk*']),
    license='BrynQ License',
    install_requires=[
        'brynq-sdk-brynq>=4,<5',
        'brynq-sdk-functions>=2,<3',
        'brynq-sdk-mysql>=3,<4',
        'brynq-sdk-mandrill>=2,<3',
        'brynq-sdk-elastic>=3,<4'
    ],
    zip_safe=False,
)