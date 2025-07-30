r'''
# `vsphere_vapp_entity`

Refer to the Terraform Registry for docs: [`vsphere_vapp_entity`](https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_entity).
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


class VappEntity(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.vappEntity.VappEntity",
):
    '''Represents a {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_entity vsphere_vapp_entity}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        container_id: builtins.str,
        target_id: builtins.str,
        custom_attributes: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        start_action: typing.Optional[builtins.str] = None,
        start_delay: typing.Optional[jsii.Number] = None,
        start_order: typing.Optional[jsii.Number] = None,
        stop_action: typing.Optional[builtins.str] = None,
        stop_delay: typing.Optional[jsii.Number] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        wait_for_guest: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_entity vsphere_vapp_entity} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param container_id: Managed object ID of the vApp container the entity is a member of. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_entity#container_id VappEntity#container_id}
        :param target_id: Managed object ID of the entity to power on or power off. This can be a virtual machine or a vApp. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_entity#target_id VappEntity#target_id}
        :param custom_attributes: A list of custom attributes to set on this resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_entity#custom_attributes VappEntity#custom_attributes}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_entity#id VappEntity#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param start_action: How to start the entity. Valid settings are none or powerOn. If set to none, then the entity does not participate in auto-start. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_entity#start_action VappEntity#start_action}
        :param start_delay: Delay in seconds before continuing with the next entity in the order of entities to be started. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_entity#start_delay VappEntity#start_delay}
        :param start_order: Order to start and stop target in vApp. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_entity#start_order VappEntity#start_order}
        :param stop_action: Defines the stop action for the entity. Can be set to none, powerOff, guestShutdown, or suspend. If set to none, then the entity does not participate in auto-stop. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_entity#stop_action VappEntity#stop_action}
        :param stop_delay: Delay in seconds before continuing with the next entity in the order of entities to be stopped. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_entity#stop_delay VappEntity#stop_delay}
        :param tags: A list of tag IDs to apply to this object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_entity#tags VappEntity#tags}
        :param wait_for_guest: Determines if the VM should be marked as being started when VMware Tools are ready instead of waiting for start_delay. This property has no effect for vApps. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_entity#wait_for_guest VappEntity#wait_for_guest}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac2cc21f17371f0815d4e8609d4e0a056a14e1d3176272af38fb155519e412c3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = VappEntityConfig(
            container_id=container_id,
            target_id=target_id,
            custom_attributes=custom_attributes,
            id=id,
            start_action=start_action,
            start_delay=start_delay,
            start_order=start_order,
            stop_action=stop_action,
            stop_delay=stop_delay,
            tags=tags,
            wait_for_guest=wait_for_guest,
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
        '''Generates CDKTF code for importing a VappEntity resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the VappEntity to import.
        :param import_from_id: The id of the existing VappEntity that should be imported. Refer to the {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_entity#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the VappEntity to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2bbb24e1c9b6f77d1df0d2f3c23935f2289dd33f6a3a9b062ff7ddaa2e4d912)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetCustomAttributes")
    def reset_custom_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomAttributes", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetStartAction")
    def reset_start_action(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStartAction", []))

    @jsii.member(jsii_name="resetStartDelay")
    def reset_start_delay(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStartDelay", []))

    @jsii.member(jsii_name="resetStartOrder")
    def reset_start_order(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStartOrder", []))

    @jsii.member(jsii_name="resetStopAction")
    def reset_stop_action(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStopAction", []))

    @jsii.member(jsii_name="resetStopDelay")
    def reset_stop_delay(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStopDelay", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetWaitForGuest")
    def reset_wait_for_guest(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWaitForGuest", []))

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
    @jsii.member(jsii_name="containerIdInput")
    def container_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "containerIdInput"))

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
    @jsii.member(jsii_name="startActionInput")
    def start_action_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "startActionInput"))

    @builtins.property
    @jsii.member(jsii_name="startDelayInput")
    def start_delay_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "startDelayInput"))

    @builtins.property
    @jsii.member(jsii_name="startOrderInput")
    def start_order_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "startOrderInput"))

    @builtins.property
    @jsii.member(jsii_name="stopActionInput")
    def stop_action_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stopActionInput"))

    @builtins.property
    @jsii.member(jsii_name="stopDelayInput")
    def stop_delay_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "stopDelayInput"))

    @builtins.property
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property
    @jsii.member(jsii_name="targetIdInput")
    def target_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetIdInput"))

    @builtins.property
    @jsii.member(jsii_name="waitForGuestInput")
    def wait_for_guest_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "waitForGuestInput"))

    @builtins.property
    @jsii.member(jsii_name="containerId")
    def container_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "containerId"))

    @container_id.setter
    def container_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__663ae4c37f3cf45d66b04bd38a624ada2e6397a9d0673824578a6e0d8504a8c4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "containerId", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__23bd3e74ee5d3fd63dfca3f2e6dbc9802c5af284626409c56bb529ec1639e275)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customAttributes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2f1ffe7e1be5805b7bab36e38aa9d76fea9c849dfdbbe5106fbe9bfa79280b5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="startAction")
    def start_action(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "startAction"))

    @start_action.setter
    def start_action(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18235ff655e4582c2ca59de7b7a6327ee0a6e218265beafce452a203a573dcde)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "startAction", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="startDelay")
    def start_delay(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "startDelay"))

    @start_delay.setter
    def start_delay(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23c92a0fd4b406d2cb14531e2ae3e52f8097107e30149a677563c19b19ec15e6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "startDelay", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="startOrder")
    def start_order(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "startOrder"))

    @start_order.setter
    def start_order(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5cdd74937cf418eb810b1e8516b152374e09c1c6293c00cfd74b26078cbcc3bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "startOrder", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="stopAction")
    def stop_action(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stopAction"))

    @stop_action.setter
    def stop_action(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__59ff7b89ea05b3ee2b7cce22681727f0e949210dfc17cea9a92f783274f3fdae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stopAction", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="stopDelay")
    def stop_delay(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "stopDelay"))

    @stop_delay.setter
    def stop_delay(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a1fc3c870b6e09c43138bce05a4de2f5a103ce0522cd152bc07c7210e6de119)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stopDelay", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2d15dbd8bfb56db5fd868e5e9c04374c368c1ebd602c387b1a9e4128ac5d1a4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="targetId")
    def target_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetId"))

    @target_id.setter
    def target_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9dbc7740ba56f947c9bd785643b6d4b0d2560ae1d44a0e38911acb010b7ee9a4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="waitForGuest")
    def wait_for_guest(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "waitForGuest"))

    @wait_for_guest.setter
    def wait_for_guest(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e6bc1618d974a3651dc34575b6541c4c9230f3c97a734a072380b61fcbef4c1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "waitForGuest", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.vappEntity.VappEntityConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "container_id": "containerId",
        "target_id": "targetId",
        "custom_attributes": "customAttributes",
        "id": "id",
        "start_action": "startAction",
        "start_delay": "startDelay",
        "start_order": "startOrder",
        "stop_action": "stopAction",
        "stop_delay": "stopDelay",
        "tags": "tags",
        "wait_for_guest": "waitForGuest",
    },
)
class VappEntityConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        container_id: builtins.str,
        target_id: builtins.str,
        custom_attributes: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        start_action: typing.Optional[builtins.str] = None,
        start_delay: typing.Optional[jsii.Number] = None,
        start_order: typing.Optional[jsii.Number] = None,
        stop_action: typing.Optional[builtins.str] = None,
        stop_delay: typing.Optional[jsii.Number] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        wait_for_guest: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param container_id: Managed object ID of the vApp container the entity is a member of. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_entity#container_id VappEntity#container_id}
        :param target_id: Managed object ID of the entity to power on or power off. This can be a virtual machine or a vApp. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_entity#target_id VappEntity#target_id}
        :param custom_attributes: A list of custom attributes to set on this resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_entity#custom_attributes VappEntity#custom_attributes}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_entity#id VappEntity#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param start_action: How to start the entity. Valid settings are none or powerOn. If set to none, then the entity does not participate in auto-start. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_entity#start_action VappEntity#start_action}
        :param start_delay: Delay in seconds before continuing with the next entity in the order of entities to be started. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_entity#start_delay VappEntity#start_delay}
        :param start_order: Order to start and stop target in vApp. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_entity#start_order VappEntity#start_order}
        :param stop_action: Defines the stop action for the entity. Can be set to none, powerOff, guestShutdown, or suspend. If set to none, then the entity does not participate in auto-stop. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_entity#stop_action VappEntity#stop_action}
        :param stop_delay: Delay in seconds before continuing with the next entity in the order of entities to be stopped. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_entity#stop_delay VappEntity#stop_delay}
        :param tags: A list of tag IDs to apply to this object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_entity#tags VappEntity#tags}
        :param wait_for_guest: Determines if the VM should be marked as being started when VMware Tools are ready instead of waiting for start_delay. This property has no effect for vApps. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_entity#wait_for_guest VappEntity#wait_for_guest}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20861961d6d80b1bf7729680cacbf0a97abf934a3334d6b4495a15b1fcada92c)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument container_id", value=container_id, expected_type=type_hints["container_id"])
            check_type(argname="argument target_id", value=target_id, expected_type=type_hints["target_id"])
            check_type(argname="argument custom_attributes", value=custom_attributes, expected_type=type_hints["custom_attributes"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument start_action", value=start_action, expected_type=type_hints["start_action"])
            check_type(argname="argument start_delay", value=start_delay, expected_type=type_hints["start_delay"])
            check_type(argname="argument start_order", value=start_order, expected_type=type_hints["start_order"])
            check_type(argname="argument stop_action", value=stop_action, expected_type=type_hints["stop_action"])
            check_type(argname="argument stop_delay", value=stop_delay, expected_type=type_hints["stop_delay"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument wait_for_guest", value=wait_for_guest, expected_type=type_hints["wait_for_guest"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "container_id": container_id,
            "target_id": target_id,
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
        if id is not None:
            self._values["id"] = id
        if start_action is not None:
            self._values["start_action"] = start_action
        if start_delay is not None:
            self._values["start_delay"] = start_delay
        if start_order is not None:
            self._values["start_order"] = start_order
        if stop_action is not None:
            self._values["stop_action"] = stop_action
        if stop_delay is not None:
            self._values["stop_delay"] = stop_delay
        if tags is not None:
            self._values["tags"] = tags
        if wait_for_guest is not None:
            self._values["wait_for_guest"] = wait_for_guest

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
    def container_id(self) -> builtins.str:
        '''Managed object ID of the vApp container the entity is a member of.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_entity#container_id VappEntity#container_id}
        '''
        result = self._values.get("container_id")
        assert result is not None, "Required property 'container_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_id(self) -> builtins.str:
        '''Managed object ID of the entity to power on or power off.

        This can be a virtual machine or a vApp.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_entity#target_id VappEntity#target_id}
        '''
        result = self._values.get("target_id")
        assert result is not None, "Required property 'target_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def custom_attributes(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''A list of custom attributes to set on this resource.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_entity#custom_attributes VappEntity#custom_attributes}
        '''
        result = self._values.get("custom_attributes")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_entity#id VappEntity#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def start_action(self) -> typing.Optional[builtins.str]:
        '''How to start the entity.

        Valid settings are none or powerOn. If set to none, then the entity does not participate in auto-start.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_entity#start_action VappEntity#start_action}
        '''
        result = self._values.get("start_action")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def start_delay(self) -> typing.Optional[jsii.Number]:
        '''Delay in seconds before continuing with the next entity in the order of entities to be started.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_entity#start_delay VappEntity#start_delay}
        '''
        result = self._values.get("start_delay")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def start_order(self) -> typing.Optional[jsii.Number]:
        '''Order to start and stop target in vApp.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_entity#start_order VappEntity#start_order}
        '''
        result = self._values.get("start_order")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def stop_action(self) -> typing.Optional[builtins.str]:
        '''Defines the stop action for the entity.

        Can be set to none, powerOff, guestShutdown, or suspend. If set to none, then the entity does not participate in auto-stop.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_entity#stop_action VappEntity#stop_action}
        '''
        result = self._values.get("stop_action")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def stop_delay(self) -> typing.Optional[jsii.Number]:
        '''Delay in seconds before continuing with the next entity in the order of entities to be stopped.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_entity#stop_delay VappEntity#stop_delay}
        '''
        result = self._values.get("stop_delay")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of tag IDs to apply to this object.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_entity#tags VappEntity#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def wait_for_guest(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Determines if the VM should be marked as being started when VMware Tools are ready instead of waiting for start_delay.

        This property has no effect for vApps.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vapp_entity#wait_for_guest VappEntity#wait_for_guest}
        '''
        result = self._values.get("wait_for_guest")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VappEntityConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "VappEntity",
    "VappEntityConfig",
]

publication.publish()

def _typecheckingstub__ac2cc21f17371f0815d4e8609d4e0a056a14e1d3176272af38fb155519e412c3(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    container_id: builtins.str,
    target_id: builtins.str,
    custom_attributes: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    start_action: typing.Optional[builtins.str] = None,
    start_delay: typing.Optional[jsii.Number] = None,
    start_order: typing.Optional[jsii.Number] = None,
    stop_action: typing.Optional[builtins.str] = None,
    stop_delay: typing.Optional[jsii.Number] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    wait_for_guest: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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

def _typecheckingstub__a2bbb24e1c9b6f77d1df0d2f3c23935f2289dd33f6a3a9b062ff7ddaa2e4d912(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__663ae4c37f3cf45d66b04bd38a624ada2e6397a9d0673824578a6e0d8504a8c4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23bd3e74ee5d3fd63dfca3f2e6dbc9802c5af284626409c56bb529ec1639e275(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2f1ffe7e1be5805b7bab36e38aa9d76fea9c849dfdbbe5106fbe9bfa79280b5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18235ff655e4582c2ca59de7b7a6327ee0a6e218265beafce452a203a573dcde(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23c92a0fd4b406d2cb14531e2ae3e52f8097107e30149a677563c19b19ec15e6(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5cdd74937cf418eb810b1e8516b152374e09c1c6293c00cfd74b26078cbcc3bc(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59ff7b89ea05b3ee2b7cce22681727f0e949210dfc17cea9a92f783274f3fdae(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a1fc3c870b6e09c43138bce05a4de2f5a103ce0522cd152bc07c7210e6de119(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2d15dbd8bfb56db5fd868e5e9c04374c368c1ebd602c387b1a9e4128ac5d1a4(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9dbc7740ba56f947c9bd785643b6d4b0d2560ae1d44a0e38911acb010b7ee9a4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e6bc1618d974a3651dc34575b6541c4c9230f3c97a734a072380b61fcbef4c1(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20861961d6d80b1bf7729680cacbf0a97abf934a3334d6b4495a15b1fcada92c(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    container_id: builtins.str,
    target_id: builtins.str,
    custom_attributes: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    start_action: typing.Optional[builtins.str] = None,
    start_delay: typing.Optional[jsii.Number] = None,
    start_order: typing.Optional[jsii.Number] = None,
    stop_action: typing.Optional[builtins.str] = None,
    stop_delay: typing.Optional[jsii.Number] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    wait_for_guest: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass
