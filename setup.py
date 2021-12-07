from setuptools import find_packages, setup

setup(
    name='nanowire_network_simulator',
    version='0.1.1',
    description='Simulator for a nano-wire-network',
    author='Paolo Baldini',
    author_email='paolobaldini01@gmail.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3.9',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Artificial Life'
    ],
    packages=['nanowire_network_simulator.' + _ for _ in find_packages('main')]
    + ['nanowire_network_simulator'],
    package_dir={'nanowire_network_simulator': 'main'},
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
