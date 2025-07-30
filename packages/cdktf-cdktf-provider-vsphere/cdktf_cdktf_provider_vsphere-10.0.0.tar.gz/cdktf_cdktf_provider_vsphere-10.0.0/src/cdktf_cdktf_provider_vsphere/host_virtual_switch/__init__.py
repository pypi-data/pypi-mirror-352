r'''
# `vsphere_host_virtual_switch`

Refer to the Terraform Registry for docs: [`vsphere_host_virtual_switch`](https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch).
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


class HostVirtualSwitch(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.hostVirtualSwitch.HostVirtualSwitch",
):
    '''Represents a {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch vsphere_host_virtual_switch}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        active_nics: typing.Sequence[builtins.str],
        host_system_id: builtins.str,
        name: builtins.str,
        network_adapters: typing.Sequence[builtins.str],
        allow_forged_transmits: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_mac_changes: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_promiscuous: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        beacon_interval: typing.Optional[jsii.Number] = None,
        check_beacon: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        failback: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        link_discovery_operation: typing.Optional[builtins.str] = None,
        link_discovery_protocol: typing.Optional[builtins.str] = None,
        mtu: typing.Optional[jsii.Number] = None,
        notify_switches: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        number_of_ports: typing.Optional[jsii.Number] = None,
        shaping_average_bandwidth: typing.Optional[jsii.Number] = None,
        shaping_burst_size: typing.Optional[jsii.Number] = None,
        shaping_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        shaping_peak_bandwidth: typing.Optional[jsii.Number] = None,
        standby_nics: typing.Optional[typing.Sequence[builtins.str]] = None,
        teaming_policy: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch vsphere_host_virtual_switch} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param active_nics: List of active network adapters used for load balancing. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#active_nics HostVirtualSwitch#active_nics}
        :param host_system_id: The managed object ID of the host to set the virtual switch up on. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#host_system_id HostVirtualSwitch#host_system_id}
        :param name: The name of the virtual switch. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#name HostVirtualSwitch#name}
        :param network_adapters: The list of network adapters to bind to this virtual switch. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#network_adapters HostVirtualSwitch#network_adapters}
        :param allow_forged_transmits: Controls whether or not the virtual network adapter is allowed to send network traffic with a different MAC address than that of its own. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#allow_forged_transmits HostVirtualSwitch#allow_forged_transmits}
        :param allow_mac_changes: Controls whether or not the Media Access Control (MAC) address can be changed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#allow_mac_changes HostVirtualSwitch#allow_mac_changes}
        :param allow_promiscuous: Enable promiscuous mode on the network. This flag indicates whether or not all traffic is seen on a given port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#allow_promiscuous HostVirtualSwitch#allow_promiscuous}
        :param beacon_interval: Determines how often, in seconds, a beacon should be sent to probe for the validity of a link. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#beacon_interval HostVirtualSwitch#beacon_interval}
        :param check_beacon: Enable beacon probing. Requires that the vSwitch has been configured to use a beacon. If disabled, link status is used only. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#check_beacon HostVirtualSwitch#check_beacon}
        :param failback: If true, the teaming policy will re-activate failed interfaces higher in precedence when they come back up. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#failback HostVirtualSwitch#failback}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#id HostVirtualSwitch#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param link_discovery_operation: Whether to advertise or listen for link discovery. Valid values are advertise, both, listen, and none. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#link_discovery_operation HostVirtualSwitch#link_discovery_operation}
        :param link_discovery_protocol: The discovery protocol type. Valid values are cdp and lldp. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#link_discovery_protocol HostVirtualSwitch#link_discovery_protocol}
        :param mtu: The maximum transmission unit (MTU) of the virtual switch in bytes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#mtu HostVirtualSwitch#mtu}
        :param notify_switches: If true, the teaming policy will notify the broadcast network of a NIC failover, triggering cache updates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#notify_switches HostVirtualSwitch#notify_switches}
        :param number_of_ports: The number of ports that this virtual switch is configured to use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#number_of_ports HostVirtualSwitch#number_of_ports}
        :param shaping_average_bandwidth: The average bandwidth in bits per second if traffic shaping is enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#shaping_average_bandwidth HostVirtualSwitch#shaping_average_bandwidth}
        :param shaping_burst_size: The maximum burst size allowed in bytes if traffic shaping is enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#shaping_burst_size HostVirtualSwitch#shaping_burst_size}
        :param shaping_enabled: Enable traffic shaping on this virtual switch or port group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#shaping_enabled HostVirtualSwitch#shaping_enabled}
        :param shaping_peak_bandwidth: The peak bandwidth during bursts in bits per second if traffic shaping is enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#shaping_peak_bandwidth HostVirtualSwitch#shaping_peak_bandwidth}
        :param standby_nics: List of standby network adapters used for failover. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#standby_nics HostVirtualSwitch#standby_nics}
        :param teaming_policy: The network adapter teaming policy. Can be one of loadbalance_ip, loadbalance_srcmac, loadbalance_srcid, or failover_explicit. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#teaming_policy HostVirtualSwitch#teaming_policy}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0cdfb02f4bbc45d69b2415d460e38b63ca07e802b7c38ef48484e7104bd2ce2e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = HostVirtualSwitchConfig(
            active_nics=active_nics,
            host_system_id=host_system_id,
            name=name,
            network_adapters=network_adapters,
            allow_forged_transmits=allow_forged_transmits,
            allow_mac_changes=allow_mac_changes,
            allow_promiscuous=allow_promiscuous,
            beacon_interval=beacon_interval,
            check_beacon=check_beacon,
            failback=failback,
            id=id,
            link_discovery_operation=link_discovery_operation,
            link_discovery_protocol=link_discovery_protocol,
            mtu=mtu,
            notify_switches=notify_switches,
            number_of_ports=number_of_ports,
            shaping_average_bandwidth=shaping_average_bandwidth,
            shaping_burst_size=shaping_burst_size,
            shaping_enabled=shaping_enabled,
            shaping_peak_bandwidth=shaping_peak_bandwidth,
            standby_nics=standby_nics,
            teaming_policy=teaming_policy,
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
        '''Generates CDKTF code for importing a HostVirtualSwitch resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the HostVirtualSwitch to import.
        :param import_from_id: The id of the existing HostVirtualSwitch that should be imported. Refer to the {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the HostVirtualSwitch to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6537a467b6584ed42607e9406316b333932a41dcfcd296254018c90ca65ec23a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAllowForgedTransmits")
    def reset_allow_forged_transmits(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowForgedTransmits", []))

    @jsii.member(jsii_name="resetAllowMacChanges")
    def reset_allow_mac_changes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowMacChanges", []))

    @jsii.member(jsii_name="resetAllowPromiscuous")
    def reset_allow_promiscuous(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowPromiscuous", []))

    @jsii.member(jsii_name="resetBeaconInterval")
    def reset_beacon_interval(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBeaconInterval", []))

    @jsii.member(jsii_name="resetCheckBeacon")
    def reset_check_beacon(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCheckBeacon", []))

    @jsii.member(jsii_name="resetFailback")
    def reset_failback(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFailback", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetLinkDiscoveryOperation")
    def reset_link_discovery_operation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLinkDiscoveryOperation", []))

    @jsii.member(jsii_name="resetLinkDiscoveryProtocol")
    def reset_link_discovery_protocol(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLinkDiscoveryProtocol", []))

    @jsii.member(jsii_name="resetMtu")
    def reset_mtu(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMtu", []))

    @jsii.member(jsii_name="resetNotifySwitches")
    def reset_notify_switches(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNotifySwitches", []))

    @jsii.member(jsii_name="resetNumberOfPorts")
    def reset_number_of_ports(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNumberOfPorts", []))

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
    @jsii.member(jsii_name="beaconIntervalInput")
    def beacon_interval_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "beaconIntervalInput"))

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
    @jsii.member(jsii_name="linkDiscoveryOperationInput")
    def link_discovery_operation_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "linkDiscoveryOperationInput"))

    @builtins.property
    @jsii.member(jsii_name="linkDiscoveryProtocolInput")
    def link_discovery_protocol_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "linkDiscoveryProtocolInput"))

    @builtins.property
    @jsii.member(jsii_name="mtuInput")
    def mtu_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "mtuInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="networkAdaptersInput")
    def network_adapters_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "networkAdaptersInput"))

    @builtins.property
    @jsii.member(jsii_name="notifySwitchesInput")
    def notify_switches_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "notifySwitchesInput"))

    @builtins.property
    @jsii.member(jsii_name="numberOfPortsInput")
    def number_of_ports_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "numberOfPortsInput"))

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
    @jsii.member(jsii_name="activeNics")
    def active_nics(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "activeNics"))

    @active_nics.setter
    def active_nics(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cde16d99c065b5c5df4ed49b095f96dbfd75f21c5be204adb9af4c11a9d7bcc6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9bec414717e0d4737565daeec0d55766fa66bf97bae79bfc4e047ec10fdfa7f2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__13ebe5841cf41ba048a6a71f405e2525871b995cec27d1572fc63f67952035d6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__115f141c26655cb401c166a6a6824be5017752a63e9fc3e73036d6119001d63c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowPromiscuous", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="beaconInterval")
    def beacon_interval(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "beaconInterval"))

    @beacon_interval.setter
    def beacon_interval(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a622eb4500b259334d71d1fe9979734106f45a2893a162a55e8d1a785e12c1d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "beaconInterval", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__2179eea029bbb1f436d299b792cf77239f5d4f905b960692b08327a0de0f1154)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f6a2e599a452a1ee85a1f4fe08b7d6e78ee159b0131192bbb04f852eb2d76a42)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "failback", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="hostSystemId")
    def host_system_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostSystemId"))

    @host_system_id.setter
    def host_system_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e05647d99ed21da0ff73646509549c70b2ac4bf75bedc3d227b62532681bd7ec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hostSystemId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e1e658fbc6ea1d6f900d5b9008d50c5ba1a6a8aed6121a3ba6e5cba97efdc24)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="linkDiscoveryOperation")
    def link_discovery_operation(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "linkDiscoveryOperation"))

    @link_discovery_operation.setter
    def link_discovery_operation(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c59e88bcf15bdea74b677e3020fdb89d3a2cf47e3a04672e9fb971925963de5f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "linkDiscoveryOperation", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="linkDiscoveryProtocol")
    def link_discovery_protocol(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "linkDiscoveryProtocol"))

    @link_discovery_protocol.setter
    def link_discovery_protocol(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf757d65790c573c0bc2a52470334cfebb91026aca47cba7d0f9565c96a88fd1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "linkDiscoveryProtocol", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="mtu")
    def mtu(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "mtu"))

    @mtu.setter
    def mtu(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dff50d0f92955374050b99a747c65719611de3365d9a42ad6114dad0157cfa6a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mtu", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b737ea5de5643fd66030e8e3085ccfe7624e05457ac3f2866ccf78da44501cf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="networkAdapters")
    def network_adapters(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "networkAdapters"))

    @network_adapters.setter
    def network_adapters(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e1b498a4f773ac1854622020655ca601d7191ec9a6ddb24142ddc0579b05bc85)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "networkAdapters", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__78fd23094358ab5ae99fe3d9be512be61695eabb7d5be84f41b5232d9598abd5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "notifySwitches", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="numberOfPorts")
    def number_of_ports(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numberOfPorts"))

    @number_of_ports.setter
    def number_of_ports(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b73038425480414e7885070743f122fff30ec7175ce702ea8498a60c77ee7d59)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "numberOfPorts", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="shapingAverageBandwidth")
    def shaping_average_bandwidth(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "shapingAverageBandwidth"))

    @shaping_average_bandwidth.setter
    def shaping_average_bandwidth(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df99803d1c7e5955265605c5018af5c30fedfb279469f125f6fd2c6495d3625d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "shapingAverageBandwidth", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="shapingBurstSize")
    def shaping_burst_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "shapingBurstSize"))

    @shaping_burst_size.setter
    def shaping_burst_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db74a08a07d923d67e28acbf30239fc1fc05456aae630a63b6f1cae992364e56)
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
            type_hints = typing.get_type_hints(_typecheckingstub__fd8207704e7c1e0673fcdd9de9959787f9a96e5403096f93a73720ea230e36d1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "shapingEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="shapingPeakBandwidth")
    def shaping_peak_bandwidth(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "shapingPeakBandwidth"))

    @shaping_peak_bandwidth.setter
    def shaping_peak_bandwidth(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d966048687e4bd6fb6bc7b904e379c163495310ed58b330e4b6ae7cc603ee084)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "shapingPeakBandwidth", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="standbyNics")
    def standby_nics(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "standbyNics"))

    @standby_nics.setter
    def standby_nics(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__946c1bb3b294c60113d4ebf934180af665d0b77c8b1f252d0988b278b572ef50)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "standbyNics", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="teamingPolicy")
    def teaming_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "teamingPolicy"))

    @teaming_policy.setter
    def teaming_policy(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17886cd8bbf50be03037ed49c18d010fe8f6babf412fc434d695e975fbca8fa0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "teamingPolicy", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.hostVirtualSwitch.HostVirtualSwitchConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "active_nics": "activeNics",
        "host_system_id": "hostSystemId",
        "name": "name",
        "network_adapters": "networkAdapters",
        "allow_forged_transmits": "allowForgedTransmits",
        "allow_mac_changes": "allowMacChanges",
        "allow_promiscuous": "allowPromiscuous",
        "beacon_interval": "beaconInterval",
        "check_beacon": "checkBeacon",
        "failback": "failback",
        "id": "id",
        "link_discovery_operation": "linkDiscoveryOperation",
        "link_discovery_protocol": "linkDiscoveryProtocol",
        "mtu": "mtu",
        "notify_switches": "notifySwitches",
        "number_of_ports": "numberOfPorts",
        "shaping_average_bandwidth": "shapingAverageBandwidth",
        "shaping_burst_size": "shapingBurstSize",
        "shaping_enabled": "shapingEnabled",
        "shaping_peak_bandwidth": "shapingPeakBandwidth",
        "standby_nics": "standbyNics",
        "teaming_policy": "teamingPolicy",
    },
)
class HostVirtualSwitchConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        active_nics: typing.Sequence[builtins.str],
        host_system_id: builtins.str,
        name: builtins.str,
        network_adapters: typing.Sequence[builtins.str],
        allow_forged_transmits: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_mac_changes: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_promiscuous: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        beacon_interval: typing.Optional[jsii.Number] = None,
        check_beacon: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        failback: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        link_discovery_operation: typing.Optional[builtins.str] = None,
        link_discovery_protocol: typing.Optional[builtins.str] = None,
        mtu: typing.Optional[jsii.Number] = None,
        notify_switches: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        number_of_ports: typing.Optional[jsii.Number] = None,
        shaping_average_bandwidth: typing.Optional[jsii.Number] = None,
        shaping_burst_size: typing.Optional[jsii.Number] = None,
        shaping_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        shaping_peak_bandwidth: typing.Optional[jsii.Number] = None,
        standby_nics: typing.Optional[typing.Sequence[builtins.str]] = None,
        teaming_policy: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param active_nics: List of active network adapters used for load balancing. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#active_nics HostVirtualSwitch#active_nics}
        :param host_system_id: The managed object ID of the host to set the virtual switch up on. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#host_system_id HostVirtualSwitch#host_system_id}
        :param name: The name of the virtual switch. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#name HostVirtualSwitch#name}
        :param network_adapters: The list of network adapters to bind to this virtual switch. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#network_adapters HostVirtualSwitch#network_adapters}
        :param allow_forged_transmits: Controls whether or not the virtual network adapter is allowed to send network traffic with a different MAC address than that of its own. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#allow_forged_transmits HostVirtualSwitch#allow_forged_transmits}
        :param allow_mac_changes: Controls whether or not the Media Access Control (MAC) address can be changed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#allow_mac_changes HostVirtualSwitch#allow_mac_changes}
        :param allow_promiscuous: Enable promiscuous mode on the network. This flag indicates whether or not all traffic is seen on a given port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#allow_promiscuous HostVirtualSwitch#allow_promiscuous}
        :param beacon_interval: Determines how often, in seconds, a beacon should be sent to probe for the validity of a link. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#beacon_interval HostVirtualSwitch#beacon_interval}
        :param check_beacon: Enable beacon probing. Requires that the vSwitch has been configured to use a beacon. If disabled, link status is used only. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#check_beacon HostVirtualSwitch#check_beacon}
        :param failback: If true, the teaming policy will re-activate failed interfaces higher in precedence when they come back up. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#failback HostVirtualSwitch#failback}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#id HostVirtualSwitch#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param link_discovery_operation: Whether to advertise or listen for link discovery. Valid values are advertise, both, listen, and none. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#link_discovery_operation HostVirtualSwitch#link_discovery_operation}
        :param link_discovery_protocol: The discovery protocol type. Valid values are cdp and lldp. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#link_discovery_protocol HostVirtualSwitch#link_discovery_protocol}
        :param mtu: The maximum transmission unit (MTU) of the virtual switch in bytes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#mtu HostVirtualSwitch#mtu}
        :param notify_switches: If true, the teaming policy will notify the broadcast network of a NIC failover, triggering cache updates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#notify_switches HostVirtualSwitch#notify_switches}
        :param number_of_ports: The number of ports that this virtual switch is configured to use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#number_of_ports HostVirtualSwitch#number_of_ports}
        :param shaping_average_bandwidth: The average bandwidth in bits per second if traffic shaping is enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#shaping_average_bandwidth HostVirtualSwitch#shaping_average_bandwidth}
        :param shaping_burst_size: The maximum burst size allowed in bytes if traffic shaping is enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#shaping_burst_size HostVirtualSwitch#shaping_burst_size}
        :param shaping_enabled: Enable traffic shaping on this virtual switch or port group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#shaping_enabled HostVirtualSwitch#shaping_enabled}
        :param shaping_peak_bandwidth: The peak bandwidth during bursts in bits per second if traffic shaping is enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#shaping_peak_bandwidth HostVirtualSwitch#shaping_peak_bandwidth}
        :param standby_nics: List of standby network adapters used for failover. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#standby_nics HostVirtualSwitch#standby_nics}
        :param teaming_policy: The network adapter teaming policy. Can be one of loadbalance_ip, loadbalance_srcmac, loadbalance_srcid, or failover_explicit. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#teaming_policy HostVirtualSwitch#teaming_policy}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b871735f286129dab91cb1fda079e52a5692596f132de552bdb7689a8be700eb)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument active_nics", value=active_nics, expected_type=type_hints["active_nics"])
            check_type(argname="argument host_system_id", value=host_system_id, expected_type=type_hints["host_system_id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument network_adapters", value=network_adapters, expected_type=type_hints["network_adapters"])
            check_type(argname="argument allow_forged_transmits", value=allow_forged_transmits, expected_type=type_hints["allow_forged_transmits"])
            check_type(argname="argument allow_mac_changes", value=allow_mac_changes, expected_type=type_hints["allow_mac_changes"])
            check_type(argname="argument allow_promiscuous", value=allow_promiscuous, expected_type=type_hints["allow_promiscuous"])
            check_type(argname="argument beacon_interval", value=beacon_interval, expected_type=type_hints["beacon_interval"])
            check_type(argname="argument check_beacon", value=check_beacon, expected_type=type_hints["check_beacon"])
            check_type(argname="argument failback", value=failback, expected_type=type_hints["failback"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument link_discovery_operation", value=link_discovery_operation, expected_type=type_hints["link_discovery_operation"])
            check_type(argname="argument link_discovery_protocol", value=link_discovery_protocol, expected_type=type_hints["link_discovery_protocol"])
            check_type(argname="argument mtu", value=mtu, expected_type=type_hints["mtu"])
            check_type(argname="argument notify_switches", value=notify_switches, expected_type=type_hints["notify_switches"])
            check_type(argname="argument number_of_ports", value=number_of_ports, expected_type=type_hints["number_of_ports"])
            check_type(argname="argument shaping_average_bandwidth", value=shaping_average_bandwidth, expected_type=type_hints["shaping_average_bandwidth"])
            check_type(argname="argument shaping_burst_size", value=shaping_burst_size, expected_type=type_hints["shaping_burst_size"])
            check_type(argname="argument shaping_enabled", value=shaping_enabled, expected_type=type_hints["shaping_enabled"])
            check_type(argname="argument shaping_peak_bandwidth", value=shaping_peak_bandwidth, expected_type=type_hints["shaping_peak_bandwidth"])
            check_type(argname="argument standby_nics", value=standby_nics, expected_type=type_hints["standby_nics"])
            check_type(argname="argument teaming_policy", value=teaming_policy, expected_type=type_hints["teaming_policy"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "active_nics": active_nics,
            "host_system_id": host_system_id,
            "name": name,
            "network_adapters": network_adapters,
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
        if allow_forged_transmits is not None:
            self._values["allow_forged_transmits"] = allow_forged_transmits
        if allow_mac_changes is not None:
            self._values["allow_mac_changes"] = allow_mac_changes
        if allow_promiscuous is not None:
            self._values["allow_promiscuous"] = allow_promiscuous
        if beacon_interval is not None:
            self._values["beacon_interval"] = beacon_interval
        if check_beacon is not None:
            self._values["check_beacon"] = check_beacon
        if failback is not None:
            self._values["failback"] = failback
        if id is not None:
            self._values["id"] = id
        if link_discovery_operation is not None:
            self._values["link_discovery_operation"] = link_discovery_operation
        if link_discovery_protocol is not None:
            self._values["link_discovery_protocol"] = link_discovery_protocol
        if mtu is not None:
            self._values["mtu"] = mtu
        if notify_switches is not None:
            self._values["notify_switches"] = notify_switches
        if number_of_ports is not None:
            self._values["number_of_ports"] = number_of_ports
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
    def active_nics(self) -> typing.List[builtins.str]:
        '''List of active network adapters used for load balancing.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#active_nics HostVirtualSwitch#active_nics}
        '''
        result = self._values.get("active_nics")
        assert result is not None, "Required property 'active_nics' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def host_system_id(self) -> builtins.str:
        '''The managed object ID of the host to set the virtual switch up on.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#host_system_id HostVirtualSwitch#host_system_id}
        '''
        result = self._values.get("host_system_id")
        assert result is not None, "Required property 'host_system_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the virtual switch.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#name HostVirtualSwitch#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def network_adapters(self) -> typing.List[builtins.str]:
        '''The list of network adapters to bind to this virtual switch.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#network_adapters HostVirtualSwitch#network_adapters}
        '''
        result = self._values.get("network_adapters")
        assert result is not None, "Required property 'network_adapters' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def allow_forged_transmits(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Controls whether or not the virtual network adapter is allowed to send network traffic with a different MAC address than that of its own.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#allow_forged_transmits HostVirtualSwitch#allow_forged_transmits}
        '''
        result = self._values.get("allow_forged_transmits")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def allow_mac_changes(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Controls whether or not the Media Access Control (MAC) address can be changed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#allow_mac_changes HostVirtualSwitch#allow_mac_changes}
        '''
        result = self._values.get("allow_mac_changes")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def allow_promiscuous(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable promiscuous mode on the network.

        This flag indicates whether or not all traffic is seen on a given port.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#allow_promiscuous HostVirtualSwitch#allow_promiscuous}
        '''
        result = self._values.get("allow_promiscuous")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def beacon_interval(self) -> typing.Optional[jsii.Number]:
        '''Determines how often, in seconds, a beacon should be sent to probe for the validity of a link.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#beacon_interval HostVirtualSwitch#beacon_interval}
        '''
        result = self._values.get("beacon_interval")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def check_beacon(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable beacon probing.

        Requires that the vSwitch has been configured to use a beacon. If disabled, link status is used only.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#check_beacon HostVirtualSwitch#check_beacon}
        '''
        result = self._values.get("check_beacon")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def failback(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If true, the teaming policy will re-activate failed interfaces higher in precedence when they come back up.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#failback HostVirtualSwitch#failback}
        '''
        result = self._values.get("failback")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#id HostVirtualSwitch#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def link_discovery_operation(self) -> typing.Optional[builtins.str]:
        '''Whether to advertise or listen for link discovery. Valid values are advertise, both, listen, and none.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#link_discovery_operation HostVirtualSwitch#link_discovery_operation}
        '''
        result = self._values.get("link_discovery_operation")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def link_discovery_protocol(self) -> typing.Optional[builtins.str]:
        '''The discovery protocol type. Valid values are cdp and lldp.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#link_discovery_protocol HostVirtualSwitch#link_discovery_protocol}
        '''
        result = self._values.get("link_discovery_protocol")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mtu(self) -> typing.Optional[jsii.Number]:
        '''The maximum transmission unit (MTU) of the virtual switch in bytes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#mtu HostVirtualSwitch#mtu}
        '''
        result = self._values.get("mtu")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def notify_switches(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If true, the teaming policy will notify the broadcast network of a NIC failover, triggering cache updates.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#notify_switches HostVirtualSwitch#notify_switches}
        '''
        result = self._values.get("notify_switches")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def number_of_ports(self) -> typing.Optional[jsii.Number]:
        '''The number of ports that this virtual switch is configured to use.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#number_of_ports HostVirtualSwitch#number_of_ports}
        '''
        result = self._values.get("number_of_ports")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def shaping_average_bandwidth(self) -> typing.Optional[jsii.Number]:
        '''The average bandwidth in bits per second if traffic shaping is enabled.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#shaping_average_bandwidth HostVirtualSwitch#shaping_average_bandwidth}
        '''
        result = self._values.get("shaping_average_bandwidth")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def shaping_burst_size(self) -> typing.Optional[jsii.Number]:
        '''The maximum burst size allowed in bytes if traffic shaping is enabled.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#shaping_burst_size HostVirtualSwitch#shaping_burst_size}
        '''
        result = self._values.get("shaping_burst_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def shaping_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable traffic shaping on this virtual switch or port group.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#shaping_enabled HostVirtualSwitch#shaping_enabled}
        '''
        result = self._values.get("shaping_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def shaping_peak_bandwidth(self) -> typing.Optional[jsii.Number]:
        '''The peak bandwidth during bursts in bits per second if traffic shaping is enabled.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#shaping_peak_bandwidth HostVirtualSwitch#shaping_peak_bandwidth}
        '''
        result = self._values.get("shaping_peak_bandwidth")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def standby_nics(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of standby network adapters used for failover.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#standby_nics HostVirtualSwitch#standby_nics}
        '''
        result = self._values.get("standby_nics")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def teaming_policy(self) -> typing.Optional[builtins.str]:
        '''The network adapter teaming policy. Can be one of loadbalance_ip, loadbalance_srcmac, loadbalance_srcid, or failover_explicit.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host_virtual_switch#teaming_policy HostVirtualSwitch#teaming_policy}
        '''
        result = self._values.get("teaming_policy")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HostVirtualSwitchConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "HostVirtualSwitch",
    "HostVirtualSwitchConfig",
]

publication.publish()

def _typecheckingstub__0cdfb02f4bbc45d69b2415d460e38b63ca07e802b7c38ef48484e7104bd2ce2e(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    active_nics: typing.Sequence[builtins.str],
    host_system_id: builtins.str,
    name: builtins.str,
    network_adapters: typing.Sequence[builtins.str],
    allow_forged_transmits: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_mac_changes: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_promiscuous: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    beacon_interval: typing.Optional[jsii.Number] = None,
    check_beacon: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    failback: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    link_discovery_operation: typing.Optional[builtins.str] = None,
    link_discovery_protocol: typing.Optional[builtins.str] = None,
    mtu: typing.Optional[jsii.Number] = None,
    notify_switches: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    number_of_ports: typing.Optional[jsii.Number] = None,
    shaping_average_bandwidth: typing.Optional[jsii.Number] = None,
    shaping_burst_size: typing.Optional[jsii.Number] = None,
    shaping_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    shaping_peak_bandwidth: typing.Optional[jsii.Number] = None,
    standby_nics: typing.Optional[typing.Sequence[builtins.str]] = None,
    teaming_policy: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__6537a467b6584ed42607e9406316b333932a41dcfcd296254018c90ca65ec23a(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cde16d99c065b5c5df4ed49b095f96dbfd75f21c5be204adb9af4c11a9d7bcc6(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9bec414717e0d4737565daeec0d55766fa66bf97bae79bfc4e047ec10fdfa7f2(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13ebe5841cf41ba048a6a71f405e2525871b995cec27d1572fc63f67952035d6(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__115f141c26655cb401c166a6a6824be5017752a63e9fc3e73036d6119001d63c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a622eb4500b259334d71d1fe9979734106f45a2893a162a55e8d1a785e12c1d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2179eea029bbb1f436d299b792cf77239f5d4f905b960692b08327a0de0f1154(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6a2e599a452a1ee85a1f4fe08b7d6e78ee159b0131192bbb04f852eb2d76a42(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e05647d99ed21da0ff73646509549c70b2ac4bf75bedc3d227b62532681bd7ec(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e1e658fbc6ea1d6f900d5b9008d50c5ba1a6a8aed6121a3ba6e5cba97efdc24(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c59e88bcf15bdea74b677e3020fdb89d3a2cf47e3a04672e9fb971925963de5f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf757d65790c573c0bc2a52470334cfebb91026aca47cba7d0f9565c96a88fd1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dff50d0f92955374050b99a747c65719611de3365d9a42ad6114dad0157cfa6a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b737ea5de5643fd66030e8e3085ccfe7624e05457ac3f2866ccf78da44501cf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1b498a4f773ac1854622020655ca601d7191ec9a6ddb24142ddc0579b05bc85(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78fd23094358ab5ae99fe3d9be512be61695eabb7d5be84f41b5232d9598abd5(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b73038425480414e7885070743f122fff30ec7175ce702ea8498a60c77ee7d59(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df99803d1c7e5955265605c5018af5c30fedfb279469f125f6fd2c6495d3625d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db74a08a07d923d67e28acbf30239fc1fc05456aae630a63b6f1cae992364e56(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd8207704e7c1e0673fcdd9de9959787f9a96e5403096f93a73720ea230e36d1(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d966048687e4bd6fb6bc7b904e379c163495310ed58b330e4b6ae7cc603ee084(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__946c1bb3b294c60113d4ebf934180af665d0b77c8b1f252d0988b278b572ef50(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17886cd8bbf50be03037ed49c18d010fe8f6babf412fc434d695e975fbca8fa0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b871735f286129dab91cb1fda079e52a5692596f132de552bdb7689a8be700eb(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    active_nics: typing.Sequence[builtins.str],
    host_system_id: builtins.str,
    name: builtins.str,
    network_adapters: typing.Sequence[builtins.str],
    allow_forged_transmits: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_mac_changes: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_promiscuous: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    beacon_interval: typing.Optional[jsii.Number] = None,
    check_beacon: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    failback: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    link_discovery_operation: typing.Optional[builtins.str] = None,
    link_discovery_protocol: typing.Optional[builtins.str] = None,
    mtu: typing.Optional[jsii.Number] = None,
    notify_switches: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    number_of_ports: typing.Optional[jsii.Number] = None,
    shaping_average_bandwidth: typing.Optional[jsii.Number] = None,
    shaping_burst_size: typing.Optional[jsii.Number] = None,
    shaping_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    shaping_peak_bandwidth: typing.Optional[jsii.Number] = None,
    standby_nics: typing.Optional[typing.Sequence[builtins.str]] = None,
    teaming_policy: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
