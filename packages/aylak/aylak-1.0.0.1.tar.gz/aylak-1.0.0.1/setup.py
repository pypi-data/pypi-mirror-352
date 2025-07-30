# !/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import find_packages, setup
import re

"""
with open("requirements.txt", "r", encoding="utf-8") as r:
    requirements = [i.strip() for i in r]"""

requirements = [
    "pythonansi==1.0.2",
    "aiofiles==23.2.1",
    "pillow==10.2.0",
    "aiohttp>=3.8.1",
    "telethon",
    "qrcode",
    "pyzbar",
    # "git+https://github.com/KurimuzonAkuma/pyrogram.git@v2.1.15",
]

with open("aylak/__init__.py", encoding="utf-8") as f:
    version = re.findall(r"__version__ = \"(.+)\"", f.read())[0]

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    # ? Genel Bilgiler
    name="aylak",
    version=version,
    url="https://github.com/aylak-github/aylak-pypi",
    description="Aylak PyPi",
    keywords=["aylak", "pypi", "aylak-pypi", "aylak-pypi"],
    author="aylak-github",
    author_email="contact@yakupkaya.net.tr",
    license="GNU AFFERO GENERAL PUBLIC LICENSE (v3)",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: Implementation",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Internet",
        "Topic :: Communications",
        "Topic :: Communications :: Chat",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    # ? Paket Bilgileri
    packages=find_packages(),
    package_data={
        "aylak": ["py.typed"],
    },
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "pyrogram=aylak.telegram.pyrogram:string",
            "telethon=aylak.telegram.telethon:string",
            "aylak=aylak.__main__:main",
        ]
    },
    install_requires=requirements,
    zip_safe=False,
    # ? PyPI Bilgileri
    long_description_content_type="text/markdown",
    dependency_links=["git+https://github.com/KurimuzonAkuma/pyrogram.git@v2.1.15"],
    # include_package_data=True,
)
