r'''
# Azure DevOps Git Repository Archiver

The documentation is available [here](https://stefanfreitag.github.io/azure_s3_repository_archiver/).

## How to contribute

* See [CONTRIBUTING.md](CONTRIBUTING.md) for how to contribute to this project.
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

import aws_cdk.aws_events as _aws_cdk_aws_events_ceddda9d
import aws_cdk.aws_kms as _aws_cdk_aws_kms_ceddda9d
import aws_cdk.aws_logs as _aws_cdk_aws_logs_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import aws_cdk.aws_sns as _aws_cdk_aws_sns_ceddda9d
import constructs as _constructs_77d1e7e8


class Archiver(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="azure-devops-repository-archiver.Archiver",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        backup_configurations: typing.Sequence[typing.Union["BackupConfiguration", typing.Dict[builtins.str, typing.Any]]],
        notification_events: typing.Optional[typing.Sequence[_aws_cdk_aws_s3_ceddda9d.EventType]] = None,
        retention_days: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param backup_configurations: Contains details on the git repositories to be backed up.
        :param notification_events: S3 events that will trigger a message to the SNS topic. For example "EventType.LIFECYCLE_EXPIRATION" or "EventType.OBJECT_CREATED".
        :param retention_days: The number of days to keep the Cloudwatch logs. Default: RetentionDays.ONE_MONTH
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__59b1d445ea6a4ea2b344c5e83eb14b7e5d57e243d55dbad607605e1e2e63c1b5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ArchiverProperties(
            backup_configurations=backup_configurations,
            notification_events=notification_events,
            retention_days=retention_days,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> _aws_cdk_aws_s3_ceddda9d.Bucket:
        '''The S3 bucket used to store the git repositories archive.

        :memberof: Archiver
        :type: {s3.Bucket}
        '''
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.Bucket, jsii.get(self, "bucket"))

    @bucket.setter
    def bucket(self, value: _aws_cdk_aws_s3_ceddda9d.Bucket) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a6323f8f3cdbd2b11e534f545ef6432e903b1c3129b74f986595de806512f745)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bucket", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="kmsKey")
    def kms_key(self) -> _aws_cdk_aws_kms_ceddda9d.Key:
        '''The KMS key used to encrypt the logs and the SNS topic.

        :memberof: Archiver
        :type: {kms.Key}
        '''
        return typing.cast(_aws_cdk_aws_kms_ceddda9d.Key, jsii.get(self, "kmsKey"))

    @kms_key.setter
    def kms_key(self, value: _aws_cdk_aws_kms_ceddda9d.Key) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c36f29d0f7853cd545faec426b34c1244d318c139f2dffe55decab75b8bed45)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "kmsKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logGroup")
    def log_group(self) -> _aws_cdk_aws_logs_ceddda9d.LogGroup:
        '''Log group used by the CodeBuild projects.

        :memberof: Archiver
        :type: {LogGroup}
        '''
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.LogGroup, jsii.get(self, "logGroup"))

    @log_group.setter
    def log_group(self, value: _aws_cdk_aws_logs_ceddda9d.LogGroup) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9bb1a921963ed134fd11e5243da72c17693bf46b95bcb2787c98f86c2344cac1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logGroup", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="props")
    def props(self) -> "ArchiverProperties":
        return typing.cast("ArchiverProperties", jsii.get(self, "props"))

    @props.setter
    def props(self, value: "ArchiverProperties") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb1dff6681014d6e509e01d6b12c3974e4810c8d1a67b368174954a280d668f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "props", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="topic")
    def topic(self) -> _aws_cdk_aws_sns_ceddda9d.Topic:
        '''SNS topic to send configured bucket events to.

        :memberof: Archiver
        :type: {sns.Topic}
        '''
        return typing.cast(_aws_cdk_aws_sns_ceddda9d.Topic, jsii.get(self, "topic"))

    @topic.setter
    def topic(self, value: _aws_cdk_aws_sns_ceddda9d.Topic) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9dd4ea8c9e2284178c61c09574e728813a93f8d586a9e4839a680d1edf560c3a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "topic", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="azure-devops-repository-archiver.ArchiverProperties",
    jsii_struct_bases=[],
    name_mapping={
        "backup_configurations": "backupConfigurations",
        "notification_events": "notificationEvents",
        "retention_days": "retentionDays",
    },
)
class ArchiverProperties:
    def __init__(
        self,
        *,
        backup_configurations: typing.Sequence[typing.Union["BackupConfiguration", typing.Dict[builtins.str, typing.Any]]],
        notification_events: typing.Optional[typing.Sequence[_aws_cdk_aws_s3_ceddda9d.EventType]] = None,
        retention_days: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    ) -> None:
        '''
        :param backup_configurations: Contains details on the git repositories to be backed up.
        :param notification_events: S3 events that will trigger a message to the SNS topic. For example "EventType.LIFECYCLE_EXPIRATION" or "EventType.OBJECT_CREATED".
        :param retention_days: The number of days to keep the Cloudwatch logs. Default: RetentionDays.ONE_MONTH
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bfaace2f4df93a4fab67f960625a0f4057a1c4ba23833a63c0ffee999a9a724d)
            check_type(argname="argument backup_configurations", value=backup_configurations, expected_type=type_hints["backup_configurations"])
            check_type(argname="argument notification_events", value=notification_events, expected_type=type_hints["notification_events"])
            check_type(argname="argument retention_days", value=retention_days, expected_type=type_hints["retention_days"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "backup_configurations": backup_configurations,
        }
        if notification_events is not None:
            self._values["notification_events"] = notification_events
        if retention_days is not None:
            self._values["retention_days"] = retention_days

    @builtins.property
    def backup_configurations(self) -> typing.List["BackupConfiguration"]:
        '''Contains details on the git repositories to be backed up.

        :memberof: ArchiverProperties
        :type: {BackupConfiguration[]}
        '''
        result = self._values.get("backup_configurations")
        assert result is not None, "Required property 'backup_configurations' is missing"
        return typing.cast(typing.List["BackupConfiguration"], result)

    @builtins.property
    def notification_events(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.EventType]]:
        '''S3 events that will trigger a message to the SNS topic.

        For example
        "EventType.LIFECYCLE_EXPIRATION" or "EventType.OBJECT_CREATED".

        :memberof: ArchiverProperties
        :type: {s3.EventType[]}
        '''
        result = self._values.get("notification_events")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.EventType]], result)

    @builtins.property
    def retention_days(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays]:
        '''The number of days to keep the Cloudwatch logs.

        :default: RetentionDays.ONE_MONTH

        :memberof: ArchiverProperties
        :type: {RetentionDays}
        '''
        result = self._values.get("retention_days")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ArchiverProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="azure-devops-repository-archiver.BackupConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "organization_name": "organizationName",
        "project_name": "projectName",
        "repository_names": "repositoryNames",
        "secret_arn": "secretArn",
        "schedule": "schedule",
    },
)
class BackupConfiguration:
    def __init__(
        self,
        *,
        organization_name: builtins.str,
        project_name: builtins.str,
        repository_names: typing.Sequence[builtins.str],
        secret_arn: builtins.str,
        schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
    ) -> None:
        '''A backup configuration defining - the repositories to backup, and  - the backup interval All repositories that are part of a backup configuration are belonging to the same Azure DevOps organization and project.

        :param organization_name: The name of the Azure DevOps organization.
        :param project_name: The name of the Azure DevOps project.
        :param repository_names: The names of the git repositories to backup.
        :param secret_arn: ARN of the secret containing the token for accessing the git repositories of the Azure DevOps organization.
        :param schedule: The schedule allows to define the frequency of backups. If not defined, a weekly backup is configured. Default: Schedule.expression('cron(0 0 ? * 1 *)')

        :export: true
        :interface: BackupConfiguration
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73a3057dbc68fd09362014a7e60186c3a5a6831c5a676af4878318e4f1323881)
            check_type(argname="argument organization_name", value=organization_name, expected_type=type_hints["organization_name"])
            check_type(argname="argument project_name", value=project_name, expected_type=type_hints["project_name"])
            check_type(argname="argument repository_names", value=repository_names, expected_type=type_hints["repository_names"])
            check_type(argname="argument secret_arn", value=secret_arn, expected_type=type_hints["secret_arn"])
            check_type(argname="argument schedule", value=schedule, expected_type=type_hints["schedule"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "organization_name": organization_name,
            "project_name": project_name,
            "repository_names": repository_names,
            "secret_arn": secret_arn,
        }
        if schedule is not None:
            self._values["schedule"] = schedule

    @builtins.property
    def organization_name(self) -> builtins.str:
        '''The name of the Azure DevOps organization.

        :memberof: BackupConfiguration
        :type: {string}
        '''
        result = self._values.get("organization_name")
        assert result is not None, "Required property 'organization_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def project_name(self) -> builtins.str:
        '''The name of the Azure DevOps project.

        :memberof: BackupConfiguration
        :type: {string}
        '''
        result = self._values.get("project_name")
        assert result is not None, "Required property 'project_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository_names(self) -> typing.List[builtins.str]:
        '''The names of the git repositories to backup.

        :memberof: BackupConfiguration
        :type: {string[]}
        '''
        result = self._values.get("repository_names")
        assert result is not None, "Required property 'repository_names' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def secret_arn(self) -> builtins.str:
        '''ARN of the secret containing the token for accessing the git repositories of the Azure DevOps organization.

        :memberof: BackupConfiguration
        :type: {string}
        '''
        result = self._values.get("secret_arn")
        assert result is not None, "Required property 'secret_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def schedule(self) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule]:
        '''The schedule allows to define the frequency of backups.

        If not defined, a weekly backup is configured.

        :default: Schedule.expression('cron(0 0 ? * 1 *)')

        :memberof: BackupConfiguration
        :type: {Schedule}
        '''
        result = self._values.get("schedule")
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BackupConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Archiver",
    "ArchiverProperties",
    "BackupConfiguration",
]

publication.publish()

def _typecheckingstub__59b1d445ea6a4ea2b344c5e83eb14b7e5d57e243d55dbad607605e1e2e63c1b5(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    backup_configurations: typing.Sequence[typing.Union[BackupConfiguration, typing.Dict[builtins.str, typing.Any]]],
    notification_events: typing.Optional[typing.Sequence[_aws_cdk_aws_s3_ceddda9d.EventType]] = None,
    retention_days: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6323f8f3cdbd2b11e534f545ef6432e903b1c3129b74f986595de806512f745(
    value: _aws_cdk_aws_s3_ceddda9d.Bucket,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c36f29d0f7853cd545faec426b34c1244d318c139f2dffe55decab75b8bed45(
    value: _aws_cdk_aws_kms_ceddda9d.Key,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9bb1a921963ed134fd11e5243da72c17693bf46b95bcb2787c98f86c2344cac1(
    value: _aws_cdk_aws_logs_ceddda9d.LogGroup,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb1dff6681014d6e509e01d6b12c3974e4810c8d1a67b368174954a280d668f6(
    value: ArchiverProperties,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9dd4ea8c9e2284178c61c09574e728813a93f8d586a9e4839a680d1edf560c3a(
    value: _aws_cdk_aws_sns_ceddda9d.Topic,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bfaace2f4df93a4fab67f960625a0f4057a1c4ba23833a63c0ffee999a9a724d(
    *,
    backup_configurations: typing.Sequence[typing.Union[BackupConfiguration, typing.Dict[builtins.str, typing.Any]]],
    notification_events: typing.Optional[typing.Sequence[_aws_cdk_aws_s3_ceddda9d.EventType]] = None,
    retention_days: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73a3057dbc68fd09362014a7e60186c3a5a6831c5a676af4878318e4f1323881(
    *,
    organization_name: builtins.str,
    project_name: builtins.str,
    repository_names: typing.Sequence[builtins.str],
    secret_arn: builtins.str,
    schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
) -> None:
    """Type checking stubs"""
    pass
