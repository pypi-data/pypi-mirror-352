r'''
# `vsphere_host_port_group`

Refer to the Terraform Registry for docs: [`vsphere_host_port_group`](https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group).
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


class HostPortGroup(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.hostPortGroup.HostPortGroup",
):
    '''Represents a {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group vsphere_host_port_group}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        host_system_id: builtins.str,
        name: builtins.str,
        virtual_switch_name: builtins.str,
        active_nics: typing.Optional[typing.Sequence[builtins.str]] = None,
        allow_forged_transmits: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_mac_changes: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_promiscuous: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        check_beacon: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        failback: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        notify_switches: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        shaping_average_bandwidth: typing.Optional[jsii.Number] = None,
        shaping_burst_size: typing.Optional[jsii.Number] = None,
        shaping_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        shaping_peak_bandwidth: typing.Optional[jsii.Number] = None,
        standby_nics: typing.Optional[typing.Sequence[builtins.str]] = None,
        teaming_policy: typing.Optional[builtins.str] = None,
        vlan_id: typing.Optional[jsii.Number] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group vsphere_host_port_group} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param host_system_id: The managed object ID of the host to set the virtual switch up on. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#host_system_id HostPortGroup#host_system_id}
        :param name: The name of the port group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#name HostPortGroup#name}
        :param virtual_switch_name: The name of the virtual switch to bind this port group to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#virtual_switch_name HostPortGroup#virtual_switch_name}
        :param active_nics: List of active network adapters used for load balancing. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#active_nics HostPortGroup#active_nics}
        :param allow_forged_transmits: Controls whether or not the virtual network adapter is allowed to send network traffic with a different MAC address than that of its own. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#allow_forged_transmits HostPortGroup#allow_forged_transmits}
        :param allow_mac_changes: Controls whether or not the Media Access Control (MAC) address can be changed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#allow_mac_changes HostPortGroup#allow_mac_changes}
        :param allow_promiscuous: Enable promiscuous mode on the network. This flag indicates whether or not all traffic is seen on a given port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#allow_promiscuous HostPortGroup#allow_promiscuous}
        :param check_beacon: Enable beacon probing. Requires that the vSwitch has been configured to use a beacon. If disabled, link status is used only. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#check_beacon HostPortGroup#check_beacon}
        :param failback: If true, the teaming policy will re-activate failed interfaces higher in precedence when they come back up. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#failback HostPortGroup#failback}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#id HostPortGroup#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param notify_switches: If true, the teaming policy will notify the broadcast network of a NIC failover, triggering cache updates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#notify_switches HostPortGroup#notify_switches}
        :param shaping_average_bandwidth: The average bandwidth in bits per second if traffic shaping is enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#shaping_average_bandwidth HostPortGroup#shaping_average_bandwidth}
        :param shaping_burst_size: The maximum burst size allowed in bytes if traffic shaping is enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#shaping_burst_size HostPortGroup#shaping_burst_size}
        :param shaping_enabled: Enable traffic shaping on this virtual switch or port group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#shaping_enabled HostPortGroup#shaping_enabled}
        :param shaping_peak_bandwidth: The peak bandwidth during bursts in bits per second if traffic shaping is enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#shaping_peak_bandwidth HostPortGroup#shaping_peak_bandwidth}
        :param standby_nics: List of standby network adapters used for failover. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#standby_nics HostPortGroup#standby_nics}
        :param teaming_policy: The network adapter teaming policy. Can be one of loadbalance_ip, loadbalance_srcmac, loadbalance_srcid, or failover_explicit. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#teaming_policy HostPortGroup#teaming_policy}
        :param vlan_id: The VLAN ID/trunk mode for this port group. An ID of 0 denotes no tagging, an ID of 1-4094 tags with the specific ID, and an ID of 4095 enables trunk mode, allowing the guest to manage its own tagging. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#vlan_id HostPortGroup#vlan_id}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f96c4bfa9745411f042ba183ea570fa9a072c898de0c8797c01058d660335ed)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = HostPortGroupConfig(
            host_system_id=host_system_id,
            name=name,
            virtual_switch_name=virtual_switch_name,
            active_nics=active_nics,
            allow_forged_transmits=allow_forged_transmits,
            allow_mac_changes=allow_mac_changes,
            allow_promiscuous=allow_promiscuous,
            check_beacon=check_beacon,
            failback=failback,
            id=id,
            notify_switches=notify_switches,
            shaping_average_bandwidth=shaping_average_bandwidth,
            shaping_burst_size=shaping_burst_size,
            shaping_enabled=shaping_enabled,
            shaping_peak_bandwidth=shaping_peak_bandwidth,
            standby_nics=standby_nics,
            teaming_policy=teaming_policy,
            vlan_id=vlan_id,
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
        '''Generates CDKTF code for importing a HostPortGroup resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the HostPortGroup to import.
        :param import_from_id: The id of the existing HostPortGroup that should be imported. Refer to the {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the HostPortGroup to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70bec01b597cf1a912f2881daa03c2a6e1707d8c485b03c3471dd4905480210e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetActiveNics")
    def reset_active_nics(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetActiveNics", []))

    @jsii.member(jsii_name="resetAllowForgedTransmits")
    def reset_allow_forged_transmits(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowForgedTransmits", []))

    @jsii.member(jsii_name="resetAllowMacChanges")
    def reset_allow_mac_changes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowMacChanges", []))

    @jsii.member(jsii_name="resetAllowPromiscuous")
    def reset_allow_promiscuous(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowPromiscuous", []))

    @jsii.member(jsii_name="resetCheckBeacon")
    def reset_check_beacon(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCheckBeacon", []))

    @jsii.member(jsii_name="resetFailback")
    def reset_failback(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFailback", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetNotifySwitches")
    def reset_notify_switches(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNotifySwitches", []))

    @jsii.member(jsii_name="resetShapingAverageBandwidth")
    def reset_shaping_average_bandwidth(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetShapingAverageBandwidth", []))

    @jsii.member(jsii_name="resetShapingBurstSize")
    def reset_shaping_burst_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetShapingBurstSize", []))

    @jsii.member(jsii_name="resetShapingEnabled")
    def reset_shaping_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetShapingEnabled", []))

    @jsii.member(jsii_name="resetShapingPeakBandwidth")
    def reset_shaping_peak_bandwidth(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetShapingPeakBandwidth", []))

    @jsii.member(jsii_name="resetStandbyNics")
    def reset_standby_nics(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStandbyNics", []))

    @jsii.member(jsii_name="resetTeamingPolicy")
    def reset_teaming_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTeamingPolicy", []))

    @jsii.member(jsii_name="resetVlanId")
    def reset_vlan_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVlanId", []))

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
    @jsii.member(jsii_name="computedPolicy")
    def computed_policy(self) -> _cdktf_9a9027ec.StringMap:
        return typing.cast(_cdktf_9a9027ec.StringMap, jsii.get(self, "computedPolicy"))

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @builtins.property
    @jsii.member(jsii_name="ports")
    def ports(self) -> "HostPortGroupPortsList":
        return typing.cast("HostPortGroupPortsList", jsii.get(self, "ports"))

    @builtins.property
    @jsii.member(jsii_name="activeNicsInput")
    def active_nics_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "activeNicsInput"))

    @builtins.property
    @jsii.member(jsii_name="allowForgedTransmitsInput")
    def allow_forged_transmits_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "allowForgedTransmitsInput"))

    @builtins.property
    @jsii.member(jsii_name="allowMacChangesInput")
    def allow_mac_changes_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "allowMacChangesInput"))

    @builtins.property
    @jsii.member(jsii_name="allowPromiscuousInput")
    def allow_promiscuous_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "allowPromiscuousInput"))

    @builtins.property
    @jsii.member(jsii_name="checkBeaconInput")
    def check_beacon_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "checkBeaconInput"))

    @builtins.property
    @jsii.member(jsii_name="failbackInput")
    def failback_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "failbackInput"))

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
    @jsii.member(jsii_name="notifySwitchesInput")
    def notify_switches_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "notifySwitchesInput"))

    @builtins.property
    @jsii.member(jsii_name="shapingAverageBandwidthInput")
    def shaping_average_bandwidth_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "shapingAverageBandwidthInput"))

    @builtins.property
    @jsii.member(jsii_name="shapingBurstSizeInput")
    def shaping_burst_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "shapingBurstSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="shapingEnabledInput")
    def shaping_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "shapingEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="shapingPeakBandwidthInput")
    def shaping_peak_bandwidth_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "shapingPeakBandwidthInput"))

    @builtins.property
    @jsii.member(jsii_name="standbyNicsInput")
    def standby_nics_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "standbyNicsInput"))

    @builtins.property
    @jsii.member(jsii_name="teamingPolicyInput")
    def teaming_policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "teamingPolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="virtualSwitchNameInput")
    def virtual_switch_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "virtualSwitchNameInput"))

    @builtins.property
    @jsii.member(jsii_name="vlanIdInput")
    def vlan_id_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "vlanIdInput"))

    @builtins.property
    @jsii.member(jsii_name="activeNics")
    def active_nics(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "activeNics"))

    @active_nics.setter
    def active_nics(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee0a16aa773de59f3eda67117420001d6065ff1202a324b2c5f3a335c5ad7963)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "activeNics", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowForgedTransmits")
    def allow_forged_transmits(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "allowForgedTransmits"))

    @allow_forged_transmits.setter
    def allow_forged_transmits(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d793e97829f9f27492f0836123faf3cff25492f415f75050d5b78eacbf67d0d0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowForgedTransmits", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowMacChanges")
    def allow_mac_changes(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "allowMacChanges"))

    @allow_mac_changes.setter
    def allow_mac_changes(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__764ff52d4a45f98de097bee949882a66e9d5d97eee839f7b0dd09df5a8f888eb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowMacChanges", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowPromiscuous")
    def allow_promiscuous(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "allowPromiscuous"))

    @allow_promiscuous.setter
    def allow_promiscuous(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b513f28744a4b13aff67e2dfe9f9d2079e7b8b50e1e16cefea9dc03867201543)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowPromiscuous", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="checkBeacon")
    def check_beacon(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "checkBeacon"))

    @check_beacon.setter
    def check_beacon(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a68f0789688c3f58357c4d68ced64b65599b2d5552beca44382f7ae9ba248d05)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "checkBeacon", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="failback")
    def failback(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "failback"))

    @failback.setter
    def failback(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a19801b7f0c63daefd56a33c02e585949df51fc03b1e43e88fd6374abaa92a8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "failback", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="hostSystemId")
    def host_system_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostSystemId"))

    @host_system_id.setter
    def host_system_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0096a6931bb581005420c41a24984a34d7a536a742a4c0370a5702cf322a5648)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hostSystemId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe26e734d76641ae3224a825931f2497b05eb507e3a4792191d7069ae454b1d2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64147035903c5fe17361a39843d417da7a7b947a4b54287ab97a0a102da91047)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="notifySwitches")
    def notify_switches(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "notifySwitches"))

    @notify_switches.setter
    def notify_switches(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e337b6da98f8d3c096e24a8746ba1df1fbcbc97ddf77ff574db1a941ba39320a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "notifySwitches", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="shapingAverageBandwidth")
    def shaping_average_bandwidth(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "shapingAverageBandwidth"))

    @shaping_average_bandwidth.setter
    def shaping_average_bandwidth(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f32dfad54a67cc4ec9ed3336e5243a9d39aa967bfb0fd3fc2ec65dd9223c783b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "shapingAverageBandwidth", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="shapingBurstSize")
    def shaping_burst_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "shapingBurstSize"))

    @shaping_burst_size.setter
    def shaping_burst_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8fef868cfd5c95a8e204dbec0fd5fabe434e374fdb8f99cbe29dcef406fb124)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "shapingBurstSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="shapingEnabled")
    def shaping_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "shapingEnabled"))

    @shaping_enabled.setter
    def shaping_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8810f4fa61947dbb924c3eed73c1475a5a0c864f5f0e9a379fcfb52b99a87c86)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "shapingEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="shapingPeakBandwidth")
    def shaping_peak_bandwidth(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "shapingPeakBandwidth"))

    @shaping_peak_bandwidth.setter
    def shaping_peak_bandwidth(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bde6d91fb5f70d644d638fa6093082519545ff43e081a16e455b4f0e5b66fe45)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "shapingPeakBandwidth", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="standbyNics")
    def standby_nics(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "standbyNics"))

    @standby_nics.setter
    def standby_nics(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__44db8afe55c5afe46bf56764b98812e3600043f8a243c1200328c5064ecadb96)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "standbyNics", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="teamingPolicy")
    def teaming_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "teamingPolicy"))

    @teaming_policy.setter
    def teaming_policy(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ffbcbac4d78b925b82ed0eac32b21b0422ad873d32d7f9e576dada9866299295)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "teamingPolicy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="virtualSwitchName")
    def virtual_switch_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "virtualSwitchName"))

    @virtual_switch_name.setter
    def virtual_switch_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87c2c168d02134f8e9d0fe58cb89133a312dfe3a22a71d4fe75f27e22407d3a7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "virtualSwitchName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vlanId")
    def vlan_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "vlanId"))

    @vlan_id.setter
    def vlan_id(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eaef8c3ff41443eaa9c8ae5fbc97513bec9cf903ba7eab1d770b653f928cd3d5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vlanId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.hostPortGroup.HostPortGroupConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "host_system_id": "hostSystemId",
        "name": "name",
        "virtual_switch_name": "virtualSwitchName",
        "active_nics": "activeNics",
        "allow_forged_transmits": "allowForgedTransmits",
        "allow_mac_changes": "allowMacChanges",
        "allow_promiscuous": "allowPromiscuous",
        "check_beacon": "checkBeacon",
        "failback": "failback",
        "id": "id",
        "notify_switches": "notifySwitches",
        "shaping_average_bandwidth": "shapingAverageBandwidth",
        "shaping_burst_size": "shapingBurstSize",
        "shaping_enabled": "shapingEnabled",
        "shaping_peak_bandwidth": "shapingPeakBandwidth",
        "standby_nics": "standbyNics",
        "teaming_policy": "teamingPolicy",
        "vlan_id": "vlanId",
    },
)
class HostPortGroupConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        host_system_id: builtins.str,
        name: builtins.str,
        virtual_switch_name: builtins.str,
        active_nics: typing.Optional[typing.Sequence[builtins.str]] = None,
        allow_forged_transmits: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_mac_changes: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_promiscuous: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        check_beacon: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        failback: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        notify_switches: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        shaping_average_bandwidth: typing.Optional[jsii.Number] = None,
        shaping_burst_size: typing.Optional[jsii.Number] = None,
        shaping_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        shaping_peak_bandwidth: typing.Optional[jsii.Number] = None,
        standby_nics: typing.Optional[typing.Sequence[builtins.str]] = None,
        teaming_policy: typing.Optional[builtins.str] = None,
        vlan_id: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param host_system_id: The managed object ID of the host to set the virtual switch up on. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#host_system_id HostPortGroup#host_system_id}
        :param name: The name of the port group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#name HostPortGroup#name}
        :param virtual_switch_name: The name of the virtual switch to bind this port group to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#virtual_switch_name HostPortGroup#virtual_switch_name}
        :param active_nics: List of active network adapters used for load balancing. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#active_nics HostPortGroup#active_nics}
        :param allow_forged_transmits: Controls whether or not the virtual network adapter is allowed to send network traffic with a different MAC address than that of its own. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#allow_forged_transmits HostPortGroup#allow_forged_transmits}
        :param allow_mac_changes: Controls whether or not the Media Access Control (MAC) address can be changed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#allow_mac_changes HostPortGroup#allow_mac_changes}
        :param allow_promiscuous: Enable promiscuous mode on the network. This flag indicates whether or not all traffic is seen on a given port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#allow_promiscuous HostPortGroup#allow_promiscuous}
        :param check_beacon: Enable beacon probing. Requires that the vSwitch has been configured to use a beacon. If disabled, link status is used only. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#check_beacon HostPortGroup#check_beacon}
        :param failback: If true, the teaming policy will re-activate failed interfaces higher in precedence when they come back up. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#failback HostPortGroup#failback}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#id HostPortGroup#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param notify_switches: If true, the teaming policy will notify the broadcast network of a NIC failover, triggering cache updates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#notify_switches HostPortGroup#notify_switches}
        :param shaping_average_bandwidth: The average bandwidth in bits per second if traffic shaping is enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#shaping_average_bandwidth HostPortGroup#shaping_average_bandwidth}
        :param shaping_burst_size: The maximum burst size allowed in bytes if traffic shaping is enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#shaping_burst_size HostPortGroup#shaping_burst_size}
        :param shaping_enabled: Enable traffic shaping on this virtual switch or port group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#shaping_enabled HostPortGroup#shaping_enabled}
        :param shaping_peak_bandwidth: The peak bandwidth during bursts in bits per second if traffic shaping is enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#shaping_peak_bandwidth HostPortGroup#shaping_peak_bandwidth}
        :param standby_nics: List of standby network adapters used for failover. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#standby_nics HostPortGroup#standby_nics}
        :param teaming_policy: The network adapter teaming policy. Can be one of loadbalance_ip, loadbalance_srcmac, loadbalance_srcid, or failover_explicit. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#teaming_policy HostPortGroup#teaming_policy}
        :param vlan_id: The VLAN ID/trunk mode for this port group. An ID of 0 denotes no tagging, an ID of 1-4094 tags with the specific ID, and an ID of 4095 enables trunk mode, allowing the guest to manage its own tagging. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#vlan_id HostPortGroup#vlan_id}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e7540654b2c7507b717be4301da367de1ca5e87f64357d7ef26d7bdb13b58914)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument host_system_id", value=host_system_id, expected_type=type_hints["host_system_id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument virtual_switch_name", value=virtual_switch_name, expected_type=type_hints["virtual_switch_name"])
            check_type(argname="argument active_nics", value=active_nics, expected_type=type_hints["active_nics"])
            check_type(argname="argument allow_forged_transmits", value=allow_forged_transmits, expected_type=type_hints["allow_forged_transmits"])
            check_type(argname="argument allow_mac_changes", value=allow_mac_changes, expected_type=type_hints["allow_mac_changes"])
            check_type(argname="argument allow_promiscuous", value=allow_promiscuous, expected_type=type_hints["allow_promiscuous"])
            check_type(argname="argument check_beacon", value=check_beacon, expected_type=type_hints["check_beacon"])
            check_type(argname="argument failback", value=failback, expected_type=type_hints["failback"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument notify_switches", value=notify_switches, expected_type=type_hints["notify_switches"])
            check_type(argname="argument shaping_average_bandwidth", value=shaping_average_bandwidth, expected_type=type_hints["shaping_average_bandwidth"])
            check_type(argname="argument shaping_burst_size", value=shaping_burst_size, expected_type=type_hints["shaping_burst_size"])
            check_type(argname="argument shaping_enabled", value=shaping_enabled, expected_type=type_hints["shaping_enabled"])
            check_type(argname="argument shaping_peak_bandwidth", value=shaping_peak_bandwidth, expected_type=type_hints["shaping_peak_bandwidth"])
            check_type(argname="argument standby_nics", value=standby_nics, expected_type=type_hints["standby_nics"])
            check_type(argname="argument teaming_policy", value=teaming_policy, expected_type=type_hints["teaming_policy"])
            check_type(argname="argument vlan_id", value=vlan_id, expected_type=type_hints["vlan_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "host_system_id": host_system_id,
            "name": name,
            "virtual_switch_name": virtual_switch_name,
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
        if active_nics is not None:
            self._values["active_nics"] = active_nics
        if allow_forged_transmits is not None:
            self._values["allow_forged_transmits"] = allow_forged_transmits
        if allow_mac_changes is not None:
            self._values["allow_mac_changes"] = allow_mac_changes
        if allow_promiscuous is not None:
            self._values["allow_promiscuous"] = allow_promiscuous
        if check_beacon is not None:
            self._values["check_beacon"] = check_beacon
        if failback is not None:
            self._values["failback"] = failback
        if id is not None:
            self._values["id"] = id
        if notify_switches is not None:
            self._values["notify_switches"] = notify_switches
        if shaping_average_bandwidth is not None:
            self._values["shaping_average_bandwidth"] = shaping_average_bandwidth
        if shaping_burst_size is not None:
            self._values["shaping_burst_size"] = shaping_burst_size
        if shaping_enabled is not None:
            self._values["shaping_enabled"] = shaping_enabled
        if shaping_peak_bandwidth is not None:
            self._values["shaping_peak_bandwidth"] = shaping_peak_bandwidth
        if standby_nics is not None:
            self._values["standby_nics"] = standby_nics
        if teaming_policy is not None:
            self._values["teaming_policy"] = teaming_policy
        if vlan_id is not None:
            self._values["vlan_id"] = vlan_id

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
    def host_system_id(self) -> builtins.str:
        '''The managed object ID of the host to set the virtual switch up on.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#host_system_id HostPortGroup#host_system_id}
        '''
        result = self._values.get("host_system_id")
        assert result is not None, "Required property 'host_system_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the port group.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#name HostPortGroup#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def virtual_switch_name(self) -> builtins.str:
        '''The name of the virtual switch to bind this port group to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#virtual_switch_name HostPortGroup#virtual_switch_name}
        '''
        result = self._values.get("virtual_switch_name")
        assert result is not None, "Required property 'virtual_switch_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def active_nics(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of active network adapters used for load balancing.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#active_nics HostPortGroup#active_nics}
        '''
        result = self._values.get("active_nics")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def allow_forged_transmits(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Controls whether or not the virtual network adapter is allowed to send network traffic with a different MAC address than that of its own.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#allow_forged_transmits HostPortGroup#allow_forged_transmits}
        '''
        result = self._values.get("allow_forged_transmits")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def allow_mac_changes(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Controls whether or not the Media Access Control (MAC) address can be changed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#allow_mac_changes HostPortGroup#allow_mac_changes}
        '''
        result = self._values.get("allow_mac_changes")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def allow_promiscuous(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable promiscuous mode on the network.

        This flag indicates whether or not all traffic is seen on a given port.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#allow_promiscuous HostPortGroup#allow_promiscuous}
        '''
        result = self._values.get("allow_promiscuous")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def check_beacon(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable beacon probing.

        Requires that the vSwitch has been configured to use a beacon. If disabled, link status is used only.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#check_beacon HostPortGroup#check_beacon}
        '''
        result = self._values.get("check_beacon")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def failback(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If true, the teaming policy will re-activate failed interfaces higher in precedence when they come back up.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#failback HostPortGroup#failback}
        '''
        result = self._values.get("failback")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#id HostPortGroup#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def notify_switches(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If true, the teaming policy will notify the broadcast network of a NIC failover, triggering cache updates.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#notify_switches HostPortGroup#notify_switches}
        '''
        result = self._values.get("notify_switches")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def shaping_average_bandwidth(self) -> typing.Optional[jsii.Number]:
        '''The average bandwidth in bits per second if traffic shaping is enabled.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#shaping_average_bandwidth HostPortGroup#shaping_average_bandwidth}
        '''
        result = self._values.get("shaping_average_bandwidth")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def shaping_burst_size(self) -> typing.Optional[jsii.Number]:
        '''The maximum burst size allowed in bytes if traffic shaping is enabled.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#shaping_burst_size HostPortGroup#shaping_burst_size}
        '''
        result = self._values.get("shaping_burst_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def shaping_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable traffic shaping on this virtual switch or port group.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#shaping_enabled HostPortGroup#shaping_enabled}
        '''
        result = self._values.get("shaping_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def shaping_peak_bandwidth(self) -> typing.Optional[jsii.Number]:
        '''The peak bandwidth during bursts in bits per second if traffic shaping is enabled.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#shaping_peak_bandwidth HostPortGroup#shaping_peak_bandwidth}
        '''
        result = self._values.get("shaping_peak_bandwidth")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def standby_nics(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of standby network adapters used for failover.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#standby_nics HostPortGroup#standby_nics}
        '''
        result = self._values.get("standby_nics")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def teaming_policy(self) -> typing.Optional[builtins.str]:
        '''The network adapter teaming policy. Can be one of loadbalance_ip, loadbalance_srcmac, loadbalance_srcid, or failover_explicit.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#teaming_policy HostPortGroup#teaming_policy}
        '''
        result = self._values.get("teaming_policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vlan_id(self) -> typing.Optional[jsii.Number]:
        '''The VLAN ID/trunk mode for this port group.

        An ID of 0 denotes no tagging, an ID of 1-4094 tags with the specific ID, and an ID of 4095 enables trunk mode, allowing the guest to manage its own tagging.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_port_group#vlan_id HostPortGroup#vlan_id}
        '''
        result = self._values.get("vlan_id")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HostPortGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.hostPortGroup.HostPortGroupPorts",
    jsii_struct_bases=[],
    name_mapping={},
)
class HostPortGroupPorts:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HostPortGroupPorts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class HostPortGroupPortsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.hostPortGroup.HostPortGroupPortsList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c64c6c69d51fe7201a7b444e9829b1b377ceab3ec2940114ed373fdb8971e1df)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "HostPortGroupPortsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ffab7993ee0afff3790cb5239a1ad74ff489ca657b85295babe70679c485b0b8)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("HostPortGroupPortsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c51c784fc053a111fa37354633b59ce13c4abffea9a6d5e00af26a05c67b1ec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18a107a39a2a7783b4b5e73b3137e38598156a0e043fb81a51e210ee74052769)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d142c21d180d0b5d7e0cfeec879cc587e3446258bdd8272eabe2f25c87f7ce3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class HostPortGroupPortsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.hostPortGroup.HostPortGroupPortsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__611c3b3e1258eb13bf45b966bf22ec7ada798649f89d2fc4f9cf382c1f7f7dc4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @builtins.property
    @jsii.member(jsii_name="macAddresses")
    def mac_addresses(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "macAddresses"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[HostPortGroupPorts]:
        return typing.cast(typing.Optional[HostPortGroupPorts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[HostPortGroupPorts]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a27ff0031519e37d4c92ab39a9b3e2237af980258a52c1c9be5b18d8de783a8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "HostPortGroup",
    "HostPortGroupConfig",
    "HostPortGroupPorts",
    "HostPortGroupPortsList",
    "HostPortGroupPortsOutputReference",
]

publication.publish()

def _typecheckingstub__8f96c4bfa9745411f042ba183ea570fa9a072c898de0c8797c01058d660335ed(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    host_system_id: builtins.str,
    name: builtins.str,
    virtual_switch_name: builtins.str,
    active_nics: typing.Optional[typing.Sequence[builtins.str]] = None,
    allow_forged_transmits: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_mac_changes: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_promiscuous: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    check_beacon: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    failback: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    notify_switches: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    shaping_average_bandwidth: typing.Optional[jsii.Number] = None,
    shaping_burst_size: typing.Optional[jsii.Number] = None,
    shaping_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    shaping_peak_bandwidth: typing.Optional[jsii.Number] = None,
    standby_nics: typing.Optional[typing.Sequence[builtins.str]] = None,
    teaming_policy: typing.Optional[builtins.str] = None,
    vlan_id: typing.Optional[jsii.Number] = None,
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

def _typecheckingstub__70bec01b597cf1a912f2881daa03c2a6e1707d8c485b03c3471dd4905480210e(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee0a16aa773de59f3eda67117420001d6065ff1202a324b2c5f3a335c5ad7963(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d793e97829f9f27492f0836123faf3cff25492f415f75050d5b78eacbf67d0d0(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__764ff52d4a45f98de097bee949882a66e9d5d97eee839f7b0dd09df5a8f888eb(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b513f28744a4b13aff67e2dfe9f9d2079e7b8b50e1e16cefea9dc03867201543(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a68f0789688c3f58357c4d68ced64b65599b2d5552beca44382f7ae9ba248d05(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a19801b7f0c63daefd56a33c02e585949df51fc03b1e43e88fd6374abaa92a8(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0096a6931bb581005420c41a24984a34d7a536a742a4c0370a5702cf322a5648(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe26e734d76641ae3224a825931f2497b05eb507e3a4792191d7069ae454b1d2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64147035903c5fe17361a39843d417da7a7b947a4b54287ab97a0a102da91047(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e337b6da98f8d3c096e24a8746ba1df1fbcbc97ddf77ff574db1a941ba39320a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f32dfad54a67cc4ec9ed3336e5243a9d39aa967bfb0fd3fc2ec65dd9223c783b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8fef868cfd5c95a8e204dbec0fd5fabe434e374fdb8f99cbe29dcef406fb124(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8810f4fa61947dbb924c3eed73c1475a5a0c864f5f0e9a379fcfb52b99a87c86(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bde6d91fb5f70d644d638fa6093082519545ff43e081a16e455b4f0e5b66fe45(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44db8afe55c5afe46bf56764b98812e3600043f8a243c1200328c5064ecadb96(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ffbcbac4d78b925b82ed0eac32b21b0422ad873d32d7f9e576dada9866299295(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87c2c168d02134f8e9d0fe58cb89133a312dfe3a22a71d4fe75f27e22407d3a7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eaef8c3ff41443eaa9c8ae5fbc97513bec9cf903ba7eab1d770b653f928cd3d5(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7540654b2c7507b717be4301da367de1ca5e87f64357d7ef26d7bdb13b58914(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    host_system_id: builtins.str,
    name: builtins.str,
    virtual_switch_name: builtins.str,
    active_nics: typing.Optional[typing.Sequence[builtins.str]] = None,
    allow_forged_transmits: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_mac_changes: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_promiscuous: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    check_beacon: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    failback: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    notify_switches: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    shaping_average_bandwidth: typing.Optional[jsii.Number] = None,
    shaping_burst_size: typing.Optional[jsii.Number] = None,
    shaping_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    shaping_peak_bandwidth: typing.Optional[jsii.Number] = None,
    standby_nics: typing.Optional[typing.Sequence[builtins.str]] = None,
    teaming_policy: typing.Optional[builtins.str] = None,
    vlan_id: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c64c6c69d51fe7201a7b444e9829b1b377ceab3ec2940114ed373fdb8971e1df(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ffab7993ee0afff3790cb5239a1ad74ff489ca657b85295babe70679c485b0b8(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c51c784fc053a111fa37354633b59ce13c4abffea9a6d5e00af26a05c67b1ec(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18a107a39a2a7783b4b5e73b3137e38598156a0e043fb81a51e210ee74052769(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d142c21d180d0b5d7e0cfeec879cc587e3446258bdd8272eabe2f25c87f7ce3(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__611c3b3e1258eb13bf45b966bf22ec7ada798649f89d2fc4f9cf382c1f7f7dc4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a27ff0031519e37d4c92ab39a9b3e2237af980258a52c1c9be5b18d8de783a8(
    value: typing.Optional[HostPortGroupPorts],
) -> None:
    """Type checking stubs"""
    pass
