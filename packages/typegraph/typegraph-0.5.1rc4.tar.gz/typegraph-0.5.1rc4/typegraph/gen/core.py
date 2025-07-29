# Copyright Metatype OÜ, licensed under the Mozilla Public License Version 2.0.
# SPDX-License-Identifier: MPL-2.0

import typing_extensions as t
from pydantic import BaseModel
from typegraph.gen.client import rpc_request

class Error(BaseModel):
    stack: t.List[str]

    def __init__(self, stack: t.List[str], **kwargs):
        super().__init__(stack=stack, **kwargs)

TypeId = int

RuntimeId = int

MaterializerId = int

PolicyId = int

class Cors(BaseModel):
    allow_origin: t.List[str]
    allow_headers: t.List[str]
    expose_headers: t.List[str]
    allow_methods: t.List[str]
    allow_credentials: bool
    max_age_sec: t.Optional[int]

    def __init__(self, allow_origin: t.List[str], allow_headers: t.List[str], expose_headers: t.List[str], allow_methods: t.List[str], allow_credentials: bool, max_age_sec: t.Optional[int], **kwargs):
        super().__init__(allow_origin=allow_origin,allow_headers=allow_headers,expose_headers=expose_headers,allow_methods=allow_methods,allow_credentials=allow_credentials,max_age_sec=max_age_sec, **kwargs)

class Rate(BaseModel):
    window_limit: int
    window_sec: int
    query_limit: int
    context_identifier: t.Optional[str]
    local_excess: int

    def __init__(self, window_limit: int, window_sec: int, query_limit: int, context_identifier: t.Optional[str], local_excess: int, **kwargs):
        super().__init__(window_limit=window_limit,window_sec=window_sec,query_limit=query_limit,context_identifier=context_identifier,local_excess=local_excess, **kwargs)

class TypegraphInitParams(BaseModel):
    name: str
    dynamic: t.Optional[bool]
    path: str
    prefix: t.Optional[str]
    cors: Cors
    rate: t.Optional[Rate]

    def __init__(self, name: str, dynamic: t.Optional[bool], path: str, prefix: t.Optional[str], cors: Cors, rate: t.Optional[Rate], **kwargs):
        super().__init__(name=name,dynamic=dynamic,path=path,prefix=prefix,cors=cors,rate=rate, **kwargs)

class Artifact(BaseModel):
    path: str
    hash: str
    size: int

    def __init__(self, path: str, hash: str, size: int, **kwargs):
        super().__init__(path=path,hash=hash,size=size, **kwargs)

class MigrationAction(BaseModel):
    apply: bool
    create: bool
    reset: bool

    def __init__(self, apply: bool, create: bool, reset: bool, **kwargs):
        super().__init__(apply=apply,create=create,reset=reset, **kwargs)

class PrismaMigrationConfig(BaseModel):
    migrations_dir: str
    migration_actions: t.List[t.Tuple[str, MigrationAction]]
    default_migration_action: MigrationAction

    def __init__(self, migrations_dir: str, migration_actions: t.List[t.Tuple[str, MigrationAction]], default_migration_action: MigrationAction, **kwargs):
        super().__init__(migrations_dir=migrations_dir,migration_actions=migration_actions,default_migration_action=default_migration_action, **kwargs)

class SerializeParams(BaseModel):
    typegraph_name: str
    typegraph_path: str
    prefix: t.Optional[str]
    artifact_resolution: bool
    codegen: bool
    prisma_migration: PrismaMigrationConfig
    pretty: bool

    def __init__(self, typegraph_name: str, typegraph_path: str, prefix: t.Optional[str], artifact_resolution: bool, codegen: bool, prisma_migration: PrismaMigrationConfig, pretty: bool, **kwargs):
        super().__init__(typegraph_name=typegraph_name,typegraph_path=typegraph_path,prefix=prefix,artifact_resolution=artifact_resolution,codegen=codegen,prisma_migration=prisma_migration,pretty=pretty, **kwargs)

class TypeProxy(BaseModel):
    name: str
    extras: t.List[t.Tuple[str, str]]

    def __init__(self, name: str, extras: t.List[t.Tuple[str, str]], **kwargs):
        super().__init__(name=name,extras=extras, **kwargs)

class TypeInteger(BaseModel):
    min: t.Optional[int]
    max: t.Optional[int]
    exclusive_minimum: t.Optional[int]
    exclusive_maximum: t.Optional[int]
    multiple_of: t.Optional[int]
    enumeration: t.Optional[t.List[int]]

    def __init__(self, min: t.Optional[int], max: t.Optional[int], exclusive_minimum: t.Optional[int], exclusive_maximum: t.Optional[int], multiple_of: t.Optional[int], enumeration: t.Optional[t.List[int]], **kwargs):
        super().__init__(min=min,max=max,exclusive_minimum=exclusive_minimum,exclusive_maximum=exclusive_maximum,multiple_of=multiple_of,enumeration=enumeration, **kwargs)

