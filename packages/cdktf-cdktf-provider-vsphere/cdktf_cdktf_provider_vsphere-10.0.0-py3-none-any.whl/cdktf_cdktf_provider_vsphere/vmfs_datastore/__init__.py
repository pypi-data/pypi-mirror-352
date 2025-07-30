r'''
# `vsphere_vmfs_datastore`

Refer to the Terraform Registry for docs: [`vsphere_vmfs_datastore`](https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vmfs_datastore).
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


class VmfsDatastore(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.vmfsDatastore.VmfsDatastore",
):
    '''Represents a {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vmfs_datastore vsphere_vmfs_datastore}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        disks: typing.Sequence[builtins.str],
        host_system_id: builtins.str,
        name: builtins.str,
        custom_attributes: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        datastore_cluster_id: typing.Optional[builtins.str] = None,
        folder: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vmfs_datastore vsphere_vmfs_datastore} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param disks: The disks to add to the datastore. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vmfs_datastore#disks VmfsDatastore#disks}
        :param host_system_id: The managed object ID of the host to set up the datastore on. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vmfs_datastore#host_system_id VmfsDatastore#host_system_id}
        :param name: The name of the datastore. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vmfs_datastore#name VmfsDatastore#name}
        :param custom_attributes: A list of custom attributes to set on this resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vmfs_datastore#custom_attributes VmfsDatastore#custom_attributes}
        :param datastore_cluster_id: The managed object ID of the datastore cluster to place the datastore in. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vmfs_datastore#datastore_cluster_id VmfsDatastore#datastore_cluster_id}
        :param folder: The path to the datastore folder to put the datastore in. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vmfs_datastore#folder VmfsDatastore#folder}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vmfs_datastore#id VmfsDatastore#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param tags: A list of tag IDs to apply to this object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vmfs_datastore#tags VmfsDatastore#tags}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f7ada1ef5232f11cfc1bc700712ff9f27a790423bd37ee761e72fc832a0876a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = VmfsDatastoreConfig(
            disks=disks,
            host_system_id=host_system_id,
            name=name,
            custom_attributes=custom_attributes,
            datastore_cluster_id=datastore_cluster_id,
            folder=folder,
            id=id,
            tags=tags,
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
        '''Generates CDKTF code for importing a VmfsDatastore resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the VmfsDatastore to import.
        :param import_from_id: The id of the existing VmfsDatastore that should be imported. Refer to the {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vmfs_datastore#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the VmfsDatastore to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6da5a66a610b33a143784a6f1949d2b5eb3090a843ef4436b401110b25689502)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetCustomAttributes")
    def reset_custom_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomAttributes", []))

    @jsii.member(jsii_name="resetDatastoreClusterId")
    def reset_datastore_cluster_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatastoreClusterId", []))

    @jsii.member(jsii_name="resetFolder")
    def reset_folder(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFolder", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

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
    @jsii.member(jsii_name="accessible")
    def accessible(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "accessible"))

    @builtins.property
    @jsii.member(jsii_name="capacity")
    def capacity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "capacity"))

    @builtins.property
    @jsii.member(jsii_name="freeSpace")
    def free_space(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "freeSpace"))

    @builtins.property
    @jsii.member(jsii_name="maintenanceMode")
    def maintenance_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maintenanceMode"))

    @builtins.property
    @jsii.member(jsii_name="multipleHostAccess")
    def multiple_host_access(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "multipleHostAccess"))

    @builtins.property
    @jsii.member(jsii_name="uncommittedSpace")
    def uncommitted_space(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "uncommittedSpace"))

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @builtins.property
    @jsii.member(jsii_name="customAttributesInput")
    def custom_attributes_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "customAttributesInput"))

    @builtins.property
    @jsii.member(jsii_name="datastoreClusterIdInput")
    def datastore_cluster_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "datastoreClusterIdInput"))

    @builtins.property
    @jsii.member(jsii_name="disksInput")
    def disks_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "disksInput"))

    @builtins.property
    @jsii.member(jsii_name="folderInput")
    def folder_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "folderInput"))

    @builtins.property
    @jsii.member(jsii_name="hostSystemIdInput")
    def host_system_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostSystemIdInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property
    @jsii.member(jsii_name="customAttributes")
    def custom_attributes(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "customAttributes"))

    @custom_attributes.setter
    def custom_attributes(
        self,
        value: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33463551429b2f988010cc19b5ca0026cd57332160d0617e2cc6ff835d15515c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customAttributes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="datastoreClusterId")
    def datastore_cluster_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "datastoreClusterId"))

    @datastore_cluster_id.setter
    def datastore_cluster_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72bd028cc37c2016cb8f2736263106e4ae219d27eca3647fccff49b3aa71beb3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "datastoreClusterId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="disks")
    def disks(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "disks"))

    @disks.setter
    def disks(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d66574cb41f02f4a04e0cc09f0fa6063e2b0c71e9fbdd79168abb9f29f886f5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disks", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="folder")
    def folder(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "folder"))

    @folder.setter
    def folder(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__09dfb5315264846d13cfafbc4c8bd7a5f031ba29df9537ded9c17d9c07a83072)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "folder", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="hostSystemId")
    def host_system_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostSystemId"))

    @host_system_id.setter
    def host_system_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d9c7b75a4b2169903cff714966d865e97b0d432aec1c6ffc7ccf8709cef44cee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hostSystemId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b0b9422cd0db89120a95efbe16f62954a901220659c0c63c659614615ebb5f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be459febdddbb1ae8c768d57d0cc6896b2fd052862a22d6c7a202fc3e6e7a5b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71d2c09cda2d68b271f098175df5707bb65b0f5999c8ec9e80ac050a0348d75c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.vmfsDatastore.VmfsDatastoreConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "disks": "disks",
        "host_system_id": "hostSystemId",
        "name": "name",
        "custom_attributes": "customAttributes",
        "datastore_cluster_id": "datastoreClusterId",
        "folder": "folder",
        "id": "id",
        "tags": "tags",
    },
)
class VmfsDatastoreConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        disks: typing.Sequence[builtins.str],
        host_system_id: builtins.str,
        name: builtins.str,
        custom_attributes: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        datastore_cluster_id: typing.Optional[builtins.str] = None,
        folder: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param disks: The disks to add to the datastore. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vmfs_datastore#disks VmfsDatastore#disks}
        :param host_system_id: The managed object ID of the host to set up the datastore on. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vmfs_datastore#host_system_id VmfsDatastore#host_system_id}
        :param name: The name of the datastore. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vmfs_datastore#name VmfsDatastore#name}
        :param custom_attributes: A list of custom attributes to set on this resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vmfs_datastore#custom_attributes VmfsDatastore#custom_attributes}
        :param datastore_cluster_id: The managed object ID of the datastore cluster to place the datastore in. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vmfs_datastore#datastore_cluster_id VmfsDatastore#datastore_cluster_id}
        :param folder: The path to the datastore folder to put the datastore in. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vmfs_datastore#folder VmfsDatastore#folder}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vmfs_datastore#id VmfsDatastore#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param tags: A list of tag IDs to apply to this object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vmfs_datastore#tags VmfsDatastore#tags}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a762dd7121685245bccd8cdad02482d523e8db03d63793955ad30be4583e896)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument disks", value=disks, expected_type=type_hints["disks"])
            check_type(argname="argument host_system_id", value=host_system_id, expected_type=type_hints["host_system_id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument custom_attributes", value=custom_attributes, expected_type=type_hints["custom_attributes"])
            check_type(argname="argument datastore_cluster_id", value=datastore_cluster_id, expected_type=type_hints["datastore_cluster_id"])
            check_type(argname="argument folder", value=folder, expected_type=type_hints["folder"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "disks": disks,
            "host_system_id": host_system_id,
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
        if custom_attributes is not None:
            self._values["custom_attributes"] = custom_attributes
        if datastore_cluster_id is not None:
            self._values["datastore_cluster_id"] = datastore_cluster_id
        if folder is not None:
            self._values["folder"] = folder
        if id is not None:
            self._values["id"] = id
        if tags is not None:
            self._values["tags"] = tags

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
    def disks(self) -> typing.List[builtins.str]:
        '''The disks to add to the datastore.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vmfs_datastore#disks VmfsDatastore#disks}
        '''
        result = self._values.get("disks")
        assert result is not None, "Required property 'disks' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def host_system_id(self) -> builtins.str:
        '''The managed object ID of the host to set up the datastore on.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vmfs_datastore#host_system_id VmfsDatastore#host_system_id}
        '''
        result = self._values.get("host_system_id")
        assert result is not None, "Required property 'host_system_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the datastore.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vmfs_datastore#name VmfsDatastore#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def custom_attributes(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''A list of custom attributes to set on this resource.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vmfs_datastore#custom_attributes VmfsDatastore#custom_attributes}
        '''
        result = self._values.get("custom_attributes")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def datastore_cluster_id(self) -> typing.Optional[builtins.str]:
        '''The managed object ID of the datastore cluster to place the datastore in.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vmfs_datastore#datastore_cluster_id VmfsDatastore#datastore_cluster_id}
        '''
        result = self._values.get("datastore_cluster_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def folder(self) -> typing.Optional[builtins.str]:
        '''The path to the datastore folder to put the datastore in.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vmfs_datastore#folder VmfsDatastore#folder}
        '''
        result = self._values.get("folder")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vmfs_datastore#id VmfsDatastore#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of tag IDs to apply to this object.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vmfs_datastore#tags VmfsDatastore#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VmfsDatastoreConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "VmfsDatastore",
    "VmfsDatastoreConfig",
]

