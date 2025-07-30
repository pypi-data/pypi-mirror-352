from setuptools import setup, find_packages

setup(
    name='pandas-toolkit-bharath',  # 👈 UNIQUE name
    version='0.1.0',
    description='Simplified Pandas data preprocessing with menu-based interaction',
    author='Bharath Kumar',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'scikit-learn'
    ],
    python_requires='>=3.7',
)
