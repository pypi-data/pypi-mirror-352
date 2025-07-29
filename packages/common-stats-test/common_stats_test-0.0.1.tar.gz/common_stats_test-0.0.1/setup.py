from setuptools import setup, find_packages

setup(
    name='common_stats_test',
    version='0.0.1',
    description='A simple library for basic statistical calculations',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Tommy Chang',
    author_email='techang1710@email.com',
    packages=find_packages(),
    install_requires=[
        "pytest"
    ],
    license='MIT',
    python_requires='>=3.7',
)