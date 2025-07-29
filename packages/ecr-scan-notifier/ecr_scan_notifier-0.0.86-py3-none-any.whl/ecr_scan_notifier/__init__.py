r'''
# CDK ECR Scan Notifier

A CDK construct capable of forwarding ECR scan results to an SNS topic.

## Sample Events

* ECR Basic Scan

  ```json
  {
     "version":"0",
     "id":"822c3bbb-574a-8d0b-828e-b33e93cc0b3a",
     "detail-type":"ECR Image Scan",
     "source":"aws.ecr",
     "account":"012345678912",
     "time":"2022-08-03T18:14:18Z",
     "region":"eu-central-1",
     "resources":[
        "arn:aws:ecr:eu-central-1:012345678912:repository/sampleapp"
     ],
     "detail":{
        "scan-status":"COMPLETE",
        "repository-name":"sampleapp",
        "image-digest":"sha256:5b5a96370efd56ae20a832244ae56e8e57b1035f493f728eb6cef026586782f7",
        "image-tags":[
           "3862",
           "latest"
        ],
        "finding-severity-counts":{
           "HIGH":3,
           "MEDIUM":14,
           "INFORMATIONAL":3,
           "LOW":1,
           "HIGH":2
        }
     }
  }
  ```
* AWS Inspector

  ```json
  {
     "version":"0",
     "id":"961d7f4a-f46c-b376-f92f-f8c3af290f9f",
     "detail-type":"Inspector2 Scan",
     "source":"aws.inspector2",
     "account":"520666953574",
     "time":"2022-09-14T19:12:46Z",
     "region":"eu-central-1",
     "resources":[
        "arn:aws:ecr:eu-central-1:520666953574:repository/azure-agent"
     ],
     "detail":{
        "scan-status":"INITIAL_SCAN_COMPLETE",
        "repository-name":"arn:aws:ecr:eu-central-1:520666953574:repository/azure-agent",
        "finding-severity-counts":{
           "CRITICAL":0,
           "HIGH":1,
           "MEDIUM":6,
           "TOTAL":10
        },
        "image-digest":"sha256:734a4d019b381f591a63c819ae88b00eed5dba8b76626530c26497128a6c46d1",
        "image-tags":[
           "latest",
           "5715"
        ]
     }
  }
  ```

## Links

* [Image scanning](https://docs.aws.amazon.com/AmazonECR/latest/userguide/image-scanning.html)
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

import aws_cdk.aws_logs as _aws_cdk_aws_logs_ceddda9d
import constructs as _constructs_77d1e7e8


class EcrScanNotifier(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="ecr-scan-notifier.EcrScanNotifier",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        topic_arn: builtins.str,
        key_arn: typing.Optional[builtins.str] = None,
        log_retention_days: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param topic_arn: ARN of the topic to forwardd the ECR scan results to.
        :param key_arn: ARN of the topics encryption key.
        :param log_retention_days: Number of days to keep the log files. Default: RetentionDays.ONE_MONTH
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f4ee61e7424a9b9ba00b7602766deb00439c37a38ce8e922dd791716d443db97)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = EcrScanNotifierProperties(
            topic_arn=topic_arn, key_arn=key_arn, log_retention_days=log_retention_days
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="props")
    def props(self) -> "EcrScanNotifierProperties":
        return typing.cast("EcrScanNotifierProperties", jsii.get(self, "props"))

    @props.setter
    def props(self, value: "EcrScanNotifierProperties") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b02656cdb7484b23b24d63a1a35e7c4e9347d4abdf3dc4e231dd3621c68af09b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "props", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="ecr-scan-notifier.EcrScanNotifierProperties",
    jsii_struct_bases=[],
    name_mapping={
        "topic_arn": "topicArn",
        "key_arn": "keyArn",
        "log_retention_days": "logRetentionDays",
    },
)
class EcrScanNotifierProperties:
    def __init__(
        self,
        *,
        topic_arn: builtins.str,
        key_arn: typing.Optional[builtins.str] = None,
        log_retention_days: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    ) -> None:
        '''
        :param topic_arn: ARN of the topic to forwardd the ECR scan results to.
        :param key_arn: ARN of the topics encryption key.
        :param log_retention_days: Number of days to keep the log files. Default: RetentionDays.ONE_MONTH
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c67c133760c22d42a004ebc06058a50480ee911a5c55f3852536ecce6dab1643)
            check_type(argname="argument topic_arn", value=topic_arn, expected_type=type_hints["topic_arn"])
            check_type(argname="argument key_arn", value=key_arn, expected_type=type_hints["key_arn"])
            check_type(argname="argument log_retention_days", value=log_retention_days, expected_type=type_hints["log_retention_days"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "topic_arn": topic_arn,
        }
        if key_arn is not None:
            self._values["key_arn"] = key_arn
        if log_retention_days is not None:
            self._values["log_retention_days"] = log_retention_days

    @builtins.property
    def topic_arn(self) -> builtins.str:
        '''ARN of the topic to forwardd the ECR scan results to.

        :memberof: EcrScanNotifierProperties
        :type: {string}
        '''
        result = self._values.get("topic_arn")
        assert result is not None, "Required property 'topic_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def key_arn(self) -> typing.Optional[builtins.str]:
        '''ARN of the topics encryption key.

        :memberof: EcrScanNotifierProperties
        :type: {string}
        '''
        result = self._values.get("key_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_retention_days(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays]:
        '''Number of days to keep the log files.

        :default: RetentionDays.ONE_MONTH

        :memberof: EcrScanNotifierProperties
        :type: {RetentionDays}
        '''
        result = self._values.get("log_retention_days")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EcrScanNotifierProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "EcrScanNotifier",
    "EcrScanNotifierProperties",
]

publication.publish()

def _typecheckingstub__f4ee61e7424a9b9ba00b7602766deb00439c37a38ce8e922dd791716d443db97(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    topic_arn: builtins.str,
    key_arn: typing.Optional[builtins.str] = None,
    log_retention_days: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b02656cdb7484b23b24d63a1a35e7c4e9347d4abdf3dc4e231dd3621c68af09b(
    value: EcrScanNotifierProperties,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c67c133760c22d42a004ebc06058a50480ee911a5c55f3852536ecce6dab1643(
    *,
    topic_arn: builtins.str,
    key_arn: typing.Optional[builtins.str] = None,
    log_retention_days: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
) -> None:
    """Type checking stubs"""
    pass
