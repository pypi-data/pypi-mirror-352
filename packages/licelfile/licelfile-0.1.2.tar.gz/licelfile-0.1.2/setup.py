from setuptools import setup, find_packages
from os.path import dirname, join

# Открытие и чтение файла README.md
with open(join(dirname(__file__), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()




setup(
    name='licelfile',
    version='0.1.2',
    description='Package that reads and writes licel lidar files.',
    long_description=long_description, 
    long_description_content_type='text/markdown',  
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