r'''
# Zeroscaler CDK TypeScript Construct Library project

[![npm version](https://badge.fury.io/js/@zeroscaler%2Fzeroscaler-cdk.svg)](https://badge.fury.io/js/@zeroscaler%2Fzeroscaler-cdk)
[![PyPI version](https://badge.fury.io/py/zeroscaler.svg)](https://badge.fury.io/py/zeroscaler)
[![NuGet version](https://badge.fury.io/nu/ZeroScalerCDK.svg)](https://badge.fury.io/nu/ZeroScalerCDK)
[![Go project version](https://badge.fury.io/go/github.com%2Flephyrius%2Fzeroscaler.svg)](https://pkg.go.dev/github.com/lephyrius/zeroscaler/zeroscaler)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.8+-blue.svg)](https://www.typescriptlang.org/)
[![AWS CDK](https://img.shields.io/badge/AWS%20CDK-2.0+-orange.svg)](https://aws.amazon.com/cdk/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)
[![License: MPL 2.0](https://img.shields.io/badge/License-MPL%202.0-brightgreen.svg)](https://opensource.org/licenses/MPL-2.0)

*The Zeroscaler construct* deploys a Lambda function that automatically starts your Fargate application in response to incoming requests. It also handles health monitoring and integrates with an ELB target group.

You can configure the construct using the (`ZeroscalerProps`) interface, which requires a target group ARN and Fargate task ARN. Optionally, you can also specify a custom VPC and ECS cluster.

## Useful commands

* `npm run build`   compile typescript to js
* `npm run watch`   watch for changes and compile
* `npm run test`    perform the jest unit tests

## Diagram of the Construct

```mermaid
flowchart TD
    A["Client"] L_A_B_0@-- HTTP Request --> B["Zeroscaler"]
    B -. Register Target .-> C["ELB Target Group"]
    B L_B_A_0@-- Serve HTML with refresh --> A
    C -- Health Check --> D["ECS Fargate"]
    D -- Boot --> E["Your Fargate Application"]
    A L_A_E_0@-- Refresh when booted --> E
    E L_E_A_0@-- Response --> A
    linkStyle 0 stroke:#00C853,fill:none
    linkStyle 1 stroke:#AA00FF,fill:none
    linkStyle 2 stroke:#00C853,fill:none
    linkStyle 3 stroke:#AA00FF,fill:none
    linkStyle 4 stroke:#AA00FF,fill:none
    linkStyle 5 stroke:#2962FF,fill:none
    linkStyle 6 stroke:#2962FF,fill:none
    L_A_B_0@{ animation: fast }
    L_B_A_0@{ animation: fast }
    L_A_E_0@{ animation: fast }
    L_E_A_0@{ animation: fast }
```

## Installation

```bash
npm install @zeroscaler/zeroscaler-cdk
```

## Usage

```python
import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { ZeroScaler } from '@zeroscaler/zeroscaler-cdk';

new Zeroscaler(stack, 'MyZeroscaler', {
    targetGroupArn: 'arn:aws:elasticloadbalancing:...',
    fargateTaskArn: 'arn:aws:ecs:...',
    // Optionally override vpc or cluster
    });
```

## License

MPL-2.0
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

import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_ecs as _aws_cdk_aws_ecs_ceddda9d
import constructs as _constructs_77d1e7e8


class Zeroscaler(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@zeroscaler/zeroscaler-cdk.Zeroscaler",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        cluster: _aws_cdk_aws_ecs_ceddda9d.ICluster,
        fargate_task_arn: builtins.str,
        target_group_arn: builtins.str,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        refresh_delay: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cluster: 
        :param fargate_task_arn: 
        :param target_group_arn: 
        :param vpc: 
        :param refresh_delay: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5509862cee0447c28875cdfa91e958949315c09d3390db36a9d3c4f6963a542)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ZeroscalerProps(
            cluster=cluster,
            fargate_task_arn=fargate_task_arn,
            target_group_arn=target_group_arn,
            vpc=vpc,
            refresh_delay=refresh_delay,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@zeroscaler/zeroscaler-cdk.ZeroscalerProps",
    jsii_struct_bases=[],
    name_mapping={
        "cluster": "cluster",
        "fargate_task_arn": "fargateTaskArn",
        "target_group_arn": "targetGroupArn",
        "vpc": "vpc",
        "refresh_delay": "refreshDelay",
    },
)
class ZeroscalerProps:
    def __init__(
        self,
        *,
        cluster: _aws_cdk_aws_ecs_ceddda9d.ICluster,
        fargate_task_arn: builtins.str,
        target_group_arn: builtins.str,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        refresh_delay: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param cluster: 
        :param fargate_task_arn: 
        :param target_group_arn: 
        :param vpc: 
        :param refresh_delay: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a085c2326d35c7fcd28239e48615fbad3f131d188dac5e7a70a05e16f61c340)
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
            check_type(argname="argument fargate_task_arn", value=fargate_task_arn, expected_type=type_hints["fargate_task_arn"])
            check_type(argname="argument target_group_arn", value=target_group_arn, expected_type=type_hints["target_group_arn"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument refresh_delay", value=refresh_delay, expected_type=type_hints["refresh_delay"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cluster": cluster,
            "fargate_task_arn": fargate_task_arn,
            "target_group_arn": target_group_arn,
            "vpc": vpc,
        }
        if refresh_delay is not None:
            self._values["refresh_delay"] = refresh_delay

    @builtins.property
    def cluster(self) -> _aws_cdk_aws_ecs_ceddda9d.ICluster:
        result = self._values.get("cluster")
        assert result is not None, "Required property 'cluster' is missing"
        return typing.cast(_aws_cdk_aws_ecs_ceddda9d.ICluster, result)

    @builtins.property
    def fargate_task_arn(self) -> builtins.str:
        result = self._values.get("fargate_task_arn")
        assert result is not None, "Required property 'fargate_task_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_group_arn(self) -> builtins.str:
        result = self._values.get("target_group_arn")
        assert result is not None, "Required property 'target_group_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    @builtins.property
    def refresh_delay(self) -> typing.Optional[builtins.str]:
        result = self._values.get("refresh_delay")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZeroscalerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Zeroscaler",
    "ZeroscalerProps",
]

publication.publish()

def _typecheckingstub__a5509862cee0447c28875cdfa91e958949315c09d3390db36a9d3c4f6963a542(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    cluster: _aws_cdk_aws_ecs_ceddda9d.ICluster,
    fargate_task_arn: builtins.str,
    target_group_arn: builtins.str,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    refresh_delay: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a085c2326d35c7fcd28239e48615fbad3f131d188dac5e7a70a05e16f61c340(
    *,
    cluster: _aws_cdk_aws_ecs_ceddda9d.ICluster,
    fargate_task_arn: builtins.str,
    target_group_arn: builtins.str,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    refresh_delay: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
