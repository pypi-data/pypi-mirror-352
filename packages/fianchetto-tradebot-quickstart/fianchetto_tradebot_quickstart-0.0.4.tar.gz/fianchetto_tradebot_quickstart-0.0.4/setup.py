from setuptools import setup, find_packages

setup(
    name='fianchetto-tradebot-quickstart',
    version='0.0.4',
    author='Fianchetto Labs',
    author_email='aleks@fianchettolabs.com',
    description='Example of using the Fianchetto Tradebot Library interacting with brokerages',
    url='https://github.com/fianchetto-labs/tradebot-quickstart',
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'Topic :: Office/Business :: Financial :: Investment',
    ],
    python_requires='>=3.6',
    include_package_data=True,
    install_requires=[
        'flask',
        'pandas',
        'pydantic',
        'pygments',
        'python-dateutil',
        'pytz',
        'rauth',
        'sortedcontainers',
        'fianchetto-tradebot'
    ],
    extras_require={
        'dev': ['pytest']
    },
    keywords='trading bot api brokerage finance automation',
)
