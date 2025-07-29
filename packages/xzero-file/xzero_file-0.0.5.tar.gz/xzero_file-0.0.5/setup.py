import os
from setuptools import setup, find_packages

def read_requirements(filename):
    with open(os.path.join(os.path.dirname(__file__), 'xzero_file', filename), 'r') as f:
        return [line.strip() for line in f if line.strip()]

setup(
    name='xzero_file',  # Replace with your project name
    version='0.0.5',  # Replace with your project version
    packages=find_packages(),
    install_requires=read_requirements('requirements.txt'),
    author='alick97',  # Replace with your name
    author_email='alick97@outlook.com',  # Replace with your email
    package_data={
        '': ['requirements.txt', 'README.md', 'assets/*']
    },
    include_package_data=True,
    description='upload and download file by web',  # Replace with your description
    long_description=open(os.path.join(os.path.dirname(__file__), 'xzero_file', 'README.md')).read(),  # Optional: Read from README.md
    long_description_content_type='text/markdown',  # Optional: If you're using Markdown in README.md
    url='https://github.com/alick97/xzero-file',  # Replace with your project's URL (e.g., GitHub)
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  # Replace with your project's license
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  # Replace with your project's minimum Python version
)
