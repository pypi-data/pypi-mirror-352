from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='synapse-memory',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'sentence-transformers',
        'numpy',
        'chromadb',
    ],
    author='kamome', # 作者名をkamomeに変更
    description='An experience-based memory system for AI, leveraging SQLite and ChromaDB.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/kamome1108/synapse_memory',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'License :: Other/Proprietary License', # BUSLは通常、OSI承認ではないためこの分類を使用
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    python_requires='>=3.9',
    keywords='ai memory agent sqlite chromadb embeddings',
)
