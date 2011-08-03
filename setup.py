"""
Copyright (C) 2010 Polar Technologies - www.polartech.es
Author: Alvaro Iradier <alvaro.iradier@polartech.es>
"""
from setuptools import setup

NAME = "PlantUML"
VERSION = 1.2

setup(
    name = NAME,
    version = VERSION,
    packages = ['plantuml'],
    author = "Alvaro J. Iradier",
    author_email = "alvaro.iradier@polartech.es",
    description = "A macro to include diagrams from PlantUML",
    license = "GPL",
    keywords = "trac macro uml plantuml embed include",
    url = "http://trac-hacks.org/wiki/TracPlantUmlPlugin",

    entry_points = {
        "trac.plugins": [
            "plantuml.macro = plantuml.macro"
        ]
    }
)
