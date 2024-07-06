from setuptools import setup, find_packages

setup(
    name='my_library',  # Replace with your package name
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'requests',
        'pandas'
    ],
    description='A library to interact with my Flask API hosted on Render',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/my_library',  # Replace with your repository URL
    author='Your Name',
    author_email='your.email@example.com',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
