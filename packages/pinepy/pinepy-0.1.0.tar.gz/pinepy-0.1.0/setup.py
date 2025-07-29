from setuptools import find_packages, setup

setup(
    name="pinepy",
    version="0.0.1",
    description="python backtest and live trading framework, make strategy looks like pine script",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "polars>=1.29.0",
        "talipp>=2.5.0",
    ],
)
