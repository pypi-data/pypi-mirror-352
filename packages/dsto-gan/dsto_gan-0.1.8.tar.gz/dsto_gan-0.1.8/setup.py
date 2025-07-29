from setuptools import setup, find_packages

# Ler o README para o PyPI
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='dsto-gan',  # Nome da sua biblioteca no PyPI
    version='0.1.8',  # Versão da sua biblioteca
    packages=find_packages(include=['dsto_gan', 'dsto_gan.*']),  # Encontra os pacotes automaticamente
    install_requires=[
    'numpy',  # Sem versão fixa (PyTorch já controla isso)
    'torch>=1.10.0',  # Mínimo garantido, sem limite superior
    'pandas>=1.3.0',
    'scikit-learn>=1.0.0',
    'xgboost>=1.5.0',  # Mínimo garantido, sem limite superior
    'scikit-optimize>=0.9.0',
],

    extras_require={  # Dependências opcionais
        'dev': [
            'pytest>=6.0',  # Para testes
            'black>=22.0',  # Para formatação de código
            'flake8>=4.0',  # Para linting
        ],
    },
    author='Erika Assis',  # Coloque seu nome aqui
    author_email='dudabh@gmail.com',  # Coloque seu email aqui
    keywords='deep smote tabular optimize gan',  # Palavras-chave para busca no PyPI
    description='Library for balancing tabular data with Deep SMOTE Optimize.',  # Descrição curta
    long_description=long_description,  # Adicionar README.md como descrição longa
    long_description_content_type='text/markdown',  # Tipo de conteúdo para renderização no PyPI
    url='https://github.com/erikaduda/dsto_gan',  # URL do repositório
    classifiers=[  # Classificação do pacote
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',  # Licença apropriada
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',  # Estágio de desenvolvimento
        'Intended Audience :: Science/Research',  # Público-alvo
        'Topic :: Scientific/Engineering :: Artificial Intelligence',  # Tópico
    ],
    python_requires='>=3.7',  # Versão mínima do Python
    include_package_data=True,  # Inclui arquivos não Python (como dados)
    package_data={  # Especifica arquivos adicionais a serem incluídos
        'dsto_gan': ['data/*.csv', 'models/*.pt'],  # Exemplo de arquivos de dados e modelos
    },
)