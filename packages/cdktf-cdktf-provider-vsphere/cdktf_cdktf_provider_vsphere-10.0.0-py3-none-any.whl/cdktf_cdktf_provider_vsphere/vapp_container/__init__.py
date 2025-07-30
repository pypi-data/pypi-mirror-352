r'''
# `vsphere_vapp_container`

Refer to the Terraform Registry for docs: [`vsphere_vapp_container`](https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container).
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


class VappContainer(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.vappContainer.VappContainer",
):
    '''Represents a {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container vsphere_vapp_container}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        parent_resource_pool_id: builtins.str,
        cpu_expandable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        cpu_limit: typing.Optional[jsii.Number] = None,
        cpu_reservation: typing.Optional[jsii.Number] = None,
        cpu_share_level: typing.Optional[builtins.str] = None,
        cpu_shares: typing.Optional[jsii.Number] = None,
        custom_attributes: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        memory_expandable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        memory_limit: typing.Optional[jsii.Number] = None,
        memory_reservation: typing.Optional[jsii.Number] = None,
        memory_share_level: typing.Optional[builtins.str] = None,
        memory_shares: typing.Optional[jsii.Number] = None,
        parent_folder_id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container vsphere_vapp_container} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: The name of the vApp container. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#name VappContainer#name}
        :param parent_resource_pool_id: The managed object ID of the parent resource pool or the compute resource the vApp container is in. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#parent_resource_pool_id VappContainer#parent_resource_pool_id}
        :param cpu_expandable: Determines if the reservation on a vApp container can grow beyond the specified value, if the parent resource pool has unreserved resources. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#cpu_expandable VappContainer#cpu_expandable}
        :param cpu_limit: The utilization of a vApp container will not exceed this limit, even if there are available resources. Set to -1 for unlimited. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#cpu_limit VappContainer#cpu_limit}
        :param cpu_reservation: Amount of CPU (MHz) that is guaranteed available to the vApp container. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#cpu_reservation VappContainer#cpu_reservation}
        :param cpu_share_level: The allocation level. The level is a simplified view of shares. Levels map to a pre-determined set of numeric values for shares. Can be one of low, normal, high, or custom. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#cpu_share_level VappContainer#cpu_share_level}
        :param cpu_shares: The number of shares allocated. Used to determine resource allocation in case of resource contention. If this is set, cpu_share_level must be custom. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#cpu_shares VappContainer#cpu_shares}
        :param custom_attributes: A list of custom attributes to set on this resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#custom_attributes VappContainer#custom_attributes}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#id VappContainer#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param memory_expandable: Determines if the reservation on a vApp container can grow beyond the specified value, if the parent resource pool has unreserved resources. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#memory_expandable VappContainer#memory_expandable}
        :param memory_limit: The utilization of a vApp container will not exceed this limit, even if there are available resources. Set to -1 for unlimited. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#memory_limit VappContainer#memory_limit}
        :param memory_reservation: Amount of memory (MB) that is guaranteed available to the vApp container. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#memory_reservation VappContainer#memory_reservation}
        :param memory_share_level: The allocation level. The level is a simplified view of shares. Levels map to a pre-determined set of numeric values for shares. Can be one of low, normal, high, or custom. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#memory_share_level VappContainer#memory_share_level}
        :param memory_shares: The number of shares allocated. Used to determine resource allocation in case of resource contention. If this is set, memory_share_level must be custom. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#memory_shares VappContainer#memory_shares}
        :param parent_folder_id: The ID of the parent VM folder. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#parent_folder_id VappContainer#parent_folder_id}
        :param tags: A list of tag IDs to apply to this object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#tags VappContainer#tags}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__31cef4d71d0934809b7ef0afc6b1fb62f6ff114eb0a6e859a3a5d85d1a7a8096)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = VappContainerConfig(
            name=name,
            parent_resource_pool_id=parent_resource_pool_id,
            cpu_expandable=cpu_expandable,
            cpu_limit=cpu_limit,
            cpu_reservation=cpu_reservation,
            cpu_share_level=cpu_share_level,
            cpu_shares=cpu_shares,
            custom_attributes=custom_attributes,
            id=id,
            memory_expandable=memory_expandable,
            memory_limit=memory_limit,
            memory_reservation=memory_reservation,
            memory_share_level=memory_share_level,
            memory_shares=memory_shares,
            parent_folder_id=parent_folder_id,
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
        '''Generates CDKTF code for importing a VappContainer resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the VappContainer to import.
        :param import_from_id: The id of the existing VappContainer that should be imported. Refer to the {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the VappContainer to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d89119a5689c3fe417e2353eb5d37adb63d5ffe48a18276b82d2c7c10dd3c146)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetCpuExpandable")
    def reset_cpu_expandable(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCpuExpandable", []))

    @jsii.member(jsii_name="resetCpuLimit")
    def reset_cpu_limit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCpuLimit", []))

    @jsii.member(jsii_name="resetCpuReservation")
    def reset_cpu_reservation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCpuReservation", []))

    @jsii.member(jsii_name="resetCpuShareLevel")
    def reset_cpu_share_level(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCpuShareLevel", []))

    @jsii.member(jsii_name="resetCpuShares")
    def reset_cpu_shares(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCpuShares", []))

    @jsii.member(jsii_name="resetCustomAttributes")
    def reset_custom_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomAttributes", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetMemoryExpandable")
    def reset_memory_expandable(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMemoryExpandable", []))

    @jsii.member(jsii_name="resetMemoryLimit")
    def reset_memory_limit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMemoryLimit", []))

    @jsii.member(jsii_name="resetMemoryReservation")
    def reset_memory_reservation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMemoryReservation", []))

    @jsii.member(jsii_name="resetMemoryShareLevel")
    def reset_memory_share_level(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMemoryShareLevel", []))

    @jsii.member(jsii_name="resetMemoryShares")
    def reset_memory_shares(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMemoryShares", []))

    @jsii.member(jsii_name="resetParentFolderId")
    def reset_parent_folder_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParentFolderId", []))

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
    @jsii.member(jsii_name="cpuExpandableInput")
    def cpu_expandable_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "cpuExpandableInput"))

    @builtins.property
    @jsii.member(jsii_name="cpuLimitInput")
    def cpu_limit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "cpuLimitInput"))

    @builtins.property
    @jsii.member(jsii_name="cpuReservationInput")
    def cpu_reservation_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "cpuReservationInput"))

    @builtins.property
    @jsii.member(jsii_name="cpuShareLevelInput")
    def cpu_share_level_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cpuShareLevelInput"))

    @builtins.property
    @jsii.member(jsii_name="cpuSharesInput")
    def cpu_shares_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "cpuSharesInput"))

    @builtins.property
    @jsii.member(jsii_name="customAttributesInput")
    def custom_attributes_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "customAttributesInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="memoryExpandableInput")
    def memory_expandable_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "memoryExpandableInput"))

    @builtins.property
    @jsii.member(jsii_name="memoryLimitInput")
    def memory_limit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "memoryLimitInput"))

    @builtins.property
    @jsii.member(jsii_name="memoryReservationInput")
    def memory_reservation_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "memoryReservationInput"))

    @builtins.property
    @jsii.member(jsii_name="memoryShareLevelInput")
    def memory_share_level_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "memoryShareLevelInput"))

    @builtins.property
    @jsii.member(jsii_name="memorySharesInput")
    def memory_shares_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "memorySharesInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="parentFolderIdInput")
    def parent_folder_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "parentFolderIdInput"))

    @builtins.property
    @jsii.member(jsii_name="parentResourcePoolIdInput")
    def parent_resource_pool_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "parentResourcePoolIdInput"))

    @builtins.property
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property
    @jsii.member(jsii_name="cpuExpandable")
    def cpu_expandable(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "cpuExpandable"))

    @cpu_expandable.setter
    def cpu_expandable(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b8af67494630cd88d63de6a70cf0c9ff7ce8a33f60847da3bcff0b6f02b7bec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cpuExpandable", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cpuLimit")
    def cpu_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cpuLimit"))

    @cpu_limit.setter
    def cpu_limit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__949d0a9f69b742fcd31b74183a9c724bcd272c38ce170a66085465610d66d716)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cpuLimit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cpuReservation")
    def cpu_reservation(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cpuReservation"))

    @cpu_reservation.setter
    def cpu_reservation(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f127875732a0d966d23419a401c807d0945a104df2f70bc446a26f8a927f24e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cpuReservation", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cpuShareLevel")
    def cpu_share_level(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cpuShareLevel"))

    @cpu_share_level.setter
    def cpu_share_level(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2d2e6b2b04989b1af3e75e5b9ca7cce63a1077a6b8e44b630d8f52491ce5afe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cpuShareLevel", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cpuShares")
    def cpu_shares(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cpuShares"))

    @cpu_shares.setter
    def cpu_shares(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3aa05e1c042462cfe11ffa2086c5e330d00d3dc859557fe3c0dbf1d43399698f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cpuShares", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__bd9aad77f646bc9a51742cd173913bc08befc037e4bf8768f5ce2421ae356c71)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customAttributes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0adba3b2976f48edd5853c1dd7698eae635e9c67d750dda9b671e53703027bb4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="memoryExpandable")
    def memory_expandable(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "memoryExpandable"))

    @memory_expandable.setter
    def memory_expandable(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b99e01aaf27c719d56e5eafe83ca871ce8979786705f484c99ef181949b68a85)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "memoryExpandable", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="memoryLimit")
    def memory_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "memoryLimit"))

    @memory_limit.setter
    def memory_limit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1feb438101ba1762f73c7620078e59f9ebab969ca78c0624caaa985b802504a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "memoryLimit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="memoryReservation")
    def memory_reservation(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "memoryReservation"))

    @memory_reservation.setter
    def memory_reservation(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__efea96baaa6a0900a043d04d5ac0c636851e094355b310245cbef8ccbea7a9ec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "memoryReservation", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="memoryShareLevel")
    def memory_share_level(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "memoryShareLevel"))

    @memory_share_level.setter
    def memory_share_level(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__364341b3507b59260731e4029202074b337e3cffb5acc97b5ffe380aee9487f1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "memoryShareLevel", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="memoryShares")
    def memory_shares(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "memoryShares"))

    @memory_shares.setter
    def memory_shares(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__03b0fc930362cc698cc31f81a646d463264c72ca98cd2f8f3bd04894eea60b1f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "memoryShares", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__774965be447da3c3b5569de10857e5f77906d51bf5257c480cbf8a0132e8594d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parentFolderId")
    def parent_folder_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parentFolderId"))

    @parent_folder_id.setter
    def parent_folder_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2189e654641c3ed338d3e8d46d685bcb6e60df34af14e62bf0aa9dcbc322bb8b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parentFolderId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parentResourcePoolId")
    def parent_resource_pool_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parentResourcePoolId"))

    @parent_resource_pool_id.setter
    def parent_resource_pool_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b6cf494ff6f784a933e6f75303f8e5517b0cbf1bf5d06c328e582f13c9e3d9f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parentResourcePoolId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__970f02b3e436d938b70c748efcbbfd3531950f82f02730105b19de642aadc624)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.vappContainer.VappContainerConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "name": "name",
        "parent_resource_pool_id": "parentResourcePoolId",
        "cpu_expandable": "cpuExpandable",
        "cpu_limit": "cpuLimit",
        "cpu_reservation": "cpuReservation",
        "cpu_share_level": "cpuShareLevel",
        "cpu_shares": "cpuShares",
        "custom_attributes": "customAttributes",
        "id": "id",
        "memory_expandable": "memoryExpandable",
        "memory_limit": "memoryLimit",
        "memory_reservation": "memoryReservation",
        "memory_share_level": "memoryShareLevel",
        "memory_shares": "memoryShares",
        "parent_folder_id": "parentFolderId",
        "tags": "tags",
    },
)
class VappContainerConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        name: builtins.str,
        parent_resource_pool_id: builtins.str,
        cpu_expandable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        cpu_limit: typing.Optional[jsii.Number] = None,
        cpu_reservation: typing.Optional[jsii.Number] = None,
        cpu_share_level: typing.Optional[builtins.str] = None,
        cpu_shares: typing.Optional[jsii.Number] = None,
        custom_attributes: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        memory_expandable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        memory_limit: typing.Optional[jsii.Number] = None,
        memory_reservation: typing.Optional[jsii.Number] = None,
        memory_share_level: typing.Optional[builtins.str] = None,
        memory_shares: typing.Optional[jsii.Number] = None,
        parent_folder_id: typing.Optional[builtins.str] = None,
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
        :param name: The name of the vApp container. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#name VappContainer#name}
        :param parent_resource_pool_id: The managed object ID of the parent resource pool or the compute resource the vApp container is in. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#parent_resource_pool_id VappContainer#parent_resource_pool_id}
        :param cpu_expandable: Determines if the reservation on a vApp container can grow beyond the specified value, if the parent resource pool has unreserved resources. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#cpu_expandable VappContainer#cpu_expandable}
        :param cpu_limit: The utilization of a vApp container will not exceed this limit, even if there are available resources. Set to -1 for unlimited. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#cpu_limit VappContainer#cpu_limit}
        :param cpu_reservation: Amount of CPU (MHz) that is guaranteed available to the vApp container. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#cpu_reservation VappContainer#cpu_reservation}
        :param cpu_share_level: The allocation level. The level is a simplified view of shares. Levels map to a pre-determined set of numeric values for shares. Can be one of low, normal, high, or custom. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#cpu_share_level VappContainer#cpu_share_level}
        :param cpu_shares: The number of shares allocated. Used to determine resource allocation in case of resource contention. If this is set, cpu_share_level must be custom. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#cpu_shares VappContainer#cpu_shares}
        :param custom_attributes: A list of custom attributes to set on this resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#custom_attributes VappContainer#custom_attributes}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#id VappContainer#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param memory_expandable: Determines if the reservation on a vApp container can grow beyond the specified value, if the parent resource pool has unreserved resources. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#memory_expandable VappContainer#memory_expandable}
        :param memory_limit: The utilization of a vApp container will not exceed this limit, even if there are available resources. Set to -1 for unlimited. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#memory_limit VappContainer#memory_limit}
        :param memory_reservation: Amount of memory (MB) that is guaranteed available to the vApp container. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#memory_reservation VappContainer#memory_reservation}
        :param memory_share_level: The allocation level. The level is a simplified view of shares. Levels map to a pre-determined set of numeric values for shares. Can be one of low, normal, high, or custom. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#memory_share_level VappContainer#memory_share_level}
        :param memory_shares: The number of shares allocated. Used to determine resource allocation in case of resource contention. If this is set, memory_share_level must be custom. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#memory_shares VappContainer#memory_shares}
        :param parent_folder_id: The ID of the parent VM folder. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#parent_folder_id VappContainer#parent_folder_id}
        :param tags: A list of tag IDs to apply to this object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#tags VappContainer#tags}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ef67a415f3a5eaa6887e33e37a97faa1045b4a581b0ffee2a4140b6746fc8d2)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument parent_resource_pool_id", value=parent_resource_pool_id, expected_type=type_hints["parent_resource_pool_id"])
            check_type(argname="argument cpu_expandable", value=cpu_expandable, expected_type=type_hints["cpu_expandable"])
            check_type(argname="argument cpu_limit", value=cpu_limit, expected_type=type_hints["cpu_limit"])
            check_type(argname="argument cpu_reservation", value=cpu_reservation, expected_type=type_hints["cpu_reservation"])
            check_type(argname="argument cpu_share_level", value=cpu_share_level, expected_type=type_hints["cpu_share_level"])
            check_type(argname="argument cpu_shares", value=cpu_shares, expected_type=type_hints["cpu_shares"])
            check_type(argname="argument custom_attributes", value=custom_attributes, expected_type=type_hints["custom_attributes"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument memory_expandable", value=memory_expandable, expected_type=type_hints["memory_expandable"])
            check_type(argname="argument memory_limit", value=memory_limit, expected_type=type_hints["memory_limit"])
            check_type(argname="argument memory_reservation", value=memory_reservation, expected_type=type_hints["memory_reservation"])
            check_type(argname="argument memory_share_level", value=memory_share_level, expected_type=type_hints["memory_share_level"])
            check_type(argname="argument memory_shares", value=memory_shares, expected_type=type_hints["memory_shares"])
            check_type(argname="argument parent_folder_id", value=parent_folder_id, expected_type=type_hints["parent_folder_id"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "parent_resource_pool_id": parent_resource_pool_id,
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
        if cpu_expandable is not None:
            self._values["cpu_expandable"] = cpu_expandable
        if cpu_limit is not None:
            self._values["cpu_limit"] = cpu_limit
        if cpu_reservation is not None:
            self._values["cpu_reservation"] = cpu_reservation
        if cpu_share_level is not None:
            self._values["cpu_share_level"] = cpu_share_level
        if cpu_shares is not None:
            self._values["cpu_shares"] = cpu_shares
        if custom_attributes is not None:
            self._values["custom_attributes"] = custom_attributes
        if id is not None:
            self._values["id"] = id
        if memory_expandable is not None:
            self._values["memory_expandable"] = memory_expandable
        if memory_limit is not None:
            self._values["memory_limit"] = memory_limit
        if memory_reservation is not None:
            self._values["memory_reservation"] = memory_reservation
        if memory_share_level is not None:
            self._values["memory_share_level"] = memory_share_level
        if memory_shares is not None:
            self._values["memory_shares"] = memory_shares
        if parent_folder_id is not None:
            self._values["parent_folder_id"] = parent_folder_id
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
    def name(self) -> builtins.str:
        '''The name of the vApp container.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#name VappContainer#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def parent_resource_pool_id(self) -> builtins.str:
        '''The managed object ID of the parent resource pool or the compute resource the vApp container is in.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#parent_resource_pool_id VappContainer#parent_resource_pool_id}
        '''
        result = self._values.get("parent_resource_pool_id")
        assert result is not None, "Required property 'parent_resource_pool_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cpu_expandable(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Determines if the reservation on a vApp container can grow beyond the specified value, if the parent resource pool has unreserved resources.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#cpu_expandable VappContainer#cpu_expandable}
        '''
        result = self._values.get("cpu_expandable")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def cpu_limit(self) -> typing.Optional[jsii.Number]:
        '''The utilization of a vApp container will not exceed this limit, even if there are available resources.

        Set to -1 for unlimited.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#cpu_limit VappContainer#cpu_limit}
        '''
        result = self._values.get("cpu_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def cpu_reservation(self) -> typing.Optional[jsii.Number]:
        '''Amount of CPU (MHz) that is guaranteed available to the vApp container.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#cpu_reservation VappContainer#cpu_reservation}
        '''
        result = self._values.get("cpu_reservation")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def cpu_share_level(self) -> typing.Optional[builtins.str]:
        '''The allocation level.

        The level is a simplified view of shares. Levels map to a pre-determined set of numeric values for shares. Can be one of low, normal, high, or custom.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#cpu_share_level VappContainer#cpu_share_level}
        '''
        result = self._values.get("cpu_share_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cpu_shares(self) -> typing.Optional[jsii.Number]:
        '''The number of shares allocated.

        Used to determine resource allocation in case of resource contention. If this is set, cpu_share_level must be custom.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#cpu_shares VappContainer#cpu_shares}
        '''
        result = self._values.get("cpu_shares")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def custom_attributes(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''A list of custom attributes to set on this resource.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#custom_attributes VappContainer#custom_attributes}
        '''
        result = self._values.get("custom_attributes")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#id VappContainer#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def memory_expandable(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Determines if the reservation on a vApp container can grow beyond the specified value, if the parent resource pool has unreserved resources.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#memory_expandable VappContainer#memory_expandable}
        '''
        result = self._values.get("memory_expandable")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def memory_limit(self) -> typing.Optional[jsii.Number]:
        '''The utilization of a vApp container will not exceed this limit, even if there are available resources.

        Set to -1 for unlimited.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#memory_limit VappContainer#memory_limit}
        '''
        result = self._values.get("memory_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def memory_reservation(self) -> typing.Optional[jsii.Number]:
        '''Amount of memory (MB) that is guaranteed available to the vApp container.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#memory_reservation VappContainer#memory_reservation}
        '''
        result = self._values.get("memory_reservation")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def memory_share_level(self) -> typing.Optional[builtins.str]:
        '''The allocation level.

        The level is a simplified view of shares. Levels map to a pre-determined set of numeric values for shares. Can be one of low, normal, high, or custom.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#memory_share_level VappContainer#memory_share_level}
        '''
        result = self._values.get("memory_share_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def memory_shares(self) -> typing.Optional[jsii.Number]:
        '''The number of shares allocated.

        Used to determine resource allocation in case of resource contention. If this is set, memory_share_level must be custom.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#memory_shares VappContainer#memory_shares}
        '''
        result = self._values.get("memory_shares")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def parent_folder_id(self) -> typing.Optional[builtins.str]:
        '''The ID of the parent VM folder.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#parent_folder_id VappContainer#parent_folder_id}
        '''
        result = self._values.get("parent_folder_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of tag IDs to apply to this object.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_container#tags VappContainer#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VappContainerConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "VappContainer",
    "VappContainerConfig",
]

publication.publish()

def _typecheckingstub__31cef4d71d0934809b7ef0afc6b1fb62f6ff114eb0a6e859a3a5d85d1a7a8096(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    parent_resource_pool_id: builtins.str,
    cpu_expandable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    cpu_limit: typing.Optional[jsii.Number] = None,
    cpu_reservation: typing.Optional[jsii.Number] = None,
    cpu_share_level: typing.Optional[builtins.str] = None,
    cpu_shares: typing.Optional[jsii.Number] = None,
    custom_attributes: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    memory_expandable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    memory_limit: typing.Optional[jsii.Number] = None,
    memory_reservation: typing.Optional[jsii.Number] = None,
    memory_share_level: typing.Optional[builtins.str] = None,
    memory_shares: typing.Optional[jsii.Number] = None,
    parent_folder_id: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__d89119a5689c3fe417e2353eb5d37adb63d5ffe48a18276b82d2c7c10dd3c146(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b8af67494630cd88d63de6a70cf0c9ff7ce8a33f60847da3bcff0b6f02b7bec(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__949d0a9f69b742fcd31b74183a9c724bcd272c38ce170a66085465610d66d716(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f127875732a0d966d23419a401c807d0945a104df2f70bc446a26f8a927f24e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2d2e6b2b04989b1af3e75e5b9ca7cce63a1077a6b8e44b630d8f52491ce5afe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3aa05e1c042462cfe11ffa2086c5e330d00d3dc859557fe3c0dbf1d43399698f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd9aad77f646bc9a51742cd173913bc08befc037e4bf8768f5ce2421ae356c71(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0adba3b2976f48edd5853c1dd7698eae635e9c67d750dda9b671e53703027bb4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b99e01aaf27c719d56e5eafe83ca871ce8979786705f484c99ef181949b68a85(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1feb438101ba1762f73c7620078e59f9ebab969ca78c0624caaa985b802504a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efea96baaa6a0900a043d04d5ac0c636851e094355b310245cbef8ccbea7a9ec(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__364341b3507b59260731e4029202074b337e3cffb5acc97b5ffe380aee9487f1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__03b0fc930362cc698cc31f81a646d463264c72ca98cd2f8f3bd04894eea60b1f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__774965be447da3c3b5569de10857e5f77906d51bf5257c480cbf8a0132e8594d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2189e654641c3ed338d3e8d46d685bcb6e60df34af14e62bf0aa9dcbc322bb8b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b6cf494ff6f784a933e6f75303f8e5517b0cbf1bf5d06c328e582f13c9e3d9f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__970f02b3e436d938b70c748efcbbfd3531950f82f02730105b19de642aadc624(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ef67a415f3a5eaa6887e33e37a97faa1045b4a581b0ffee2a4140b6746fc8d2(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    parent_resource_pool_id: builtins.str,
    cpu_expandable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    cpu_limit: typing.Optional[jsii.Number] = None,
    cpu_reservation: typing.Optional[jsii.Number] = None,
    cpu_share_level: typing.Optional[builtins.str] = None,
    cpu_shares: typing.Optional[jsii.Number] = None,
    custom_attributes: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    memory_expandable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    memory_limit: typing.Optional[jsii.Number] = None,
    memory_reservation: typing.Optional[jsii.Number] = None,
    memory_share_level: typing.Optional[builtins.str] = None,
    memory_shares: typing.Optional[jsii.Number] = None,
    parent_folder_id: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass
