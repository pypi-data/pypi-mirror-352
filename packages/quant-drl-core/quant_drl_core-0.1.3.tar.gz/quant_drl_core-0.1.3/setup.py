from setuptools import find_packages, setup

setup(
    name="quant_drl",
    version="0.1.0",
    description="Deep Reinforcement Learning for Financial Portfolio Management",
    author="Pablo Diego Acosta",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "numpy>=2.00",
        "pandas>=2.2.3",
        "gym>=0.23.0",
        "matplotlib>=3.9.0",
        "stable-baselines3>=2.5.0",
        "scikit-learn>=1.6.1",
        "loguru>=0.7.3",
        "tqdm>=4.66.1",
        "tensorflow>=2.18.0",
        "torch==2.6.0",
        "plotly==6.0.0",
        "seaborn>=0.13.2",
        "yfinance>=0.2.54",
        "ta>=0.11.0",
        "pandas_market_calendars>=4.6.0",
        "tensorboard>=2.18.0"
    ],
    include_package_data=True,
)
