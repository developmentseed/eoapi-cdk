"""Setup stac_fastapi
Based on https://github.com/developmentseed/eoAPI/tree/master/src/eoapi/stac
"""

from setuptools import find_namespace_packages, setup

# TODO: add long description
# with open("README.md") as f:
#     long_description = f.read()

inst_reqs = [
    "mangum~=0.15",
    "stac-fastapi.api~=2.4",
    "stac-fastapi.extensions~=2.4",
    "stac-fastapi.pgstac~=2.4",    
    "stac-fastapi.types~=2.4",
    "jinja2>=2.11.2,<4.0.0",
    "importlib_resources>=1.1.0;python_version<'3.9'",
    "pygeoif<=0.8",  # newest release (1.0+ / 09-22-2022) breaks a number of other geo libs
    "aws-lambda-powertools>=1.18.0",
    "aws_xray_sdk>=2.6.0,<3",
    "starlette-cramjam>=0.1.0.a0,<0.2"    
]

extra_reqs = {
    "test": ["pytest", "pytest-cov", "pytest-asyncio", "requests"],
}


setup(
    name="stac_api",
    description="",
    python_requires=">=3.7",
    packages=find_namespace_packages(exclude=["tests*"]),
    # package_data={"veda": ["stac/templates/*.html"]},
    include_package_data=True,
    zip_safe=False,
    install_requires=inst_reqs,
    extras_require=extra_reqs,
)
