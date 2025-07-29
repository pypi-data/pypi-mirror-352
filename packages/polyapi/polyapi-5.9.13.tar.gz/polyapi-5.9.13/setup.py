from setuptools import find_packages, setup

classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: End Users/Desktop",
    "Operating System :: OS Independent",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
]

setup(
    name='polyapi',
    version='5.9.13',
    description='Wrapper for Polymatica API',
    long_description=open('README.txt', encoding='utf-8').read(),
    url='https://www.polymatica.ru',
    author='Polymatica Rus LLC',
    author_email='development@polymatica.com',
    license='MIT',
    classifiers=classifiers,
    keywords="polymatica",
    packages=find_packages(),
    install_requires=["setuptools", "pandas", "requests", "pydantic", "packaging"],
)
