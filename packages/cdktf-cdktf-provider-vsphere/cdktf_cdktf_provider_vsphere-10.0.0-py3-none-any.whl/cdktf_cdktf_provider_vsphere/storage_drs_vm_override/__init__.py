r'''
# `vsphere_storage_drs_vm_override`

Refer to the Terraform Registry for docs: [`vsphere_storage_drs_vm_override`](https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/storage_drs_vm_override).
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


class StorageDrsVmOverride(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.storageDrsVmOverride.StorageDrsVmOverride",
):
    '''Represents a {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/storage_drs_vm_override vsphere_storage_drs_vm_override}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        datastore_cluster_id: builtins.str,
        virtual_machine_id: builtins.str,
        id: typing.Optional[builtins.str] = None,
        sdrs_automation_level: typing.Optional[builtins.str] = None,
        sdrs_enabled: typing.Optional[builtins.str] = None,
        sdrs_intra_vm_affinity: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/storage_drs_vm_override vsphere_storage_drs_vm_override} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param datastore_cluster_id: The managed object ID of the datastore cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/storage_drs_vm_override#datastore_cluster_id StorageDrsVmOverride#datastore_cluster_id}
        :param virtual_machine_id: The managed object ID of the virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/storage_drs_vm_override#virtual_machine_id StorageDrsVmOverride#virtual_machine_id}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/storage_drs_vm_override#id StorageDrsVmOverride#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param sdrs_automation_level: Overrides any Storage DRS automation levels for this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/storage_drs_vm_override#sdrs_automation_level StorageDrsVmOverride#sdrs_automation_level}
        :param sdrs_enabled: Overrides the default Storage DRS setting for this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/storage_drs_vm_override#sdrs_enabled StorageDrsVmOverride#sdrs_enabled}
        :param sdrs_intra_vm_affinity: Overrides the intra-VM affinity setting for this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/storage_drs_vm_override#sdrs_intra_vm_affinity StorageDrsVmOverride#sdrs_intra_vm_affinity}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4fcf893ab74141f76e3e898de0d79bdfac36b04fa8a740d457c5876a1096f1c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = StorageDrsVmOverrideConfig(
            datastore_cluster_id=datastore_cluster_id,
            virtual_machine_id=virtual_machine_id,
            id=id,
            sdrs_automation_level=sdrs_automation_level,
            sdrs_enabled=sdrs_enabled,
            sdrs_intra_vm_affinity=sdrs_intra_vm_affinity,
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
        '''Generates CDKTF code for importing a StorageDrsVmOverride resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the StorageDrsVmOverride to import.
        :param import_from_id: The id of the existing StorageDrsVmOverride that should be imported. Refer to the {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/storage_drs_vm_override#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the StorageDrsVmOverride to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf699c3bc61f760a9c336166a4332c3c1e8d7e173e937608c4fba023baba7891)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetSdrsAutomationLevel")
    def reset_sdrs_automation_level(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSdrsAutomationLevel", []))

    @jsii.member(jsii_name="resetSdrsEnabled")
    def reset_sdrs_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSdrsEnabled", []))

    @jsii.member(jsii_name="resetSdrsIntraVmAffinity")
    def reset_sdrs_intra_vm_affinity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSdrsIntraVmAffinity", []))

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
    @jsii.member(jsii_name="datastoreClusterIdInput")
    def datastore_cluster_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "datastoreClusterIdInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="sdrsAutomationLevelInput")
    def sdrs_automation_level_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sdrsAutomationLevelInput"))

    @builtins.property
    @jsii.member(jsii_name="sdrsEnabledInput")
    def sdrs_enabled_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sdrsEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="sdrsIntraVmAffinityInput")
    def sdrs_intra_vm_affinity_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sdrsIntraVmAffinityInput"))

    @builtins.property
    @jsii.member(jsii_name="virtualMachineIdInput")
    def virtual_machine_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "virtualMachineIdInput"))

    @builtins.property
    @jsii.member(jsii_name="datastoreClusterId")
    def datastore_cluster_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "datastoreClusterId"))

    @datastore_cluster_id.setter
    def datastore_cluster_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__637eed354b160f72a4f10f3dec20ca6fc55688fabae07821f9af593082962011)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "datastoreClusterId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a42474d59e8784ea293f9a273424a9004d0f25f44f358b9ac176b370681cb56)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sdrsAutomationLevel")
    def sdrs_automation_level(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sdrsAutomationLevel"))

    @sdrs_automation_level.setter
    def sdrs_automation_level(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36bb821f1ef03025d105a9146da3f5536c9b67c9d4105195bceed1f2b9ef5f94)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sdrsAutomationLevel", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sdrsEnabled")
    def sdrs_enabled(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sdrsEnabled"))

    @sdrs_enabled.setter
    def sdrs_enabled(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0cef87fcac5a8030895e6c0e017fe0895a6cebe8d9c2442860562f571bf81d82)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sdrsEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sdrsIntraVmAffinity")
    def sdrs_intra_vm_affinity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sdrsIntraVmAffinity"))

    @sdrs_intra_vm_affinity.setter
    def sdrs_intra_vm_affinity(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1465fb4f954e710de8721a09b4896c8e4606ba4044b87ce85641af869819bfbe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sdrsIntraVmAffinity", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="virtualMachineId")
    def virtual_machine_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "virtualMachineId"))

    @virtual_machine_id.setter
    def virtual_machine_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35717d92952cc36b7d37ae29ea232fcf3d16cdc9fbf22f21b857fd972d0d5216)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "virtualMachineId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.storageDrsVmOverride.StorageDrsVmOverrideConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "datastore_cluster_id": "datastoreClusterId",
        "virtual_machine_id": "virtualMachineId",
        "id": "id",
        "sdrs_automation_level": "sdrsAutomationLevel",
        "sdrs_enabled": "sdrsEnabled",
        "sdrs_intra_vm_affinity": "sdrsIntraVmAffinity",
    },
)
class StorageDrsVmOverrideConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        datastore_cluster_id: builtins.str,
        virtual_machine_id: builtins.str,
        id: typing.Optional[builtins.str] = None,
        sdrs_automation_level: typing.Optional[builtins.str] = None,
        sdrs_enabled: typing.Optional[builtins.str] = None,
        sdrs_intra_vm_affinity: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param datastore_cluster_id: The managed object ID of the datastore cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/storage_drs_vm_override#datastore_cluster_id StorageDrsVmOverride#datastore_cluster_id}
        :param virtual_machine_id: The managed object ID of the virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/storage_drs_vm_override#virtual_machine_id StorageDrsVmOverride#virtual_machine_id}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/storage_drs_vm_override#id StorageDrsVmOverride#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param sdrs_automation_level: Overrides any Storage DRS automation levels for this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/storage_drs_vm_override#sdrs_automation_level StorageDrsVmOverride#sdrs_automation_level}
        :param sdrs_enabled: Overrides the default Storage DRS setting for this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/storage_drs_vm_override#sdrs_enabled StorageDrsVmOverride#sdrs_enabled}
        :param sdrs_intra_vm_affinity: Overrides the intra-VM affinity setting for this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/storage_drs_vm_override#sdrs_intra_vm_affinity StorageDrsVmOverride#sdrs_intra_vm_affinity}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d382ad4132f4729fe1812bcee222add177b0ca3cfa3e260fcf48868b2a1038e0)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument datastore_cluster_id", value=datastore_cluster_id, expected_type=type_hints["datastore_cluster_id"])
            check_type(argname="argument virtual_machine_id", value=virtual_machine_id, expected_type=type_hints["virtual_machine_id"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument sdrs_automation_level", value=sdrs_automation_level, expected_type=type_hints["sdrs_automation_level"])
            check_type(argname="argument sdrs_enabled", value=sdrs_enabled, expected_type=type_hints["sdrs_enabled"])
            check_type(argname="argument sdrs_intra_vm_affinity", value=sdrs_intra_vm_affinity, expected_type=type_hints["sdrs_intra_vm_affinity"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "datastore_cluster_id": datastore_cluster_id,
            "virtual_machine_id": virtual_machine_id,
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
        if id is not None:
            self._values["id"] = id
        if sdrs_automation_level is not None:
            self._values["sdrs_automation_level"] = sdrs_automation_level
        if sdrs_enabled is not None:
            self._values["sdrs_enabled"] = sdrs_enabled
        if sdrs_intra_vm_affinity is not None:
            self._values["sdrs_intra_vm_affinity"] = sdrs_intra_vm_affinity

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
    def datastore_cluster_id(self) -> builtins.str:
        '''The managed object ID of the datastore cluster.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/storage_drs_vm_override#datastore_cluster_id StorageDrsVmOverride#datastore_cluster_id}
        '''
        result = self._values.get("datastore_cluster_id")
        assert result is not None, "Required property 'datastore_cluster_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def virtual_machine_id(self) -> builtins.str:
        '''The managed object ID of the virtual machine.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/storage_drs_vm_override#virtual_machine_id StorageDrsVmOverride#virtual_machine_id}
        '''
        result = self._values.get("virtual_machine_id")
        assert result is not None, "Required property 'virtual_machine_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/storage_drs_vm_override#id StorageDrsVmOverride#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sdrs_automation_level(self) -> typing.Optional[builtins.str]:
        '''Overrides any Storage DRS automation levels for this virtual machine.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/storage_drs_vm_override#sdrs_automation_level StorageDrsVmOverride#sdrs_automation_level}
        '''
        result = self._values.get("sdrs_automation_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sdrs_enabled(self) -> typing.Optional[builtins.str]:
        '''Overrides the default Storage DRS setting for this virtual machine.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/storage_drs_vm_override#sdrs_enabled StorageDrsVmOverride#sdrs_enabled}
        '''
        result = self._values.get("sdrs_enabled")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sdrs_intra_vm_affinity(self) -> typing.Optional[builtins.str]:
        '''Overrides the intra-VM affinity setting for this virtual machine.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/storage_drs_vm_override#sdrs_intra_vm_affinity StorageDrsVmOverride#sdrs_intra_vm_affinity}
        '''
        result = self._values.get("sdrs_intra_vm_affinity")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StorageDrsVmOverrideConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "StorageDrsVmOverride",
    "StorageDrsVmOverrideConfig",
]

publication.publish()

def _typecheckingstub__d4fcf893ab74141f76e3e898de0d79bdfac36b04fa8a740d457c5876a1096f1c(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    datastore_cluster_id: builtins.str,
    virtual_machine_id: builtins.str,
    id: typing.Optional[builtins.str] = None,
    sdrs_automation_level: typing.Optional[builtins.str] = None,
    sdrs_enabled: typing.Optional[builtins.str] = None,
    sdrs_intra_vm_affinity: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__cf699c3bc61f760a9c336166a4332c3c1e8d7e173e937608c4fba023baba7891(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__637eed354b160f72a4f10f3dec20ca6fc55688fabae07821f9af593082962011(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a42474d59e8784ea293f9a273424a9004d0f25f44f358b9ac176b370681cb56(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36bb821f1ef03025d105a9146da3f5536c9b67c9d4105195bceed1f2b9ef5f94(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0cef87fcac5a8030895e6c0e017fe0895a6cebe8d9c2442860562f571bf81d82(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1465fb4f954e710de8721a09b4896c8e4606ba4044b87ce85641af869819bfbe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35717d92952cc36b7d37ae29ea232fcf3d16cdc9fbf22f21b857fd972d0d5216(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d382ad4132f4729fe1812bcee222add177b0ca3cfa3e260fcf48868b2a1038e0(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    datastore_cluster_id: builtins.str,
    virtual_machine_id: builtins.str,
    id: typing.Optional[builtins.str] = None,
    sdrs_automation_level: typing.Optional[builtins.str] = None,
    sdrs_enabled: typing.Optional[builtins.str] = None,
    sdrs_intra_vm_affinity: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
