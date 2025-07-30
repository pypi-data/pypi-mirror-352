r'''
# `vsphere_content_library_item`

Refer to the Terraform Registry for docs: [`vsphere_content_library_item`](https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/content_library_item).
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

from .._jsii import *

import cdktf as _cdktf_9a9027ec
import constructs as _constructs_77d1e7e8


class ContentLibraryItem(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.contentLibraryItem.ContentLibraryItem",
):
    '''Represents a {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/content_library_item vsphere_content_library_item}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        library_id: builtins.str,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        file_url: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        source_uuid: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/content_library_item vsphere_content_library_item} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param library_id: ID of the content library to contain item. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/content_library_item#library_id ContentLibraryItem#library_id}
        :param name: The name of the content library item. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/content_library_item#name ContentLibraryItem#name}
        :param description: Optional description of the content library item. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/content_library_item#description ContentLibraryItem#description}
        :param file_url: ID of source VM of content library item. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/content_library_item#file_url ContentLibraryItem#file_url}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/content_library_item#id ContentLibraryItem#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param source_uuid: The managed object ID of an existing VM to be cloned to the content library. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/content_library_item#source_uuid ContentLibraryItem#source_uuid}
        :param type: Type of content library item. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/content_library_item#type ContentLibraryItem#type}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f63eb8884f6cb087a33cbd116db8a4c77c055d120103dd69e4a13d1b89374b4)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ContentLibraryItemConfig(
            library_id=library_id,
            name=name,
            description=description,
            file_url=file_url,
            id=id,
            source_uuid=source_uuid,
            type=type,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a ContentLibraryItem resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ContentLibraryItem to import.
        :param import_from_id: The id of the existing ContentLibraryItem that should be imported. Refer to the {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/content_library_item#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ContentLibraryItem to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55d315bc0245c35e5a77de66d427ffb7ff506060edc93ef41fc112a224f8c927)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetFileUrl")
    def reset_file_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFileUrl", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetSourceUuid")
    def reset_source_uuid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceUuid", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.member(jsii_name="synthesizeHclAttributes")
    def _synthesize_hcl_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeHclAttributes", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="fileUrlInput")
    def file_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fileUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="libraryIdInput")
    def library_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "libraryIdInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="sourceUuidInput")
    def source_uuid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceUuidInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5c42b8bb8f005a3d500502e92400383e3cea90926f355665a7c4996ba9906562)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="fileUrl")
    def file_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fileUrl"))

    @file_url.setter
    def file_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f4c8bf9ca6132b77efbe3b4ea81e2dc6796e1a09c9b894f31a93b9b8c42966f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fileUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5148213296e19cd38efe6cce2b4ee616495452c41a3ef31b31c182620029124)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="libraryId")
    def library_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "libraryId"))

    @library_id.setter
    def library_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf77b1aa088d4de4a5c97a61df137f48036e265f29bd59bdf29aa771ebd6d4c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "libraryId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fea8ac79d6f2cc76ba15cd041ce94f0daf1146d42895371f18ce287bcb3e514b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sourceUuid")
    def source_uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceUuid"))

    @source_uuid.setter
    def source_uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e18ff6b72de3d98f5d09d5203995e71111b9e29752c644e766d5b3e1908dabe8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceUuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0baa599d0b4a0232fb55c626263127b8fbbc95094f8255175d9e8a66f3b887cf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.contentLibraryItem.ContentLibraryItemConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "library_id": "libraryId",
        "name": "name",
        "description": "description",
        "file_url": "fileUrl",
        "id": "id",
        "source_uuid": "sourceUuid",
        "type": "type",
    },
)
class ContentLibraryItemConfig(_cdktf_9a9027ec.TerraformMetaArguments):
    def __init__(
        self,
        *,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
        library_id: builtins.str,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        file_url: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        source_uuid: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param library_id: ID of the content library to contain item. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/content_library_item#library_id ContentLibraryItem#library_id}
        :param name: The name of the content library item. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/content_library_item#name ContentLibraryItem#name}
        :param description: Optional description of the content library item. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/content_library_item#description ContentLibraryItem#description}
        :param file_url: ID of source VM of content library item. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/content_library_item#file_url ContentLibraryItem#file_url}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/content_library_item#id ContentLibraryItem#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param source_uuid: The managed object ID of an existing VM to be cloned to the content library. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/content_library_item#source_uuid ContentLibraryItem#source_uuid}
        :param type: Type of content library item. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/content_library_item#type ContentLibraryItem#type}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71d7686a37d2e7077cc503de8b7efee77d1abd38ab9e51372c76d9c096120d87)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument library_id", value=library_id, expected_type=type_hints["library_id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument file_url", value=file_url, expected_type=type_hints["file_url"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument source_uuid", value=source_uuid, expected_type=type_hints["source_uuid"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "library_id": library_id,
            "name": name,
        }
        if connection is not None:
            self._values["connection"] = connection
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if for_each is not None:
            self._values["for_each"] = for_each
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if provisioners is not None:
            self._values["provisioners"] = provisioners
        if description is not None:
            self._values["description"] = description
        if file_url is not None:
            self._values["file_url"] = file_url
        if id is not None:
            self._values["id"] = id
        if source_uuid is not None:
            self._values["source_uuid"] = source_uuid
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def connection(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("connection")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]], result)

    @builtins.property
    def count(
        self,
    ) -> typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]], result)

    @builtins.property
    def depends_on(
        self,
    ) -> typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]], result)

    @builtins.property
    def for_each(self) -> typing.Optional[_cdktf_9a9027ec.ITerraformIterator]:
        '''
        :stability: experimental
        '''
        result = self._values.get("for_each")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.ITerraformIterator], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[_cdktf_9a9027ec.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformProvider], result)

    @builtins.property
    def provisioners(
        self,
    ) -> typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provisioners")
        return typing.cast(typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]], result)

    @builtins.property
    def library_id(self) -> builtins.str:
        '''ID of the content library to contain item.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/content_library_item#library_id ContentLibraryItem#library_id}
        '''
        result = self._values.get("library_id")
        assert result is not None, "Required property 'library_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the content library item.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/content_library_item#name ContentLibraryItem#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Optional description of the content library item.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/content_library_item#description ContentLibraryItem#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def file_url(self) -> typing.Optional[builtins.str]:
        '''ID of source VM of content library item.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/content_library_item#file_url ContentLibraryItem#file_url}
        '''
        result = self._values.get("file_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/content_library_item#id ContentLibraryItem#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_uuid(self) -> typing.Optional[builtins.str]:
        '''The managed object ID of an existing VM to be cloned to the content library.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/content_library_item#source_uuid ContentLibraryItem#source_uuid}
        '''
        result = self._values.get("source_uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Type of content library item.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/content_library_item#type ContentLibraryItem#type}
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContentLibraryItemConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ContentLibraryItem",
    "ContentLibraryItemConfig",
]

publication.publish()

def _typecheckingstub__3f63eb8884f6cb087a33cbd116db8a4c77c055d120103dd69e4a13d1b89374b4(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    library_id: builtins.str,
    name: builtins.str,
    description: typing.Optional[builtins.str] = None,
    file_url: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    source_uuid: typing.Optional[builtins.str] = None,
    type: typing.Optional[builtins.str] = None,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55d315bc0245c35e5a77de66d427ffb7ff506060edc93ef41fc112a224f8c927(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c42b8bb8f005a3d500502e92400383e3cea90926f355665a7c4996ba9906562(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f4c8bf9ca6132b77efbe3b4ea81e2dc6796e1a09c9b894f31a93b9b8c42966f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5148213296e19cd38efe6cce2b4ee616495452c41a3ef31b31c182620029124(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf77b1aa088d4de4a5c97a61df137f48036e265f29bd59bdf29aa771ebd6d4c0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fea8ac79d6f2cc76ba15cd041ce94f0daf1146d42895371f18ce287bcb3e514b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e18ff6b72de3d98f5d09d5203995e71111b9e29752c644e766d5b3e1908dabe8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0baa599d0b4a0232fb55c626263127b8fbbc95094f8255175d9e8a66f3b887cf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71d7686a37d2e7077cc503de8b7efee77d1abd38ab9e51372c76d9c096120d87(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    library_id: builtins.str,
    name: builtins.str,
    description: typing.Optional[builtins.str] = None,
    file_url: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    source_uuid: typing.Optional[builtins.str] = None,
    type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
