#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

from setuptools import setup, find_packages


setup(
    name="hpctinterfaces",
    version="0.1.0",
    description="Relation interfaces for the HPC team at Canonical",
    license="Apache-2.0",
    packages=find_packages(where="lib", include=["hpctinterfaces*"]),
    package_dir={"": "lib"},
    install_requires=["ops"],
)
