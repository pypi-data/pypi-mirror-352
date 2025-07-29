import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "ecr-scan-notifier",
    "version": "0.0.86",
    "description": "Notifies on new AWS ECR scan results",
    "license": "Apache-2.0",
    "url": "https://github.com/stefanfreitag/ecr-scan-notifier.git",
    "long_description_content_type": "text/markdown",
    "author": "Stefan Freitag<stefan.freitag@udo.edu>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/stefanfreitag/ecr-scan-notifier.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "ecr_scan_notifier",
        "ecr_scan_notifier._jsii"
    ],
    "package_data": {
        "ecr_scan_notifier._jsii": [
            "ecr-scan-notifier@0.0.86.jsii.tgz"
        ],
        "ecr_scan_notifier": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "aws-cdk-lib>=2.159.1, <3.0.0",
        "constructs>=10.0.5, <11.0.0",
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
