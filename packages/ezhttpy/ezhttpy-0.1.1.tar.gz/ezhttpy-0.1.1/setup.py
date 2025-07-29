from setuptools import setup, find_packages

setup(
    name='ezhttpy',
    version='0.1.1',
    description='Simple HTTP server with custom commands and HTML support',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Denis Varga',
    url='https://easy_http.denisvarga.eu/',
    author_email='mail@denisvarga.eu',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
