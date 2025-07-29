r'''
# Gradle Uploader

This CDK construct checks for new releases of the [Gradle](https://gradle.org/) build software.

The new release will be made available as copy in an S3 bucket. An information about
the new release can be sent via e-mail or via Slack.

Internally the construct uses

* an [S3](https://aws.amazon.com/s3/) bucket for storing the Gradle software
* a [Lambda](https://aws.amazon.com/lambda/) function and one Lambda layer to

  * check for the latest Gradle release
  * upload if required and notify users via [SNS](https://aws.amazon.com/sns/) and e-Mail or alternatively Slack
* a [Cloudwatch](https://aws.amazon.com/cloudwatch/) event rule to trigger the Lambda function

![Overview](docs/overview.png)

## Setup of the components

### The S3 Bucket

By default, public access to the S3 bucket is disabled. Only the access from a specific IP address (the one I got from my ISP) is allowed and ensured via [bucket policies](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-policy.html).

```javascript
  const bucket = new Bucket(this, "bucket", {
      blockPublicAccess: BlockPublicAccess.BLOCK_ALL,
      encryption: BucketEncryption.S3_MANAGED,
      publicReadAccess: false,
      versioned: false,
      removalPolicy: RemovalPolicy.DESTROY,
    });

    const bucketContentStatement = new PolicyStatement({
      effect: Effect.ALLOW,
      actions: ["s3:GetObject"],
      resources: [bucket.bucketArn + "/*"],
      principals: [new AnyPrincipal()],
    });
    bucketContentStatement.addCondition("IpAddress", {
      "aws:SourceIp": "87.122.220.125/32",
    });

    const bucketStatement: PolicyStatement = new PolicyStatement({
      effect: Effect.ALLOW,
      actions: ["s3:ListBucket", "s3:GetBucketLocation"],
      resources: [bucket.bucketArn],
      principals: [new AnyPrincipal()],
    });
    bucketStatement.addCondition("IpAddress", {
      "aws:SourceIp": "87.122.220.125/32",
    });

    const bucketPolicy = new BucketPolicy(this, "bucketPolicy", {
      bucket: bucket,
    });
```

## The Lambda function

The Lambda function is written in Python (version 3.8). The execution time is limited to five minutes and the memory consumption to 512 MByte. Additionally the function gets read/ write access to the S3 bucket and has a log retention period is set to one week.

```javascript
const fn = new Function(this, "fnUpload", {
  runtime: Runtime.PYTHON_3_8,
  description: "Download Gradle distribution to S3 bucket",
  handler: "gradleUploader.main",
  code: Code.fromAsset("./lambda/"),
  timeout: Duration.minutes(5),
  memorySize: 512,
  logRetention: RetentionDays.ONE_WEEK,
  layers: [layer],
  environment: {
    BUCKET_NAME: bucket.bucketName,
    TOPIC_ARN: topic.topicArn,
  },
});

bucket.grantReadWrite(fn);
```

If Slack is selected as notification channel, then also the `WEBHOOK_URL`
is part of the `environment`.

In the additional layer modules like boto3 are included.

```javascript
const layer = new LayerVersion(this, "GradleUploaderLayer", {
  code: Code.fromAsset(path.join(__dirname, "../layer-code")),
  compatibleRuntimes: [Runtime.PYTHON_3_8],
  license: "Apache-2.0",
  description: "A layer containing dependencies for thr Gradle Uploader",
});
```

## The Cloudwatch event rule

Every first of a month the Lambda function `fn` will be triggered automatically. That seems to be a reasonable period for the update check.

```javascript
const target = new LambdaFunction(fn);
new Rule(this, "ScheduleRule", {
  schedule: Schedule.cron({ minute: "0", hour: "0", day: "1", month: "*" }),
   targets: [target],
});
```

## Notifying about new releases

Whenever the release of a new Gradle version is detected, the stack will sent an e-mail to the list of subscriber using SNS.

```javascript
private addSubscribers(topic: Topic, subscribers:Array<string>) {
    for (var subscriber of subscribers) {
      topic.addSubscription(new EmailSubscription(subscriber));
    }
  }
```

The forwarding of information to a [Slack](https://slack.com/) channel is done from within the Lambda function.

## Testing the Python code

```shell
docker run --rm -v "$PWD":/var/task:ro,delegated   -v /home/stefan/Private/programmieren/aws/cdk/gradle_uploader/layer-code:/opt:ro,delegated  -e AWS_ACCESS_KEY_ID=XXXXXXXXXX -e AWS_SECRET_ACCESS_KEY=XXXXXXXXXX lambci/lambda:python3.8 gradleUploader.main
```

## How to use the construct in a stack

Here is an example how to use the construct:

```javascript
export class GradleUploaderStack extends Stack {
  constructor(scope: Construct, id: string) {
    super(scope, id);
    new GradleUploader(this, 'TestStack', {
      mailProperties: { subscribers: ['<e-mail address>'] },
      slackProperties: {
        webhook:
          'https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX',
      },
      whitelist: ['CIDR_1', 'CIDR_2'],
    });
  }
}

const app = new App();
new GradleUploaderStack(app, 'TestApp');
app.synth();
```

## Links

* [AWS Cloud Development Kit](https://github.com/aws/aws-cdk)
* [Gradle Homepage](https://gradle.org/)
* [boto3](https://github.com/boto/boto3)
* [Slack](https://slack.com/)
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
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.enum(jsii_type="gradle_s3_uploader.GradleDistribution")
class GradleDistribution(enum.Enum):
    '''Types of available Gradle distributions.'''

    BIN = "BIN"
    '''Binaries only.'''
    ALL = "ALL"
    '''Binaries, sources and documentation.'''
    BOTH = "BOTH"
    '''BINARY and ALL.'''


class GradleUploader(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="gradle_s3_uploader.GradleUploader",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        whitelist: typing.Sequence[builtins.str],
        distribution: typing.Optional[GradleDistribution] = None,
        mail_properties: typing.Optional[typing.Union["MailProperties", typing.Dict[builtins.str, typing.Any]]] = None,
        schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
        slack_properties: typing.Optional[typing.Union["SlackProperties", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param whitelist: 
        :param distribution: The {@link GradleDistributionGradle distribution} type to download. If no value is specified, only the binaries will be downloaded.
        :param mail_properties: Optional properties required for sending messages via mail.
        :param schedule: 
        :param slack_properties: Optional properties required for sending messages via Slack.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__810ca2b936ff9befd1e91b579eb95fdc9e6e45479db7765c74e1f5009c4fcf78)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        uploader_properties = UploaderProperties(
            whitelist=whitelist,
            distribution=distribution,
            mail_properties=mail_properties,
            schedule=schedule,
            slack_properties=slack_properties,
        )

        jsii.create(self.__class__, self, [scope, id, uploader_properties])

    @jsii.member(jsii_name="createBucket")
    def create_bucket(
        self,
        whitelist: typing.Sequence[builtins.str],
    ) -> _aws_cdk_aws_s3_ceddda9d.Bucket:
        '''
        :param whitelist: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21d6456a82860179209d1f12b62c4c4a4ecf9b505cf9b560fe5110d97d938264)
            check_type(argname="argument whitelist", value=whitelist, expected_type=type_hints["whitelist"])
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.Bucket, jsii.invoke(self, "createBucket", [whitelist]))


