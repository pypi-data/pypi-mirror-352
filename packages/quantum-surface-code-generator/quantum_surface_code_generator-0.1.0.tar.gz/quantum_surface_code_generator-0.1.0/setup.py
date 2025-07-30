from setuptools import setup, find_packages

setup(
    name='quantum_surface_code_generator',
    version='0.1.0',
    description='Quantum Surface Code Generator using RL with GUI',
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
            'quantum-gui = circuit_designer.gui_main:main',
            'quantum-train = scode.rl_agent.__main__:main_sb3',
        ],
    },
    include_package_data=True,
    package_data={
        'scode': ['code_switcher/*.py'],
    },
) 