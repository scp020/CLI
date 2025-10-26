from setuptools import setup, find_packages

setup(
    name='cli',
    version='0.1.1',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'cli=cli.main:run',
        ],
    },
    author='Haiyan Yang',
    author_email='her email',
    description='一个每日一笑的Python小程序',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/scp020/daily_joke',
)