@jsii.data_type(
    jsii_type="gradle_s3_uploader.MailProperties",
    jsii_struct_bases=[],
    name_mapping={"subscribers": "subscribers"},
)
class MailProperties:
    def __init__(self, *, subscribers: typing.Sequence[builtins.str]) -> None:
        '''Properties related to forwarding messages via mail.

        :param subscribers: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__955e61e34828c1c736a2f0b33ce3e04310bf011e2daed09c539568cd464e2ccf)
            check_type(argname="argument subscribers", value=subscribers, expected_type=type_hints["subscribers"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "subscribers": subscribers,
        }

    @builtins.property
    def subscribers(self) -> typing.List[builtins.str]:
        result = self._values.get("subscribers")
        assert result is not None, "Required property 'subscribers' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MailProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="gradle_s3_uploader.SlackProperties",
    jsii_struct_bases=[],
    name_mapping={"webhook": "webhook"},
)
class SlackProperties:
    def __init__(self, *, webhook: builtins.str) -> None:
        '''Properties related to forwarding messages to Slack.

        :param webhook: (experimental) The Slack webhook used to send messages. Details on setting up a webhook can be found at https://api.slack.com/messaging/webhooks.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb55e77d651c029e341b370f073188ae80dad5ae911065ac03743011b5da144a)
            check_type(argname="argument webhook", value=webhook, expected_type=type_hints["webhook"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "webhook": webhook,
        }

    @builtins.property
    def webhook(self) -> builtins.str:
        '''(experimental) The Slack webhook used to send messages.

        Details on setting up a webhook can be found at https://api.slack.com/messaging/webhooks.

        :stability: experimental
        '''
        result = self._values.get("webhook")
        assert result is not None, "Required property 'webhook' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SlackProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="gradle_s3_uploader.UploaderProperties",
    jsii_struct_bases=[],
    name_mapping={
        "whitelist": "whitelist",
        "distribution": "distribution",
        "mail_properties": "mailProperties",
        "schedule": "schedule",
        "slack_properties": "slackProperties",
    },
)
class UploaderProperties:
    def __init__(
        self,
        *,
        whitelist: typing.Sequence[builtins.str],
        distribution: typing.Optional[GradleDistribution] = None,
        mail_properties: typing.Optional[typing.Union[MailProperties, typing.Dict[builtins.str, typing.Any]]] = None,
        schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
        slack_properties: typing.Optional[typing.Union[SlackProperties, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param whitelist: 
        :param distribution: The {@link GradleDistributionGradle distribution} type to download. If no value is specified, only the binaries will be downloaded.
        :param mail_properties: Optional properties required for sending messages via mail.
        :param schedule: 
        :param slack_properties: Optional properties required for sending messages via Slack.
        '''
        if isinstance(mail_properties, dict):
            mail_properties = MailProperties(**mail_properties)
        if isinstance(slack_properties, dict):
            slack_properties = SlackProperties(**slack_properties)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9260286f7de904b25faf646683c1ea17f1fb0e0046fffccbc2d5f5782a2bfa05)
            check_type(argname="argument whitelist", value=whitelist, expected_type=type_hints["whitelist"])
            check_type(argname="argument distribution", value=distribution, expected_type=type_hints["distribution"])
            check_type(argname="argument mail_properties", value=mail_properties, expected_type=type_hints["mail_properties"])
            check_type(argname="argument schedule", value=schedule, expected_type=type_hints["schedule"])
            check_type(argname="argument slack_properties", value=slack_properties, expected_type=type_hints["slack_properties"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "whitelist": whitelist,
        }
        if distribution is not None:
            self._values["distribution"] = distribution
        if mail_properties is not None:
            self._values["mail_properties"] = mail_properties
        if schedule is not None:
            self._values["schedule"] = schedule
        if slack_properties is not None:
            self._values["slack_properties"] = slack_properties

    @builtins.property
    def whitelist(self) -> typing.List[builtins.str]:
        result = self._values.get("whitelist")
        assert result is not None, "Required property 'whitelist' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def distribution(self) -> typing.Optional[GradleDistribution]:
        '''The {@link GradleDistributionGradle distribution} type to download.

        If no value is specified, only the binaries will be downloaded.
        '''
        result = self._values.get("distribution")
        return typing.cast(typing.Optional[GradleDistribution], result)

    @builtins.property
    def mail_properties(self) -> typing.Optional[MailProperties]:
        '''Optional properties required for sending messages via mail.'''
        result = self._values.get("mail_properties")
        return typing.cast(typing.Optional[MailProperties], result)

    @builtins.property
    def schedule(self) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule]:
        result = self._values.get("schedule")
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule], result)

    @builtins.property
    def slack_properties(self) -> typing.Optional[SlackProperties]:
        '''Optional properties required for sending messages via Slack.'''
        result = self._values.get("slack_properties")
        return typing.cast(typing.Optional[SlackProperties], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "UploaderProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "GradleDistribution",
    "GradleUploader",
    "MailProperties",
    "SlackProperties",
    "UploaderProperties",
]

publication.publish()

def _typecheckingstub__810ca2b936ff9befd1e91b579eb95fdc9e6e45479db7765c74e1f5009c4fcf78(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    whitelist: typing.Sequence[builtins.str],
    distribution: typing.Optional[GradleDistribution] = None,
    mail_properties: typing.Optional[typing.Union[MailProperties, typing.Dict[builtins.str, typing.Any]]] = None,
    schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
    slack_properties: typing.Optional[typing.Union[SlackProperties, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21d6456a82860179209d1f12b62c4c4a4ecf9b505cf9b560fe5110d97d938264(
    whitelist: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__955e61e34828c1c736a2f0b33ce3e04310bf011e2daed09c539568cd464e2ccf(
    *,
    subscribers: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb55e77d651c029e341b370f073188ae80dad5ae911065ac03743011b5da144a(
    *,
    webhook: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9260286f7de904b25faf646683c1ea17f1fb0e0046fffccbc2d5f5782a2bfa05(
    *,
    whitelist: typing.Sequence[builtins.str],
    distribution: typing.Optional[GradleDistribution] = None,
    mail_properties: typing.Optional[typing.Union[MailProperties, typing.Dict[builtins.str, typing.Any]]] = None,
    schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
    slack_properties: typing.Optional[typing.Union[SlackProperties, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass
