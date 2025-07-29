# Copyright Metatype OÜ, licensed under the Mozilla Public License Version 2.0.
# SPDX-License-Identifier: MPL-2.0

import typing_extensions as t
from pydantic import BaseModel
from typegraph.gen.client import rpc_request
from typegraph.gen.core import FuncParams, MaterializerId, RuntimeId, TypeId

Idempotency = bool

Effect = t.Union[
    t.Literal["read"],
    t.TypedDict("EffectCreate", {"create": Idempotency}),
    t.TypedDict("EffectUpdate", {"update": Idempotency}),
    t.TypedDict("EffectDelete", {"delete": Idempotency}),
]

class BaseMaterializer(BaseModel):
    runtime: RuntimeId
    effect: Effect

    def __init__(self, runtime: RuntimeId, effect: Effect, **kwargs):
        super().__init__(runtime=runtime,effect=effect, **kwargs)

class MaterializerDenoFunc(BaseModel):
    code: str
    secrets: t.List[str]

    def __init__(self, code: str, secrets: t.List[str], **kwargs):
        super().__init__(code=code,secrets=secrets, **kwargs)

class MaterializerDenoStatic(BaseModel):
    value: str

    def __init__(self, value: str, **kwargs):
        super().__init__(value=value, **kwargs)

class MaterializerDenoPredefined(BaseModel):
    name: str
    param: t.Optional[str]

    def __init__(self, name: str, param: t.Optional[str], **kwargs):
        super().__init__(name=name,param=param, **kwargs)

class MaterializerDenoImport(BaseModel):
    func_name: str
    module: str
    deps: t.List[str]
    secrets: t.List[str]

    def __init__(self, func_name: str, module: str, deps: t.List[str], secrets: t.List[str], **kwargs):
        super().__init__(func_name=func_name,module=module,deps=deps,secrets=secrets, **kwargs)

class GraphqlRuntimeData(BaseModel):
    endpoint: str

    def __init__(self, endpoint: str, **kwargs):
        super().__init__(endpoint=endpoint, **kwargs)

class MaterializerGraphqlQuery(BaseModel):
    path: t.Optional[t.List[str]]

    def __init__(self, path: t.Optional[t.List[str]], **kwargs):
        super().__init__(path=path, **kwargs)

class HttpRuntimeData(BaseModel):
    endpoint: str
    cert_secret: t.Optional[str]
    basic_auth_secret: t.Optional[str]

    def __init__(self, endpoint: str, cert_secret: t.Optional[str], basic_auth_secret: t.Optional[str], **kwargs):
        super().__init__(endpoint=endpoint,cert_secret=cert_secret,basic_auth_secret=basic_auth_secret, **kwargs)

HttpMethod = t.Union[
    t.Literal["get"],
    t.Literal["post"],
    t.Literal["put"],
    t.Literal["patch"],
    t.Literal["delete"],
]

class MaterializerHttpRequest(BaseModel):
    method: HttpMethod
    path: str
    content_type: t.Optional[str]
    header_prefix: t.Optional[str]
    query_fields: t.Optional[t.List[str]]
    rename_fields: t.Optional[t.List[t.Tuple[str, str]]]
    body_fields: t.Optional[t.List[str]]
    auth_token_field: t.Optional[str]

    def __init__(self, method: HttpMethod, path: str, content_type: t.Optional[str], header_prefix: t.Optional[str], query_fields: t.Optional[t.List[str]], rename_fields: t.Optional[t.List[t.Tuple[str, str]]], body_fields: t.Optional[t.List[str]], auth_token_field: t.Optional[str], **kwargs):
        super().__init__(method=method,path=path,content_type=content_type,header_prefix=header_prefix,query_fields=query_fields,rename_fields=rename_fields,body_fields=body_fields,auth_token_field=auth_token_field, **kwargs)

class MaterializerPythonDef(BaseModel):
    runtime: RuntimeId
    name: str
    function: str

    def __init__(self, runtime: RuntimeId, name: str, function: str, **kwargs):
        super().__init__(runtime=runtime,name=name,function=function, **kwargs)

