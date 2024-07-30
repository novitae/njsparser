from setuptools import setup, find_packages

setup(
    name='njsparser',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'lxml',
        'ujson',
    ],
    author='novitae',
    description='A Python NextJS data parser from HTML',
    url='https://github.com/novitae/njsparser',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.10',
)
