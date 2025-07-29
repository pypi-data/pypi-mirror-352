import setuptools
import version

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name='oidc-jwt-validation',
    version=version.VERSION,
    packages=setuptools.find_packages(exclude=["tests", "tests.*"], where='src'),
    package_dir={'': 'src'},
    install_requires=requirements,
    author="Axa_france",
    author_email="guillaume.chervet@axa.fr, guillaume.thomas@axa.fr",
    url='https://github.com/AxaGuilDEv/oidc-jwt-validation',
    description="Oidc JWT Token validation",
    long_description="You can use the Authentication class as a FastAPI Dependency, in order to validate the oidc token given in http headers :)",
    platforms='POSIX',
    classifiers=["Programming Language :: Python :: 3 :: Only",
                 "Programming Language :: Python :: 3.8",
                 "Topic :: Scientific/Engineering :: Information Analysis",
                 ]
)
