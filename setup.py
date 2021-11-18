from setuptools import find_packages, setup

setup(
    name='nanowire_network_simulator',
    packages=find_packages(include=['nanowire_network_simulator']),
    version='0.1.0',
    description='Simulator for a nanowire-network',
    author='Paolo Baldini',
    # license='MIT',
    install_requires=[
        'numpy',
        'networkx',
        'scipy',
        'matplotlib'
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest>=4.4.1'],
    test_suite='tests',
)
