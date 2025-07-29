from setuptools import setup, find_packages
from os import path

working_directory = path.abspath(path.dirname(__file__))

with open(path.join(working_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='gestao_aluguer',
    version='0.1.1',
    url='https://github.com/DasilvaCatarina/-gest-o-de-aluguer-de-im-veis',
    author='Catarina Silva,João Pedro Pinto Costa,Ana Martins,Daniel Teixeira da Silva',
    author_email='seu@email.com',
    description='Ferramenta para gestão de aluguer de imóveis.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=['pandas', 'matplotlib', 'datetime', 'tabulate'],
)