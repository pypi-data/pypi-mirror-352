from setuptools import setup, find_packages

setup(
    name='gradio_themes_red',
    version='1.0.0',
    license="MIT",  # Especifica la licencia directamente
    include_package_data=True,  # ← Añade esta línea
    author='IA (Sistema de Intres)',
    author_email='system.ai.of.interest@gmail.com',
    description='Esta librería fue creada por IA Sistema de Intres pro',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://www.youtube.com/@IA.Sistema.de.Interes',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        'requests',
        'tqdm',
        'Pillow',
        'IPython',
    ],
)

