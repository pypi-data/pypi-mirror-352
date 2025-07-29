from setuptools import setup, find_packages


def readme():
    with open('README.md', 'r') as f:
        return f.read()


setup(
    name='python-easyvenv',
    version='1.6.6',
    author='afguy',
    author_email='alwaysfrownguy@gmail.com',
    description='Make your work with venv easier',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    keywords='python venv',
    project_urls={
        'Documentation': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
    },
    python_requires='>=3.7'
)
