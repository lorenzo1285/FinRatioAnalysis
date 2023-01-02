
from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.7'
DESCRIPTION = 'Quantitative Finance Ratio Analysis'
LONG_DESCRIPTION = 'Package that allows analyse the fundamentals of yahoo finance tickers'

# Setting up
setup(
    name="FinRatioAnalysis",
    version=VERSION,
    author="Lorenzo Cárdenas Cárdenas",
    author_email="<lorenzo_cardenas@msn.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    license='MIT',
    packages=find_packages(),
    install_requires=[  'yfinance', 
                        'numpy',
                        'pandas',
                        'pandas_datareader',
                        'plotly',
                   ],
    keywords=['python', 'finance', 'quantitative analysis', 'fundamental analysis', 'portfolio'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)