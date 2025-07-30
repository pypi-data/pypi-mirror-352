import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "moia-dev.bastion-host-forward",
    "version": "2.4.2",
    "description": "CDK Construct for creating a bastion host to forward a connection to several AWS data services inside a private subnet from your local machine",
    "license": "Apache-2.0",
    "url": "https://github.com/moia-oss/bastion-host-forward",
    "long_description_content_type": "text/markdown",
    "author": "MOIA GmbH",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/moia-oss/bastion-host-forward"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "moia_dev.bastion_host_forward",
        "moia_dev.bastion_host_forward._jsii"
    ],
    "package_data": {
        "moia_dev.bastion_host_forward._jsii": [
            "bastion-host-forward@2.4.2.jsii.tgz"
        ],
        "moia_dev.bastion_host_forward": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "aws-cdk-lib>=2.121.1, <3.0.0",
        "constructs>=10.3.0, <11.0.0",
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
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
