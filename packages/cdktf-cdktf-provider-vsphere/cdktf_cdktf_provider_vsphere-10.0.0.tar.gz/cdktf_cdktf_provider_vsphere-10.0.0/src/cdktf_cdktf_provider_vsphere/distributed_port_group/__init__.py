r'''
# `vsphere_distributed_port_group`

Refer to the Terraform Registry for docs: [`vsphere_distributed_port_group`](https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group).
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


class DistributedPortGroup(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.distributedPortGroup.DistributedPortGroup",
):
    '''Represents a {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group vsphere_distributed_port_group}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        distributed_virtual_switch_uuid: builtins.str,
        name: builtins.str,
        active_uplinks: typing.Optional[typing.Sequence[builtins.str]] = None,
        allow_forged_transmits: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_mac_changes: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_promiscuous: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        auto_expand: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        block_all_ports: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        block_override_allowed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        check_beacon: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        custom_attributes: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        directpath_gen2_allowed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        egress_shaping_average_bandwidth: typing.Optional[jsii.Number] = None,
        egress_shaping_burst_size: typing.Optional[jsii.Number] = None,
        egress_shaping_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        egress_shaping_peak_bandwidth: typing.Optional[jsii.Number] = None,
        failback: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        ingress_shaping_average_bandwidth: typing.Optional[jsii.Number] = None,
        ingress_shaping_burst_size: typing.Optional[jsii.Number] = None,
        ingress_shaping_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ingress_shaping_peak_bandwidth: typing.Optional[jsii.Number] = None,
        lacp_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        lacp_mode: typing.Optional[builtins.str] = None,
        live_port_moving_allowed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        netflow_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        netflow_override_allowed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        network_resource_pool_key: typing.Optional[builtins.str] = None,
        network_resource_pool_override_allowed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        notify_switches: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        number_of_ports: typing.Optional[jsii.Number] = None,
        port_config_reset_at_disconnect: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        port_name_format: typing.Optional[builtins.str] = None,
        port_private_secondary_vlan_id: typing.Optional[jsii.Number] = None,
        security_policy_override_allowed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        shaping_override_allowed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        standby_uplinks: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        teaming_policy: typing.Optional[builtins.str] = None,
        traffic_filter_override_allowed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tx_uplink: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        type: typing.Optional[builtins.str] = None,
        uplink_teaming_override_allowed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        vlan_id: typing.Optional[jsii.Number] = None,
        vlan_override_allowed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        vlan_range: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DistributedPortGroupVlanRange", typing.Dict[builtins.str, typing.Any]]]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group vsphere_distributed_port_group} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param distributed_virtual_switch_uuid: The UUID of the DVS to attach this port group to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#distributed_virtual_switch_uuid DistributedPortGroup#distributed_virtual_switch_uuid}
        :param name: The name of the portgroup. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#name DistributedPortGroup#name}
        :param active_uplinks: List of active uplinks used for load balancing, matching the names of the uplinks assigned in the DVS. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#active_uplinks DistributedPortGroup#active_uplinks}
        :param allow_forged_transmits: Controls whether or not the virtual network adapter is allowed to send network traffic with a different MAC address than that of its own. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#allow_forged_transmits DistributedPortGroup#allow_forged_transmits}
        :param allow_mac_changes: Controls whether or not the Media Access Control (MAC) address can be changed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#allow_mac_changes DistributedPortGroup#allow_mac_changes}
        :param allow_promiscuous: Enable promiscuous mode on the network. This flag indicates whether or not all traffic is seen on a given port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#allow_promiscuous DistributedPortGroup#allow_promiscuous}
        :param auto_expand: Auto-expands the port group beyond the port count configured in number_of_ports when necessary. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#auto_expand DistributedPortGroup#auto_expand}
        :param block_all_ports: Indicates whether to block all ports by default. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#block_all_ports DistributedPortGroup#block_all_ports}
        :param block_override_allowed: Allow the blocked setting of an individual port to override the setting in the portgroup. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#block_override_allowed DistributedPortGroup#block_override_allowed}
        :param check_beacon: Enable beacon probing on the ports this policy applies to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#check_beacon DistributedPortGroup#check_beacon}
        :param custom_attributes: A list of custom attributes to set on this resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#custom_attributes DistributedPortGroup#custom_attributes}
        :param description: The description of the portgroup. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#description DistributedPortGroup#description}
        :param directpath_gen2_allowed: Allow VMDirectPath Gen2 on the ports this policy applies to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#directpath_gen2_allowed DistributedPortGroup#directpath_gen2_allowed}
        :param egress_shaping_average_bandwidth: The average egress bandwidth in bits per second if egress shaping is enabled on the port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#egress_shaping_average_bandwidth DistributedPortGroup#egress_shaping_average_bandwidth}
        :param egress_shaping_burst_size: The maximum egress burst size allowed in bytes if egress shaping is enabled on the port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#egress_shaping_burst_size DistributedPortGroup#egress_shaping_burst_size}
        :param egress_shaping_enabled: True if the traffic shaper is enabled for egress traffic on the port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#egress_shaping_enabled DistributedPortGroup#egress_shaping_enabled}
        :param egress_shaping_peak_bandwidth: The peak egress bandwidth during bursts in bits per second if egress traffic shaping is enabled on the port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#egress_shaping_peak_bandwidth DistributedPortGroup#egress_shaping_peak_bandwidth}
        :param failback: If true, the teaming policy will re-activate failed interfaces higher in precedence when they come back up. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#failback DistributedPortGroup#failback}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#id DistributedPortGroup#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param ingress_shaping_average_bandwidth: The average ingress bandwidth in bits per second if ingress shaping is enabled on the port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#ingress_shaping_average_bandwidth DistributedPortGroup#ingress_shaping_average_bandwidth}
        :param ingress_shaping_burst_size: The maximum ingress burst size allowed in bytes if ingress shaping is enabled on the port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#ingress_shaping_burst_size DistributedPortGroup#ingress_shaping_burst_size}
        :param ingress_shaping_enabled: True if the traffic shaper is enabled for ingress traffic on the port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#ingress_shaping_enabled DistributedPortGroup#ingress_shaping_enabled}
        :param ingress_shaping_peak_bandwidth: The peak ingress bandwidth during bursts in bits per second if ingress traffic shaping is enabled on the port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#ingress_shaping_peak_bandwidth DistributedPortGroup#ingress_shaping_peak_bandwidth}
        :param lacp_enabled: Whether or not to enable LACP on all uplink ports. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#lacp_enabled DistributedPortGroup#lacp_enabled}
        :param lacp_mode: The uplink LACP mode to use. Can be one of active or passive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#lacp_mode DistributedPortGroup#lacp_mode}
        :param live_port_moving_allowed: Allow a live port to be moved in and out of the portgroup. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#live_port_moving_allowed DistributedPortGroup#live_port_moving_allowed}
        :param netflow_enabled: Indicates whether to enable netflow on all ports. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#netflow_enabled DistributedPortGroup#netflow_enabled}
        :param netflow_override_allowed: Allow the enabling or disabling of Netflow on a port, contrary to the policy in the portgroup. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#netflow_override_allowed DistributedPortGroup#netflow_override_allowed}
        :param network_resource_pool_key: The key of a network resource pool to associate with this portgroup. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#network_resource_pool_key DistributedPortGroup#network_resource_pool_key}
        :param network_resource_pool_override_allowed: Allow the network resource pool of an individual port to override the setting in the portgroup. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#network_resource_pool_override_allowed DistributedPortGroup#network_resource_pool_override_allowed}
        :param notify_switches: If true, the teaming policy will notify the broadcast network of a NIC failover, triggering cache updates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#notify_switches DistributedPortGroup#notify_switches}
        :param number_of_ports: The number of ports in this portgroup. The DVS will expand and shrink by modifying this setting. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#number_of_ports DistributedPortGroup#number_of_ports}
        :param port_config_reset_at_disconnect: Reset the setting of any ports in this portgroup back to the default setting when the port disconnects. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#port_config_reset_at_disconnect DistributedPortGroup#port_config_reset_at_disconnect}
        :param port_name_format: A template string to use when creating ports in the portgroup. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#port_name_format DistributedPortGroup#port_name_format}
        :param port_private_secondary_vlan_id: The secondary VLAN ID for this port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#port_private_secondary_vlan_id DistributedPortGroup#port_private_secondary_vlan_id}
        :param security_policy_override_allowed: Allow security policy settings on a port to override those on the portgroup. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#security_policy_override_allowed DistributedPortGroup#security_policy_override_allowed}
        :param shaping_override_allowed: Allow the traffic shaping policies of an individual port to override the settings in the portgroup. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#shaping_override_allowed DistributedPortGroup#shaping_override_allowed}
        :param standby_uplinks: List of standby uplinks used for load balancing, matching the names of the uplinks assigned in the DVS. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#standby_uplinks DistributedPortGroup#standby_uplinks}
        :param tags: A list of tag IDs to apply to this object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#tags DistributedPortGroup#tags}
        :param teaming_policy: The network adapter teaming policy. Can be one of loadbalance_ip, loadbalance_srcmac, loadbalance_srcid, failover_explicit, or loadbalance_loadbased. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#teaming_policy DistributedPortGroup#teaming_policy}
        :param traffic_filter_override_allowed: Allow any filter policies set on the individual port to override those in the portgroup. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#traffic_filter_override_allowed DistributedPortGroup#traffic_filter_override_allowed}
        :param tx_uplink: If true, a copy of packets sent to the switch will always be forwarded to an uplink in addition to the regular packet forwarded done by the switch. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#tx_uplink DistributedPortGroup#tx_uplink}
        :param type: The type of portgroup. Can be one of earlyBinding (static) or ephemeral. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#type DistributedPortGroup#type}
        :param uplink_teaming_override_allowed: Allow the uplink teaming policies on a port to override those on the portgroup. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#uplink_teaming_override_allowed DistributedPortGroup#uplink_teaming_override_allowed}
        :param vlan_id: The VLAN ID for single VLAN mode. 0 denotes no VLAN. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#vlan_id DistributedPortGroup#vlan_id}
        :param vlan_override_allowed: Allow the VLAN configuration on a port to override those on the portgroup. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#vlan_override_allowed DistributedPortGroup#vlan_override_allowed}
        :param vlan_range: vlan_range block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#vlan_range DistributedPortGroup#vlan_range}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c580137018193f484820e913d3012240d00760ac5e2338023a0979e2c65ad9c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DistributedPortGroupConfig(
            distributed_virtual_switch_uuid=distributed_virtual_switch_uuid,
            name=name,
            active_uplinks=active_uplinks,
            allow_forged_transmits=allow_forged_transmits,
            allow_mac_changes=allow_mac_changes,
            allow_promiscuous=allow_promiscuous,
            auto_expand=auto_expand,
            block_all_ports=block_all_ports,
            block_override_allowed=block_override_allowed,
            check_beacon=check_beacon,
            custom_attributes=custom_attributes,
            description=description,
            directpath_gen2_allowed=directpath_gen2_allowed,
            egress_shaping_average_bandwidth=egress_shaping_average_bandwidth,
            egress_shaping_burst_size=egress_shaping_burst_size,
            egress_shaping_enabled=egress_shaping_enabled,
            egress_shaping_peak_bandwidth=egress_shaping_peak_bandwidth,
            failback=failback,
            id=id,
            ingress_shaping_average_bandwidth=ingress_shaping_average_bandwidth,
            ingress_shaping_burst_size=ingress_shaping_burst_size,
            ingress_shaping_enabled=ingress_shaping_enabled,
            ingress_shaping_peak_bandwidth=ingress_shaping_peak_bandwidth,
            lacp_enabled=lacp_enabled,
            lacp_mode=lacp_mode,
            live_port_moving_allowed=live_port_moving_allowed,
            netflow_enabled=netflow_enabled,
            netflow_override_allowed=netflow_override_allowed,
            network_resource_pool_key=network_resource_pool_key,
            network_resource_pool_override_allowed=network_resource_pool_override_allowed,
            notify_switches=notify_switches,
            number_of_ports=number_of_ports,
            port_config_reset_at_disconnect=port_config_reset_at_disconnect,
            port_name_format=port_name_format,
            port_private_secondary_vlan_id=port_private_secondary_vlan_id,
            security_policy_override_allowed=security_policy_override_allowed,
            shaping_override_allowed=shaping_override_allowed,
            standby_uplinks=standby_uplinks,
            tags=tags,
            teaming_policy=teaming_policy,
            traffic_filter_override_allowed=traffic_filter_override_allowed,
            tx_uplink=tx_uplink,
            type=type,
            uplink_teaming_override_allowed=uplink_teaming_override_allowed,
            vlan_id=vlan_id,
            vlan_override_allowed=vlan_override_allowed,
            vlan_range=vlan_range,
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
        '''Generates CDKTF code for importing a DistributedPortGroup resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DistributedPortGroup to import.
        :param import_from_id: The id of the existing DistributedPortGroup that should be imported. Refer to the {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DistributedPortGroup to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__37a3950d06fd5b50ebd14099511f4bdf51c7b617e1306554fde552b7b0d45a2a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putVlanRange")
    def put_vlan_range(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DistributedPortGroupVlanRange", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__91c1a5de8427e7eebea35113cc7bd5f5b75e00640f319d09c68c99f698c624d3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putVlanRange", [value]))

    @jsii.member(jsii_name="resetActiveUplinks")
    def reset_active_uplinks(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetActiveUplinks", []))

    @jsii.member(jsii_name="resetAllowForgedTransmits")
    def reset_allow_forged_transmits(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowForgedTransmits", []))

    @jsii.member(jsii_name="resetAllowMacChanges")
    def reset_allow_mac_changes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowMacChanges", []))

    @jsii.member(jsii_name="resetAllowPromiscuous")
    def reset_allow_promiscuous(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowPromiscuous", []))

    @jsii.member(jsii_name="resetAutoExpand")
    def reset_auto_expand(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoExpand", []))

    @jsii.member(jsii_name="resetBlockAllPorts")
    def reset_block_all_ports(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBlockAllPorts", []))

    @jsii.member(jsii_name="resetBlockOverrideAllowed")
    def reset_block_override_allowed(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBlockOverrideAllowed", []))

    @jsii.member(jsii_name="resetCheckBeacon")
    def reset_check_beacon(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCheckBeacon", []))

    @jsii.member(jsii_name="resetCustomAttributes")
    def reset_custom_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomAttributes", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetDirectpathGen2Allowed")
    def reset_directpath_gen2_allowed(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDirectpathGen2Allowed", []))

    @jsii.member(jsii_name="resetEgressShapingAverageBandwidth")
    def reset_egress_shaping_average_bandwidth(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEgressShapingAverageBandwidth", []))

    @jsii.member(jsii_name="resetEgressShapingBurstSize")
    def reset_egress_shaping_burst_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEgressShapingBurstSize", []))

    @jsii.member(jsii_name="resetEgressShapingEnabled")
    def reset_egress_shaping_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEgressShapingEnabled", []))

    @jsii.member(jsii_name="resetEgressShapingPeakBandwidth")
    def reset_egress_shaping_peak_bandwidth(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEgressShapingPeakBandwidth", []))

    @jsii.member(jsii_name="resetFailback")
    def reset_failback(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFailback", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIngressShapingAverageBandwidth")
    def reset_ingress_shaping_average_bandwidth(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIngressShapingAverageBandwidth", []))

    @jsii.member(jsii_name="resetIngressShapingBurstSize")
    def reset_ingress_shaping_burst_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIngressShapingBurstSize", []))

    @jsii.member(jsii_name="resetIngressShapingEnabled")
    def reset_ingress_shaping_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIngressShapingEnabled", []))

    @jsii.member(jsii_name="resetIngressShapingPeakBandwidth")
    def reset_ingress_shaping_peak_bandwidth(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIngressShapingPeakBandwidth", []))

    @jsii.member(jsii_name="resetLacpEnabled")
    def reset_lacp_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLacpEnabled", []))

    @jsii.member(jsii_name="resetLacpMode")
    def reset_lacp_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLacpMode", []))

    @jsii.member(jsii_name="resetLivePortMovingAllowed")
    def reset_live_port_moving_allowed(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLivePortMovingAllowed", []))

    @jsii.member(jsii_name="resetNetflowEnabled")
    def reset_netflow_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetflowEnabled", []))

    @jsii.member(jsii_name="resetNetflowOverrideAllowed")
    def reset_netflow_override_allowed(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetflowOverrideAllowed", []))

    @jsii.member(jsii_name="resetNetworkResourcePoolKey")
    def reset_network_resource_pool_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworkResourcePoolKey", []))

    @jsii.member(jsii_name="resetNetworkResourcePoolOverrideAllowed")
    def reset_network_resource_pool_override_allowed(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworkResourcePoolOverrideAllowed", []))

    @jsii.member(jsii_name="resetNotifySwitches")
    def reset_notify_switches(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNotifySwitches", []))

    @jsii.member(jsii_name="resetNumberOfPorts")
    def reset_number_of_ports(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNumberOfPorts", []))

    @jsii.member(jsii_name="resetPortConfigResetAtDisconnect")
    def reset_port_config_reset_at_disconnect(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPortConfigResetAtDisconnect", []))

    @jsii.member(jsii_name="resetPortNameFormat")
    def reset_port_name_format(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPortNameFormat", []))

    @jsii.member(jsii_name="resetPortPrivateSecondaryVlanId")
    def reset_port_private_secondary_vlan_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPortPrivateSecondaryVlanId", []))

    @jsii.member(jsii_name="resetSecurityPolicyOverrideAllowed")
    def reset_security_policy_override_allowed(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecurityPolicyOverrideAllowed", []))

    @jsii.member(jsii_name="resetShapingOverrideAllowed")
    def reset_shaping_override_allowed(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetShapingOverrideAllowed", []))

    @jsii.member(jsii_name="resetStandbyUplinks")
    def reset_standby_uplinks(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStandbyUplinks", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTeamingPolicy")
    def reset_teaming_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTeamingPolicy", []))

    @jsii.member(jsii_name="resetTrafficFilterOverrideAllowed")
    def reset_traffic_filter_override_allowed(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTrafficFilterOverrideAllowed", []))

    @jsii.member(jsii_name="resetTxUplink")
    def reset_tx_uplink(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTxUplink", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

    @jsii.member(jsii_name="resetUplinkTeamingOverrideAllowed")
    def reset_uplink_teaming_override_allowed(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUplinkTeamingOverrideAllowed", []))

    @jsii.member(jsii_name="resetVlanId")
    def reset_vlan_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVlanId", []))

    @jsii.member(jsii_name="resetVlanOverrideAllowed")
    def reset_vlan_override_allowed(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVlanOverrideAllowed", []))

    @jsii.member(jsii_name="resetVlanRange")
    def reset_vlan_range(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVlanRange", []))

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
    @jsii.member(jsii_name="configVersion")
    def config_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "configVersion"))

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @builtins.property
    @jsii.member(jsii_name="vlanRange")
    def vlan_range(self) -> "DistributedPortGroupVlanRangeList":
        return typing.cast("DistributedPortGroupVlanRangeList", jsii.get(self, "vlanRange"))

    @builtins.property
    @jsii.member(jsii_name="activeUplinksInput")
    def active_uplinks_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "activeUplinksInput"))

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
    @jsii.member(jsii_name="autoExpandInput")
    def auto_expand_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "autoExpandInput"))

    @builtins.property
    @jsii.member(jsii_name="blockAllPortsInput")
    def block_all_ports_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "blockAllPortsInput"))

    @builtins.property
    @jsii.member(jsii_name="blockOverrideAllowedInput")
    def block_override_allowed_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "blockOverrideAllowedInput"))

    @builtins.property
    @jsii.member(jsii_name="checkBeaconInput")
    def check_beacon_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "checkBeaconInput"))

    @builtins.property
    @jsii.member(jsii_name="customAttributesInput")
    def custom_attributes_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "customAttributesInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="directpathGen2AllowedInput")
    def directpath_gen2_allowed_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "directpathGen2AllowedInput"))

    @builtins.property
    @jsii.member(jsii_name="distributedVirtualSwitchUuidInput")
    def distributed_virtual_switch_uuid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "distributedVirtualSwitchUuidInput"))

    @builtins.property
    @jsii.member(jsii_name="egressShapingAverageBandwidthInput")
    def egress_shaping_average_bandwidth_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "egressShapingAverageBandwidthInput"))

    @builtins.property
    @jsii.member(jsii_name="egressShapingBurstSizeInput")
    def egress_shaping_burst_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "egressShapingBurstSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="egressShapingEnabledInput")
    def egress_shaping_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "egressShapingEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="egressShapingPeakBandwidthInput")
    def egress_shaping_peak_bandwidth_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "egressShapingPeakBandwidthInput"))

    @builtins.property
    @jsii.member(jsii_name="failbackInput")
    def failback_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "failbackInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="ingressShapingAverageBandwidthInput")
    def ingress_shaping_average_bandwidth_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ingressShapingAverageBandwidthInput"))

    @builtins.property
    @jsii.member(jsii_name="ingressShapingBurstSizeInput")
    def ingress_shaping_burst_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ingressShapingBurstSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="ingressShapingEnabledInput")
    def ingress_shaping_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "ingressShapingEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="ingressShapingPeakBandwidthInput")
    def ingress_shaping_peak_bandwidth_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ingressShapingPeakBandwidthInput"))

    @builtins.property
    @jsii.member(jsii_name="lacpEnabledInput")
    def lacp_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "lacpEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="lacpModeInput")
    def lacp_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "lacpModeInput"))

    @builtins.property
    @jsii.member(jsii_name="livePortMovingAllowedInput")
    def live_port_moving_allowed_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "livePortMovingAllowedInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="netflowEnabledInput")
    def netflow_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "netflowEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="netflowOverrideAllowedInput")
    def netflow_override_allowed_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "netflowOverrideAllowedInput"))

    @builtins.property
    @jsii.member(jsii_name="networkResourcePoolKeyInput")
    def network_resource_pool_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "networkResourcePoolKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="networkResourcePoolOverrideAllowedInput")
    def network_resource_pool_override_allowed_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "networkResourcePoolOverrideAllowedInput"))

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
    @jsii.member(jsii_name="portConfigResetAtDisconnectInput")
    def port_config_reset_at_disconnect_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "portConfigResetAtDisconnectInput"))

    @builtins.property
    @jsii.member(jsii_name="portNameFormatInput")
    def port_name_format_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "portNameFormatInput"))

    @builtins.property
    @jsii.member(jsii_name="portPrivateSecondaryVlanIdInput")
    def port_private_secondary_vlan_id_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portPrivateSecondaryVlanIdInput"))

    @builtins.property
    @jsii.member(jsii_name="securityPolicyOverrideAllowedInput")
    def security_policy_override_allowed_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "securityPolicyOverrideAllowedInput"))

    @builtins.property
    @jsii.member(jsii_name="shapingOverrideAllowedInput")
    def shaping_override_allowed_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "shapingOverrideAllowedInput"))

    @builtins.property
    @jsii.member(jsii_name="standbyUplinksInput")
    def standby_uplinks_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "standbyUplinksInput"))

    @builtins.property
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property
    @jsii.member(jsii_name="teamingPolicyInput")
    def teaming_policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "teamingPolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="trafficFilterOverrideAllowedInput")
    def traffic_filter_override_allowed_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "trafficFilterOverrideAllowedInput"))

    @builtins.property
    @jsii.member(jsii_name="txUplinkInput")
    def tx_uplink_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "txUplinkInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="uplinkTeamingOverrideAllowedInput")
    def uplink_teaming_override_allowed_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "uplinkTeamingOverrideAllowedInput"))

    @builtins.property
    @jsii.member(jsii_name="vlanIdInput")
    def vlan_id_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "vlanIdInput"))

    @builtins.property
    @jsii.member(jsii_name="vlanOverrideAllowedInput")
    def vlan_override_allowed_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "vlanOverrideAllowedInput"))

    @builtins.property
    @jsii.member(jsii_name="vlanRangeInput")
    def vlan_range_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DistributedPortGroupVlanRange"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DistributedPortGroupVlanRange"]]], jsii.get(self, "vlanRangeInput"))

    @builtins.property
    @jsii.member(jsii_name="activeUplinks")
    def active_uplinks(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "activeUplinks"))

    @active_uplinks.setter
    def active_uplinks(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ffa2b115d2ff765a514b7d9f1f7364aaf340f51d607000486b7c987cf200395)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "activeUplinks", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__97443f33742be3d07a79349661ec9f05efae4d1a151a0ccbb355975b435986c4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__17049d2ffdabc75d9a85e65419c2cf9fa28cfec2181a6892be43ec0e6fdaacc4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1999e1074602c2fd9118540fedfc9120fe289f3529570657fb7431f49f1c2e92)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowPromiscuous", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="autoExpand")
    def auto_expand(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "autoExpand"))

    @auto_expand.setter
    def auto_expand(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b694b193695f90a198dfb16f4dbcf91d9407efc979d4990dc5b4fac3ec711cdb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoExpand", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="blockAllPorts")
    def block_all_ports(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "blockAllPorts"))

    @block_all_ports.setter
    def block_all_ports(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12d52a19d860c41af15a2921a0ed93f1492818f04e0af690ef6fe2c364f0f4ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "blockAllPorts", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="blockOverrideAllowed")
    def block_override_allowed(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "blockOverrideAllowed"))

    @block_override_allowed.setter
    def block_override_allowed(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a287cc621cbbf79ce4196cdfa25b5db9a69940c8ab4a1669605aeb02f0041f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "blockOverrideAllowed", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__24960a5719cab0a933e12cb9c83768de18dfa4f3eda2be72f18db50470967b80)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "checkBeacon", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__01ce9cc16610b05ce4c7f65b1cab669791dd51832893aaf668a2c13f91557c4a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customAttributes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__144466094e093ea3a63f45a47850eb13687972907513c3a25cfbaee906fa92b6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="directpathGen2Allowed")
    def directpath_gen2_allowed(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "directpathGen2Allowed"))

    @directpath_gen2_allowed.setter
    def directpath_gen2_allowed(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5239bbfd60844d7f861ad46c9ae83fbb79611cbfe91eac4eb67bd5aa14902e90)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "directpathGen2Allowed", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="distributedVirtualSwitchUuid")
    def distributed_virtual_switch_uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "distributedVirtualSwitchUuid"))

    @distributed_virtual_switch_uuid.setter
    def distributed_virtual_switch_uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5df734eed73768c997b81727ee35d598cf754987a8e32f772a23d7f80179d615)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "distributedVirtualSwitchUuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="egressShapingAverageBandwidth")
    def egress_shaping_average_bandwidth(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "egressShapingAverageBandwidth"))

    @egress_shaping_average_bandwidth.setter
    def egress_shaping_average_bandwidth(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__82186264e3410f6594b9fab0af3b3385b5a8ca43b455e062f52cbce674bd95fe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "egressShapingAverageBandwidth", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="egressShapingBurstSize")
    def egress_shaping_burst_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "egressShapingBurstSize"))

    @egress_shaping_burst_size.setter
    def egress_shaping_burst_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7dc98f998cf52dde44a7baaf6cefc1bebc64e2d26a1fdf15b0b4fe0c2a643c6a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "egressShapingBurstSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="egressShapingEnabled")
    def egress_shaping_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "egressShapingEnabled"))

    @egress_shaping_enabled.setter
    def egress_shaping_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80dfe53e6464aa1fec60c9c01692f3ca2fb64ca400fa97507543ecd38d4e520f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "egressShapingEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="egressShapingPeakBandwidth")
    def egress_shaping_peak_bandwidth(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "egressShapingPeakBandwidth"))

    @egress_shaping_peak_bandwidth.setter
    def egress_shaping_peak_bandwidth(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2eb24d812baf07fe4615d253f13299fd07f6dff8b0a6416059e84d2a96f74afc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "egressShapingPeakBandwidth", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__4c94dce3276e2015456231da03f5fca37e0a9a3b4fdb676d1b753c8bf4b837fe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "failback", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a4b2b732d7c75deaf6d0963dc058b0e797584cf93d4fb4f616c15669b31b988)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ingressShapingAverageBandwidth")
    def ingress_shaping_average_bandwidth(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ingressShapingAverageBandwidth"))

    @ingress_shaping_average_bandwidth.setter
    def ingress_shaping_average_bandwidth(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f76ed0cbadbf75afec646b9e98685adfe090aac22f574265313ab845954e7bbf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ingressShapingAverageBandwidth", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ingressShapingBurstSize")
    def ingress_shaping_burst_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ingressShapingBurstSize"))

    @ingress_shaping_burst_size.setter
    def ingress_shaping_burst_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1949d95957b1fed02fee5d2283a623d7c53adb741ad8c57dee759f2178120f58)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ingressShapingBurstSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ingressShapingEnabled")
    def ingress_shaping_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "ingressShapingEnabled"))

    @ingress_shaping_enabled.setter
    def ingress_shaping_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dca493db4ddff2f106f2f80a1c08da2cde9358bc2ffbfd1605339d3ad76a44ba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ingressShapingEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ingressShapingPeakBandwidth")
    def ingress_shaping_peak_bandwidth(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ingressShapingPeakBandwidth"))

    @ingress_shaping_peak_bandwidth.setter
    def ingress_shaping_peak_bandwidth(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e4f20a49f160f67696c8f9894f344233da1272a49a614be634fb474947d628a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ingressShapingPeakBandwidth", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="lacpEnabled")
    def lacp_enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "lacpEnabled"))

    @lacp_enabled.setter
    def lacp_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__240fccc0c6cef54b59a7cc0341482aa05a6d1f81ecab13a294deb362f188c811)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lacpEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="lacpMode")
    def lacp_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lacpMode"))

    @lacp_mode.setter
    def lacp_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8a8bb1ea5188b7d0decaf532e9b03641c72975987c7da02c991cd60a19b6903)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lacpMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="livePortMovingAllowed")
    def live_port_moving_allowed(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "livePortMovingAllowed"))

    @live_port_moving_allowed.setter
    def live_port_moving_allowed(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__727d0776c254c37fd28b563e10053d9a276b798de996506afc8b651efc2fbdf4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "livePortMovingAllowed", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05ae6ff1536890be7f023d9e0457c188223cbaf7b92f9b01eda8a99bf35a6c9b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="netflowEnabled")
    def netflow_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "netflowEnabled"))

    @netflow_enabled.setter
    def netflow_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f297f20812fff7ba12f60cccd9be22b214c28f9a87e82c54117ad8473d5db56)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "netflowEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="netflowOverrideAllowed")
    def netflow_override_allowed(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "netflowOverrideAllowed"))

    @netflow_override_allowed.setter
    def netflow_override_allowed(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5124ec93eae1187113e46502f18f33f4461449db0a97f8704030174f919d8a30)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "netflowOverrideAllowed", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="networkResourcePoolKey")
    def network_resource_pool_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "networkResourcePoolKey"))

    @network_resource_pool_key.setter
    def network_resource_pool_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc08b4b23587d721140fdcad30280071154a0ae9595e0db05a5dace3574225b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "networkResourcePoolKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="networkResourcePoolOverrideAllowed")
    def network_resource_pool_override_allowed(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "networkResourcePoolOverrideAllowed"))

    @network_resource_pool_override_allowed.setter
    def network_resource_pool_override_allowed(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b117af1a0de08df5cb4bd753a2ec513813a52b334271824511d77f589c1a8c18)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "networkResourcePoolOverrideAllowed", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__4775f25ba0ffbfbe3e9a24214ed7bbb1313522bc1800093b3f9a51baaa82c5c9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "notifySwitches", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="numberOfPorts")
    def number_of_ports(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numberOfPorts"))

    @number_of_ports.setter
    def number_of_ports(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6547c457bcb9374652aa06537fad0d1471b7ca2d9af510d389d07470334a712)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "numberOfPorts", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="portConfigResetAtDisconnect")
    def port_config_reset_at_disconnect(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "portConfigResetAtDisconnect"))

    @port_config_reset_at_disconnect.setter
    def port_config_reset_at_disconnect(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5a3bf495808f75fac25224ae82a4be2a2c49c7fed2d378d859d1f779052825e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "portConfigResetAtDisconnect", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="portNameFormat")
    def port_name_format(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "portNameFormat"))

    @port_name_format.setter
    def port_name_format(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__789747700f548cf01a8ccbae9d8641ec8d017c8fcbda9b975048fa47af49dc26)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "portNameFormat", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="portPrivateSecondaryVlanId")
    def port_private_secondary_vlan_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "portPrivateSecondaryVlanId"))

    @port_private_secondary_vlan_id.setter
    def port_private_secondary_vlan_id(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af785231cc5ede90e096aa34dfe4e32b146d1a5d2417ef869fe2f3fe00700fbe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "portPrivateSecondaryVlanId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="securityPolicyOverrideAllowed")
    def security_policy_override_allowed(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "securityPolicyOverrideAllowed"))

    @security_policy_override_allowed.setter
    def security_policy_override_allowed(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28a8c8cbbb8f0c2d9e6940f5920d23b129109ea3841d1781101d3f73ff64fd6f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "securityPolicyOverrideAllowed", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="shapingOverrideAllowed")
    def shaping_override_allowed(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "shapingOverrideAllowed"))

    @shaping_override_allowed.setter
    def shaping_override_allowed(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7050e1f08e733b9c9aea91a2572f1cbfe466e26aa3e87a9cd76ecd2c25c1ddb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "shapingOverrideAllowed", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="standbyUplinks")
    def standby_uplinks(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "standbyUplinks"))

    @standby_uplinks.setter
    def standby_uplinks(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6669d09cd1a9d0a68e8777b5a9c9138fae07cda6748260c4bb2c64d5d7b73e83)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "standbyUplinks", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04e165e43caddddf49a67497fd431af40f2d7409cbbc13a1d6826c58800a7f2a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="teamingPolicy")
    def teaming_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "teamingPolicy"))

    @teaming_policy.setter
    def teaming_policy(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23ab96fa182173fad5643739962f3ec543bad52e8a1c398ac2ef8e53fa64d348)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "teamingPolicy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="trafficFilterOverrideAllowed")
    def traffic_filter_override_allowed(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "trafficFilterOverrideAllowed"))

    @traffic_filter_override_allowed.setter
    def traffic_filter_override_allowed(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ce3a5fa0a01e819106adaed2ff7fa2bbe040bba5219483947bc9e6581141c7e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "trafficFilterOverrideAllowed", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="txUplink")
    def tx_uplink(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "txUplink"))

    @tx_uplink.setter
    def tx_uplink(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c90895be218d24a2cb7d0b8e77d4884f0d8756531f669a6805bf187d221b7d4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "txUplink", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__267e9f1c744878a18b7a9149e2e47e5f119407b84fe6d84abb3333144003f8c2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uplinkTeamingOverrideAllowed")
    def uplink_teaming_override_allowed(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "uplinkTeamingOverrideAllowed"))

    @uplink_teaming_override_allowed.setter
    def uplink_teaming_override_allowed(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__679fd9939999150f93d8fb2ed47cfa79af5945c7b8955b760bfd55221314b7da)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uplinkTeamingOverrideAllowed", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vlanId")
    def vlan_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "vlanId"))

    @vlan_id.setter
    def vlan_id(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63afc30fb949fc17829334cd57c40640ca9afdcf5129af45d245a7c098754656)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vlanId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vlanOverrideAllowed")
    def vlan_override_allowed(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "vlanOverrideAllowed"))

    @vlan_override_allowed.setter
    def vlan_override_allowed(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86346ad9cd9c55dc98949307324ef4f14ea368392ea4676a0ecdd94c2d0df170)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vlanOverrideAllowed", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.distributedPortGroup.DistributedPortGroupConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "distributed_virtual_switch_uuid": "distributedVirtualSwitchUuid",
        "name": "name",
        "active_uplinks": "activeUplinks",
        "allow_forged_transmits": "allowForgedTransmits",
        "allow_mac_changes": "allowMacChanges",
        "allow_promiscuous": "allowPromiscuous",
        "auto_expand": "autoExpand",
        "block_all_ports": "blockAllPorts",
        "block_override_allowed": "blockOverrideAllowed",
        "check_beacon": "checkBeacon",
        "custom_attributes": "customAttributes",
        "description": "description",
        "directpath_gen2_allowed": "directpathGen2Allowed",
        "egress_shaping_average_bandwidth": "egressShapingAverageBandwidth",
        "egress_shaping_burst_size": "egressShapingBurstSize",
        "egress_shaping_enabled": "egressShapingEnabled",
        "egress_shaping_peak_bandwidth": "egressShapingPeakBandwidth",
        "failback": "failback",
        "id": "id",
        "ingress_shaping_average_bandwidth": "ingressShapingAverageBandwidth",
        "ingress_shaping_burst_size": "ingressShapingBurstSize",
        "ingress_shaping_enabled": "ingressShapingEnabled",
        "ingress_shaping_peak_bandwidth": "ingressShapingPeakBandwidth",
        "lacp_enabled": "lacpEnabled",
        "lacp_mode": "lacpMode",
        "live_port_moving_allowed": "livePortMovingAllowed",
        "netflow_enabled": "netflowEnabled",
        "netflow_override_allowed": "netflowOverrideAllowed",
        "network_resource_pool_key": "networkResourcePoolKey",
        "network_resource_pool_override_allowed": "networkResourcePoolOverrideAllowed",
        "notify_switches": "notifySwitches",
        "number_of_ports": "numberOfPorts",
        "port_config_reset_at_disconnect": "portConfigResetAtDisconnect",
        "port_name_format": "portNameFormat",
        "port_private_secondary_vlan_id": "portPrivateSecondaryVlanId",
        "security_policy_override_allowed": "securityPolicyOverrideAllowed",
        "shaping_override_allowed": "shapingOverrideAllowed",
        "standby_uplinks": "standbyUplinks",
        "tags": "tags",
        "teaming_policy": "teamingPolicy",
        "traffic_filter_override_allowed": "trafficFilterOverrideAllowed",
        "tx_uplink": "txUplink",
        "type": "type",
        "uplink_teaming_override_allowed": "uplinkTeamingOverrideAllowed",
        "vlan_id": "vlanId",
        "vlan_override_allowed": "vlanOverrideAllowed",
        "vlan_range": "vlanRange",
    },
)
class DistributedPortGroupConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        distributed_virtual_switch_uuid: builtins.str,
        name: builtins.str,
        active_uplinks: typing.Optional[typing.Sequence[builtins.str]] = None,
        allow_forged_transmits: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_mac_changes: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_promiscuous: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        auto_expand: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        block_all_ports: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        block_override_allowed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        check_beacon: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        custom_attributes: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        directpath_gen2_allowed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        egress_shaping_average_bandwidth: typing.Optional[jsii.Number] = None,
        egress_shaping_burst_size: typing.Optional[jsii.Number] = None,
        egress_shaping_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        egress_shaping_peak_bandwidth: typing.Optional[jsii.Number] = None,
        failback: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        ingress_shaping_average_bandwidth: typing.Optional[jsii.Number] = None,
        ingress_shaping_burst_size: typing.Optional[jsii.Number] = None,
        ingress_shaping_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ingress_shaping_peak_bandwidth: typing.Optional[jsii.Number] = None,
        lacp_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        lacp_mode: typing.Optional[builtins.str] = None,
        live_port_moving_allowed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        netflow_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        netflow_override_allowed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        network_resource_pool_key: typing.Optional[builtins.str] = None,
        network_resource_pool_override_allowed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        notify_switches: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        number_of_ports: typing.Optional[jsii.Number] = None,
        port_config_reset_at_disconnect: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        port_name_format: typing.Optional[builtins.str] = None,
        port_private_secondary_vlan_id: typing.Optional[jsii.Number] = None,
        security_policy_override_allowed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        shaping_override_allowed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        standby_uplinks: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        teaming_policy: typing.Optional[builtins.str] = None,
        traffic_filter_override_allowed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tx_uplink: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        type: typing.Optional[builtins.str] = None,
        uplink_teaming_override_allowed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        vlan_id: typing.Optional[jsii.Number] = None,
        vlan_override_allowed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        vlan_range: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DistributedPortGroupVlanRange", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param distributed_virtual_switch_uuid: The UUID of the DVS to attach this port group to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#distributed_virtual_switch_uuid DistributedPortGroup#distributed_virtual_switch_uuid}
        :param name: The name of the portgroup. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#name DistributedPortGroup#name}
        :param active_uplinks: List of active uplinks used for load balancing, matching the names of the uplinks assigned in the DVS. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#active_uplinks DistributedPortGroup#active_uplinks}
        :param allow_forged_transmits: Controls whether or not the virtual network adapter is allowed to send network traffic with a different MAC address than that of its own. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#allow_forged_transmits DistributedPortGroup#allow_forged_transmits}
        :param allow_mac_changes: Controls whether or not the Media Access Control (MAC) address can be changed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#allow_mac_changes DistributedPortGroup#allow_mac_changes}
        :param allow_promiscuous: Enable promiscuous mode on the network. This flag indicates whether or not all traffic is seen on a given port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#allow_promiscuous DistributedPortGroup#allow_promiscuous}
        :param auto_expand: Auto-expands the port group beyond the port count configured in number_of_ports when necessary. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#auto_expand DistributedPortGroup#auto_expand}
        :param block_all_ports: Indicates whether to block all ports by default. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#block_all_ports DistributedPortGroup#block_all_ports}
        :param block_override_allowed: Allow the blocked setting of an individual port to override the setting in the portgroup. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#block_override_allowed DistributedPortGroup#block_override_allowed}
        :param check_beacon: Enable beacon probing on the ports this policy applies to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#check_beacon DistributedPortGroup#check_beacon}
        :param custom_attributes: A list of custom attributes to set on this resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#custom_attributes DistributedPortGroup#custom_attributes}
        :param description: The description of the portgroup. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#description DistributedPortGroup#description}
        :param directpath_gen2_allowed: Allow VMDirectPath Gen2 on the ports this policy applies to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#directpath_gen2_allowed DistributedPortGroup#directpath_gen2_allowed}
        :param egress_shaping_average_bandwidth: The average egress bandwidth in bits per second if egress shaping is enabled on the port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#egress_shaping_average_bandwidth DistributedPortGroup#egress_shaping_average_bandwidth}
        :param egress_shaping_burst_size: The maximum egress burst size allowed in bytes if egress shaping is enabled on the port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#egress_shaping_burst_size DistributedPortGroup#egress_shaping_burst_size}
        :param egress_shaping_enabled: True if the traffic shaper is enabled for egress traffic on the port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#egress_shaping_enabled DistributedPortGroup#egress_shaping_enabled}
        :param egress_shaping_peak_bandwidth: The peak egress bandwidth during bursts in bits per second if egress traffic shaping is enabled on the port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#egress_shaping_peak_bandwidth DistributedPortGroup#egress_shaping_peak_bandwidth}
        :param failback: If true, the teaming policy will re-activate failed interfaces higher in precedence when they come back up. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#failback DistributedPortGroup#failback}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#id DistributedPortGroup#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param ingress_shaping_average_bandwidth: The average ingress bandwidth in bits per second if ingress shaping is enabled on the port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#ingress_shaping_average_bandwidth DistributedPortGroup#ingress_shaping_average_bandwidth}
        :param ingress_shaping_burst_size: The maximum ingress burst size allowed in bytes if ingress shaping is enabled on the port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#ingress_shaping_burst_size DistributedPortGroup#ingress_shaping_burst_size}
        :param ingress_shaping_enabled: True if the traffic shaper is enabled for ingress traffic on the port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#ingress_shaping_enabled DistributedPortGroup#ingress_shaping_enabled}
        :param ingress_shaping_peak_bandwidth: The peak ingress bandwidth during bursts in bits per second if ingress traffic shaping is enabled on the port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#ingress_shaping_peak_bandwidth DistributedPortGroup#ingress_shaping_peak_bandwidth}
        :param lacp_enabled: Whether or not to enable LACP on all uplink ports. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#lacp_enabled DistributedPortGroup#lacp_enabled}
        :param lacp_mode: The uplink LACP mode to use. Can be one of active or passive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#lacp_mode DistributedPortGroup#lacp_mode}
        :param live_port_moving_allowed: Allow a live port to be moved in and out of the portgroup. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#live_port_moving_allowed DistributedPortGroup#live_port_moving_allowed}
        :param netflow_enabled: Indicates whether to enable netflow on all ports. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#netflow_enabled DistributedPortGroup#netflow_enabled}
        :param netflow_override_allowed: Allow the enabling or disabling of Netflow on a port, contrary to the policy in the portgroup. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#netflow_override_allowed DistributedPortGroup#netflow_override_allowed}
        :param network_resource_pool_key: The key of a network resource pool to associate with this portgroup. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#network_resource_pool_key DistributedPortGroup#network_resource_pool_key}
        :param network_resource_pool_override_allowed: Allow the network resource pool of an individual port to override the setting in the portgroup. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#network_resource_pool_override_allowed DistributedPortGroup#network_resource_pool_override_allowed}
        :param notify_switches: If true, the teaming policy will notify the broadcast network of a NIC failover, triggering cache updates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#notify_switches DistributedPortGroup#notify_switches}
        :param number_of_ports: The number of ports in this portgroup. The DVS will expand and shrink by modifying this setting. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#number_of_ports DistributedPortGroup#number_of_ports}
        :param port_config_reset_at_disconnect: Reset the setting of any ports in this portgroup back to the default setting when the port disconnects. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#port_config_reset_at_disconnect DistributedPortGroup#port_config_reset_at_disconnect}
        :param port_name_format: A template string to use when creating ports in the portgroup. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#port_name_format DistributedPortGroup#port_name_format}
        :param port_private_secondary_vlan_id: The secondary VLAN ID for this port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#port_private_secondary_vlan_id DistributedPortGroup#port_private_secondary_vlan_id}
        :param security_policy_override_allowed: Allow security policy settings on a port to override those on the portgroup. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#security_policy_override_allowed DistributedPortGroup#security_policy_override_allowed}
        :param shaping_override_allowed: Allow the traffic shaping policies of an individual port to override the settings in the portgroup. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#shaping_override_allowed DistributedPortGroup#shaping_override_allowed}
        :param standby_uplinks: List of standby uplinks used for load balancing, matching the names of the uplinks assigned in the DVS. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#standby_uplinks DistributedPortGroup#standby_uplinks}
        :param tags: A list of tag IDs to apply to this object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#tags DistributedPortGroup#tags}
        :param teaming_policy: The network adapter teaming policy. Can be one of loadbalance_ip, loadbalance_srcmac, loadbalance_srcid, failover_explicit, or loadbalance_loadbased. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#teaming_policy DistributedPortGroup#teaming_policy}
        :param traffic_filter_override_allowed: Allow any filter policies set on the individual port to override those in the portgroup. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#traffic_filter_override_allowed DistributedPortGroup#traffic_filter_override_allowed}
        :param tx_uplink: If true, a copy of packets sent to the switch will always be forwarded to an uplink in addition to the regular packet forwarded done by the switch. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#tx_uplink DistributedPortGroup#tx_uplink}
        :param type: The type of portgroup. Can be one of earlyBinding (static) or ephemeral. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#type DistributedPortGroup#type}
        :param uplink_teaming_override_allowed: Allow the uplink teaming policies on a port to override those on the portgroup. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#uplink_teaming_override_allowed DistributedPortGroup#uplink_teaming_override_allowed}
        :param vlan_id: The VLAN ID for single VLAN mode. 0 denotes no VLAN. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#vlan_id DistributedPortGroup#vlan_id}
        :param vlan_override_allowed: Allow the VLAN configuration on a port to override those on the portgroup. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#vlan_override_allowed DistributedPortGroup#vlan_override_allowed}
        :param vlan_range: vlan_range block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#vlan_range DistributedPortGroup#vlan_range}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94b336c963c7511a380896c9f402d9934ac93e17bfb20a0df10b758361bf699a)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument distributed_virtual_switch_uuid", value=distributed_virtual_switch_uuid, expected_type=type_hints["distributed_virtual_switch_uuid"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument active_uplinks", value=active_uplinks, expected_type=type_hints["active_uplinks"])
            check_type(argname="argument allow_forged_transmits", value=allow_forged_transmits, expected_type=type_hints["allow_forged_transmits"])
            check_type(argname="argument allow_mac_changes", value=allow_mac_changes, expected_type=type_hints["allow_mac_changes"])
            check_type(argname="argument allow_promiscuous", value=allow_promiscuous, expected_type=type_hints["allow_promiscuous"])
            check_type(argname="argument auto_expand", value=auto_expand, expected_type=type_hints["auto_expand"])
            check_type(argname="argument block_all_ports", value=block_all_ports, expected_type=type_hints["block_all_ports"])
            check_type(argname="argument block_override_allowed", value=block_override_allowed, expected_type=type_hints["block_override_allowed"])
            check_type(argname="argument check_beacon", value=check_beacon, expected_type=type_hints["check_beacon"])
            check_type(argname="argument custom_attributes", value=custom_attributes, expected_type=type_hints["custom_attributes"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument directpath_gen2_allowed", value=directpath_gen2_allowed, expected_type=type_hints["directpath_gen2_allowed"])
            check_type(argname="argument egress_shaping_average_bandwidth", value=egress_shaping_average_bandwidth, expected_type=type_hints["egress_shaping_average_bandwidth"])
            check_type(argname="argument egress_shaping_burst_size", value=egress_shaping_burst_size, expected_type=type_hints["egress_shaping_burst_size"])
            check_type(argname="argument egress_shaping_enabled", value=egress_shaping_enabled, expected_type=type_hints["egress_shaping_enabled"])
            check_type(argname="argument egress_shaping_peak_bandwidth", value=egress_shaping_peak_bandwidth, expected_type=type_hints["egress_shaping_peak_bandwidth"])
            check_type(argname="argument failback", value=failback, expected_type=type_hints["failback"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument ingress_shaping_average_bandwidth", value=ingress_shaping_average_bandwidth, expected_type=type_hints["ingress_shaping_average_bandwidth"])
            check_type(argname="argument ingress_shaping_burst_size", value=ingress_shaping_burst_size, expected_type=type_hints["ingress_shaping_burst_size"])
            check_type(argname="argument ingress_shaping_enabled", value=ingress_shaping_enabled, expected_type=type_hints["ingress_shaping_enabled"])
            check_type(argname="argument ingress_shaping_peak_bandwidth", value=ingress_shaping_peak_bandwidth, expected_type=type_hints["ingress_shaping_peak_bandwidth"])
            check_type(argname="argument lacp_enabled", value=lacp_enabled, expected_type=type_hints["lacp_enabled"])
            check_type(argname="argument lacp_mode", value=lacp_mode, expected_type=type_hints["lacp_mode"])
            check_type(argname="argument live_port_moving_allowed", value=live_port_moving_allowed, expected_type=type_hints["live_port_moving_allowed"])
            check_type(argname="argument netflow_enabled", value=netflow_enabled, expected_type=type_hints["netflow_enabled"])
            check_type(argname="argument netflow_override_allowed", value=netflow_override_allowed, expected_type=type_hints["netflow_override_allowed"])
            check_type(argname="argument network_resource_pool_key", value=network_resource_pool_key, expected_type=type_hints["network_resource_pool_key"])
            check_type(argname="argument network_resource_pool_override_allowed", value=network_resource_pool_override_allowed, expected_type=type_hints["network_resource_pool_override_allowed"])
            check_type(argname="argument notify_switches", value=notify_switches, expected_type=type_hints["notify_switches"])
            check_type(argname="argument number_of_ports", value=number_of_ports, expected_type=type_hints["number_of_ports"])
            check_type(argname="argument port_config_reset_at_disconnect", value=port_config_reset_at_disconnect, expected_type=type_hints["port_config_reset_at_disconnect"])
            check_type(argname="argument port_name_format", value=port_name_format, expected_type=type_hints["port_name_format"])
            check_type(argname="argument port_private_secondary_vlan_id", value=port_private_secondary_vlan_id, expected_type=type_hints["port_private_secondary_vlan_id"])
            check_type(argname="argument security_policy_override_allowed", value=security_policy_override_allowed, expected_type=type_hints["security_policy_override_allowed"])
            check_type(argname="argument shaping_override_allowed", value=shaping_override_allowed, expected_type=type_hints["shaping_override_allowed"])
            check_type(argname="argument standby_uplinks", value=standby_uplinks, expected_type=type_hints["standby_uplinks"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument teaming_policy", value=teaming_policy, expected_type=type_hints["teaming_policy"])
            check_type(argname="argument traffic_filter_override_allowed", value=traffic_filter_override_allowed, expected_type=type_hints["traffic_filter_override_allowed"])
            check_type(argname="argument tx_uplink", value=tx_uplink, expected_type=type_hints["tx_uplink"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument uplink_teaming_override_allowed", value=uplink_teaming_override_allowed, expected_type=type_hints["uplink_teaming_override_allowed"])
            check_type(argname="argument vlan_id", value=vlan_id, expected_type=type_hints["vlan_id"])
            check_type(argname="argument vlan_override_allowed", value=vlan_override_allowed, expected_type=type_hints["vlan_override_allowed"])
            check_type(argname="argument vlan_range", value=vlan_range, expected_type=type_hints["vlan_range"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "distributed_virtual_switch_uuid": distributed_virtual_switch_uuid,
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
        if active_uplinks is not None:
            self._values["active_uplinks"] = active_uplinks
        if allow_forged_transmits is not None:
            self._values["allow_forged_transmits"] = allow_forged_transmits
        if allow_mac_changes is not None:
            self._values["allow_mac_changes"] = allow_mac_changes
        if allow_promiscuous is not None:
            self._values["allow_promiscuous"] = allow_promiscuous
        if auto_expand is not None:
            self._values["auto_expand"] = auto_expand
        if block_all_ports is not None:
            self._values["block_all_ports"] = block_all_ports
        if block_override_allowed is not None:
            self._values["block_override_allowed"] = block_override_allowed
        if check_beacon is not None:
            self._values["check_beacon"] = check_beacon
        if custom_attributes is not None:
            self._values["custom_attributes"] = custom_attributes
        if description is not None:
            self._values["description"] = description
        if directpath_gen2_allowed is not None:
            self._values["directpath_gen2_allowed"] = directpath_gen2_allowed
        if egress_shaping_average_bandwidth is not None:
            self._values["egress_shaping_average_bandwidth"] = egress_shaping_average_bandwidth
        if egress_shaping_burst_size is not None:
            self._values["egress_shaping_burst_size"] = egress_shaping_burst_size
        if egress_shaping_enabled is not None:
            self._values["egress_shaping_enabled"] = egress_shaping_enabled
        if egress_shaping_peak_bandwidth is not None:
            self._values["egress_shaping_peak_bandwidth"] = egress_shaping_peak_bandwidth
        if failback is not None:
            self._values["failback"] = failback
        if id is not None:
            self._values["id"] = id
        if ingress_shaping_average_bandwidth is not None:
            self._values["ingress_shaping_average_bandwidth"] = ingress_shaping_average_bandwidth
        if ingress_shaping_burst_size is not None:
            self._values["ingress_shaping_burst_size"] = ingress_shaping_burst_size
        if ingress_shaping_enabled is not None:
            self._values["ingress_shaping_enabled"] = ingress_shaping_enabled
        if ingress_shaping_peak_bandwidth is not None:
            self._values["ingress_shaping_peak_bandwidth"] = ingress_shaping_peak_bandwidth
        if lacp_enabled is not None:
            self._values["lacp_enabled"] = lacp_enabled
        if lacp_mode is not None:
            self._values["lacp_mode"] = lacp_mode
        if live_port_moving_allowed is not None:
            self._values["live_port_moving_allowed"] = live_port_moving_allowed
        if netflow_enabled is not None:
            self._values["netflow_enabled"] = netflow_enabled
        if netflow_override_allowed is not None:
            self._values["netflow_override_allowed"] = netflow_override_allowed
        if network_resource_pool_key is not None:
            self._values["network_resource_pool_key"] = network_resource_pool_key
        if network_resource_pool_override_allowed is not None:
            self._values["network_resource_pool_override_allowed"] = network_resource_pool_override_allowed
        if notify_switches is not None:
            self._values["notify_switches"] = notify_switches
        if number_of_ports is not None:
            self._values["number_of_ports"] = number_of_ports
        if port_config_reset_at_disconnect is not None:
            self._values["port_config_reset_at_disconnect"] = port_config_reset_at_disconnect
        if port_name_format is not None:
            self._values["port_name_format"] = port_name_format
        if port_private_secondary_vlan_id is not None:
            self._values["port_private_secondary_vlan_id"] = port_private_secondary_vlan_id
        if security_policy_override_allowed is not None:
            self._values["security_policy_override_allowed"] = security_policy_override_allowed
        if shaping_override_allowed is not None:
            self._values["shaping_override_allowed"] = shaping_override_allowed
        if standby_uplinks is not None:
            self._values["standby_uplinks"] = standby_uplinks
        if tags is not None:
            self._values["tags"] = tags
        if teaming_policy is not None:
            self._values["teaming_policy"] = teaming_policy
        if traffic_filter_override_allowed is not None:
            self._values["traffic_filter_override_allowed"] = traffic_filter_override_allowed
        if tx_uplink is not None:
            self._values["tx_uplink"] = tx_uplink
        if type is not None:
            self._values["type"] = type
        if uplink_teaming_override_allowed is not None:
            self._values["uplink_teaming_override_allowed"] = uplink_teaming_override_allowed
        if vlan_id is not None:
            self._values["vlan_id"] = vlan_id
        if vlan_override_allowed is not None:
            self._values["vlan_override_allowed"] = vlan_override_allowed
        if vlan_range is not None:
            self._values["vlan_range"] = vlan_range

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
    def distributed_virtual_switch_uuid(self) -> builtins.str:
        '''The UUID of the DVS to attach this port group to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#distributed_virtual_switch_uuid DistributedPortGroup#distributed_virtual_switch_uuid}
        '''
        result = self._values.get("distributed_virtual_switch_uuid")
        assert result is not None, "Required property 'distributed_virtual_switch_uuid' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the portgroup.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#name DistributedPortGroup#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def active_uplinks(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of active uplinks used for load balancing, matching the names of the uplinks assigned in the DVS.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#active_uplinks DistributedPortGroup#active_uplinks}
        '''
        result = self._values.get("active_uplinks")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def allow_forged_transmits(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Controls whether or not the virtual network adapter is allowed to send network traffic with a different MAC address than that of its own.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#allow_forged_transmits DistributedPortGroup#allow_forged_transmits}
        '''
        result = self._values.get("allow_forged_transmits")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def allow_mac_changes(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Controls whether or not the Media Access Control (MAC) address can be changed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#allow_mac_changes DistributedPortGroup#allow_mac_changes}
        '''
        result = self._values.get("allow_mac_changes")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def allow_promiscuous(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable promiscuous mode on the network.

        This flag indicates whether or not all traffic is seen on a given port.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#allow_promiscuous DistributedPortGroup#allow_promiscuous}
        '''
        result = self._values.get("allow_promiscuous")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def auto_expand(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Auto-expands the port group beyond the port count configured in number_of_ports when necessary.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#auto_expand DistributedPortGroup#auto_expand}
        '''
        result = self._values.get("auto_expand")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def block_all_ports(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Indicates whether to block all ports by default.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#block_all_ports DistributedPortGroup#block_all_ports}
        '''
        result = self._values.get("block_all_ports")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def block_override_allowed(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Allow the blocked setting of an individual port to override the setting in the portgroup.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#block_override_allowed DistributedPortGroup#block_override_allowed}
        '''
        result = self._values.get("block_override_allowed")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def check_beacon(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable beacon probing on the ports this policy applies to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#check_beacon DistributedPortGroup#check_beacon}
        '''
        result = self._values.get("check_beacon")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def custom_attributes(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''A list of custom attributes to set on this resource.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#custom_attributes DistributedPortGroup#custom_attributes}
        '''
        result = self._values.get("custom_attributes")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The description of the portgroup.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#description DistributedPortGroup#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def directpath_gen2_allowed(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Allow VMDirectPath Gen2 on the ports this policy applies to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#directpath_gen2_allowed DistributedPortGroup#directpath_gen2_allowed}
        '''
        result = self._values.get("directpath_gen2_allowed")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def egress_shaping_average_bandwidth(self) -> typing.Optional[jsii.Number]:
        '''The average egress bandwidth in bits per second if egress shaping is enabled on the port.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#egress_shaping_average_bandwidth DistributedPortGroup#egress_shaping_average_bandwidth}
        '''
        result = self._values.get("egress_shaping_average_bandwidth")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def egress_shaping_burst_size(self) -> typing.Optional[jsii.Number]:
        '''The maximum egress burst size allowed in bytes if egress shaping is enabled on the port.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#egress_shaping_burst_size DistributedPortGroup#egress_shaping_burst_size}
        '''
        result = self._values.get("egress_shaping_burst_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def egress_shaping_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''True if the traffic shaper is enabled for egress traffic on the port.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#egress_shaping_enabled DistributedPortGroup#egress_shaping_enabled}
        '''
        result = self._values.get("egress_shaping_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def egress_shaping_peak_bandwidth(self) -> typing.Optional[jsii.Number]:
        '''The peak egress bandwidth during bursts in bits per second if egress traffic shaping is enabled on the port.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#egress_shaping_peak_bandwidth DistributedPortGroup#egress_shaping_peak_bandwidth}
        '''
        result = self._values.get("egress_shaping_peak_bandwidth")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def failback(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If true, the teaming policy will re-activate failed interfaces higher in precedence when they come back up.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#failback DistributedPortGroup#failback}
        '''
        result = self._values.get("failback")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#id DistributedPortGroup#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ingress_shaping_average_bandwidth(self) -> typing.Optional[jsii.Number]:
        '''The average ingress bandwidth in bits per second if ingress shaping is enabled on the port.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#ingress_shaping_average_bandwidth DistributedPortGroup#ingress_shaping_average_bandwidth}
        '''
        result = self._values.get("ingress_shaping_average_bandwidth")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ingress_shaping_burst_size(self) -> typing.Optional[jsii.Number]:
        '''The maximum ingress burst size allowed in bytes if ingress shaping is enabled on the port.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#ingress_shaping_burst_size DistributedPortGroup#ingress_shaping_burst_size}
        '''
        result = self._values.get("ingress_shaping_burst_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ingress_shaping_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''True if the traffic shaper is enabled for ingress traffic on the port.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#ingress_shaping_enabled DistributedPortGroup#ingress_shaping_enabled}
        '''
        result = self._values.get("ingress_shaping_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def ingress_shaping_peak_bandwidth(self) -> typing.Optional[jsii.Number]:
        '''The peak ingress bandwidth during bursts in bits per second if ingress traffic shaping is enabled on the port.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#ingress_shaping_peak_bandwidth DistributedPortGroup#ingress_shaping_peak_bandwidth}
        '''
        result = self._values.get("ingress_shaping_peak_bandwidth")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def lacp_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether or not to enable LACP on all uplink ports.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#lacp_enabled DistributedPortGroup#lacp_enabled}
        '''
        result = self._values.get("lacp_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def lacp_mode(self) -> typing.Optional[builtins.str]:
        '''The uplink LACP mode to use. Can be one of active or passive.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#lacp_mode DistributedPortGroup#lacp_mode}
        '''
        result = self._values.get("lacp_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def live_port_moving_allowed(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Allow a live port to be moved in and out of the portgroup.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#live_port_moving_allowed DistributedPortGroup#live_port_moving_allowed}
        '''
        result = self._values.get("live_port_moving_allowed")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def netflow_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Indicates whether to enable netflow on all ports.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#netflow_enabled DistributedPortGroup#netflow_enabled}
        '''
        result = self._values.get("netflow_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def netflow_override_allowed(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Allow the enabling or disabling of Netflow on a port, contrary to the policy in the portgroup.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#netflow_override_allowed DistributedPortGroup#netflow_override_allowed}
        '''
        result = self._values.get("netflow_override_allowed")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def network_resource_pool_key(self) -> typing.Optional[builtins.str]:
        '''The key of a network resource pool to associate with this portgroup.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#network_resource_pool_key DistributedPortGroup#network_resource_pool_key}
        '''
        result = self._values.get("network_resource_pool_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def network_resource_pool_override_allowed(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Allow the network resource pool of an individual port to override the setting in the portgroup.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#network_resource_pool_override_allowed DistributedPortGroup#network_resource_pool_override_allowed}
        '''
        result = self._values.get("network_resource_pool_override_allowed")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def notify_switches(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If true, the teaming policy will notify the broadcast network of a NIC failover, triggering cache updates.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#notify_switches DistributedPortGroup#notify_switches}
        '''
        result = self._values.get("notify_switches")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def number_of_ports(self) -> typing.Optional[jsii.Number]:
        '''The number of ports in this portgroup. The DVS will expand and shrink by modifying this setting.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#number_of_ports DistributedPortGroup#number_of_ports}
        '''
        result = self._values.get("number_of_ports")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def port_config_reset_at_disconnect(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Reset the setting of any ports in this portgroup back to the default setting when the port disconnects.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#port_config_reset_at_disconnect DistributedPortGroup#port_config_reset_at_disconnect}
        '''
        result = self._values.get("port_config_reset_at_disconnect")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def port_name_format(self) -> typing.Optional[builtins.str]:
        '''A template string to use when creating ports in the portgroup.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#port_name_format DistributedPortGroup#port_name_format}
        '''
        result = self._values.get("port_name_format")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def port_private_secondary_vlan_id(self) -> typing.Optional[jsii.Number]:
        '''The secondary VLAN ID for this port.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#port_private_secondary_vlan_id DistributedPortGroup#port_private_secondary_vlan_id}
        '''
        result = self._values.get("port_private_secondary_vlan_id")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def security_policy_override_allowed(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Allow security policy settings on a port to override those on the portgroup.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#security_policy_override_allowed DistributedPortGroup#security_policy_override_allowed}
        '''
        result = self._values.get("security_policy_override_allowed")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def shaping_override_allowed(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Allow the traffic shaping policies of an individual port to override the settings in the portgroup.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#shaping_override_allowed DistributedPortGroup#shaping_override_allowed}
        '''
        result = self._values.get("shaping_override_allowed")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def standby_uplinks(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of standby uplinks used for load balancing, matching the names of the uplinks assigned in the DVS.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#standby_uplinks DistributedPortGroup#standby_uplinks}
        '''
        result = self._values.get("standby_uplinks")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of tag IDs to apply to this object.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#tags DistributedPortGroup#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def teaming_policy(self) -> typing.Optional[builtins.str]:
        '''The network adapter teaming policy. Can be one of loadbalance_ip, loadbalance_srcmac, loadbalance_srcid, failover_explicit, or loadbalance_loadbased.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#teaming_policy DistributedPortGroup#teaming_policy}
        '''
        result = self._values.get("teaming_policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def traffic_filter_override_allowed(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Allow any filter policies set on the individual port to override those in the portgroup.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#traffic_filter_override_allowed DistributedPortGroup#traffic_filter_override_allowed}
        '''
        result = self._values.get("traffic_filter_override_allowed")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tx_uplink(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If true, a copy of packets sent to the switch will always be forwarded to an uplink in addition to the regular packet forwarded done by the switch.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#tx_uplink DistributedPortGroup#tx_uplink}
        '''
        result = self._values.get("tx_uplink")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''The type of portgroup. Can be one of earlyBinding (static) or ephemeral.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#type DistributedPortGroup#type}
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def uplink_teaming_override_allowed(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Allow the uplink teaming policies on a port to override those on the portgroup.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#uplink_teaming_override_allowed DistributedPortGroup#uplink_teaming_override_allowed}
        '''
        result = self._values.get("uplink_teaming_override_allowed")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def vlan_id(self) -> typing.Optional[jsii.Number]:
        '''The VLAN ID for single VLAN mode. 0 denotes no VLAN.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#vlan_id DistributedPortGroup#vlan_id}
        '''
        result = self._values.get("vlan_id")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def vlan_override_allowed(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Allow the VLAN configuration on a port to override those on the portgroup.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#vlan_override_allowed DistributedPortGroup#vlan_override_allowed}
        '''
        result = self._values.get("vlan_override_allowed")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def vlan_range(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DistributedPortGroupVlanRange"]]]:
        '''vlan_range block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#vlan_range DistributedPortGroup#vlan_range}
        '''
        result = self._values.get("vlan_range")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DistributedPortGroupVlanRange"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DistributedPortGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.distributedPortGroup.DistributedPortGroupVlanRange",
    jsii_struct_bases=[],
    name_mapping={"max_vlan": "maxVlan", "min_vlan": "minVlan"},
)
class DistributedPortGroupVlanRange:
    def __init__(self, *, max_vlan: jsii.Number, min_vlan: jsii.Number) -> None:
        '''
        :param max_vlan: The minimum VLAN to use in the range. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#max_vlan DistributedPortGroup#max_vlan}
        :param min_vlan: The minimum VLAN to use in the range. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#min_vlan DistributedPortGroup#min_vlan}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52bd7440208683f7e74f25e7931a6a49182a6c62b38b85bb883413f10f2bcb7f)
            check_type(argname="argument max_vlan", value=max_vlan, expected_type=type_hints["max_vlan"])
            check_type(argname="argument min_vlan", value=min_vlan, expected_type=type_hints["min_vlan"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "max_vlan": max_vlan,
            "min_vlan": min_vlan,
        }

    @builtins.property
    def max_vlan(self) -> jsii.Number:
        '''The minimum VLAN to use in the range.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#max_vlan DistributedPortGroup#max_vlan}
        '''
        result = self._values.get("max_vlan")
        assert result is not None, "Required property 'max_vlan' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def min_vlan(self) -> jsii.Number:
        '''The minimum VLAN to use in the range.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_port_group#min_vlan DistributedPortGroup#min_vlan}
        '''
        result = self._values.get("min_vlan")
        assert result is not None, "Required property 'min_vlan' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DistributedPortGroupVlanRange(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DistributedPortGroupVlanRangeList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.distributedPortGroup.DistributedPortGroupVlanRangeList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__db2d10c70a44ff3554d8acc924c0e23529f8f57dd4a78e703106b1d925254d68)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "DistributedPortGroupVlanRangeOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58eb5a34127ddb1d0fe4512c7f2101bb175b5e1d99c4b036607d114a9485cfd0)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DistributedPortGroupVlanRangeOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73296e5bf71ca6c53395fc05b408f7beb33f6b3de8b54bd80b98f3771ed97dbd)
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
            type_hints = typing.get_type_hints(_typecheckingstub__aaad4eda1694436203cf52876ff2f76bb9fde6bd8b0103cf2627ea0f8d62df5e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__05c0e15920b71ec98358bffb1109789d586d28ba8d9cc8569d65c638a32bf1c3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DistributedPortGroupVlanRange]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DistributedPortGroupVlanRange]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DistributedPortGroupVlanRange]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4fa9c47f40317d419e6b9b364f3617d3dd6db06e5cee61150bdeba54ac6716d2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DistributedPortGroupVlanRangeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.distributedPortGroup.DistributedPortGroupVlanRangeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__70040af7009fe39bc84ca22cd88355d2adeae0a9dac0754ea4155b579e865993)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="maxVlanInput")
    def max_vlan_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxVlanInput"))

    @builtins.property
    @jsii.member(jsii_name="minVlanInput")
    def min_vlan_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minVlanInput"))

    @builtins.property
    @jsii.member(jsii_name="maxVlan")
    def max_vlan(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxVlan"))

    @max_vlan.setter
    def max_vlan(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__419eb7413f36e85fe4f6f6cda9f8c68195fc453a81a08546ffa29f3edf9328d1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxVlan", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minVlan")
    def min_vlan(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minVlan"))

    @min_vlan.setter
    def min_vlan(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d23dfeab0710b6aad2ba9bc76f26d52b7c5552072f1f75bd517cbbed158c2765)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minVlan", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DistributedPortGroupVlanRange]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DistributedPortGroupVlanRange]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DistributedPortGroupVlanRange]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6fd299f28ed200fed751cc93d8f3237ff8acbce261b9ae7843368218cddce713)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DistributedPortGroup",
    "DistributedPortGroupConfig",
    "DistributedPortGroupVlanRange",
    "DistributedPortGroupVlanRangeList",
    "DistributedPortGroupVlanRangeOutputReference",
]

publication.publish()

def _typecheckingstub__0c580137018193f484820e913d3012240d00760ac5e2338023a0979e2c65ad9c(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    distributed_virtual_switch_uuid: builtins.str,
    name: builtins.str,
    active_uplinks: typing.Optional[typing.Sequence[builtins.str]] = None,
    allow_forged_transmits: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_mac_changes: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_promiscuous: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    auto_expand: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    block_all_ports: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    block_override_allowed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    check_beacon: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    custom_attributes: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    description: typing.Optional[builtins.str] = None,
    directpath_gen2_allowed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    egress_shaping_average_bandwidth: typing.Optional[jsii.Number] = None,
    egress_shaping_burst_size: typing.Optional[jsii.Number] = None,
    egress_shaping_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    egress_shaping_peak_bandwidth: typing.Optional[jsii.Number] = None,
    failback: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    ingress_shaping_average_bandwidth: typing.Optional[jsii.Number] = None,
    ingress_shaping_burst_size: typing.Optional[jsii.Number] = None,
    ingress_shaping_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ingress_shaping_peak_bandwidth: typing.Optional[jsii.Number] = None,
    lacp_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    lacp_mode: typing.Optional[builtins.str] = None,
    live_port_moving_allowed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    netflow_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    netflow_override_allowed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    network_resource_pool_key: typing.Optional[builtins.str] = None,
    network_resource_pool_override_allowed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    notify_switches: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    number_of_ports: typing.Optional[jsii.Number] = None,
    port_config_reset_at_disconnect: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    port_name_format: typing.Optional[builtins.str] = None,
    port_private_secondary_vlan_id: typing.Optional[jsii.Number] = None,
    security_policy_override_allowed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    shaping_override_allowed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    standby_uplinks: typing.Optional[typing.Sequence[builtins.str]] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    teaming_policy: typing.Optional[builtins.str] = None,
    traffic_filter_override_allowed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tx_uplink: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    type: typing.Optional[builtins.str] = None,
    uplink_teaming_override_allowed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    vlan_id: typing.Optional[jsii.Number] = None,
    vlan_override_allowed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    vlan_range: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DistributedPortGroupVlanRange, typing.Dict[builtins.str, typing.Any]]]]] = None,
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

def _typecheckingstub__37a3950d06fd5b50ebd14099511f4bdf51c7b617e1306554fde552b7b0d45a2a(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91c1a5de8427e7eebea35113cc7bd5f5b75e00640f319d09c68c99f698c624d3(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DistributedPortGroupVlanRange, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ffa2b115d2ff765a514b7d9f1f7364aaf340f51d607000486b7c987cf200395(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97443f33742be3d07a79349661ec9f05efae4d1a151a0ccbb355975b435986c4(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17049d2ffdabc75d9a85e65419c2cf9fa28cfec2181a6892be43ec0e6fdaacc4(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1999e1074602c2fd9118540fedfc9120fe289f3529570657fb7431f49f1c2e92(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b694b193695f90a198dfb16f4dbcf91d9407efc979d4990dc5b4fac3ec711cdb(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12d52a19d860c41af15a2921a0ed93f1492818f04e0af690ef6fe2c364f0f4ed(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a287cc621cbbf79ce4196cdfa25b5db9a69940c8ab4a1669605aeb02f0041f8(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24960a5719cab0a933e12cb9c83768de18dfa4f3eda2be72f18db50470967b80(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01ce9cc16610b05ce4c7f65b1cab669791dd51832893aaf668a2c13f91557c4a(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__144466094e093ea3a63f45a47850eb13687972907513c3a25cfbaee906fa92b6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5239bbfd60844d7f861ad46c9ae83fbb79611cbfe91eac4eb67bd5aa14902e90(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5df734eed73768c997b81727ee35d598cf754987a8e32f772a23d7f80179d615(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82186264e3410f6594b9fab0af3b3385b5a8ca43b455e062f52cbce674bd95fe(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7dc98f998cf52dde44a7baaf6cefc1bebc64e2d26a1fdf15b0b4fe0c2a643c6a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80dfe53e6464aa1fec60c9c01692f3ca2fb64ca400fa97507543ecd38d4e520f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2eb24d812baf07fe4615d253f13299fd07f6dff8b0a6416059e84d2a96f74afc(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c94dce3276e2015456231da03f5fca37e0a9a3b4fdb676d1b753c8bf4b837fe(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a4b2b732d7c75deaf6d0963dc058b0e797584cf93d4fb4f616c15669b31b988(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f76ed0cbadbf75afec646b9e98685adfe090aac22f574265313ab845954e7bbf(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1949d95957b1fed02fee5d2283a623d7c53adb741ad8c57dee759f2178120f58(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dca493db4ddff2f106f2f80a1c08da2cde9358bc2ffbfd1605339d3ad76a44ba(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e4f20a49f160f67696c8f9894f344233da1272a49a614be634fb474947d628a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__240fccc0c6cef54b59a7cc0341482aa05a6d1f81ecab13a294deb362f188c811(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8a8bb1ea5188b7d0decaf532e9b03641c72975987c7da02c991cd60a19b6903(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__727d0776c254c37fd28b563e10053d9a276b798de996506afc8b651efc2fbdf4(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05ae6ff1536890be7f023d9e0457c188223cbaf7b92f9b01eda8a99bf35a6c9b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f297f20812fff7ba12f60cccd9be22b214c28f9a87e82c54117ad8473d5db56(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5124ec93eae1187113e46502f18f33f4461449db0a97f8704030174f919d8a30(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc08b4b23587d721140fdcad30280071154a0ae9595e0db05a5dace3574225b4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b117af1a0de08df5cb4bd753a2ec513813a52b334271824511d77f589c1a8c18(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4775f25ba0ffbfbe3e9a24214ed7bbb1313522bc1800093b3f9a51baaa82c5c9(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6547c457bcb9374652aa06537fad0d1471b7ca2d9af510d389d07470334a712(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5a3bf495808f75fac25224ae82a4be2a2c49c7fed2d378d859d1f779052825e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__789747700f548cf01a8ccbae9d8641ec8d017c8fcbda9b975048fa47af49dc26(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af785231cc5ede90e096aa34dfe4e32b146d1a5d2417ef869fe2f3fe00700fbe(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28a8c8cbbb8f0c2d9e6940f5920d23b129109ea3841d1781101d3f73ff64fd6f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7050e1f08e733b9c9aea91a2572f1cbfe466e26aa3e87a9cd76ecd2c25c1ddb(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6669d09cd1a9d0a68e8777b5a9c9138fae07cda6748260c4bb2c64d5d7b73e83(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04e165e43caddddf49a67497fd431af40f2d7409cbbc13a1d6826c58800a7f2a(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23ab96fa182173fad5643739962f3ec543bad52e8a1c398ac2ef8e53fa64d348(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ce3a5fa0a01e819106adaed2ff7fa2bbe040bba5219483947bc9e6581141c7e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c90895be218d24a2cb7d0b8e77d4884f0d8756531f669a6805bf187d221b7d4(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__267e9f1c744878a18b7a9149e2e47e5f119407b84fe6d84abb3333144003f8c2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__679fd9939999150f93d8fb2ed47cfa79af5945c7b8955b760bfd55221314b7da(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63afc30fb949fc17829334cd57c40640ca9afdcf5129af45d245a7c098754656(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86346ad9cd9c55dc98949307324ef4f14ea368392ea4676a0ecdd94c2d0df170(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94b336c963c7511a380896c9f402d9934ac93e17bfb20a0df10b758361bf699a(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    distributed_virtual_switch_uuid: builtins.str,
    name: builtins.str,
    active_uplinks: typing.Optional[typing.Sequence[builtins.str]] = None,
    allow_forged_transmits: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_mac_changes: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_promiscuous: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    auto_expand: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    block_all_ports: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    block_override_allowed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    check_beacon: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    custom_attributes: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    description: typing.Optional[builtins.str] = None,
    directpath_gen2_allowed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    egress_shaping_average_bandwidth: typing.Optional[jsii.Number] = None,
    egress_shaping_burst_size: typing.Optional[jsii.Number] = None,
    egress_shaping_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    egress_shaping_peak_bandwidth: typing.Optional[jsii.Number] = None,
    failback: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    ingress_shaping_average_bandwidth: typing.Optional[jsii.Number] = None,
    ingress_shaping_burst_size: typing.Optional[jsii.Number] = None,
    ingress_shaping_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ingress_shaping_peak_bandwidth: typing.Optional[jsii.Number] = None,
    lacp_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    lacp_mode: typing.Optional[builtins.str] = None,
    live_port_moving_allowed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    netflow_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    netflow_override_allowed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    network_resource_pool_key: typing.Optional[builtins.str] = None,
    network_resource_pool_override_allowed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    notify_switches: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    number_of_ports: typing.Optional[jsii.Number] = None,
    port_config_reset_at_disconnect: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    port_name_format: typing.Optional[builtins.str] = None,
    port_private_secondary_vlan_id: typing.Optional[jsii.Number] = None,
    security_policy_override_allowed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    shaping_override_allowed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    standby_uplinks: typing.Optional[typing.Sequence[builtins.str]] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    teaming_policy: typing.Optional[builtins.str] = None,
    traffic_filter_override_allowed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tx_uplink: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    type: typing.Optional[builtins.str] = None,
    uplink_teaming_override_allowed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    vlan_id: typing.Optional[jsii.Number] = None,
    vlan_override_allowed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    vlan_range: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DistributedPortGroupVlanRange, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52bd7440208683f7e74f25e7931a6a49182a6c62b38b85bb883413f10f2bcb7f(
    *,
    max_vlan: jsii.Number,
    min_vlan: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db2d10c70a44ff3554d8acc924c0e23529f8f57dd4a78e703106b1d925254d68(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58eb5a34127ddb1d0fe4512c7f2101bb175b5e1d99c4b036607d114a9485cfd0(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73296e5bf71ca6c53395fc05b408f7beb33f6b3de8b54bd80b98f3771ed97dbd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aaad4eda1694436203cf52876ff2f76bb9fde6bd8b0103cf2627ea0f8d62df5e(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05c0e15920b71ec98358bffb1109789d586d28ba8d9cc8569d65c638a32bf1c3(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4fa9c47f40317d419e6b9b364f3617d3dd6db06e5cee61150bdeba54ac6716d2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DistributedPortGroupVlanRange]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70040af7009fe39bc84ca22cd88355d2adeae0a9dac0754ea4155b579e865993(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__419eb7413f36e85fe4f6f6cda9f8c68195fc453a81a08546ffa29f3edf9328d1(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d23dfeab0710b6aad2ba9bc76f26d52b7c5552072f1f75bd517cbbed158c2765(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6fd299f28ed200fed751cc93d8f3237ff8acbce261b9ae7843368218cddce713(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DistributedPortGroupVlanRange]],
) -> None:
    """Type checking stubs"""
    pass