publication.publish()

def _typecheckingstub__1f7ada1ef5232f11cfc1bc700712ff9f27a790423bd37ee761e72fc832a0876a(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    disks: typing.Sequence[builtins.str],
    host_system_id: builtins.str,
    name: builtins.str,
    custom_attributes: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    datastore_cluster_id: typing.Optional[builtins.str] = None,
    folder: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
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

def _typecheckingstub__6da5a66a610b33a143784a6f1949d2b5eb3090a843ef4436b401110b25689502(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33463551429b2f988010cc19b5ca0026cd57332160d0617e2cc6ff835d15515c(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72bd028cc37c2016cb8f2736263106e4ae219d27eca3647fccff49b3aa71beb3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d66574cb41f02f4a04e0cc09f0fa6063e2b0c71e9fbdd79168abb9f29f886f5(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09dfb5315264846d13cfafbc4c8bd7a5f031ba29df9537ded9c17d9c07a83072(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9c7b75a4b2169903cff714966d865e97b0d432aec1c6ffc7ccf8709cef44cee(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b0b9422cd0db89120a95efbe16f62954a901220659c0c63c659614615ebb5f9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be459febdddbb1ae8c768d57d0cc6896b2fd052862a22d6c7a202fc3e6e7a5b4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71d2c09cda2d68b271f098175df5707bb65b0f5999c8ec9e80ac050a0348d75c(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a762dd7121685245bccd8cdad02482d523e8db03d63793955ad30be4583e896(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    disks: typing.Sequence[builtins.str],
    host_system_id: builtins.str,
    name: builtins.str,
    custom_attributes: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    datastore_cluster_id: typing.Optional[builtins.str] = None,
    folder: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass
