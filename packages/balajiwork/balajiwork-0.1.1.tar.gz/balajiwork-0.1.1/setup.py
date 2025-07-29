from setuptools import setup, find_packages

setup(
    name='balajiwork',
    version='0.1.1',
    packages=find_packages(),
    author='Balaji',
    author_email='',
    description='Minimal Python library with info() function.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://balaji.work',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.6',
    install_requires=[],
)
