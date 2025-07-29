# Copyright Metatype OÜ, licensed under the Mozilla Public License Version 2.0.
# SPDX-License-Identifier: MPL-2.0

import typing_extensions as t
from pydantic import BaseModel
from typegraph.gen.client import rpc_request
from typegraph.gen.core import MaterializerId, RuntimeId

class S3RuntimeData(BaseModel):
    host_secret: str
    region_secret: str
    access_key_secret: str
    secret_key_secret: str
    path_style_secret: str

    def __init__(self, host_secret: str, region_secret: str, access_key_secret: str, secret_key_secret: str, path_style_secret: str, **kwargs):
        super().__init__(host_secret=host_secret,region_secret=region_secret,access_key_secret=access_key_secret,secret_key_secret=secret_key_secret,path_style_secret=path_style_secret, **kwargs)

class S3PresignGetParams(BaseModel):
    bucket: str
    expiry_secs: t.Optional[int]

    def __init__(self, bucket: str, expiry_secs: t.Optional[int], **kwargs):
        super().__init__(bucket=bucket,expiry_secs=expiry_secs, **kwargs)

class S3PresignPutParams(BaseModel):
    bucket: str
    expiry_secs: t.Optional[int]
    content_type: t.Optional[str]

    def __init__(self, bucket: str, expiry_secs: t.Optional[int], content_type: t.Optional[str], **kwargs):
        super().__init__(bucket=bucket,expiry_secs=expiry_secs,content_type=content_type, **kwargs)

def register_s3_runtime(data: S3RuntimeData) -> RuntimeId:
    class RequestType(BaseModel):
        data: S3RuntimeData

    class ReturnType(BaseModel):
        value: RuntimeId

    req = RequestType(data=data)
    res = rpc_request("register_s3_runtime", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def s3_presign_get(runtime: RuntimeId, data: S3PresignGetParams) -> MaterializerId:
    class RequestType(BaseModel):
        runtime: RuntimeId
        data: S3PresignGetParams

    class ReturnType(BaseModel):
        value: MaterializerId

    req = RequestType(runtime=runtime, data=data)
    res = rpc_request("s3_presign_get", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def s3_presign_put(runtime: RuntimeId, data: S3PresignPutParams) -> MaterializerId:
    class RequestType(BaseModel):
        runtime: RuntimeId
        data: S3PresignPutParams

    class ReturnType(BaseModel):
        value: MaterializerId

    req = RequestType(runtime=runtime, data=data)
    res = rpc_request("s3_presign_put", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def s3_list(runtime: RuntimeId, bucket: str) -> MaterializerId:
    class RequestType(BaseModel):
        runtime: RuntimeId
        bucket: str

    class ReturnType(BaseModel):
        value: MaterializerId

    req = RequestType(runtime=runtime, bucket=bucket)
    res = rpc_request("s3_list", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def s3_upload(runtime: RuntimeId, bucket: str) -> MaterializerId:
    class RequestType(BaseModel):
        runtime: RuntimeId
        bucket: str

    class ReturnType(BaseModel):
        value: MaterializerId

    req = RequestType(runtime=runtime, bucket=bucket)
    res = rpc_request("s3_upload", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def s3_upload_all(runtime: RuntimeId, bucket: str) -> MaterializerId:
    class RequestType(BaseModel):
        runtime: RuntimeId
        bucket: str

    class ReturnType(BaseModel):
        value: MaterializerId

    req = RequestType(runtime=runtime, bucket=bucket)
    res = rpc_request("s3_upload_all", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value