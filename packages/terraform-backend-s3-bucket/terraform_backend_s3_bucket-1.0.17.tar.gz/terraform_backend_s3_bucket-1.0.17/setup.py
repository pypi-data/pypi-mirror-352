import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "terraform-backend-s3-bucket",
    "version": "1.0.17",
    "description": "Creates an S3 bucket and a DynamoDB table for Terraform state and lock management.",
    "license": "Apache-2.0",
    "url": "https://github.com/stefanfreitag/terraform-backend-s3-bucket.git",
    "long_description_content_type": "text/markdown",
    "author": "Stefan Freitag<stefan.freitag@udo.edu>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/stefanfreitag/terraform-backend-s3-bucket.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "terraform_backend_s3_bucket",
        "terraform_backend_s3_bucket._jsii"
    ],
    "package_data": {
        "terraform_backend_s3_bucket._jsii": [
            "terraform-backend-s3-bucket@1.0.17.jsii.tgz"
        ],
        "terraform_backend_s3_bucket": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "aws-cdk-lib>=2.161.0, <3.0.0",
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