class TypeFloat(BaseModel):
    min: t.Optional[float]
    max: t.Optional[float]
    exclusive_minimum: t.Optional[float]
    exclusive_maximum: t.Optional[float]
    multiple_of: t.Optional[float]
    enumeration: t.Optional[t.List[float]]

    def __init__(self, min: t.Optional[float], max: t.Optional[float], exclusive_minimum: t.Optional[float], exclusive_maximum: t.Optional[float], multiple_of: t.Optional[float], enumeration: t.Optional[t.List[float]], **kwargs):
        super().__init__(min=min,max=max,exclusive_minimum=exclusive_minimum,exclusive_maximum=exclusive_maximum,multiple_of=multiple_of,enumeration=enumeration, **kwargs)

class TypeString(BaseModel):
    max: t.Optional[int]
    min: t.Optional[int]
    format: t.Optional[str]
    pattern: t.Optional[str]
    enumeration: t.Optional[t.List[str]]

    def __init__(self, max: t.Optional[int], min: t.Optional[int], format: t.Optional[str], pattern: t.Optional[str], enumeration: t.Optional[t.List[str]], **kwargs):
        super().__init__(max=max,min=min,format=format,pattern=pattern,enumeration=enumeration, **kwargs)

class TypeFile(BaseModel):
    min: t.Optional[int]
    max: t.Optional[int]
    allow: t.Optional[t.List[str]]

    def __init__(self, min: t.Optional[int], max: t.Optional[int], allow: t.Optional[t.List[str]], **kwargs):
        super().__init__(min=min,max=max,allow=allow, **kwargs)

class TypeList(BaseModel):
    of: TypeId
    min: t.Optional[int]
    max: t.Optional[int]
    unique_items: t.Optional[bool]

    def __init__(self, of: TypeId, min: t.Optional[int], max: t.Optional[int], unique_items: t.Optional[bool], **kwargs):
        super().__init__(of=of,min=min,max=max,unique_items=unique_items, **kwargs)

class TypeOptional(BaseModel):
    of: TypeId
    default_item: t.Optional[str]

    def __init__(self, of: TypeId, default_item: t.Optional[str], **kwargs):
        super().__init__(of=of,default_item=default_item, **kwargs)

class TypeUnion(BaseModel):
    variants: t.List[TypeId]

    def __init__(self, variants: t.List[TypeId], **kwargs):
        super().__init__(variants=variants, **kwargs)

class TypeEither(BaseModel):
    variants: t.List[TypeId]

    def __init__(self, variants: t.List[TypeId], **kwargs):
        super().__init__(variants=variants, **kwargs)

class TypeStruct(BaseModel):
    props: t.List[t.Tuple[str, TypeId]]
    additional_props: bool
    min: t.Optional[int]
    max: t.Optional[int]
    enumeration: t.Optional[t.List[str]]

    def __init__(self, props: t.List[t.Tuple[str, TypeId]], additional_props: bool, min: t.Optional[int], max: t.Optional[int], enumeration: t.Optional[t.List[str]], **kwargs):
        super().__init__(props=props,additional_props=additional_props,min=min,max=max,enumeration=enumeration, **kwargs)

ValueSource = t.Union[
    t.TypedDict("ValueSourceRaw", {"raw": str}),
    t.TypedDict("ValueSourceContext", {"context": str}),
    t.TypedDict("ValueSourceSecret", {"secret": str}),
    t.TypedDict("ValueSourceParent", {"parent": str}),
    t.TypedDict("ValueSourceParam", {"param": str}),
]

class ParameterTransform(BaseModel):
    resolver_input: TypeId
    transform_tree: str

    def __init__(self, resolver_input: TypeId, transform_tree: str, **kwargs):
        super().__init__(resolver_input=resolver_input,transform_tree=transform_tree, **kwargs)

class TypeFunc(BaseModel):
    inp: TypeId
    parameter_transform: t.Optional[ParameterTransform]
    out: TypeId
    mat: MaterializerId
    rate_calls: bool
    rate_weight: t.Optional[int]

    def __init__(self, inp: TypeId, parameter_transform: t.Optional[ParameterTransform], out: TypeId, mat: MaterializerId, rate_calls: bool, rate_weight: t.Optional[int], **kwargs):
        super().__init__(inp=inp,parameter_transform=parameter_transform,out=out,mat=mat,rate_calls=rate_calls,rate_weight=rate_weight, **kwargs)

class TransformData(BaseModel):
    query_input: TypeId
    parameter_transform: ParameterTransform

    def __init__(self, query_input: TypeId, parameter_transform: ParameterTransform, **kwargs):
        super().__init__(query_input=query_input,parameter_transform=parameter_transform, **kwargs)

class Policy(BaseModel):
    name: str
    materializer: MaterializerId

    def __init__(self, name: str, materializer: MaterializerId, **kwargs):
        super().__init__(name=name,materializer=materializer, **kwargs)

class PolicyPerEffect(BaseModel):
    read: t.Optional[PolicyId]
    create: t.Optional[PolicyId]
    update: t.Optional[PolicyId]
    delete: t.Optional[PolicyId]

    def __init__(self, read: t.Optional[PolicyId], create: t.Optional[PolicyId], update: t.Optional[PolicyId], delete: t.Optional[PolicyId], **kwargs):
        super().__init__(read=read,create=create,update=update,delete=delete, **kwargs)

PolicySpec = t.Union[
    t.TypedDict("PolicySpecSimple", {"simple": PolicyId}),
    t.TypedDict("PolicySpecPerEffect", {"per_effect": PolicyPerEffect}),
]

ContextCheck = t.Union[
    t.Literal["not_null"],
    t.TypedDict("ContextCheckValue", {"value": str}),
    t.TypedDict("ContextCheckPattern", {"pattern": str}),
]

class FuncParams(BaseModel):
    inp: TypeId
    out: TypeId
    mat: MaterializerId

    def __init__(self, inp: TypeId, out: TypeId, mat: MaterializerId, **kwargs):
        super().__init__(inp=inp,out=out,mat=mat, **kwargs)

def init_typegraph(params: TypegraphInitParams) -> None:
    class RequestType(BaseModel):
        params: TypegraphInitParams

    class ReturnType(BaseModel):
        value: None

    req = RequestType(params=params)
    res = rpc_request("init_typegraph", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def serialize_typegraph(params: SerializeParams) -> t.Tuple[str, t.List[Artifact]]:
    class RequestType(BaseModel):
        params: SerializeParams

    class ReturnType(BaseModel):
        value: t.Tuple[str, t.List[Artifact]]

    req = RequestType(params=params)
    res = rpc_request("serialize_typegraph", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def with_injection(type_id: TypeId, injection: str) -> TypeId:
    class RequestType(BaseModel):
        type_id: TypeId
        injection: str

    class ReturnType(BaseModel):
        value: TypeId

    req = RequestType(type_id=type_id, injection=injection)
    res = rpc_request("with_injection", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def with_config(type_id: TypeId, config: str) -> TypeId:
    class RequestType(BaseModel):
        type_id: TypeId
        config: str

    class ReturnType(BaseModel):
        value: TypeId

    req = RequestType(type_id=type_id, config=config)
    res = rpc_request("with_config", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def refb(name: str, attributes: t.Optional[str] = None) -> TypeId:
    class RequestType(BaseModel):
        name: str
        attributes: t.Optional[str]

    class ReturnType(BaseModel):
        value: TypeId

    req = RequestType(name=name, attributes=attributes)
    res = rpc_request("refb", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def floatb(data: TypeFloat) -> TypeId:
    class RequestType(BaseModel):
        data: TypeFloat

    class ReturnType(BaseModel):
        value: TypeId

    req = RequestType(data=data)
    res = rpc_request("floatb", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def integerb(data: TypeInteger) -> TypeId:
    class RequestType(BaseModel):
        data: TypeInteger

    class ReturnType(BaseModel):
        value: TypeId

    req = RequestType(data=data)
    res = rpc_request("integerb", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def booleanb() -> TypeId:
    class ReturnType(BaseModel):
        value: TypeId

    res = rpc_request("booleanb")
    ret = ReturnType(value=res)

    return ret.value

def stringb(data: TypeString) -> TypeId:
    class RequestType(BaseModel):
        data: TypeString

    class ReturnType(BaseModel):
        value: TypeId

    req = RequestType(data=data)
    res = rpc_request("stringb", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def as_id(id: TypeId, composite: bool) -> TypeId:
    class RequestType(BaseModel):
        id: TypeId
        composite: bool

    class ReturnType(BaseModel):
        value: TypeId

    req = RequestType(id=id, composite=composite)
    res = rpc_request("as_id", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def fileb(data: TypeFile) -> TypeId:
    class RequestType(BaseModel):
        data: TypeFile

    class ReturnType(BaseModel):
        value: TypeId

    req = RequestType(data=data)
    res = rpc_request("fileb", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def listb(data: TypeList) -> TypeId:
    class RequestType(BaseModel):
        data: TypeList

    class ReturnType(BaseModel):
        value: TypeId

    req = RequestType(data=data)
    res = rpc_request("listb", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def optionalb(data: TypeOptional) -> TypeId:
    class RequestType(BaseModel):
        data: TypeOptional

    class ReturnType(BaseModel):
        value: TypeId

    req = RequestType(data=data)
    res = rpc_request("optionalb", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def unionb(data: TypeUnion) -> TypeId:
    class RequestType(BaseModel):
        data: TypeUnion

    class ReturnType(BaseModel):
        value: TypeId

    req = RequestType(data=data)
    res = rpc_request("unionb", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def eitherb(data: TypeEither) -> TypeId:
    class RequestType(BaseModel):
        data: TypeEither

    class ReturnType(BaseModel):
        value: TypeId

    req = RequestType(data=data)
    res = rpc_request("eitherb", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def structb(data: TypeStruct) -> TypeId:
    class RequestType(BaseModel):
        data: TypeStruct

    class ReturnType(BaseModel):
        value: TypeId

    req = RequestType(data=data)
    res = rpc_request("structb", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def extend_struct(tpe: TypeId, props: t.List[t.Tuple[str, TypeId]]) -> TypeId:
    class RequestType(BaseModel):
        tpe: TypeId
        props: t.List[t.Tuple[str, TypeId]]

    class ReturnType(BaseModel):
        value: TypeId

    req = RequestType(tpe=tpe, props=props)
    res = rpc_request("extend_struct", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def get_type_repr(id: TypeId) -> str:
    class RequestType(BaseModel):
        id: TypeId

    class ReturnType(BaseModel):
        value: str

    req = RequestType(id=id)
    res = rpc_request("get_type_repr", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def funcb(data: TypeFunc) -> TypeId:
    class RequestType(BaseModel):
        data: TypeFunc

    class ReturnType(BaseModel):
        value: TypeId

    req = RequestType(data=data)
    res = rpc_request("funcb", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def get_transform_data(resolver_input: TypeId, transform_tree: str) -> TransformData:
    class RequestType(BaseModel):
        resolver_input: TypeId
        transform_tree: str

    class ReturnType(BaseModel):
        value: TransformData

    req = RequestType(resolver_input=resolver_input, transform_tree=transform_tree)
    res = rpc_request("get_transform_data", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def register_policy(pol: Policy) -> PolicyId:
    class RequestType(BaseModel):
        pol: Policy

    class ReturnType(BaseModel):
        value: PolicyId

    req = RequestType(pol=pol)
    res = rpc_request("register_policy", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def with_policy(type_id: TypeId, policy_chain: t.List[PolicySpec]) -> TypeId:
    class RequestType(BaseModel):
        type_id: TypeId
        policy_chain: t.List[PolicySpec]

    class ReturnType(BaseModel):
        value: TypeId

    req = RequestType(type_id=type_id, policy_chain=policy_chain)
    res = rpc_request("with_policy", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def get_public_policy() -> t.Tuple[PolicyId, str]:
    class ReturnType(BaseModel):
        value: t.Tuple[PolicyId, str]

    res = rpc_request("get_public_policy")
    ret = ReturnType(value=res)

    return ret.value

def get_internal_policy() -> t.Tuple[PolicyId, str]:
    class ReturnType(BaseModel):
        value: t.Tuple[PolicyId, str]

    res = rpc_request("get_internal_policy")
    ret = ReturnType(value=res)

    return ret.value

def register_context_policy(key: str, check: ContextCheck) -> t.Tuple[PolicyId, str]:
    class RequestType(BaseModel):
        key: str
        check: ContextCheck

    class ReturnType(BaseModel):
        value: t.Tuple[PolicyId, str]

    req = RequestType(key=key, check=check)
    res = rpc_request("register_context_policy", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def rename_type(tpe: TypeId, new_name: str) -> TypeId:
    class RequestType(BaseModel):
        tpe: TypeId
        new_name: str

    class ReturnType(BaseModel):
        value: TypeId

    req = RequestType(tpe=tpe, new_name=new_name)
    res = rpc_request("rename_type", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def expose(fns: t.List[t.Tuple[str, TypeId]], default_policy: t.Optional[t.List[PolicySpec]] = None) -> None:
    class RequestType(BaseModel):
        fns: t.List[t.Tuple[str, TypeId]]
        default_policy: t.Optional[t.List[PolicySpec]]

    class ReturnType(BaseModel):
        value: None

    req = RequestType(fns=fns, default_policy=default_policy)
    res = rpc_request("expose", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value

def set_seed(seed: t.Optional[int] = None) -> None:
    class RequestType(BaseModel):
        seed: t.Optional[int]

    class ReturnType(BaseModel):
        value: None

    req = RequestType(seed=seed)
    res = rpc_request("set_seed", req.model_dump())
    ret = ReturnType(value=res)

    return ret.value