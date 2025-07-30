from setuptools import setup, find_packages
from pathlib import Path

def read_requirements(file_path):
    return Path(file_path).read_text().splitlines()

# Base requirements
base_requirements = read_requirements('requirements/base.txt')

# Optional feature requirements
extras = {
    'openai': read_requirements('requirements/openai_requirements.txt'),
    'anthropic': read_requirements('requirements/anthropic_requirements.txt'),
    'huggingface': read_requirements('requirements/huggingface_requirements.txt'),
    'fireworks': read_requirements('requirements/fireworks_requirements.txt'),
    'ollama': read_requirements('requirements/ollama_requirements.txt'),
    'vllm': read_requirements('requirements/openai_requirements.txt'),
    'deepseek': read_requirements('requirements/openai_requirements.txt')
}

# Combined install for "all" optional features
extras['all'] = sorted(set(req for group in extras.values() for req in group))

setup(
    name='ecq_llmfactory',
    version='0.1.20',
    description='LLMFactory is a modular framework built on LangChain...',
    long_description=Path('README.md').read_text(),
    long_description_content_type='text/markdown',
    author='Linh Vo',
    author_email='linh.vo@e-cq.net',
    url='https://kappa.e-cq.net/linh.vo/llmfactory',
    packages=find_packages(),
    install_requires=base_requirements,
    extras_require=extras,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',
)
