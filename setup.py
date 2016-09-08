from setuptools import setup, find_packages

setup(
    name='secundus',
    version='0.1.dev0',
    description="Another ecs for Python, one day it'll be special",
    author="Martijn Faassen, Paul Everitt",
    author_email="faassen@startifact.com",
    license="BSD",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Programming Language :: Python :: 3.5',
    ],
    install_requires=[
        'setuptools',
        'pyglet',
        'dectate',
        'pandas',
    ],
    extras_require=dict(
        test=[
            'pytest >= 2.5.2',
            'py >= 1.4.20',
            'pytest-cov',
            'pytest-remove-stale-bytecode',
        ],
    ),
)
