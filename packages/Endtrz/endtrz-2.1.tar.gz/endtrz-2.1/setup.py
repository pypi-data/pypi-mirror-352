#!/usr/bin/env python3

import re
import sys
import os
from setuptools import setup


SRC = os.path.abspath(os.path.dirname(__file__))


def get_version():
    with open(os.path.join(SRC, 'Endtrz/__init__.py')) as f:
        for line in f:
            m = re.match("__version__ = '(.*)'", line)
            if m:
                return m.group(1)
    raise SystemExit("Could not find version string.")


if sys.version_info < (3, 9):
    sys.exit('Endtrz requires Python >= 3.9.')

requirements = ['requests>=2.25']
optional_requirements = {
    'browser_cookie3': ['browser_cookie3>=0.19.1'],
}

keywords = (['instagram', 'instagram-scraper', 'instagram-client', 'instagram-feed', 'downloader', 'videos', 'photos',
             'pictures', 'instagram-user-photos', 'instagram-photos', 'instagram-metadata', 'instagram-downloader',
             'instagram-stories'])

# NOTE that many of the values defined in this file are duplicated on other places, such as the
# documentation.

setup(
    name='Endtrz',
    version=get_version(),
    packages=['Endtrz'],
    package_data={'Endtrz': ['py.typed']},
    url='https://Endtrz.github.io/',
    license='MIT',
    author='Endtrz',
    author_email='lord_izana@yahoo.com, dilshadhasnain89@gmail.com',
    description='Insta downloader of https://hasnainkk-07.vercel.app'
                'Download video, images, stories from Instagram.',
    long_description=open(os.path.join(SRC, 'README.rst')).read(),
    install_requires=requirements,
    python_requires='>=3.9',
    extras_require=optional_requirements,
    entry_points={'console_scripts': ['Endtrz=Endtrz.__main__:main']},
    zip_safe=False,
    keywords=keywords,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet',
        'Topic :: Multimedia :: Graphics'
    ]
)
