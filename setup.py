from setuptools import find_packages, setup

setup(
    name='nanowire_network_simulator',
    version='1.0.0',
    author='Paolo Baldini',
    author_email='paolobaldini01@gmail.com',
    description='Simulator for a nanowire-network with memristive behaviour',
    url='https://github.com/Mandrab/nanowire-network-simulator',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3.9',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Artificial Life'
    ],
    packages=['nanowire_network_simulator'] + [
        'nanowire_network_simulator.' + _
        for _ in find_packages(where='nanowire_network_simulator')
    ],
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
