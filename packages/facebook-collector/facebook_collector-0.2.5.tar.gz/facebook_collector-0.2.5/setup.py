from setuptools import setup, find_packages

setup(
    name="facebook_collector",
    version="0.2.5",
    description="A Python library for collecting data from Facebook using Selenium and GraphQL",
    author="Vu Dinh",
    author_email="vu.dinh@hiip.asia",
    packages=find_packages(),
    install_requires=[
        "selenium",
        "requests",
        "webdriver-manager>=3.8.0",
        "python-dotenv>=0.19.0",
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "pytz>=2021.1",
        "sqlalchemy>=1.4.0",
        "openpyxl>=3.0.0",
    ],
    python_requires=">=3.7",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
