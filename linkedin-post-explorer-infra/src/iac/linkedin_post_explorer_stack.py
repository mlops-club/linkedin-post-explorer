import aws_cdk as cdk
from aws_cdk import Stack  # Duration,; aws_sqs as sqs,
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_s3_assets as s3_assets
from constructs import Construct

from pathlib import Path

THIS_DIR = Path(__file__).parent
DOCKER_IMAGE_DIR = (THIS_DIR / "../../../linkedin-post-explorer-api").resolve()
POSTS_DB_FPATH = (THIS_DIR / "../../../output/posts.db").resolve()


class LinkedinPostExplorerStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket = s3.Bucket(
            self,
            "LinkedinPostExplorerBucket",
        )

        # Upload posts.db to the S3 bucket under the 'posts' subfolder
        asset = s3_assets.Asset(self, "PostsDBAsset",
            path=str(POSTS_DB_FPATH),
        )

        # Define the Lambda function using the Docker image
        fn = _lambda.DockerImageFunction(
            self,
            "LinkedinPostExplorerLambda",
            code=_lambda.DockerImageCode.from_image_asset(directory=str(DOCKER_IMAGE_DIR)),
            environment={
                "S3_POSTS_DB_ASSET_PATH": asset.s3_object_url,
            }
        )
        url = fn.add_function_url(auth_type=_lambda.FunctionUrlAuthType.NONE)

        bucket.grant_read_write(fn.role)
        asset.grant_read(fn.role)

        # output the asset path and bucket name
        cdk.CfnOutput(self, "PostsDBAssetPath", value=asset.s3_object_url)
        cdk.CfnOutput(self, "BucketName", value=bucket.bucket_name)
        cdk.CfnOutput(self, "FunctionUrl", value=url.url)


# new python.PythonFunction(this, 'MyFunction', {
#   entry: '/path/to/my/function', // required
#   runtime: Runtime.PYTHON_3_8, // required
#   index: 'my_index.py', // optional, defaults to 'index.py'
#   handler: 'my_exported_func', // optional, defaults to 'handler'
# });
