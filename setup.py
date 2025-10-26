from setuptools import setup, find_packages

setup(
    name='cli',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'cli=cli.main:main',
        ],
    },
    author='Tianyi Zhao',
    author_email='33299235@qq.com',
    description='CLI 时间管理终端程序',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/scp020/CLI',
)