class MaterializerPythonLambda(BaseModel):
    runtime: RuntimeId
    function: str

    def __init__(self, runtime: RuntimeId, function: str, **kwargs):
        super().__init__(runtime=runtime,function=function, **kwargs)

class MaterializerPythonModule(BaseModel):
    runtime: RuntimeId
    file: str
    deps: t.List[str]

    def __init__(self, runtime: RuntimeId, file: str, deps: t.List[str], **kwargs):
        super().__init__(runtime=runtime,file=file,deps=deps, **kwargs)

class MaterializerPythonImport(BaseModel):
    module: int
    func_name: str
    secrets: t.List[str]

    def __init__(self, module: int, func_name: str, secrets: t.List[str], **kwargs):
        super().__init__(module=module,func_name=func_name,secrets=secrets, **kwargs)

class RandomRuntimeData(BaseModel):
    seed: t.Optional[int]
    reset: t.Optional[str]

    def __init__(self, seed: t.Optional[int], reset: t.Optional[str], **kwargs):
        super().__init__(seed=seed,reset=reset, **kwargs)

class MaterializerRandom(BaseModel):
    runtime: RuntimeId

    def __init__(self, runtime: RuntimeId, **kwargs):
        super().__init__(runtime=runtime, **kwargs)

class WasmRuntimeData(BaseModel):
    wasm_artifact: str

    def __init__(self, wasm_artifact: str, **kwargs):
        super().__init__(wasm_artifact=wasm_artifact, **kwargs)

class MaterializerWasmReflectedFunc(BaseModel):
    func_name: str

    def __init__(self, func_name: str, **kwargs):
        super().__init__(func_name=func_name, **kwargs)

class MaterializerWasmWireHandler(BaseModel):
    func_name: str

    def __init__(self, func_name: str, **kwargs):
        super().__init__(func_name=func_name, **kwargs)

class PrismaRuntimeData(BaseModel):
    name: str
    connection_string_secret: str

    def __init__(self, name: str, connection_string_secret: str, **kwargs):
        super().__init__(name=name,connection_string_secret=connection_string_secret, **kwargs)

class PrismaLinkData(BaseModel):
    target_type: TypeId
    relationship_name: t.Optional[str]
    foreign_key: t.Optional[bool]
    target_field: t.Optional[str]
    unique: t.Optional[bool]

    def __init__(self, target_type: TypeId, relationship_name: t.Optional[str], foreign_key: t.Optional[bool], target_field: t.Optional[str], unique: t.Optional[bool], **kwargs):
        super().__init__(target_type=target_type,relationship_name=relationship_name,foreign_key=foreign_key,target_field=target_field,unique=unique, **kwargs)

PrismaMigrationOperation = t.Union[
    t.Literal["diff"],
    t.Literal["create"],
    t.Literal["apply"],
    t.Literal["deploy"],
    t.Literal["reset"],
]

class TemporalRuntimeData(BaseModel):
    name: str
    host_secret: str
    namespace_secret: t.Optional[str]

    def __init__(self, name: str, host_secret: str, namespace_secret: t.Optional[str], **kwargs):
        super().__init__(name=name,host_secret=host_secret,namespace_secret=namespace_secret, **kwargs)

TemporalOperationType = t.Union[
    t.Literal["start_workflow"],
    t.Literal["signal_workflow"],
    t.Literal["query_workflow"],
    t.Literal["describe_workflow"],
]

class TemporalOperationData(BaseModel):
    mat_arg: t.Optional[str]
    func_arg: t.Optional[TypeId]
    func_out: t.Optional[TypeId]
    operation: TemporalOperationType

    def __init__(self, mat_arg: t.Optional[str], func_arg: t.Optional[TypeId], func_out: t.Optional[TypeId], operation: TemporalOperationType, **kwargs):
        super().__init__(mat_arg=mat_arg,func_arg=func_arg,func_out=func_out,operation=operation, **kwargs)

