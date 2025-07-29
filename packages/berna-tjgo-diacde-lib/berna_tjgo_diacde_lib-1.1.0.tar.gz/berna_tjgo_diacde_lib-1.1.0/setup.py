'''
Created on Sun Jul 21 09:54:07 2024

@authors:
    Antonio Pires
    Milton Ávila
    João Gabriel
    Wesley Oliveira

@License:
Este projeto está licenciado sob a Licença Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0). Você pode compartilhar, adaptar e construir sobre o material, desde que atribua crédito apropriado, não use o material para fins comerciais e distribua suas contribuições sob a mesma licença.
Para mais informações, consulte o arquivo [LICENSE](./LICENSE).
'''
from setuptools import setup, find_packages

with open('berna_tjgo_diacde_lib/README.md', 'r', encoding='utf-8') as f:
    description = f.read()

setup(
    name='berna_tjgo_diacde_lib',
    version='1.1.0',
    author='DIACDE - TJGO',
    python_requires=">=3.9.4",
    requirements=[
        'pandas', 
        'spacy',
        'nltk', 
    ],
    license='Attribution-NonCommercial-ShareAlike',
    packages=find_packages(),
    long_description=description,
    long_description_content_type='text/markdown',
    url='https://github.com/TJGO-DIACDE/berna_tjgo_diacde_lib',
)