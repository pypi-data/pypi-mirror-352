from setuptools import setup, find_packages

setup(
    name='licelfile',
    version='0.1.0',
    description='Package that reads and writes licel lidar files.',
    author='Konstantin Shmirko',
    packages=find_packages(),
    install_requires=[
        # здесь перечисляются зависимости, если они нужны
    ],
    classifiers=[
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
)