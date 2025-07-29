r'''
# Terraform Backend S3 Bucket

Provides a CDK construct for Terraform state management.

The documentation is available [here](https://stefanfreitag.github.io/terraform-backend-s3-bucket/).

## Contributing

We welcome community contributions and pull requests. See [CONTRIBUTING.md](./CONTRIBUTING.md) for
details.

## License

This project is licensed under Apache 2.0 - see the [LICENSE](./LICENSE) file for details.
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from ._jsii import *

import aws_cdk.aws_dynamodb as _aws_cdk_aws_dynamodb_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import constructs as _constructs_77d1e7e8


class TerraformStateBackend(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="terraform-backend-s3-bucket.TerraformStateBackend",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        bucket_name: builtins.str,
        table_name: builtins.str,
        table_deletion_protection: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param bucket_name: The name of the bucket to create.
        :param table_name: The name of the DynamoDB table to create.
        :param table_deletion_protection: Whether to protect the created DynamoDB table from being accidentally deleted. Default: false
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83bbb44712bab4215c0c079313514a4fafb1a8c25b8b3bff9e816e6d0ec53d3c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = TerraformStateBackendProperties(
            bucket_name=bucket_name,
            table_name=table_name,
            table_deletion_protection=table_deletion_protection,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> _aws_cdk_aws_s3_ceddda9d.IBucket:
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.IBucket, jsii.get(self, "bucket"))

    @builtins.property
    @jsii.member(jsii_name="table")
    def table(self) -> _aws_cdk_aws_dynamodb_ceddda9d.ITable:
        return typing.cast(_aws_cdk_aws_dynamodb_ceddda9d.ITable, jsii.get(self, "table"))


@jsii.data_type(
    jsii_type="terraform-backend-s3-bucket.TerraformStateBackendProperties",
    jsii_struct_bases=[],
    name_mapping={
        "bucket_name": "bucketName",
        "table_name": "tableName",
        "table_deletion_protection": "tableDeletionProtection",
    },
)
class TerraformStateBackendProperties:
    def __init__(
        self,
        *,
        bucket_name: builtins.str,
        table_name: builtins.str,
        table_deletion_protection: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param bucket_name: The name of the bucket to create.
        :param table_name: The name of the DynamoDB table to create.
        :param table_deletion_protection: Whether to protect the created DynamoDB table from being accidentally deleted. Default: false
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab43988013da6b34677c29733476fd212fa82e21bdf835a483d12aacbecd7ce7)
            check_type(argname="argument bucket_name", value=bucket_name, expected_type=type_hints["bucket_name"])
            check_type(argname="argument table_name", value=table_name, expected_type=type_hints["table_name"])
            check_type(argname="argument table_deletion_protection", value=table_deletion_protection, expected_type=type_hints["table_deletion_protection"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "bucket_name": bucket_name,
            "table_name": table_name,
        }
        if table_deletion_protection is not None:
            self._values["table_deletion_protection"] = table_deletion_protection

    @builtins.property
    def bucket_name(self) -> builtins.str:
        '''The name of the bucket to create.

        :memberof: TerraformStateBackendProperties
        :type: {string}
        '''
        result = self._values.get("bucket_name")
        assert result is not None, "Required property 'bucket_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def table_name(self) -> builtins.str:
        '''The name of the DynamoDB table to create.

        :memberof: TerraformStateBackendProperties
        :type: {string}
        '''
        result = self._values.get("table_name")
        assert result is not None, "Required property 'table_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def table_deletion_protection(self) -> typing.Optional[builtins.bool]:
        '''Whether to protect the created DynamoDB table from being accidentally deleted.

        :default: false

        :memberof: TerraformStateBackendProperties
        :type: {boolean}
        '''
        result = self._values.get("table_deletion_protection")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TerraformStateBackendProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "TerraformStateBackend",
    "TerraformStateBackendProperties",
]

publication.publish()

def _typecheckingstub__83bbb44712bab4215c0c079313514a4fafb1a8c25b8b3bff9e816e6d0ec53d3c(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    bucket_name: builtins.str,
    table_name: builtins.str,
    table_deletion_protection: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab43988013da6b34677c29733476fd212fa82e21bdf835a483d12aacbecd7ce7(
    *,
    bucket_name: builtins.str,
    table_name: builtins.str,
    table_deletion_protection: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass
