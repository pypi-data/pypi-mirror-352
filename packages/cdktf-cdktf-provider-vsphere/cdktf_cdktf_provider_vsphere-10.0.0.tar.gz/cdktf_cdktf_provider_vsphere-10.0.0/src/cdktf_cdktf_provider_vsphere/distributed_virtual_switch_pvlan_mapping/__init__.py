r'''
# `vsphere_distributed_virtual_switch_pvlan_mapping`

Refer to the Terraform Registry for docs: [`vsphere_distributed_virtual_switch_pvlan_mapping`](https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch_pvlan_mapping).
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


class DistributedVirtualSwitchPvlanMappingA(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.distributedVirtualSwitchPvlanMapping.DistributedVirtualSwitchPvlanMappingA",
):
    '''Represents a {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch_pvlan_mapping vsphere_distributed_virtual_switch_pvlan_mapping}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        distributed_virtual_switch_id: builtins.str,
        primary_vlan_id: jsii.Number,
        pvlan_type: builtins.str,
        secondary_vlan_id: jsii.Number,
        id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch_pvlan_mapping vsphere_distributed_virtual_switch_pvlan_mapping} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param distributed_virtual_switch_id: The ID of the distributed virtual switch to attach this mapping to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch_pvlan_mapping#distributed_virtual_switch_id DistributedVirtualSwitchPvlanMappingA#distributed_virtual_switch_id}
        :param primary_vlan_id: The primary VLAN ID. The VLAN IDs of 0 and 4095 are reserved and cannot be used in this property. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch_pvlan_mapping#primary_vlan_id DistributedVirtualSwitchPvlanMappingA#primary_vlan_id}
        :param pvlan_type: The private VLAN type. Valid values are promiscuous, community and isolated. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch_pvlan_mapping#pvlan_type DistributedVirtualSwitchPvlanMappingA#pvlan_type}
        :param secondary_vlan_id: The secondary VLAN ID. The VLAN IDs of 0 and 4095 are reserved and cannot be used in this property. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch_pvlan_mapping#secondary_vlan_id DistributedVirtualSwitchPvlanMappingA#secondary_vlan_id}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch_pvlan_mapping#id DistributedVirtualSwitchPvlanMappingA#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e9ac87064d9fe18e68e6d2b493b9096d058b14199b24f7cf8f56fc47699b797)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DistributedVirtualSwitchPvlanMappingAConfig(
            distributed_virtual_switch_id=distributed_virtual_switch_id,
            primary_vlan_id=primary_vlan_id,
            pvlan_type=pvlan_type,
            secondary_vlan_id=secondary_vlan_id,
            id=id,
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
        '''Generates CDKTF code for importing a DistributedVirtualSwitchPvlanMappingA resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DistributedVirtualSwitchPvlanMappingA to import.
        :param import_from_id: The id of the existing DistributedVirtualSwitchPvlanMappingA that should be imported. Refer to the {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch_pvlan_mapping#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DistributedVirtualSwitchPvlanMappingA to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f9d0011aee04b0590f8ae2d7d45d15d2e7ff5907c4d99252d3d30e87ddc5635)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

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
    @jsii.member(jsii_name="distributedVirtualSwitchIdInput")
    def distributed_virtual_switch_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "distributedVirtualSwitchIdInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="primaryVlanIdInput")
    def primary_vlan_id_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "primaryVlanIdInput"))

    @builtins.property
    @jsii.member(jsii_name="pvlanTypeInput")
    def pvlan_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pvlanTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="secondaryVlanIdInput")
    def secondary_vlan_id_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "secondaryVlanIdInput"))

    @builtins.property
    @jsii.member(jsii_name="distributedVirtualSwitchId")
    def distributed_virtual_switch_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "distributedVirtualSwitchId"))

    @distributed_virtual_switch_id.setter
    def distributed_virtual_switch_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3fb08431130592eff2023fabab22090ecbece715d791302e76fecad23397134b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "distributedVirtualSwitchId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d02bc3eee7a7166de8fa53490f260e1e9666a46910ebbbb1fdecdf4f27b0c643)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="primaryVlanId")
    def primary_vlan_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "primaryVlanId"))

    @primary_vlan_id.setter
    def primary_vlan_id(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d389dedb1909404d10bded76f1dd609ff1f5d03e540781def18ca5f57856c99)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "primaryVlanId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pvlanType")
    def pvlan_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pvlanType"))

    @pvlan_type.setter
    def pvlan_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4a35dbf225832528ebc272e2442de521a67095a89090041498e36b4b088ce1c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pvlanType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="secondaryVlanId")
    def secondary_vlan_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "secondaryVlanId"))

    @secondary_vlan_id.setter
    def secondary_vlan_id(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ca840d8a78004d2367a1bb096a392bb3f3919f4776db5a527844aff39d039b6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secondaryVlanId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.distributedVirtualSwitchPvlanMapping.DistributedVirtualSwitchPvlanMappingAConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "distributed_virtual_switch_id": "distributedVirtualSwitchId",
        "primary_vlan_id": "primaryVlanId",
        "pvlan_type": "pvlanType",
        "secondary_vlan_id": "secondaryVlanId",
        "id": "id",
    },
)
class DistributedVirtualSwitchPvlanMappingAConfig(
    _cdktf_9a9027ec.TerraformMetaArguments,
):
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
        distributed_virtual_switch_id: builtins.str,
        primary_vlan_id: jsii.Number,
        pvlan_type: builtins.str,
        secondary_vlan_id: jsii.Number,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param distributed_virtual_switch_id: The ID of the distributed virtual switch to attach this mapping to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch_pvlan_mapping#distributed_virtual_switch_id DistributedVirtualSwitchPvlanMappingA#distributed_virtual_switch_id}
        :param primary_vlan_id: The primary VLAN ID. The VLAN IDs of 0 and 4095 are reserved and cannot be used in this property. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch_pvlan_mapping#primary_vlan_id DistributedVirtualSwitchPvlanMappingA#primary_vlan_id}
        :param pvlan_type: The private VLAN type. Valid values are promiscuous, community and isolated. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch_pvlan_mapping#pvlan_type DistributedVirtualSwitchPvlanMappingA#pvlan_type}
        :param secondary_vlan_id: The secondary VLAN ID. The VLAN IDs of 0 and 4095 are reserved and cannot be used in this property. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch_pvlan_mapping#secondary_vlan_id DistributedVirtualSwitchPvlanMappingA#secondary_vlan_id}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch_pvlan_mapping#id DistributedVirtualSwitchPvlanMappingA#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c2605517212ae4673d0e45347a5d0193bf720e290fb39a04583601367132574f)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument distributed_virtual_switch_id", value=distributed_virtual_switch_id, expected_type=type_hints["distributed_virtual_switch_id"])
            check_type(argname="argument primary_vlan_id", value=primary_vlan_id, expected_type=type_hints["primary_vlan_id"])
            check_type(argname="argument pvlan_type", value=pvlan_type, expected_type=type_hints["pvlan_type"])
            check_type(argname="argument secondary_vlan_id", value=secondary_vlan_id, expected_type=type_hints["secondary_vlan_id"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "distributed_virtual_switch_id": distributed_virtual_switch_id,
            "primary_vlan_id": primary_vlan_id,
            "pvlan_type": pvlan_type,
            "secondary_vlan_id": secondary_vlan_id,
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
    def distributed_virtual_switch_id(self) -> builtins.str:
        '''The ID of the distributed virtual switch to attach this mapping to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch_pvlan_mapping#distributed_virtual_switch_id DistributedVirtualSwitchPvlanMappingA#distributed_virtual_switch_id}
        '''
        result = self._values.get("distributed_virtual_switch_id")
        assert result is not None, "Required property 'distributed_virtual_switch_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def primary_vlan_id(self) -> jsii.Number:
        '''The primary VLAN ID.

        The VLAN IDs of 0 and 4095 are reserved and cannot be used in this property.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch_pvlan_mapping#primary_vlan_id DistributedVirtualSwitchPvlanMappingA#primary_vlan_id}
        '''
        result = self._values.get("primary_vlan_id")
        assert result is not None, "Required property 'primary_vlan_id' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def pvlan_type(self) -> builtins.str:
        '''The private VLAN type. Valid values are promiscuous, community and isolated.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch_pvlan_mapping#pvlan_type DistributedVirtualSwitchPvlanMappingA#pvlan_type}
        '''
        result = self._values.get("pvlan_type")
        assert result is not None, "Required property 'pvlan_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def secondary_vlan_id(self) -> jsii.Number:
        '''The secondary VLAN ID.

        The VLAN IDs of 0 and 4095 are reserved and cannot be used in this property.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch_pvlan_mapping#secondary_vlan_id DistributedVirtualSwitchPvlanMappingA#secondary_vlan_id}
        '''
        result = self._values.get("secondary_vlan_id")
        assert result is not None, "Required property 'secondary_vlan_id' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch_pvlan_mapping#id DistributedVirtualSwitchPvlanMappingA#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DistributedVirtualSwitchPvlanMappingAConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DistributedVirtualSwitchPvlanMappingA",
    "DistributedVirtualSwitchPvlanMappingAConfig",
]

publication.publish()

def _typecheckingstub__6e9ac87064d9fe18e68e6d2b493b9096d058b14199b24f7cf8f56fc47699b797(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    distributed_virtual_switch_id: builtins.str,
    primary_vlan_id: jsii.Number,
    pvlan_type: builtins.str,
    secondary_vlan_id: jsii.Number,
    id: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__7f9d0011aee04b0590f8ae2d7d45d15d2e7ff5907c4d99252d3d30e87ddc5635(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3fb08431130592eff2023fabab22090ecbece715d791302e76fecad23397134b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d02bc3eee7a7166de8fa53490f260e1e9666a46910ebbbb1fdecdf4f27b0c643(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d389dedb1909404d10bded76f1dd609ff1f5d03e540781def18ca5f57856c99(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4a35dbf225832528ebc272e2442de521a67095a89090041498e36b4b088ce1c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ca840d8a78004d2367a1bb096a392bb3f3919f4776db5a527844aff39d039b6(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2605517212ae4673d0e45347a5d0193bf720e290fb39a04583601367132574f(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    distributed_virtual_switch_id: builtins.str,
    primary_vlan_id: jsii.Number,
    pvlan_type: builtins.str,
    secondary_vlan_id: jsii.Number,
    id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
