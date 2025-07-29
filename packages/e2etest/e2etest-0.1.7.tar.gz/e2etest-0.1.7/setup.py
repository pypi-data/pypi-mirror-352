from setuptools import setup

DESCRIPTION = 'e2etest: Simple End-to-End Test for Web'
NAME = 'e2etest'
AUTHOR = 'Yuya Sato'
AUTHOR_EMAIL = 'yuya@lapisai.com'
URL = 'https://lapisai.com/query'
LICENSE = 'CREATIVE COMMONS'
DOWNLOAD_URL = 'https://github.com/yuyalapis/e2etest/'
PACKAGES = [
    'e2etest'
]
KEYWORDS = 'e2e test End-to-End'
VERSION = '0.1.7'

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    maintainer=AUTHOR,
    maintainer_email=AUTHOR_EMAIL,
    url=URL,
    download_url=DOWNLOAD_URL,
    packages=PACKAGES,
    license=LICENSE,
    keywords=KEYWORDS
)
