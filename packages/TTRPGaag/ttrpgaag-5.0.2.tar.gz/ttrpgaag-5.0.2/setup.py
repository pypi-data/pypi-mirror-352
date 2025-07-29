from setuptools import setup, find_packages


def le_arquivo(nome):
    with open(nome, 'r', encoding='utf-8') as file:
        return file.read()


setup(
    name="TTRPGaag",
    version='5.0.2',
    packages=find_packages(),
    author='Alessandro Guarita',
    description='Pacote básico de Ferramentas de RPG em português',
    long_description=le_arquivo('README.md'),
    long_description_content_type='text/markdown',
    LICENCE='MIT',
    python_requires='>=3.11',
)

