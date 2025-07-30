# -*- encoding: utf-8 -*-
'''
Description:  PyPI     
@created   : 2021/09/08 09:33:59
'''

#test
from setuptools import setup, find_packages

setup(
    name="raser",
    version="4.1.0",
    author="Xin Shi",
    author_email="Xin.Shi@outlook.com",
    description="RAdiation SEmiconductoR Detector Simulation",
    url="https://raser.team",

    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
    ],
)
