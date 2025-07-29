from setuptools import setup, find_packages

setup(
    name='lbl-qubic-emulator',
    version='0.2',
    packages=find_packages(include=['emulator', 'emulator.*']),
    install_requires=[
        'numpy', 'matplotlib', 'pyvcd', 'pyyaml', 'scipy', 'qutip'
    ],
    package_dir={'': '.'},
)