TypegateOperation = t.Union[
    t.Literal["list_typegraphs"],
    t.Literal["find_typegraph"],
    t.Literal["add_typegraph"],
    t.Literal["remove_typegraphs"],
    t.Literal["get_serialized_typegraph"],
    t.Literal["get_arg_info_by_path"],
    t.Literal["find_available_operations"],
    t.Literal["find_prisma_models"],
    t.Literal["raw_prisma_read"],
    t.Literal["raw_prisma_create"],
    t.Literal["raw_prisma_update"],
    t.Literal["raw_prisma_delete"],
    t.Literal["query_prisma_model"],
    t.Literal["ping"],
]

TypegraphOperation = t.Union[
    t.Literal["resolver"],
    t.Literal["get_type"],
    t.Literal["get_schema"],
]

class RedisBackend(BaseModel):
    connection_string_secret: str

    def __init__(self, connection_string_secret: str, **kwargs):
        super().__init__(connection_string_secret=connection_string_secret, **kwargs)

SubstantialBackend = t.Union[
    t.Literal["memory"],
    t.Literal["fs"],
    t.TypedDict("SubstantialBackendRedis", {"redis": RedisBackend}),
]

WorkflowKind = t.Union[
    t.Literal["python"],
    t.Literal["deno"],
]

class WorkflowFileDescription(BaseModel):
    workflows: t.List[str]
    file: str
    deps: t.List[str]
    kind: WorkflowKind

    def __init__(self, workflows: t.List[str], file: str, deps: t.List[str], kind: WorkflowKind, **kwargs):
        super().__init__(workflows=workflows,file=file,deps=deps,kind=kind, **kwargs)

class SubstantialRuntimeData(BaseModel):
    backend: SubstantialBackend
    file_descriptions: t.List[WorkflowFileDescription]

    def __init__(self, backend: SubstantialBackend, file_descriptions: t.List[WorkflowFileDescription], **kwargs):
        super().__init__(backend=backend,file_descriptions=file_descriptions, **kwargs)

class SubstantialStartData(BaseModel):
    func_arg: t.Optional[TypeId]
    secrets: t.List[str]

    def __init__(self, func_arg: t.Optional[TypeId], secrets: t.List[str], **kwargs):
        super().__init__(func_arg=func_arg,secrets=secrets, **kwargs)

SubstantialOperationData = t.Union[
    t.TypedDict("SubstantialOperationDataStart", {"start": SubstantialStartData}),
    t.TypedDict("SubstantialOperationDataStartRaw", {"start_raw": SubstantialStartData}),
    t.Literal["stop"],
    t.TypedDict("SubstantialOperationDataSend", {"send": TypeId}),
    t.Literal["send_raw"],
    t.Literal["resources"],
    t.TypedDict("SubstantialOperationDataResults", {"results": TypeId}),
    t.Literal["results_raw"],
    t.Literal["internal_link_parent_child"],
    t.Literal["advanced_filters"],
]

class KvRuntimeData(BaseModel):
    url: str

    def __init__(self, url: str, **kwargs):
        super().__init__(url=url, **kwargs)

KvMaterializer = t.Union[
    t.Literal["get"],
    t.Literal["set"],
    t.Literal["delete"],
    t.Literal["keys"],
    t.Literal["values"],
    t.Literal["lpush"],
    t.Literal["rpush"],
    t.Literal["lpop"],
    t.Literal["rpop"],
]

class GrpcRuntimeData(BaseModel):
    proto_file: str
    endpoint: str

    def __init__(self, proto_file: str, endpoint: str, **kwargs):
        super().__init__(proto_file=proto_file,endpoint=endpoint, **kwargs)

class GrpcData(BaseModel):
    method: str

    def __init__(self, method: str, **kwargs):
        super().__init__(method=method, **kwargs)

