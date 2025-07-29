from io import open
from setuptools import setup

version = '1.1.0'

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()
setup(
    name = 'CryptoBotSDK',
    author = 'Daniil Yumieiko',
    author_email = 'r3s1zetv@gmail.com',
    url = 'https://github.com/yumieiko/CryptoBotSDK',
    description = 'CryptoBot Software Development Kit',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    license = 'MIT',
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    packages = ['CryptoBotSDK', 'CryptoBotSDK/types'],
    where = ['where'],
    install_requires = ['requests'],
)