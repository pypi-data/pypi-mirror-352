from setuptools import setup, find_packages

setup(
    name='pygen-search',
    version='0.1.0',
    author='PyGen Labs',
    author_email='pygen.co@gmail.com',
    description='A simple and extensible search SDK for Python applications.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/pygen-labs/pygen-search',
    packages=find_packages(exclude=['tests*']),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Indexing',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.7',
    install_requires=[
        # No external dependencies required
    ],
    keywords='search, text search, information retrieval, sdk, pygen, search engine library, pygen-search',
    project_urls={
        'Source': 'https://github.com/pygen-labs/pygen-search/',
    },
)