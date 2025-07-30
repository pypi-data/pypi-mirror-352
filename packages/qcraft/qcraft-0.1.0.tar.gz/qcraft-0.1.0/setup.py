from setuptools import setup, find_packages

setup(
    name='qcraft',
    version='0.1.0',
    description='Qcraft: Quantum Circuit Design, Optimization, and Surface Code Mapping Platform',
    author='Your Name',
    packages=find_packages(),
    install_requires=[
        'PySide6',
        'PyYAML',
        'jsonschema',
        'qiskit',
        'networkx',
        'matplotlib',
        'numpy',
        'stable-baselines3',
        'scikit-learn',
        'pandas',
        'torch',
        'gymnasium',
        'stim',
        'pymatching',
    ],
    entry_points={
        'console_scripts': [
            'qcraft = circuit_designer.gui_main:main',
            'qcraft-train-optimize = circuit_optimization.__main__:main_optimize',
            'qcraft-train-mapper = scode.rl_agent.__main__:main_sb3',
        ],
    },
    include_package_data=True,
    package_data={
        'scode': ['code_switcher/*.py'],
        'configs': ['*.json', '*.yaml'],
    },
) 