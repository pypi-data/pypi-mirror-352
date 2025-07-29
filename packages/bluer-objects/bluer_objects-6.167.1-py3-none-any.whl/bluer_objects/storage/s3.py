import boto3
from botocore.exceptions import ClientError
import glob
from typing import Tuple, List
from xml.etree import ElementTree as ET
from tqdm import tqdm
from functools import reduce

from bluer_objects.storage.base import StorageInterface
from bluer_objects import env, file, path
from bluer_objects import objects
from bluer_objects.logger import logger


# https://docs.arvancloud.ir/fa/developer-tools/sdk/object-storage/
class S3Interface(StorageInterface):
    name = "s3"

    def download(
        self,
        object_name: str,
        filename: str = "",
        log: bool = True,
    ) -> bool:
        if filename:
            local_path = objects.path_of(
                object_name=object_name,
                filename=filename,
                create=True,
            )

            if not path.create(file.path(local_path)):
                return False

            try:
                s3_resource = boto3.resource(
                    "s3",
                    endpoint_url=env.S3_STORAGE_ENDPOINT_URL,
                    aws_access_key_id=env.S3_STORAGE_AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=env.S3_STORAGE_AWS_SECRET_ACCESS_KEY,
                )
            except Exception as e:
                logger.error(e)
                return False

            try:
                bucket = s3_resource.Bucket(env.S3_STORAGE_BUCKET)

                bucket.download_file(
                    f"{object_name}/{filename}",
                    local_path,
                )
            except ClientError as e:
                if int(e.response["Error"]["Code"]) == 404:  # Not found
                    return True
                logger.error(e)
                return False

            return super().download(
                object_name=object_name,
                filename=filename,
                log=log,
            )

        success, list_of_files = self.ls(
            object_name=object_name,
            where="cloud",
        )
        if not success:
            return False

        for filename_ in tqdm(list_of_files):
            if not self.download(
                object_name=object_name,
                filename=filename_,
                log=log,
            ):
                return False

        return True

    def ls(
        self,
        object_name: str,
        where: str = "local",
    ) -> Tuple[bool, List[str]]:
        if where == "cloud":
            try:
                s3 = boto3.client(
                    "s3",
                    endpoint_url=env.S3_STORAGE_ENDPOINT_URL,
                    aws_access_key_id=env.S3_STORAGE_AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=env.S3_STORAGE_AWS_SECRET_ACCESS_KEY,
                )

                prefix = f"{object_name}/"

                paginator = s3.get_paginator("list_objects_v2")
                pages = paginator.paginate(
                    Bucket=env.S3_STORAGE_BUCKET,
                    Prefix=prefix,
                )
            except Exception as e:
                logger.error(e)
                return False, []

            return True, sorted(
                reduce(
                    lambda x, y: x + y,
                    [
                        [
                            obj["Key"].split(prefix, 1)[1]
                            for obj in page.get("Contents", [])
                        ]
                        for page in pages
                    ],
                    [],
                )
            )

        return super().ls(
            object_name=object_name,
            where=where,
        )

    def upload(
        self,
        object_name: str,
        filename: str = "",
        log: bool = True,
    ) -> bool:
        if filename:
            local_path = objects.path_of(
                object_name=object_name,
                filename=filename,
            )

            try:
                s3_resource = boto3.resource(
                    "s3",
                    endpoint_url=env.S3_STORAGE_ENDPOINT_URL,
                    aws_access_key_id=env.S3_STORAGE_AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=env.S3_STORAGE_AWS_SECRET_ACCESS_KEY,
                )

                bucket = s3_resource.Bucket(env.S3_STORAGE_BUCKET)

                with open(local_path, "rb") as fp:
                    bucket.put_object(
                        ACL="private",
                        Body=fp,
                        Key=f"{object_name}/{filename}",
                    )
            except ClientError as e:
                logger.error(e)
                return False

            return super().upload(
                object_name=object_name,
                filename=filename,
                log=log,
            )

        object_path = "{}/".format(objects.object_path(object_name=object_name))
        for filename_ in tqdm(
            sorted(
                glob.glob(
                    objects.path_of(
                        object_name=object_name,
                        filename="**",
                    ),
                    recursive=True,
                )
            )
        ):
            if not file.exists(filename_):
                continue

            if not self.upload(
                object_name=object_name,
                filename=filename_.split(object_path, 1)[1],
                log=log,
            ):
                return False

        return True
