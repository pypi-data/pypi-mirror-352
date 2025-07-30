import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "zeroscaler",
    "version": "0.1.5",
    "description": "AWS CDK constructs for ZeroScaler.io",
    "license": "MPL-2.0",
    "url": "https://zeroscaler.io",
    "long_description_content_type": "text/markdown",
    "author": "Jonas Innala",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/lephyrius/zeroscaler.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk",
        "cdk._jsii"
    ],
    "package_data": {
        "cdk._jsii": [
            "zeroscaler-cdk@0.1.5.jsii.tgz"
        ],
        "cdk": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "aws-cdk-lib>=2.0.0, <3.0.0",
        "constructs>=10.0.0, <11.0.0",
        "jsii>=1.112.0, <2.0.0",
        "publication>=0.0.3",
        "typeguard>=2.13.3,<4.3.0"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Typing :: Typed",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
