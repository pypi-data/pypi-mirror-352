from setuptools import setup, find_packages
import os

setup(
    name="limitify",
    version="0.1.0",
    description="A simple api rate-limiting library with analytics support",
    long_description=open('README.md').read() if os.path.exists('README.md') else '',
    long_description_content_type='text/markdown',
    author="Aryan KC",
    author_email="kc.aryan3536@gmail.com.com",
    url='https://github.com/Mr-Aaryan/limitify',
    packages=find_packages(),
    include_package_data=True,
    package_data={
    	'limitify':['GeoLite2-Country.mmdb'],
    },
    install_requires=[
        "httpx",
        "geoip2"
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires=">=3.13.3"
)
