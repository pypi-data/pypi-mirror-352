# Copyright Metatype OÜ, licensed under the Mozilla Public License Version 2.0.
# SPDX-License-Identifier: MPL-2.0

import typing_extensions as t
from pydantic import BaseModel
from typegraph.gen.client import rpc_request
from typegraph.gen.core import TypeId

class ReduceEntry(BaseModel):
    path: t.List[str]
    injection_data: str

    def __init__(self, path: t.List[str], injection_data: str, **kwargs):
        super().__init__(path=path,injection_data=injection_data, **kwargs)

AuthProtocol = t.Union[
    t.Literal["oauth2"],
    t.Literal["jwt"],
    t.Literal["basic"],
]

class Auth(BaseModel):
    name: str
    protocol: AuthProtocol
    auth_data: t.List[t.Tuple[str, str]]

    def __init__(self, name: str, protocol: AuthProtocol, auth_data: t.List[t.Tuple[str, str]], **kwargs):
        super().__init__(name=name,protocol=protocol,auth_data=auth_data, **kwargs)

class QueryDeployParams(BaseModel):
    tg: str
    secrets: t.Optional[t.List[t.Tuple[str, str]]]

    def __init__(self, tg: str, secrets: t.Optional[t.List[t.Tuple[str, str]]], **kwargs):
        super().__init__(tg=tg,secrets=secrets, **kwargs)

class FdkConfig(BaseModel):
    workspace_path: str
    target_name: str
    config_json: str
    tg_json: str

    def __init__(self, workspace_path: str, target_name: str, config_json: str, tg_json: str, **kwargs):
        super().__init__(workspace_path=workspace_path,target_name=target_name,config_json=config_json,tg_json=tg_json, **kwargs)

class FdkOutput(BaseModel):
    path: str
    content: str
    overwrite: bool

    def __init__(self, path: str, content: str, overwrite: bool, **kwargs):
        super().__init__(path=path,content=content,overwrite=overwrite, **kwargs)

def reduceb(super_type_id: TypeId, entries: t.List[ReduceEntry]) -> TypeId:
    class RequestType(BaseModel):
        super_type_id: TypeId
        entries: t.List[ReduceEntry]

    class ReturnType(BaseModel):
        value: TypeId

    req = RequestType(super_type_id=super_type_id, entries=entries)
    res = rpc_request("reduceb", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def add_graphql_endpoint(graphql: str) -> int:
    class RequestType(BaseModel):
        graphql: str

    class ReturnType(BaseModel):
        value: int

    req = RequestType(graphql=graphql)
    res = rpc_request("add_graphql_endpoint", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def add_auth(data: Auth) -> int:
    class RequestType(BaseModel):
        data: Auth

    class ReturnType(BaseModel):
        value: int

    req = RequestType(data=data)
    res = rpc_request("add_auth", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def add_raw_auth(data: str) -> int:
    class RequestType(BaseModel):
        data: str

    class ReturnType(BaseModel):
        value: int

    req = RequestType(data=data)
    res = rpc_request("add_raw_auth", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def oauth2(service_name: str, scopes: str) -> str:
    class RequestType(BaseModel):
        service_name: str
        scopes: str

    class ReturnType(BaseModel):
        value: str

    req = RequestType(service_name=service_name, scopes=scopes)
    res = rpc_request("oauth2", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def oauth2_without_profiler(service_name: str, scopes: str) -> str:
    class RequestType(BaseModel):
        service_name: str
        scopes: str

    class ReturnType(BaseModel):
        value: str

    req = RequestType(service_name=service_name, scopes=scopes)
    res = rpc_request("oauth2_without_profiler", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def oauth2_with_extended_profiler(service_name: str, scopes: str, extension: str) -> str:
    class RequestType(BaseModel):
        service_name: str
        scopes: str
        extension: str

    class ReturnType(BaseModel):
        value: str

    req = RequestType(service_name=service_name, scopes=scopes, extension=extension)
    res = rpc_request("oauth2_with_extended_profiler", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def oauth2_with_custom_profiler(service_name: str, scopes: str, profiler: TypeId) -> str:
    class RequestType(BaseModel):
        service_name: str
        scopes: str
        profiler: TypeId

    class ReturnType(BaseModel):
        value: str

    req = RequestType(service_name=service_name, scopes=scopes, profiler=profiler)
    res = rpc_request("oauth2_with_custom_profiler", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def gql_deploy_query(params: QueryDeployParams) -> str:
    class RequestType(BaseModel):
        params: QueryDeployParams

    class ReturnType(BaseModel):
        value: str

    req = RequestType(params=params)
    res = rpc_request("gql_deploy_query", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def gql_remove_query(tg_name: t.List[str]) -> str:
    class RequestType(BaseModel):
        tg_name: t.List[str]

    class ReturnType(BaseModel):
        value: str

    req = RequestType(tg_name=tg_name)
    res = rpc_request("gql_remove_query", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def gql_ping_query() -> str:
    class ReturnType(BaseModel):
        value: str

    res = rpc_request("gql_ping_query")
    ret = ReturnType(value=res)

    return ret.value

def metagen_exec(config: FdkConfig) -> t.List[FdkOutput]:
    class RequestType(BaseModel):
        config: FdkConfig

    class ReturnType(BaseModel):
        value: t.List[FdkOutput]

    req = RequestType(config=config)
    res = rpc_request("metagen_exec", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def metagen_write_files(items: t.List[FdkOutput], typegraph_dir: str) -> None:
    class RequestType(BaseModel):
        items: t.List[FdkOutput]
        typegraph_dir: str

    class ReturnType(BaseModel):
        value: None

    req = RequestType(items=items, typegraph_dir=typegraph_dir)
    res = rpc_request("metagen_write_files", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value