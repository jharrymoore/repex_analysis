# write the setup script

from setuptools import setup, find_packages


setup(
    name="repex_analysis",
    version="0.1",
    description="repex analysis",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "mace-fep=mace_fep.entrypoint:main",
        ],
    },
)