def get_deno_runtime() -> RuntimeId:
    class ReturnType(BaseModel):
        value: RuntimeId

    res = rpc_request("get_deno_runtime")
    ret = ReturnType(value=res)

    return ret.value

def register_deno_func(data: MaterializerDenoFunc, effect: Effect) -> MaterializerId:
    class RequestType(BaseModel):
        data: MaterializerDenoFunc
        effect: Effect

    class ReturnType(BaseModel):
        value: MaterializerId

    req = RequestType(data=data, effect=effect)
    res = rpc_request("register_deno_func", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def register_deno_static(data: MaterializerDenoStatic, type_id: TypeId) -> MaterializerId:
    class RequestType(BaseModel):
        data: MaterializerDenoStatic
        type_id: TypeId

    class ReturnType(BaseModel):
        value: MaterializerId

    req = RequestType(data=data, type_id=type_id)
    res = rpc_request("register_deno_static", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def get_predefined_deno_func(data: MaterializerDenoPredefined) -> MaterializerId:
    class RequestType(BaseModel):
        data: MaterializerDenoPredefined

    class ReturnType(BaseModel):
        value: MaterializerId

    req = RequestType(data=data)
    res = rpc_request("get_predefined_deno_func", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def import_deno_function(data: MaterializerDenoImport, effect: Effect) -> MaterializerId:
    class RequestType(BaseModel):
        data: MaterializerDenoImport
        effect: Effect

    class ReturnType(BaseModel):
        value: MaterializerId

    req = RequestType(data=data, effect=effect)
    res = rpc_request("import_deno_function", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def register_graphql_runtime(data: GraphqlRuntimeData) -> RuntimeId:
    class RequestType(BaseModel):
        data: GraphqlRuntimeData

    class ReturnType(BaseModel):
        value: RuntimeId

    req = RequestType(data=data)
    res = rpc_request("register_graphql_runtime", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def graphql_query(base: BaseMaterializer, data: MaterializerGraphqlQuery) -> MaterializerId:
    class RequestType(BaseModel):
        base: BaseMaterializer
        data: MaterializerGraphqlQuery

    class ReturnType(BaseModel):
        value: MaterializerId

    req = RequestType(base=base, data=data)
    res = rpc_request("graphql_query", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def graphql_mutation(base: BaseMaterializer, data: MaterializerGraphqlQuery) -> MaterializerId:
    class RequestType(BaseModel):
        base: BaseMaterializer
        data: MaterializerGraphqlQuery

    class ReturnType(BaseModel):
        value: MaterializerId

    req = RequestType(base=base, data=data)
    res = rpc_request("graphql_mutation", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def register_http_runtime(data: HttpRuntimeData) -> RuntimeId:
    class RequestType(BaseModel):
        data: HttpRuntimeData

    class ReturnType(BaseModel):
        value: RuntimeId

    req = RequestType(data=data)
    res = rpc_request("register_http_runtime", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def http_request(base: BaseMaterializer, data: MaterializerHttpRequest) -> MaterializerId:
    class RequestType(BaseModel):
        base: BaseMaterializer
        data: MaterializerHttpRequest

    class ReturnType(BaseModel):
        value: MaterializerId

    req = RequestType(base=base, data=data)
    res = rpc_request("http_request", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def register_python_runtime() -> RuntimeId:
    class ReturnType(BaseModel):
        value: RuntimeId

    res = rpc_request("register_python_runtime")
    ret = ReturnType(value=res)

    return ret.value

def from_python_lambda(base: BaseMaterializer, data: MaterializerPythonLambda) -> MaterializerId:
    class RequestType(BaseModel):
        base: BaseMaterializer
        data: MaterializerPythonLambda

    class ReturnType(BaseModel):
        value: MaterializerId

    req = RequestType(base=base, data=data)
    res = rpc_request("from_python_lambda", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def from_python_def(base: BaseMaterializer, data: MaterializerPythonDef) -> MaterializerId:
    class RequestType(BaseModel):
        base: BaseMaterializer
        data: MaterializerPythonDef

    class ReturnType(BaseModel):
        value: MaterializerId

    req = RequestType(base=base, data=data)
    res = rpc_request("from_python_def", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def from_python_module(base: BaseMaterializer, data: MaterializerPythonModule) -> MaterializerId:
    class RequestType(BaseModel):
        base: BaseMaterializer
        data: MaterializerPythonModule

    class ReturnType(BaseModel):
        value: MaterializerId

    req = RequestType(base=base, data=data)
    res = rpc_request("from_python_module", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def from_python_import(base: BaseMaterializer, data: MaterializerPythonImport) -> MaterializerId:
    class RequestType(BaseModel):
        base: BaseMaterializer
        data: MaterializerPythonImport

    class ReturnType(BaseModel):
        value: MaterializerId

    req = RequestType(base=base, data=data)
    res = rpc_request("from_python_import", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def register_random_runtime(data: RandomRuntimeData) -> MaterializerId:
    class RequestType(BaseModel):
        data: RandomRuntimeData

    class ReturnType(BaseModel):
        value: MaterializerId

    req = RequestType(data=data)
    res = rpc_request("register_random_runtime", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def create_random_mat(base: BaseMaterializer, data: MaterializerRandom) -> MaterializerId:
    class RequestType(BaseModel):
        base: BaseMaterializer
        data: MaterializerRandom

    class ReturnType(BaseModel):
        value: MaterializerId

    req = RequestType(base=base, data=data)
    res = rpc_request("create_random_mat", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def register_wasm_reflected_runtime(data: WasmRuntimeData) -> RuntimeId:
    class RequestType(BaseModel):
        data: WasmRuntimeData

    class ReturnType(BaseModel):
        value: RuntimeId

    req = RequestType(data=data)
    res = rpc_request("register_wasm_reflected_runtime", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def from_wasm_reflected_func(base: BaseMaterializer, data: MaterializerWasmReflectedFunc) -> MaterializerId:
    class RequestType(BaseModel):
        base: BaseMaterializer
        data: MaterializerWasmReflectedFunc

    class ReturnType(BaseModel):
        value: MaterializerId

    req = RequestType(base=base, data=data)
    res = rpc_request("from_wasm_reflected_func", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def register_wasm_wire_runtime(data: WasmRuntimeData) -> RuntimeId:
    class RequestType(BaseModel):
        data: WasmRuntimeData

    class ReturnType(BaseModel):
        value: RuntimeId

    req = RequestType(data=data)
    res = rpc_request("register_wasm_wire_runtime", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def from_wasm_wire_handler(base: BaseMaterializer, data: MaterializerWasmWireHandler) -> MaterializerId:
    class RequestType(BaseModel):
        base: BaseMaterializer
        data: MaterializerWasmWireHandler

    class ReturnType(BaseModel):
        value: MaterializerId

    req = RequestType(base=base, data=data)
    res = rpc_request("from_wasm_wire_handler", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def register_prisma_runtime(data: PrismaRuntimeData) -> RuntimeId:
    class RequestType(BaseModel):
        data: PrismaRuntimeData

    class ReturnType(BaseModel):
        value: RuntimeId

    req = RequestType(data=data)
    res = rpc_request("register_prisma_runtime", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def prisma_find_unique(runtime: RuntimeId, model: TypeId) -> FuncParams:
    class RequestType(BaseModel):
        runtime: RuntimeId
        model: TypeId

    class ReturnType(BaseModel):
        value: FuncParams

    req = RequestType(runtime=runtime, model=model)
    res = rpc_request("prisma_find_unique", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def prisma_find_many(runtime: RuntimeId, model: TypeId) -> FuncParams:
    class RequestType(BaseModel):
        runtime: RuntimeId
        model: TypeId

    class ReturnType(BaseModel):
        value: FuncParams

    req = RequestType(runtime=runtime, model=model)
    res = rpc_request("prisma_find_many", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def prisma_find_first(runtime: RuntimeId, model: TypeId) -> FuncParams:
    class RequestType(BaseModel):
        runtime: RuntimeId
        model: TypeId

    class ReturnType(BaseModel):
        value: FuncParams

    req = RequestType(runtime=runtime, model=model)
    res = rpc_request("prisma_find_first", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def prisma_aggregate(runtime: RuntimeId, model: TypeId) -> FuncParams:
    class RequestType(BaseModel):
        runtime: RuntimeId
        model: TypeId

    class ReturnType(BaseModel):
        value: FuncParams

    req = RequestType(runtime=runtime, model=model)
    res = rpc_request("prisma_aggregate", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def prisma_group_by(runtime: RuntimeId, model: TypeId) -> FuncParams:
    class RequestType(BaseModel):
        runtime: RuntimeId
        model: TypeId

    class ReturnType(BaseModel):
        value: FuncParams

    req = RequestType(runtime=runtime, model=model)
    res = rpc_request("prisma_group_by", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def prisma_create_one(runtime: RuntimeId, model: TypeId) -> FuncParams:
    class RequestType(BaseModel):
        runtime: RuntimeId
        model: TypeId

    class ReturnType(BaseModel):
        value: FuncParams

    req = RequestType(runtime=runtime, model=model)
    res = rpc_request("prisma_create_one", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def prisma_create_many(runtime: RuntimeId, model: TypeId) -> FuncParams:
    class RequestType(BaseModel):
        runtime: RuntimeId
        model: TypeId

    class ReturnType(BaseModel):
        value: FuncParams

    req = RequestType(runtime=runtime, model=model)
    res = rpc_request("prisma_create_many", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def prisma_update_one(runtime: RuntimeId, model: TypeId) -> FuncParams:
    class RequestType(BaseModel):
        runtime: RuntimeId
        model: TypeId

    class ReturnType(BaseModel):
        value: FuncParams

    req = RequestType(runtime=runtime, model=model)
    res = rpc_request("prisma_update_one", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def prisma_update_many(runtime: RuntimeId, model: TypeId) -> FuncParams:
    class RequestType(BaseModel):
        runtime: RuntimeId
        model: TypeId

    class ReturnType(BaseModel):
        value: FuncParams

    req = RequestType(runtime=runtime, model=model)
    res = rpc_request("prisma_update_many", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def prisma_upsert_one(runtime: RuntimeId, model: TypeId) -> FuncParams:
    class RequestType(BaseModel):
        runtime: RuntimeId
        model: TypeId

    class ReturnType(BaseModel):
        value: FuncParams

    req = RequestType(runtime=runtime, model=model)
    res = rpc_request("prisma_upsert_one", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def prisma_delete_one(runtime: RuntimeId, model: TypeId) -> FuncParams:
    class RequestType(BaseModel):
        runtime: RuntimeId
        model: TypeId

    class ReturnType(BaseModel):
        value: FuncParams

    req = RequestType(runtime=runtime, model=model)
    res = rpc_request("prisma_delete_one", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def prisma_delete_many(runtime: RuntimeId, model: TypeId) -> FuncParams:
    class RequestType(BaseModel):
        runtime: RuntimeId
        model: TypeId

    class ReturnType(BaseModel):
        value: FuncParams

    req = RequestType(runtime=runtime, model=model)
    res = rpc_request("prisma_delete_many", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def prisma_execute(runtime: RuntimeId, query: str, param: TypeId, effect: Effect) -> FuncParams:
    class RequestType(BaseModel):
        runtime: RuntimeId
        query: str
        param: TypeId
        effect: Effect

    class ReturnType(BaseModel):
        value: FuncParams

    req = RequestType(runtime=runtime, query=query, param=param, effect=effect)
    res = rpc_request("prisma_execute", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def prisma_query_raw(runtime: RuntimeId, query: str, out: TypeId, param: t.Optional[TypeId] = None) -> FuncParams:
    class RequestType(BaseModel):
        runtime: RuntimeId
        query: str
        out: TypeId
        param: t.Optional[TypeId]

    class ReturnType(BaseModel):
        value: FuncParams

    req = RequestType(runtime=runtime, query=query, out=out, param=param)
    res = rpc_request("prisma_query_raw", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def prisma_link(data: PrismaLinkData) -> TypeId:
    class RequestType(BaseModel):
        data: PrismaLinkData

    class ReturnType(BaseModel):
        value: TypeId

    req = RequestType(data=data)
    res = rpc_request("prisma_link", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def prisma_migration(operation: PrismaMigrationOperation) -> FuncParams:
    class RequestType(BaseModel):
        operation: PrismaMigrationOperation

    class ReturnType(BaseModel):
        value: FuncParams

    req = RequestType(operation=operation)
    res = rpc_request("prisma_migration", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def register_temporal_runtime(data: TemporalRuntimeData) -> RuntimeId:
    class RequestType(BaseModel):
        data: TemporalRuntimeData

    class ReturnType(BaseModel):
        value: RuntimeId

    req = RequestType(data=data)
    res = rpc_request("register_temporal_runtime", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def generate_temporal_operation(runtime: RuntimeId, data: TemporalOperationData) -> FuncParams:
    class RequestType(BaseModel):
        runtime: RuntimeId
        data: TemporalOperationData

    class ReturnType(BaseModel):
        value: FuncParams

    req = RequestType(runtime=runtime, data=data)
    res = rpc_request("generate_temporal_operation", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def register_typegate_materializer(operation: TypegateOperation) -> MaterializerId:
    class RequestType(BaseModel):
        operation: TypegateOperation

    class ReturnType(BaseModel):
        value: MaterializerId

    req = RequestType(operation=operation)
    res = rpc_request("register_typegate_materializer", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def register_typegraph_materializer(operation: TypegraphOperation) -> MaterializerId:
    class RequestType(BaseModel):
        operation: TypegraphOperation

    class ReturnType(BaseModel):
        value: MaterializerId

    req = RequestType(operation=operation)
    res = rpc_request("register_typegraph_materializer", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def register_substantial_runtime(data: SubstantialRuntimeData) -> RuntimeId:
    class RequestType(BaseModel):
        data: SubstantialRuntimeData

    class ReturnType(BaseModel):
        value: RuntimeId

    req = RequestType(data=data)
    res = rpc_request("register_substantial_runtime", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def generate_substantial_operation(runtime: RuntimeId, data: SubstantialOperationData) -> FuncParams:
    class RequestType(BaseModel):
        runtime: RuntimeId
        data: SubstantialOperationData

    class ReturnType(BaseModel):
        value: FuncParams

    req = RequestType(runtime=runtime, data=data)
    res = rpc_request("generate_substantial_operation", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def register_kv_runtime(data: KvRuntimeData) -> RuntimeId:
    class RequestType(BaseModel):
        data: KvRuntimeData

    class ReturnType(BaseModel):
        value: RuntimeId

    req = RequestType(data=data)
    res = rpc_request("register_kv_runtime", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def kv_operation(base: BaseMaterializer, data: KvMaterializer) -> MaterializerId:
    class RequestType(BaseModel):
        base: BaseMaterializer
        data: KvMaterializer

    class ReturnType(BaseModel):
        value: MaterializerId

    req = RequestType(base=base, data=data)
    res = rpc_request("kv_operation", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def register_grpc_runtime(data: GrpcRuntimeData) -> RuntimeId:
    class RequestType(BaseModel):
        data: GrpcRuntimeData

    class ReturnType(BaseModel):
        value: RuntimeId

    req = RequestType(data=data)
    res = rpc_request("register_grpc_runtime", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def call_grpc_method(runtime: RuntimeId, data: GrpcData) -> FuncParams:
    class RequestType(BaseModel):
        runtime: RuntimeId
        data: GrpcData

    class ReturnType(BaseModel):
        value: FuncParams

    req = RequestType(runtime=runtime, data=data)
    res = rpc_request("call_grpc_method", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value