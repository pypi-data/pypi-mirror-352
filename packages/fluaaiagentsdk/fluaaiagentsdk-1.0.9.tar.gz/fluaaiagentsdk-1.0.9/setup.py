from setuptools import setup
import setuptools

# Use a string direta para o README em vez de ler o arquivo
long_description = """
# SDK de Agentes Fluaai

SDK em Python para interagir com a API de Agentes da Fluaai, oferecendo integração simples com LLMs e operadores, suporte a streaming, e respostas estruturadas em classes tipadas.

## Funcionalidades

- Invocação de agentes LLM e Operador
- Streaming em tempo real de respostas
- Tratamento consistente de diferentes engines
- Respostas tipadas com classes ou compatíveis com JSON
- Suporte a ferramentas e processamento de conversas

*1.0.9 - New Parameter debug
*1.0.8 - Fix :)
*1.0.7 - Refactor
*1.0.6 - Fix & Simplificação das variáveis dinâmicas.
*1.0.5 - Atualização de serviço.
*1.0.4 - Introdução das variáveis dinâmicas (dynamic_variables).
*1.0.3 - Suporte a identificação de "channel" para registro de monitoramento dos seus agentes!
"""

# Ler requirements.txt
try:
    with open("requirements.txt", "r", encoding="utf-8") as f:
        requirements = f.read().splitlines()
except:
    # Fallback se não conseguir ler o arquivo
    requirements = ["aiohttp>=3.8.0", "typing-extensions>=4.0.0"]

setup(
    name="fluaaiagentsdk",
    version="1.0.9",
    author="Gabriel Fraga",
    author_email="gabriellff130@gmail.com",
    description="SDK para integração com agentes da plataforma FluaAI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GabrielFragaM/fluaai-agent-sdk",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
)