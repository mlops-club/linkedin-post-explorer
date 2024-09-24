import aws_cdk as cdk
from aws_cdk import Stack  # Duration,; aws_sqs as sqs,
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_lambda_python_alpha as lambda_python
from aws_cdk import aws_s3 as s3
from aws_cdk.aws_ecr_assets import DockerImageAsset
from constructs import Construct


class LinkedinPostExplorerStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket = s3.Bucket(
            self,
            "LinkedinPostExplorerBucket",
        )

        fn = lambda_python.PythonFunction(
            self,
            "LinkedinPostExplorerLambda",
            entry="assets/linkedin-post-explorer-api/src",
            index="linkedin_post_explorer/aws_lambda_handler.py",
            handler="handler",
            runtime=_lambda.Runtime.PYTHON_3_11,
            architecture=_lambda.Architecture.X86_64,
            environment={
                "BUCKET_NAME": bucket.bucket_name,
            },
            layers=[
                lambda_python.PythonLayerVersion(
                    self,
                    "LinkedinPostExplorerLayer",
                    entry="assets/linkedin-post-explorer-api/",
                    compatible_runtimes=[_lambda.Runtime.PYTHON_3_11],
                    compatible_architectures=[_lambda.Architecture.X86_64],
                    bundling=lambda_python.BundlingOptions(
                        image=cdk.DockerImage.from_registry("public.ecr.aws/lambda/python:3.11"),
                        platform="linux/amd64",
                        entrypoint=[
                            "bash",
                            "-c",
                            "pip install -r requirements.txt -t /asset-output/python && cp -au . /asset-output/python",
                        ],
                    ),
                )
            ],
        )

        bucket.grant_read_write(fn.role)


# new python.PythonFunction(this, 'MyFunction', {
#   entry: '/path/to/my/function', // required
#   runtime: Runtime.PYTHON_3_8, // required
#   index: 'my_index.py', // optional, defaults to 'index.py'
#   handler: 'my_exported_func', // optional, defaults to 'handler'
# });
