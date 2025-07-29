from setuptools import setup, find_packages

setup(
    name='misato',
    version='0.8.1',
    packages=find_packages(),
    install_requires=[
        'curl_cffi',
        'DrissionPage'
    ],
    entry_points={
        'console_scripts': [
            'misato=misato.main:main',
        ],
    },
    python_requires='>=3.9',
)
