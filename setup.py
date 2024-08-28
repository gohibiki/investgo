from setuptools import setup, find_packages

setup(
    name='investgo',
    version='1.0.2',
    packages=find_packages(),
    install_requires=[
        'cloudscraper',
        'pandas',
    ],
    author='gohibiki',
    author_email='gohibiki@protonmail.com',
    description='A package to fetch historical stock prices from Investing.com',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/gohibiki/investgo',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
