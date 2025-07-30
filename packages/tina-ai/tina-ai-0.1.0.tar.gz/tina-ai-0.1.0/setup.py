# setup.py
from setuptools import setup, find_packages

setup(
    name='tina-ai',
    version='0.1.0',
    description='Biblioteca Python para interação com a IA Tina',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Eliobros Tech',
    author_email='contato@eliobros.co.mz',
    url='https://github.com/Habibo017/tina-ai-py',  # Coloque seu GitHub se tiver
    packages=find_packages(),
    install_requires=['requests'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
