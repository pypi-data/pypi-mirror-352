r'''
# `vsphere_distributed_virtual_switch`

Refer to the Terraform Registry for docs: [`vsphere_distributed_virtual_switch`](https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch).
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


class DistributedVirtualSwitch(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.distributedVirtualSwitch.DistributedVirtualSwitch",
):
    '''Represents a {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch vsphere_distributed_virtual_switch}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        datacenter_id: builtins.str,
        name: builtins.str,
        active_uplinks: typing.Optional[typing.Sequence[builtins.str]] = None,
        allow_forged_transmits: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_mac_changes: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_promiscuous: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        backupnfc_maximum_mbit: typing.Optional[jsii.Number] = None,
        backupnfc_reservation_mbit: typing.Optional[jsii.Number] = None,
        backupnfc_share_count: typing.Optional[jsii.Number] = None,
        backupnfc_share_level: typing.Optional[builtins.str] = None,
        block_all_ports: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        check_beacon: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        contact_detail: typing.Optional[builtins.str] = None,
        contact_name: typing.Optional[builtins.str] = None,
        custom_attributes: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        directpath_gen2_allowed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        egress_shaping_average_bandwidth: typing.Optional[jsii.Number] = None,
        egress_shaping_burst_size: typing.Optional[jsii.Number] = None,
        egress_shaping_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        egress_shaping_peak_bandwidth: typing.Optional[jsii.Number] = None,
        failback: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        faulttolerance_maximum_mbit: typing.Optional[jsii.Number] = None,
        faulttolerance_reservation_mbit: typing.Optional[jsii.Number] = None,
        faulttolerance_share_count: typing.Optional[jsii.Number] = None,
        faulttolerance_share_level: typing.Optional[builtins.str] = None,
        folder: typing.Optional[builtins.str] = None,
        hbr_maximum_mbit: typing.Optional[jsii.Number] = None,
        hbr_reservation_mbit: typing.Optional[jsii.Number] = None,
        hbr_share_count: typing.Optional[jsii.Number] = None,
        hbr_share_level: typing.Optional[builtins.str] = None,
        host: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DistributedVirtualSwitchHost", typing.Dict[builtins.str, typing.Any]]]]] = None,
        id: typing.Optional[builtins.str] = None,
        ignore_other_pvlan_mappings: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ingress_shaping_average_bandwidth: typing.Optional[jsii.Number] = None,
        ingress_shaping_burst_size: typing.Optional[jsii.Number] = None,
        ingress_shaping_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ingress_shaping_peak_bandwidth: typing.Optional[jsii.Number] = None,
        ipv4_address: typing.Optional[builtins.str] = None,
        iscsi_maximum_mbit: typing.Optional[jsii.Number] = None,
        iscsi_reservation_mbit: typing.Optional[jsii.Number] = None,
        iscsi_share_count: typing.Optional[jsii.Number] = None,
        iscsi_share_level: typing.Optional[builtins.str] = None,
        lacp_api_version: typing.Optional[builtins.str] = None,
        lacp_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        lacp_mode: typing.Optional[builtins.str] = None,
        link_discovery_operation: typing.Optional[builtins.str] = None,
        link_discovery_protocol: typing.Optional[builtins.str] = None,
        management_maximum_mbit: typing.Optional[jsii.Number] = None,
        management_reservation_mbit: typing.Optional[jsii.Number] = None,
        management_share_count: typing.Optional[jsii.Number] = None,
        management_share_level: typing.Optional[builtins.str] = None,
        max_mtu: typing.Optional[jsii.Number] = None,
        multicast_filtering_mode: typing.Optional[builtins.str] = None,
        netflow_active_flow_timeout: typing.Optional[jsii.Number] = None,
        netflow_collector_ip_address: typing.Optional[builtins.str] = None,
        netflow_collector_port: typing.Optional[jsii.Number] = None,
        netflow_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        netflow_idle_flow_timeout: typing.Optional[jsii.Number] = None,
        netflow_internal_flows_only: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        netflow_observation_domain_id: typing.Optional[jsii.Number] = None,
        netflow_sampling_rate: typing.Optional[jsii.Number] = None,
        network_resource_control_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        network_resource_control_version: typing.Optional[builtins.str] = None,
        nfs_maximum_mbit: typing.Optional[jsii.Number] = None,
        nfs_reservation_mbit: typing.Optional[jsii.Number] = None,
        nfs_share_count: typing.Optional[jsii.Number] = None,
        nfs_share_level: typing.Optional[builtins.str] = None,
        notify_switches: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        port_private_secondary_vlan_id: typing.Optional[jsii.Number] = None,
        pvlan_mapping: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DistributedVirtualSwitchPvlanMapping", typing.Dict[builtins.str, typing.Any]]]]] = None,
        standby_uplinks: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        teaming_policy: typing.Optional[builtins.str] = None,
        tx_uplink: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        uplinks: typing.Optional[typing.Sequence[builtins.str]] = None,
        vdp_maximum_mbit: typing.Optional[jsii.Number] = None,
        vdp_reservation_mbit: typing.Optional[jsii.Number] = None,
        vdp_share_count: typing.Optional[jsii.Number] = None,
        vdp_share_level: typing.Optional[builtins.str] = None,
        version: typing.Optional[builtins.str] = None,
        virtualmachine_maximum_mbit: typing.Optional[jsii.Number] = None,
        virtualmachine_reservation_mbit: typing.Optional[jsii.Number] = None,
        virtualmachine_share_count: typing.Optional[jsii.Number] = None,
        virtualmachine_share_level: typing.Optional[builtins.str] = None,
        vlan_id: typing.Optional[jsii.Number] = None,
        vlan_range: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DistributedVirtualSwitchVlanRange", typing.Dict[builtins.str, typing.Any]]]]] = None,
        vmotion_maximum_mbit: typing.Optional[jsii.Number] = None,
        vmotion_reservation_mbit: typing.Optional[jsii.Number] = None,
        vmotion_share_count: typing.Optional[jsii.Number] = None,
        vmotion_share_level: typing.Optional[builtins.str] = None,
        vsan_maximum_mbit: typing.Optional[jsii.Number] = None,
        vsan_reservation_mbit: typing.Optional[jsii.Number] = None,
        vsan_share_count: typing.Optional[jsii.Number] = None,
        vsan_share_level: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch vsphere_distributed_virtual_switch} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param datacenter_id: The ID of the datacenter to create this virtual switch in. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#datacenter_id DistributedVirtualSwitch#datacenter_id}
        :param name: The name for the DVS. Must be unique in the folder that it is being created in. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#name DistributedVirtualSwitch#name}
        :param active_uplinks: List of active uplinks used for load balancing, matching the names of the uplinks assigned in the DVS. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#active_uplinks DistributedVirtualSwitch#active_uplinks}
        :param allow_forged_transmits: Controls whether or not the virtual network adapter is allowed to send network traffic with a different MAC address than that of its own. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#allow_forged_transmits DistributedVirtualSwitch#allow_forged_transmits}
        :param allow_mac_changes: Controls whether or not the Media Access Control (MAC) address can be changed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#allow_mac_changes DistributedVirtualSwitch#allow_mac_changes}
        :param allow_promiscuous: Enable promiscuous mode on the network. This flag indicates whether or not all traffic is seen on a given port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#allow_promiscuous DistributedVirtualSwitch#allow_promiscuous}
        :param backupnfc_maximum_mbit: The maximum allowed usage for the backupNfc traffic class, in Mbits/sec. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#backupnfc_maximum_mbit DistributedVirtualSwitch#backupnfc_maximum_mbit}
        :param backupnfc_reservation_mbit: The amount of guaranteed bandwidth for the backupNfc traffic class, in Mbits/sec. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#backupnfc_reservation_mbit DistributedVirtualSwitch#backupnfc_reservation_mbit}
        :param backupnfc_share_count: The amount of shares to allocate to the backupNfc traffic class for a custom share level. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#backupnfc_share_count DistributedVirtualSwitch#backupnfc_share_count}
        :param backupnfc_share_level: The allocation level for the backupNfc traffic class. Can be one of high, low, normal, or custom. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#backupnfc_share_level DistributedVirtualSwitch#backupnfc_share_level}
        :param block_all_ports: Indicates whether to block all ports by default. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#block_all_ports DistributedVirtualSwitch#block_all_ports}
        :param check_beacon: Enable beacon probing on the ports this policy applies to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#check_beacon DistributedVirtualSwitch#check_beacon}
        :param contact_detail: The contact detail for this DVS. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#contact_detail DistributedVirtualSwitch#contact_detail}
        :param contact_name: The contact name for this DVS. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#contact_name DistributedVirtualSwitch#contact_name}
        :param custom_attributes: A list of custom attributes to set on this resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#custom_attributes DistributedVirtualSwitch#custom_attributes}
        :param description: The description of the DVS. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#description DistributedVirtualSwitch#description}
        :param directpath_gen2_allowed: Allow VMDirectPath Gen2 on the ports this policy applies to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#directpath_gen2_allowed DistributedVirtualSwitch#directpath_gen2_allowed}
        :param egress_shaping_average_bandwidth: The average egress bandwidth in bits per second if egress shaping is enabled on the port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#egress_shaping_average_bandwidth DistributedVirtualSwitch#egress_shaping_average_bandwidth}
        :param egress_shaping_burst_size: The maximum egress burst size allowed in bytes if egress shaping is enabled on the port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#egress_shaping_burst_size DistributedVirtualSwitch#egress_shaping_burst_size}
        :param egress_shaping_enabled: True if the traffic shaper is enabled for egress traffic on the port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#egress_shaping_enabled DistributedVirtualSwitch#egress_shaping_enabled}
        :param egress_shaping_peak_bandwidth: The peak egress bandwidth during bursts in bits per second if egress traffic shaping is enabled on the port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#egress_shaping_peak_bandwidth DistributedVirtualSwitch#egress_shaping_peak_bandwidth}
        :param failback: If true, the teaming policy will re-activate failed interfaces higher in precedence when they come back up. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#failback DistributedVirtualSwitch#failback}
        :param faulttolerance_maximum_mbit: The maximum allowed usage for the faultTolerance traffic class, in Mbits/sec. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#faulttolerance_maximum_mbit DistributedVirtualSwitch#faulttolerance_maximum_mbit}
        :param faulttolerance_reservation_mbit: The amount of guaranteed bandwidth for the faultTolerance traffic class, in Mbits/sec. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#faulttolerance_reservation_mbit DistributedVirtualSwitch#faulttolerance_reservation_mbit}
        :param faulttolerance_share_count: The amount of shares to allocate to the faultTolerance traffic class for a custom share level. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#faulttolerance_share_count DistributedVirtualSwitch#faulttolerance_share_count}
        :param faulttolerance_share_level: The allocation level for the faultTolerance traffic class. Can be one of high, low, normal, or custom. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#faulttolerance_share_level DistributedVirtualSwitch#faulttolerance_share_level}
        :param folder: The folder to create this virtual switch in, relative to the datacenter. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#folder DistributedVirtualSwitch#folder}
        :param hbr_maximum_mbit: The maximum allowed usage for the hbr traffic class, in Mbits/sec. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#hbr_maximum_mbit DistributedVirtualSwitch#hbr_maximum_mbit}
        :param hbr_reservation_mbit: The amount of guaranteed bandwidth for the hbr traffic class, in Mbits/sec. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#hbr_reservation_mbit DistributedVirtualSwitch#hbr_reservation_mbit}
        :param hbr_share_count: The amount of shares to allocate to the hbr traffic class for a custom share level. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#hbr_share_count DistributedVirtualSwitch#hbr_share_count}
        :param hbr_share_level: The allocation level for the hbr traffic class. Can be one of high, low, normal, or custom. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#hbr_share_level DistributedVirtualSwitch#hbr_share_level}
        :param host: host block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#host DistributedVirtualSwitch#host}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#id DistributedVirtualSwitch#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param ignore_other_pvlan_mappings: Whether to ignore existing PVLAN mappings not managed by this resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#ignore_other_pvlan_mappings DistributedVirtualSwitch#ignore_other_pvlan_mappings}
        :param ingress_shaping_average_bandwidth: The average ingress bandwidth in bits per second if ingress shaping is enabled on the port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#ingress_shaping_average_bandwidth DistributedVirtualSwitch#ingress_shaping_average_bandwidth}
        :param ingress_shaping_burst_size: The maximum ingress burst size allowed in bytes if ingress shaping is enabled on the port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#ingress_shaping_burst_size DistributedVirtualSwitch#ingress_shaping_burst_size}
        :param ingress_shaping_enabled: True if the traffic shaper is enabled for ingress traffic on the port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#ingress_shaping_enabled DistributedVirtualSwitch#ingress_shaping_enabled}
        :param ingress_shaping_peak_bandwidth: The peak ingress bandwidth during bursts in bits per second if ingress traffic shaping is enabled on the port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#ingress_shaping_peak_bandwidth DistributedVirtualSwitch#ingress_shaping_peak_bandwidth}
        :param ipv4_address: The IPv4 address of the switch. This can be used to see the DVS as a unique device with NetFlow. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#ipv4_address DistributedVirtualSwitch#ipv4_address}
        :param iscsi_maximum_mbit: The maximum allowed usage for the iSCSI traffic class, in Mbits/sec. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#iscsi_maximum_mbit DistributedVirtualSwitch#iscsi_maximum_mbit}
        :param iscsi_reservation_mbit: The amount of guaranteed bandwidth for the iSCSI traffic class, in Mbits/sec. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#iscsi_reservation_mbit DistributedVirtualSwitch#iscsi_reservation_mbit}
        :param iscsi_share_count: The amount of shares to allocate to the iSCSI traffic class for a custom share level. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#iscsi_share_count DistributedVirtualSwitch#iscsi_share_count}
        :param iscsi_share_level: The allocation level for the iSCSI traffic class. Can be one of high, low, normal, or custom. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#iscsi_share_level DistributedVirtualSwitch#iscsi_share_level}
        :param lacp_api_version: The Link Aggregation Control Protocol group version in the switch. Can be one of singleLag or multipleLag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#lacp_api_version DistributedVirtualSwitch#lacp_api_version}
        :param lacp_enabled: Whether or not to enable LACP on all uplink ports. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#lacp_enabled DistributedVirtualSwitch#lacp_enabled}
        :param lacp_mode: The uplink LACP mode to use. Can be one of active or passive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#lacp_mode DistributedVirtualSwitch#lacp_mode}
        :param link_discovery_operation: Whether to advertise or listen for link discovery. Valid values are advertise, both, listen, and none. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#link_discovery_operation DistributedVirtualSwitch#link_discovery_operation}
        :param link_discovery_protocol: The discovery protocol type. Valid values are cdp and lldp. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#link_discovery_protocol DistributedVirtualSwitch#link_discovery_protocol}
        :param management_maximum_mbit: The maximum allowed usage for the management traffic class, in Mbits/sec. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#management_maximum_mbit DistributedVirtualSwitch#management_maximum_mbit}
        :param management_reservation_mbit: The amount of guaranteed bandwidth for the management traffic class, in Mbits/sec. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#management_reservation_mbit DistributedVirtualSwitch#management_reservation_mbit}
        :param management_share_count: The amount of shares to allocate to the management traffic class for a custom share level. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#management_share_count DistributedVirtualSwitch#management_share_count}
        :param management_share_level: The allocation level for the management traffic class. Can be one of high, low, normal, or custom. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#management_share_level DistributedVirtualSwitch#management_share_level}
        :param max_mtu: The maximum MTU on the switch. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#max_mtu DistributedVirtualSwitch#max_mtu}
        :param multicast_filtering_mode: The multicast filtering mode on the switch. Can be one of legacyFiltering, or snooping. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#multicast_filtering_mode DistributedVirtualSwitch#multicast_filtering_mode}
        :param netflow_active_flow_timeout: The number of seconds after which active flows are forced to be exported to the collector. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#netflow_active_flow_timeout DistributedVirtualSwitch#netflow_active_flow_timeout}
        :param netflow_collector_ip_address: IP address for the netflow collector, using IPv4 or IPv6. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#netflow_collector_ip_address DistributedVirtualSwitch#netflow_collector_ip_address}
        :param netflow_collector_port: The port for the netflow collector. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#netflow_collector_port DistributedVirtualSwitch#netflow_collector_port}
        :param netflow_enabled: Indicates whether to enable netflow on all ports. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#netflow_enabled DistributedVirtualSwitch#netflow_enabled}
        :param netflow_idle_flow_timeout: The number of seconds after which idle flows are forced to be exported to the collector. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#netflow_idle_flow_timeout DistributedVirtualSwitch#netflow_idle_flow_timeout}
        :param netflow_internal_flows_only: Whether to limit analysis to traffic that has both source and destination served by the same host. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#netflow_internal_flows_only DistributedVirtualSwitch#netflow_internal_flows_only}
        :param netflow_observation_domain_id: The observation Domain ID for the netflow collector. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#netflow_observation_domain_id DistributedVirtualSwitch#netflow_observation_domain_id}
        :param netflow_sampling_rate: The ratio of total number of packets to the number of packets analyzed. Set to 0 to disable sampling, meaning that all packets are analyzed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#netflow_sampling_rate DistributedVirtualSwitch#netflow_sampling_rate}
        :param network_resource_control_enabled: Whether or not to enable network resource control, enabling advanced traffic shaping and resource control features. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#network_resource_control_enabled DistributedVirtualSwitch#network_resource_control_enabled}
        :param network_resource_control_version: The network I/O control version to use. Can be one of version2 or version3. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#network_resource_control_version DistributedVirtualSwitch#network_resource_control_version}
        :param nfs_maximum_mbit: The maximum allowed usage for the nfs traffic class, in Mbits/sec. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#nfs_maximum_mbit DistributedVirtualSwitch#nfs_maximum_mbit}
        :param nfs_reservation_mbit: The amount of guaranteed bandwidth for the nfs traffic class, in Mbits/sec. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#nfs_reservation_mbit DistributedVirtualSwitch#nfs_reservation_mbit}
        :param nfs_share_count: The amount of shares to allocate to the nfs traffic class for a custom share level. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#nfs_share_count DistributedVirtualSwitch#nfs_share_count}
        :param nfs_share_level: The allocation level for the nfs traffic class. Can be one of high, low, normal, or custom. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#nfs_share_level DistributedVirtualSwitch#nfs_share_level}
        :param notify_switches: If true, the teaming policy will notify the broadcast network of a NIC failover, triggering cache updates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#notify_switches DistributedVirtualSwitch#notify_switches}
        :param port_private_secondary_vlan_id: The secondary VLAN ID for this port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#port_private_secondary_vlan_id DistributedVirtualSwitch#port_private_secondary_vlan_id}
        :param pvlan_mapping: pvlan_mapping block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#pvlan_mapping DistributedVirtualSwitch#pvlan_mapping}
        :param standby_uplinks: List of standby uplinks used for load balancing, matching the names of the uplinks assigned in the DVS. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#standby_uplinks DistributedVirtualSwitch#standby_uplinks}
        :param tags: A list of tag IDs to apply to this object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#tags DistributedVirtualSwitch#tags}
        :param teaming_policy: The network adapter teaming policy. Can be one of loadbalance_ip, loadbalance_srcmac, loadbalance_srcid, failover_explicit, or loadbalance_loadbased. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#teaming_policy DistributedVirtualSwitch#teaming_policy}
        :param tx_uplink: If true, a copy of packets sent to the switch will always be forwarded to an uplink in addition to the regular packet forwarded done by the switch. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#tx_uplink DistributedVirtualSwitch#tx_uplink}
        :param uplinks: A list of uplink ports. The contents of this list control both the uplink count and names of the uplinks on the DVS across hosts. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#uplinks DistributedVirtualSwitch#uplinks}
        :param vdp_maximum_mbit: The maximum allowed usage for the vdp traffic class, in Mbits/sec. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#vdp_maximum_mbit DistributedVirtualSwitch#vdp_maximum_mbit}
        :param vdp_reservation_mbit: The amount of guaranteed bandwidth for the vdp traffic class, in Mbits/sec. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#vdp_reservation_mbit DistributedVirtualSwitch#vdp_reservation_mbit}
        :param vdp_share_count: The amount of shares to allocate to the vdp traffic class for a custom share level. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#vdp_share_count DistributedVirtualSwitch#vdp_share_count}
        :param vdp_share_level: The allocation level for the vdp traffic class. Can be one of high, low, normal, or custom. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#vdp_share_level DistributedVirtualSwitch#vdp_share_level}
        :param version: The version of this virtual switch. Allowed versions are 8.0.3, 8.0.0, 7.0.3, 7.0.2, 7.0.0, 6.6.0, 6.5.0, 6.0.0, 5.5.0, 5.1.0, and 5.0.0. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#version DistributedVirtualSwitch#version}
        :param virtualmachine_maximum_mbit: The maximum allowed usage for the virtualMachine traffic class, in Mbits/sec. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#virtualmachine_maximum_mbit DistributedVirtualSwitch#virtualmachine_maximum_mbit}
        :param virtualmachine_reservation_mbit: The amount of guaranteed bandwidth for the virtualMachine traffic class, in Mbits/sec. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#virtualmachine_reservation_mbit DistributedVirtualSwitch#virtualmachine_reservation_mbit}
        :param virtualmachine_share_count: The amount of shares to allocate to the virtualMachine traffic class for a custom share level. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#virtualmachine_share_count DistributedVirtualSwitch#virtualmachine_share_count}
        :param virtualmachine_share_level: The allocation level for the virtualMachine traffic class. Can be one of high, low, normal, or custom. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#virtualmachine_share_level DistributedVirtualSwitch#virtualmachine_share_level}
        :param vlan_id: The VLAN ID for single VLAN mode. 0 denotes no VLAN. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#vlan_id DistributedVirtualSwitch#vlan_id}
        :param vlan_range: vlan_range block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#vlan_range DistributedVirtualSwitch#vlan_range}
        :param vmotion_maximum_mbit: The maximum allowed usage for the vmotion traffic class, in Mbits/sec. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#vmotion_maximum_mbit DistributedVirtualSwitch#vmotion_maximum_mbit}
        :param vmotion_reservation_mbit: The amount of guaranteed bandwidth for the vmotion traffic class, in Mbits/sec. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#vmotion_reservation_mbit DistributedVirtualSwitch#vmotion_reservation_mbit}
        :param vmotion_share_count: The amount of shares to allocate to the vmotion traffic class for a custom share level. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#vmotion_share_count DistributedVirtualSwitch#vmotion_share_count}
        :param vmotion_share_level: The allocation level for the vmotion traffic class. Can be one of high, low, normal, or custom. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#vmotion_share_level DistributedVirtualSwitch#vmotion_share_level}
        :param vsan_maximum_mbit: The maximum allowed usage for the vsan traffic class, in Mbits/sec. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#vsan_maximum_mbit DistributedVirtualSwitch#vsan_maximum_mbit}
        :param vsan_reservation_mbit: The amount of guaranteed bandwidth for the vsan traffic class, in Mbits/sec. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#vsan_reservation_mbit DistributedVirtualSwitch#vsan_reservation_mbit}
        :param vsan_share_count: The amount of shares to allocate to the vsan traffic class for a custom share level. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#vsan_share_count DistributedVirtualSwitch#vsan_share_count}
        :param vsan_share_level: The allocation level for the vsan traffic class. Can be one of high, low, normal, or custom. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#vsan_share_level DistributedVirtualSwitch#vsan_share_level}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d3687ae93fa4b327b751d3748a3385265380d804ecaf8116c5d4895cce67f53)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DistributedVirtualSwitchConfig(
            datacenter_id=datacenter_id,
            name=name,
            active_uplinks=active_uplinks,
            allow_forged_transmits=allow_forged_transmits,
            allow_mac_changes=allow_mac_changes,
            allow_promiscuous=allow_promiscuous,
            backupnfc_maximum_mbit=backupnfc_maximum_mbit,
            backupnfc_reservation_mbit=backupnfc_reservation_mbit,
            backupnfc_share_count=backupnfc_share_count,
            backupnfc_share_level=backupnfc_share_level,
            block_all_ports=block_all_ports,
            check_beacon=check_beacon,
            contact_detail=contact_detail,
            contact_name=contact_name,
            custom_attributes=custom_attributes,
            description=description,
            directpath_gen2_allowed=directpath_gen2_allowed,
            egress_shaping_average_bandwidth=egress_shaping_average_bandwidth,
            egress_shaping_burst_size=egress_shaping_burst_size,
            egress_shaping_enabled=egress_shaping_enabled,
            egress_shaping_peak_bandwidth=egress_shaping_peak_bandwidth,
            failback=failback,
            faulttolerance_maximum_mbit=faulttolerance_maximum_mbit,
            faulttolerance_reservation_mbit=faulttolerance_reservation_mbit,
            faulttolerance_share_count=faulttolerance_share_count,
            faulttolerance_share_level=faulttolerance_share_level,
            folder=folder,
            hbr_maximum_mbit=hbr_maximum_mbit,
            hbr_reservation_mbit=hbr_reservation_mbit,
            hbr_share_count=hbr_share_count,
            hbr_share_level=hbr_share_level,
            host=host,
            id=id,
            ignore_other_pvlan_mappings=ignore_other_pvlan_mappings,
            ingress_shaping_average_bandwidth=ingress_shaping_average_bandwidth,
            ingress_shaping_burst_size=ingress_shaping_burst_size,
            ingress_shaping_enabled=ingress_shaping_enabled,
            ingress_shaping_peak_bandwidth=ingress_shaping_peak_bandwidth,
            ipv4_address=ipv4_address,
            iscsi_maximum_mbit=iscsi_maximum_mbit,
            iscsi_reservation_mbit=iscsi_reservation_mbit,
            iscsi_share_count=iscsi_share_count,
            iscsi_share_level=iscsi_share_level,
            lacp_api_version=lacp_api_version,
            lacp_enabled=lacp_enabled,
            lacp_mode=lacp_mode,
            link_discovery_operation=link_discovery_operation,
            link_discovery_protocol=link_discovery_protocol,
            management_maximum_mbit=management_maximum_mbit,
            management_reservation_mbit=management_reservation_mbit,
            management_share_count=management_share_count,
            management_share_level=management_share_level,
            max_mtu=max_mtu,
            multicast_filtering_mode=multicast_filtering_mode,
            netflow_active_flow_timeout=netflow_active_flow_timeout,
            netflow_collector_ip_address=netflow_collector_ip_address,
            netflow_collector_port=netflow_collector_port,
            netflow_enabled=netflow_enabled,
            netflow_idle_flow_timeout=netflow_idle_flow_timeout,
            netflow_internal_flows_only=netflow_internal_flows_only,
            netflow_observation_domain_id=netflow_observation_domain_id,
            netflow_sampling_rate=netflow_sampling_rate,
            network_resource_control_enabled=network_resource_control_enabled,
            network_resource_control_version=network_resource_control_version,
            nfs_maximum_mbit=nfs_maximum_mbit,
            nfs_reservation_mbit=nfs_reservation_mbit,
            nfs_share_count=nfs_share_count,
            nfs_share_level=nfs_share_level,
            notify_switches=notify_switches,
            port_private_secondary_vlan_id=port_private_secondary_vlan_id,
            pvlan_mapping=pvlan_mapping,
            standby_uplinks=standby_uplinks,
            tags=tags,
            teaming_policy=teaming_policy,
            tx_uplink=tx_uplink,
            uplinks=uplinks,
            vdp_maximum_mbit=vdp_maximum_mbit,
            vdp_reservation_mbit=vdp_reservation_mbit,
            vdp_share_count=vdp_share_count,
            vdp_share_level=vdp_share_level,
            version=version,
            virtualmachine_maximum_mbit=virtualmachine_maximum_mbit,
            virtualmachine_reservation_mbit=virtualmachine_reservation_mbit,
            virtualmachine_share_count=virtualmachine_share_count,
            virtualmachine_share_level=virtualmachine_share_level,
            vlan_id=vlan_id,
            vlan_range=vlan_range,
            vmotion_maximum_mbit=vmotion_maximum_mbit,
            vmotion_reservation_mbit=vmotion_reservation_mbit,
            vmotion_share_count=vmotion_share_count,
            vmotion_share_level=vmotion_share_level,
            vsan_maximum_mbit=vsan_maximum_mbit,
            vsan_reservation_mbit=vsan_reservation_mbit,
            vsan_share_count=vsan_share_count,
            vsan_share_level=vsan_share_level,
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
        '''Generates CDKTF code for importing a DistributedVirtualSwitch resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DistributedVirtualSwitch to import.
        :param import_from_id: The id of the existing DistributedVirtualSwitch that should be imported. Refer to the {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DistributedVirtualSwitch to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__acf0e4939da365843266edb7c5f140f619eb17b2d2cb57d1dc7436ea76aa25f3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putHost")
    def put_host(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DistributedVirtualSwitchHost", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06231c32da6a95236e80fae43caebdb912880c03d94d5a2090c603aedbd30456)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putHost", [value]))

    @jsii.member(jsii_name="putPvlanMapping")
    def put_pvlan_mapping(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DistributedVirtualSwitchPvlanMapping", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4301a2a6098e670a5913de0dcb2409f8cf429b0c10eaf0c2a12020425308b10)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putPvlanMapping", [value]))

    @jsii.member(jsii_name="putVlanRange")
    def put_vlan_range(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DistributedVirtualSwitchVlanRange", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0442724c46e2564d8880a14e12e303c7cc18a25114a6055cae762736dcebec1d)
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

    @jsii.member(jsii_name="resetBackupnfcMaximumMbit")
    def reset_backupnfc_maximum_mbit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackupnfcMaximumMbit", []))

    @jsii.member(jsii_name="resetBackupnfcReservationMbit")
    def reset_backupnfc_reservation_mbit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackupnfcReservationMbit", []))

    @jsii.member(jsii_name="resetBackupnfcShareCount")
    def reset_backupnfc_share_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackupnfcShareCount", []))

    @jsii.member(jsii_name="resetBackupnfcShareLevel")
    def reset_backupnfc_share_level(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackupnfcShareLevel", []))

    @jsii.member(jsii_name="resetBlockAllPorts")
    def reset_block_all_ports(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBlockAllPorts", []))

    @jsii.member(jsii_name="resetCheckBeacon")
    def reset_check_beacon(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCheckBeacon", []))

    @jsii.member(jsii_name="resetContactDetail")
    def reset_contact_detail(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContactDetail", []))

    @jsii.member(jsii_name="resetContactName")
    def reset_contact_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContactName", []))

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

    @jsii.member(jsii_name="resetFaulttoleranceMaximumMbit")
    def reset_faulttolerance_maximum_mbit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFaulttoleranceMaximumMbit", []))

    @jsii.member(jsii_name="resetFaulttoleranceReservationMbit")
    def reset_faulttolerance_reservation_mbit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFaulttoleranceReservationMbit", []))

    @jsii.member(jsii_name="resetFaulttoleranceShareCount")
    def reset_faulttolerance_share_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFaulttoleranceShareCount", []))

    @jsii.member(jsii_name="resetFaulttoleranceShareLevel")
    def reset_faulttolerance_share_level(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFaulttoleranceShareLevel", []))

    @jsii.member(jsii_name="resetFolder")
    def reset_folder(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFolder", []))

    @jsii.member(jsii_name="resetHbrMaximumMbit")
    def reset_hbr_maximum_mbit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHbrMaximumMbit", []))

    @jsii.member(jsii_name="resetHbrReservationMbit")
    def reset_hbr_reservation_mbit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHbrReservationMbit", []))

    @jsii.member(jsii_name="resetHbrShareCount")
    def reset_hbr_share_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHbrShareCount", []))

    @jsii.member(jsii_name="resetHbrShareLevel")
    def reset_hbr_share_level(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHbrShareLevel", []))

    @jsii.member(jsii_name="resetHost")
    def reset_host(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHost", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIgnoreOtherPvlanMappings")
    def reset_ignore_other_pvlan_mappings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIgnoreOtherPvlanMappings", []))

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

    @jsii.member(jsii_name="resetIpv4Address")
    def reset_ipv4_address(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpv4Address", []))

    @jsii.member(jsii_name="resetIscsiMaximumMbit")
    def reset_iscsi_maximum_mbit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIscsiMaximumMbit", []))

    @jsii.member(jsii_name="resetIscsiReservationMbit")
    def reset_iscsi_reservation_mbit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIscsiReservationMbit", []))

    @jsii.member(jsii_name="resetIscsiShareCount")
    def reset_iscsi_share_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIscsiShareCount", []))

    @jsii.member(jsii_name="resetIscsiShareLevel")
    def reset_iscsi_share_level(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIscsiShareLevel", []))

    @jsii.member(jsii_name="resetLacpApiVersion")
    def reset_lacp_api_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLacpApiVersion", []))

    @jsii.member(jsii_name="resetLacpEnabled")
    def reset_lacp_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLacpEnabled", []))

    @jsii.member(jsii_name="resetLacpMode")
    def reset_lacp_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLacpMode", []))

    @jsii.member(jsii_name="resetLinkDiscoveryOperation")
    def reset_link_discovery_operation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLinkDiscoveryOperation", []))

    @jsii.member(jsii_name="resetLinkDiscoveryProtocol")
    def reset_link_discovery_protocol(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLinkDiscoveryProtocol", []))

    @jsii.member(jsii_name="resetManagementMaximumMbit")
    def reset_management_maximum_mbit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetManagementMaximumMbit", []))

    @jsii.member(jsii_name="resetManagementReservationMbit")
    def reset_management_reservation_mbit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetManagementReservationMbit", []))

    @jsii.member(jsii_name="resetManagementShareCount")
    def reset_management_share_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetManagementShareCount", []))

    @jsii.member(jsii_name="resetManagementShareLevel")
    def reset_management_share_level(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetManagementShareLevel", []))

    @jsii.member(jsii_name="resetMaxMtu")
    def reset_max_mtu(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxMtu", []))

    @jsii.member(jsii_name="resetMulticastFilteringMode")
    def reset_multicast_filtering_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMulticastFilteringMode", []))

    @jsii.member(jsii_name="resetNetflowActiveFlowTimeout")
    def reset_netflow_active_flow_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetflowActiveFlowTimeout", []))

    @jsii.member(jsii_name="resetNetflowCollectorIpAddress")
    def reset_netflow_collector_ip_address(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetflowCollectorIpAddress", []))

    @jsii.member(jsii_name="resetNetflowCollectorPort")
    def reset_netflow_collector_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetflowCollectorPort", []))

    @jsii.member(jsii_name="resetNetflowEnabled")
    def reset_netflow_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetflowEnabled", []))

    @jsii.member(jsii_name="resetNetflowIdleFlowTimeout")
    def reset_netflow_idle_flow_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetflowIdleFlowTimeout", []))

    @jsii.member(jsii_name="resetNetflowInternalFlowsOnly")
    def reset_netflow_internal_flows_only(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetflowInternalFlowsOnly", []))

    @jsii.member(jsii_name="resetNetflowObservationDomainId")
    def reset_netflow_observation_domain_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetflowObservationDomainId", []))

    @jsii.member(jsii_name="resetNetflowSamplingRate")
    def reset_netflow_sampling_rate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetflowSamplingRate", []))

    @jsii.member(jsii_name="resetNetworkResourceControlEnabled")
    def reset_network_resource_control_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworkResourceControlEnabled", []))

    @jsii.member(jsii_name="resetNetworkResourceControlVersion")
    def reset_network_resource_control_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworkResourceControlVersion", []))

    @jsii.member(jsii_name="resetNfsMaximumMbit")
    def reset_nfs_maximum_mbit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNfsMaximumMbit", []))

    @jsii.member(jsii_name="resetNfsReservationMbit")
    def reset_nfs_reservation_mbit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNfsReservationMbit", []))

    @jsii.member(jsii_name="resetNfsShareCount")
    def reset_nfs_share_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNfsShareCount", []))

    @jsii.member(jsii_name="resetNfsShareLevel")
    def reset_nfs_share_level(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNfsShareLevel", []))

    @jsii.member(jsii_name="resetNotifySwitches")
    def reset_notify_switches(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNotifySwitches", []))

    @jsii.member(jsii_name="resetPortPrivateSecondaryVlanId")
    def reset_port_private_secondary_vlan_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPortPrivateSecondaryVlanId", []))

    @jsii.member(jsii_name="resetPvlanMapping")
    def reset_pvlan_mapping(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPvlanMapping", []))

    @jsii.member(jsii_name="resetStandbyUplinks")
    def reset_standby_uplinks(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStandbyUplinks", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTeamingPolicy")
    def reset_teaming_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTeamingPolicy", []))

    @jsii.member(jsii_name="resetTxUplink")
    def reset_tx_uplink(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTxUplink", []))

    @jsii.member(jsii_name="resetUplinks")
    def reset_uplinks(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUplinks", []))

    @jsii.member(jsii_name="resetVdpMaximumMbit")
    def reset_vdp_maximum_mbit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVdpMaximumMbit", []))

    @jsii.member(jsii_name="resetVdpReservationMbit")
    def reset_vdp_reservation_mbit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVdpReservationMbit", []))

    @jsii.member(jsii_name="resetVdpShareCount")
    def reset_vdp_share_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVdpShareCount", []))

    @jsii.member(jsii_name="resetVdpShareLevel")
    def reset_vdp_share_level(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVdpShareLevel", []))

    @jsii.member(jsii_name="resetVersion")
    def reset_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVersion", []))

    @jsii.member(jsii_name="resetVirtualmachineMaximumMbit")
    def reset_virtualmachine_maximum_mbit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVirtualmachineMaximumMbit", []))

    @jsii.member(jsii_name="resetVirtualmachineReservationMbit")
    def reset_virtualmachine_reservation_mbit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVirtualmachineReservationMbit", []))

    @jsii.member(jsii_name="resetVirtualmachineShareCount")
    def reset_virtualmachine_share_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVirtualmachineShareCount", []))

    @jsii.member(jsii_name="resetVirtualmachineShareLevel")
    def reset_virtualmachine_share_level(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVirtualmachineShareLevel", []))

    @jsii.member(jsii_name="resetVlanId")
    def reset_vlan_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVlanId", []))

    @jsii.member(jsii_name="resetVlanRange")
    def reset_vlan_range(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVlanRange", []))

    @jsii.member(jsii_name="resetVmotionMaximumMbit")
    def reset_vmotion_maximum_mbit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVmotionMaximumMbit", []))

    @jsii.member(jsii_name="resetVmotionReservationMbit")
    def reset_vmotion_reservation_mbit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVmotionReservationMbit", []))

    @jsii.member(jsii_name="resetVmotionShareCount")
    def reset_vmotion_share_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVmotionShareCount", []))

    @jsii.member(jsii_name="resetVmotionShareLevel")
    def reset_vmotion_share_level(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVmotionShareLevel", []))

    @jsii.member(jsii_name="resetVsanMaximumMbit")
    def reset_vsan_maximum_mbit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVsanMaximumMbit", []))

    @jsii.member(jsii_name="resetVsanReservationMbit")
    def reset_vsan_reservation_mbit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVsanReservationMbit", []))

    @jsii.member(jsii_name="resetVsanShareCount")
    def reset_vsan_share_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVsanShareCount", []))

    @jsii.member(jsii_name="resetVsanShareLevel")
    def reset_vsan_share_level(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVsanShareLevel", []))

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
    @jsii.member(jsii_name="host")
    def host(self) -> "DistributedVirtualSwitchHostList":
        return typing.cast("DistributedVirtualSwitchHostList", jsii.get(self, "host"))

    @builtins.property
    @jsii.member(jsii_name="pvlanMapping")
    def pvlan_mapping(self) -> "DistributedVirtualSwitchPvlanMappingList":
        return typing.cast("DistributedVirtualSwitchPvlanMappingList", jsii.get(self, "pvlanMapping"))

    @builtins.property
    @jsii.member(jsii_name="vlanRange")
    def vlan_range(self) -> "DistributedVirtualSwitchVlanRangeList":
        return typing.cast("DistributedVirtualSwitchVlanRangeList", jsii.get(self, "vlanRange"))

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
    @jsii.member(jsii_name="backupnfcMaximumMbitInput")
    def backupnfc_maximum_mbit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "backupnfcMaximumMbitInput"))

    @builtins.property
    @jsii.member(jsii_name="backupnfcReservationMbitInput")
    def backupnfc_reservation_mbit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "backupnfcReservationMbitInput"))

    @builtins.property
    @jsii.member(jsii_name="backupnfcShareCountInput")
    def backupnfc_share_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "backupnfcShareCountInput"))

    @builtins.property
    @jsii.member(jsii_name="backupnfcShareLevelInput")
    def backupnfc_share_level_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "backupnfcShareLevelInput"))

    @builtins.property
    @jsii.member(jsii_name="blockAllPortsInput")
    def block_all_ports_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "blockAllPortsInput"))

    @builtins.property
    @jsii.member(jsii_name="checkBeaconInput")
    def check_beacon_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "checkBeaconInput"))

    @builtins.property
    @jsii.member(jsii_name="contactDetailInput")
    def contact_detail_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "contactDetailInput"))

    @builtins.property
    @jsii.member(jsii_name="contactNameInput")
    def contact_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "contactNameInput"))

    @builtins.property
    @jsii.member(jsii_name="customAttributesInput")
    def custom_attributes_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "customAttributesInput"))

    @builtins.property
    @jsii.member(jsii_name="datacenterIdInput")
    def datacenter_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "datacenterIdInput"))

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
    @jsii.member(jsii_name="faulttoleranceMaximumMbitInput")
    def faulttolerance_maximum_mbit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "faulttoleranceMaximumMbitInput"))

    @builtins.property
    @jsii.member(jsii_name="faulttoleranceReservationMbitInput")
    def faulttolerance_reservation_mbit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "faulttoleranceReservationMbitInput"))

    @builtins.property
    @jsii.member(jsii_name="faulttoleranceShareCountInput")
    def faulttolerance_share_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "faulttoleranceShareCountInput"))

    @builtins.property
    @jsii.member(jsii_name="faulttoleranceShareLevelInput")
    def faulttolerance_share_level_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "faulttoleranceShareLevelInput"))

    @builtins.property
    @jsii.member(jsii_name="folderInput")
    def folder_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "folderInput"))

    @builtins.property
    @jsii.member(jsii_name="hbrMaximumMbitInput")
    def hbr_maximum_mbit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "hbrMaximumMbitInput"))

    @builtins.property
    @jsii.member(jsii_name="hbrReservationMbitInput")
    def hbr_reservation_mbit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "hbrReservationMbitInput"))

    @builtins.property
    @jsii.member(jsii_name="hbrShareCountInput")
    def hbr_share_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "hbrShareCountInput"))

    @builtins.property
    @jsii.member(jsii_name="hbrShareLevelInput")
    def hbr_share_level_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hbrShareLevelInput"))

    @builtins.property
    @jsii.member(jsii_name="hostInput")
    def host_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DistributedVirtualSwitchHost"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DistributedVirtualSwitchHost"]]], jsii.get(self, "hostInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="ignoreOtherPvlanMappingsInput")
    def ignore_other_pvlan_mappings_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "ignoreOtherPvlanMappingsInput"))

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
    @jsii.member(jsii_name="ipv4AddressInput")
    def ipv4_address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ipv4AddressInput"))

    @builtins.property
    @jsii.member(jsii_name="iscsiMaximumMbitInput")
    def iscsi_maximum_mbit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "iscsiMaximumMbitInput"))

    @builtins.property
    @jsii.member(jsii_name="iscsiReservationMbitInput")
    def iscsi_reservation_mbit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "iscsiReservationMbitInput"))

    @builtins.property
    @jsii.member(jsii_name="iscsiShareCountInput")
    def iscsi_share_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "iscsiShareCountInput"))

    @builtins.property
    @jsii.member(jsii_name="iscsiShareLevelInput")
    def iscsi_share_level_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "iscsiShareLevelInput"))

    @builtins.property
    @jsii.member(jsii_name="lacpApiVersionInput")
    def lacp_api_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "lacpApiVersionInput"))

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
    @jsii.member(jsii_name="linkDiscoveryOperationInput")
    def link_discovery_operation_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "linkDiscoveryOperationInput"))

    @builtins.property
    @jsii.member(jsii_name="linkDiscoveryProtocolInput")
    def link_discovery_protocol_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "linkDiscoveryProtocolInput"))

    @builtins.property
    @jsii.member(jsii_name="managementMaximumMbitInput")
    def management_maximum_mbit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "managementMaximumMbitInput"))

    @builtins.property
    @jsii.member(jsii_name="managementReservationMbitInput")
    def management_reservation_mbit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "managementReservationMbitInput"))

    @builtins.property
    @jsii.member(jsii_name="managementShareCountInput")
    def management_share_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "managementShareCountInput"))

    @builtins.property
    @jsii.member(jsii_name="managementShareLevelInput")
    def management_share_level_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "managementShareLevelInput"))

    @builtins.property
    @jsii.member(jsii_name="maxMtuInput")
    def max_mtu_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxMtuInput"))

    @builtins.property
    @jsii.member(jsii_name="multicastFilteringModeInput")
    def multicast_filtering_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "multicastFilteringModeInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="netflowActiveFlowTimeoutInput")
    def netflow_active_flow_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "netflowActiveFlowTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="netflowCollectorIpAddressInput")
    def netflow_collector_ip_address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "netflowCollectorIpAddressInput"))

    @builtins.property
    @jsii.member(jsii_name="netflowCollectorPortInput")
    def netflow_collector_port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "netflowCollectorPortInput"))

    @builtins.property
    @jsii.member(jsii_name="netflowEnabledInput")
    def netflow_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "netflowEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="netflowIdleFlowTimeoutInput")
    def netflow_idle_flow_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "netflowIdleFlowTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="netflowInternalFlowsOnlyInput")
    def netflow_internal_flows_only_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "netflowInternalFlowsOnlyInput"))

    @builtins.property
    @jsii.member(jsii_name="netflowObservationDomainIdInput")
    def netflow_observation_domain_id_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "netflowObservationDomainIdInput"))

    @builtins.property
    @jsii.member(jsii_name="netflowSamplingRateInput")
    def netflow_sampling_rate_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "netflowSamplingRateInput"))

    @builtins.property
    @jsii.member(jsii_name="networkResourceControlEnabledInput")
    def network_resource_control_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "networkResourceControlEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="networkResourceControlVersionInput")
    def network_resource_control_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "networkResourceControlVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="nfsMaximumMbitInput")
    def nfs_maximum_mbit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "nfsMaximumMbitInput"))

    @builtins.property
    @jsii.member(jsii_name="nfsReservationMbitInput")
    def nfs_reservation_mbit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "nfsReservationMbitInput"))

    @builtins.property
    @jsii.member(jsii_name="nfsShareCountInput")
    def nfs_share_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "nfsShareCountInput"))

    @builtins.property
    @jsii.member(jsii_name="nfsShareLevelInput")
    def nfs_share_level_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nfsShareLevelInput"))

    @builtins.property
    @jsii.member(jsii_name="notifySwitchesInput")
    def notify_switches_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "notifySwitchesInput"))

    @builtins.property
    @jsii.member(jsii_name="portPrivateSecondaryVlanIdInput")
    def port_private_secondary_vlan_id_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portPrivateSecondaryVlanIdInput"))

    @builtins.property
    @jsii.member(jsii_name="pvlanMappingInput")
    def pvlan_mapping_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DistributedVirtualSwitchPvlanMapping"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DistributedVirtualSwitchPvlanMapping"]]], jsii.get(self, "pvlanMappingInput"))

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
    @jsii.member(jsii_name="txUplinkInput")
    def tx_uplink_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "txUplinkInput"))

    @builtins.property
    @jsii.member(jsii_name="uplinksInput")
    def uplinks_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "uplinksInput"))

    @builtins.property
    @jsii.member(jsii_name="vdpMaximumMbitInput")
    def vdp_maximum_mbit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "vdpMaximumMbitInput"))

    @builtins.property
    @jsii.member(jsii_name="vdpReservationMbitInput")
    def vdp_reservation_mbit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "vdpReservationMbitInput"))

    @builtins.property
    @jsii.member(jsii_name="vdpShareCountInput")
    def vdp_share_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "vdpShareCountInput"))

    @builtins.property
    @jsii.member(jsii_name="vdpShareLevelInput")
    def vdp_share_level_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vdpShareLevelInput"))

    @builtins.property
    @jsii.member(jsii_name="versionInput")
    def version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "versionInput"))

    @builtins.property
    @jsii.member(jsii_name="virtualmachineMaximumMbitInput")
    def virtualmachine_maximum_mbit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "virtualmachineMaximumMbitInput"))

    @builtins.property
    @jsii.member(jsii_name="virtualmachineReservationMbitInput")
    def virtualmachine_reservation_mbit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "virtualmachineReservationMbitInput"))

    @builtins.property
    @jsii.member(jsii_name="virtualmachineShareCountInput")
    def virtualmachine_share_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "virtualmachineShareCountInput"))

    @builtins.property
    @jsii.member(jsii_name="virtualmachineShareLevelInput")
    def virtualmachine_share_level_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "virtualmachineShareLevelInput"))

    @builtins.property
    @jsii.member(jsii_name="vlanIdInput")
    def vlan_id_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "vlanIdInput"))

    @builtins.property
    @jsii.member(jsii_name="vlanRangeInput")
    def vlan_range_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DistributedVirtualSwitchVlanRange"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DistributedVirtualSwitchVlanRange"]]], jsii.get(self, "vlanRangeInput"))

    @builtins.property
    @jsii.member(jsii_name="vmotionMaximumMbitInput")
    def vmotion_maximum_mbit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "vmotionMaximumMbitInput"))

    @builtins.property
    @jsii.member(jsii_name="vmotionReservationMbitInput")
    def vmotion_reservation_mbit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "vmotionReservationMbitInput"))

    @builtins.property
    @jsii.member(jsii_name="vmotionShareCountInput")
    def vmotion_share_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "vmotionShareCountInput"))

    @builtins.property
    @jsii.member(jsii_name="vmotionShareLevelInput")
    def vmotion_share_level_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vmotionShareLevelInput"))

    @builtins.property
    @jsii.member(jsii_name="vsanMaximumMbitInput")
    def vsan_maximum_mbit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "vsanMaximumMbitInput"))

    @builtins.property
    @jsii.member(jsii_name="vsanReservationMbitInput")
    def vsan_reservation_mbit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "vsanReservationMbitInput"))

    @builtins.property
    @jsii.member(jsii_name="vsanShareCountInput")
    def vsan_share_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "vsanShareCountInput"))

    @builtins.property
    @jsii.member(jsii_name="vsanShareLevelInput")
    def vsan_share_level_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vsanShareLevelInput"))

    @builtins.property
    @jsii.member(jsii_name="activeUplinks")
    def active_uplinks(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "activeUplinks"))

    @active_uplinks.setter
    def active_uplinks(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a11636edf7599cd231cfae9eabc7a5ad724a2ee3b8df5b72944066c5b027ec0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a77d17fea7873f83c93e2ee4a9f097dd1b0ef0f318ee95f0216c2a08b62dd702)
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
            type_hints = typing.get_type_hints(_typecheckingstub__62cff42b489d3b659fbfe250c68deeda5209269d0a60898698d99235e83132b0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__19ec6bc7dfad7447c16a5f5d4bf10e58a80b01313d8319f9a1f16854492f17ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowPromiscuous", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="backupnfcMaximumMbit")
    def backupnfc_maximum_mbit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "backupnfcMaximumMbit"))

    @backupnfc_maximum_mbit.setter
    def backupnfc_maximum_mbit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3de15ae2deb3f787864c74e1948a2e944d5adc0fb4d9b607f8a3119a0ead07b0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backupnfcMaximumMbit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="backupnfcReservationMbit")
    def backupnfc_reservation_mbit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "backupnfcReservationMbit"))

    @backupnfc_reservation_mbit.setter
    def backupnfc_reservation_mbit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88799553a38cc4ae4d5e73cebad4ba19d14a8acf71db614203ecd382158a5356)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backupnfcReservationMbit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="backupnfcShareCount")
    def backupnfc_share_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "backupnfcShareCount"))

    @backupnfc_share_count.setter
    def backupnfc_share_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18cf2c9757a0e1f79c4543d26e7cd27b20403365cc429957417003838a1f9f22)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backupnfcShareCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="backupnfcShareLevel")
    def backupnfc_share_level(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backupnfcShareLevel"))

    @backupnfc_share_level.setter
    def backupnfc_share_level(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b0de7511e2934739946da54300ebc617fdd5d62e7f0b0ecc70e09b331324c44)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backupnfcShareLevel", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__47c902b3d9dd46cd632e62446b22a713cde27eade1c08839719ec8079a4cae61)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "blockAllPorts", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__32cdc019d8e5294c3dbdfbed5d23c4b51c15fb8cd7821ae747953dbba452cc11)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "checkBeacon", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="contactDetail")
    def contact_detail(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "contactDetail"))

    @contact_detail.setter
    def contact_detail(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc86333573b5c81f77240ea7453ccba60b9c5cda55957afd5d2657f4500a1752)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "contactDetail", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="contactName")
    def contact_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "contactName"))

    @contact_name.setter
    def contact_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f05155ffd3db7a93266d4cee9558cd2246a8ee8b755cffddb56b9b3534dfa590)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "contactName", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__68cc5c938c5c12d82822a3fcbeb0aaa521d379ca0c94c021a4863c7e8ff7c0e9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customAttributes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="datacenterId")
    def datacenter_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "datacenterId"))

    @datacenter_id.setter
    def datacenter_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7fc2ee53e164c6a9339c5d9c1eac181c3a90f022cd34235843b23a8aa931929a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "datacenterId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f4aa311214ee0c24675140418dd909f62f86b85c0c8815f66fcee3a5c716d3fe)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b0cdc3f5c16ebeaf67bde53a8baf6d34c4af65953c68e52f183b40e1c7af570f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "directpathGen2Allowed", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="egressShapingAverageBandwidth")
    def egress_shaping_average_bandwidth(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "egressShapingAverageBandwidth"))

    @egress_shaping_average_bandwidth.setter
    def egress_shaping_average_bandwidth(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5bc318b970c83c5752f3427a3394c78da3d70f7b4bc5db29261a83473a87bda9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "egressShapingAverageBandwidth", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="egressShapingBurstSize")
    def egress_shaping_burst_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "egressShapingBurstSize"))

    @egress_shaping_burst_size.setter
    def egress_shaping_burst_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__84b40c48a12f4382ff480ba07da558780c38fca8301d5c6796b13a10a9d72ec1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7d99b8a1edd7752d5edd3e93d7e620a032593e3450b66103155a93808d974996)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "egressShapingEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="egressShapingPeakBandwidth")
    def egress_shaping_peak_bandwidth(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "egressShapingPeakBandwidth"))

    @egress_shaping_peak_bandwidth.setter
    def egress_shaping_peak_bandwidth(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1296b8d14d8d346ac5b99307800fc50ec32fd47a3292ae2be2da918f302b8365)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6c7a9618c95ab3d424c32a460b3cf4f3b0532543ae6aad6a5b44a376fc7fd4cf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "failback", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="faulttoleranceMaximumMbit")
    def faulttolerance_maximum_mbit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "faulttoleranceMaximumMbit"))

    @faulttolerance_maximum_mbit.setter
    def faulttolerance_maximum_mbit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__19fc98d55c27a4fbf34a3549cd0bd640a77205dab1ced47b441be8248d3e5b01)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "faulttoleranceMaximumMbit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="faulttoleranceReservationMbit")
    def faulttolerance_reservation_mbit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "faulttoleranceReservationMbit"))

    @faulttolerance_reservation_mbit.setter
    def faulttolerance_reservation_mbit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07e402c60c29e7ad5e19b2706ab1d25ae4796efda84be045981803a05fdc1ec0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "faulttoleranceReservationMbit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="faulttoleranceShareCount")
    def faulttolerance_share_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "faulttoleranceShareCount"))

    @faulttolerance_share_count.setter
    def faulttolerance_share_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b1f53e5cd29a0ed2f8157a7832810f6e62ae0186e1f97edf692f9ace3250a2c2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "faulttoleranceShareCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="faulttoleranceShareLevel")
    def faulttolerance_share_level(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "faulttoleranceShareLevel"))

    @faulttolerance_share_level.setter
    def faulttolerance_share_level(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e6ed6fbfe9a8bfde6417f05ec7827ec6358de9772b89d9dec94b295f307f403)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "faulttoleranceShareLevel", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="folder")
    def folder(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "folder"))

    @folder.setter
    def folder(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__37e9e4091e3b7e6b0fddd0c4d11e9f303ad9f63947c896d3404408b19e7877c7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "folder", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="hbrMaximumMbit")
    def hbr_maximum_mbit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "hbrMaximumMbit"))

    @hbr_maximum_mbit.setter
    def hbr_maximum_mbit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0446d12bad820a458775fef7e65e7e53151505d3d82da0f712fba25aec154943)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hbrMaximumMbit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="hbrReservationMbit")
    def hbr_reservation_mbit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "hbrReservationMbit"))

    @hbr_reservation_mbit.setter
    def hbr_reservation_mbit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8605f368855445ec3d30dfac468a2c234705f36726c0ea94786da0bdf9d63e9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hbrReservationMbit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="hbrShareCount")
    def hbr_share_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "hbrShareCount"))

    @hbr_share_count.setter
    def hbr_share_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49609ae0c56d799730f26c199fb988a56a14a5cdc42627f5df596d4524fdb229)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hbrShareCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="hbrShareLevel")
    def hbr_share_level(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hbrShareLevel"))

    @hbr_share_level.setter
    def hbr_share_level(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a3d52c246c0ad6f23f1097ff3d595837ea7b517c87b8686b28903e29c787ce44)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hbrShareLevel", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f3a21a553235bd4518b257010851b242a626c8c0fc5bc9cd97507a831ff725f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ignoreOtherPvlanMappings")
    def ignore_other_pvlan_mappings(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "ignoreOtherPvlanMappings"))

    @ignore_other_pvlan_mappings.setter
    def ignore_other_pvlan_mappings(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a77a70509529aaed3964131e434d235bd7e589ce306eb93f0ceb5bbf06379bf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ignoreOtherPvlanMappings", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ingressShapingAverageBandwidth")
    def ingress_shaping_average_bandwidth(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ingressShapingAverageBandwidth"))

    @ingress_shaping_average_bandwidth.setter
    def ingress_shaping_average_bandwidth(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__775d0f97776e8b352a968f4c9bd5c0ca37ce69029133f80c028ff797e4501387)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ingressShapingAverageBandwidth", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ingressShapingBurstSize")
    def ingress_shaping_burst_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ingressShapingBurstSize"))

    @ingress_shaping_burst_size.setter
    def ingress_shaping_burst_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7615157cfa880dc077a08b9b7a8e42f897a46c1efdc5d465774390b6a40fd88)
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
            type_hints = typing.get_type_hints(_typecheckingstub__785d331ae9cf7f75e78219ddeadf3fe3c62a2e470597ca94cadf8174e4a185a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ingressShapingEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ingressShapingPeakBandwidth")
    def ingress_shaping_peak_bandwidth(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ingressShapingPeakBandwidth"))

    @ingress_shaping_peak_bandwidth.setter
    def ingress_shaping_peak_bandwidth(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be7524a2298f48a71060cfc97c2c2b0e8cd6dd194495bd7ff8e58094c1055035)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ingressShapingPeakBandwidth", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipv4Address")
    def ipv4_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipv4Address"))

    @ipv4_address.setter
    def ipv4_address(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d590d1e3701df1771de802df354fb4aaa4a7c45a5970cb086698434f57c7779)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipv4Address", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="iscsiMaximumMbit")
    def iscsi_maximum_mbit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "iscsiMaximumMbit"))

    @iscsi_maximum_mbit.setter
    def iscsi_maximum_mbit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba6fa135913b8e9a7bc7c361e9d21e4d378e2819c101c319fe2618932d80cf4b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "iscsiMaximumMbit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="iscsiReservationMbit")
    def iscsi_reservation_mbit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "iscsiReservationMbit"))

    @iscsi_reservation_mbit.setter
    def iscsi_reservation_mbit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f7a338d7831974a6f7856d700f67d4322dd7b50b0ffbe05adc97e255e78aaa3e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "iscsiReservationMbit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="iscsiShareCount")
    def iscsi_share_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "iscsiShareCount"))

    @iscsi_share_count.setter
    def iscsi_share_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e1fb832b7743bed78b3b660a6d4a046d84be984db542bf4a987ed15b643a6fa0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "iscsiShareCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="iscsiShareLevel")
    def iscsi_share_level(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "iscsiShareLevel"))

    @iscsi_share_level.setter
    def iscsi_share_level(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e875a9234718732930ed986b929d3243dfc8dba6759676b10f1f77989046f162)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "iscsiShareLevel", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="lacpApiVersion")
    def lacp_api_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lacpApiVersion"))

    @lacp_api_version.setter
    def lacp_api_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f209afb7bc11e1a5d7c541f0389f73aebc3d9ff455551579549618255ba611da)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lacpApiVersion", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__231f468379c197e7ed84f3afc2a271cccd573e22a5bddff3b0bf3b9eb42b6b0f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lacpEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="lacpMode")
    def lacp_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lacpMode"))

    @lacp_mode.setter
    def lacp_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de9d2f4b1b43ca24e46cbe947a07c94304d548131478588327c619c07624a0bf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lacpMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="linkDiscoveryOperation")
    def link_discovery_operation(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "linkDiscoveryOperation"))

    @link_discovery_operation.setter
    def link_discovery_operation(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb8c7af4a25698ea936a3b07dca71b52ccee76e6a995b9cccaac4d37b603e7cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "linkDiscoveryOperation", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="linkDiscoveryProtocol")
    def link_discovery_protocol(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "linkDiscoveryProtocol"))

    @link_discovery_protocol.setter
    def link_discovery_protocol(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14304848776145b12155292fa345388c5be98448282d9672113dd3be9f1fb92e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "linkDiscoveryProtocol", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="managementMaximumMbit")
    def management_maximum_mbit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "managementMaximumMbit"))

    @management_maximum_mbit.setter
    def management_maximum_mbit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8042501a86a08d321e2d042521e18fbf65e2feb0da68bbf5e5d644086da5ea48)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "managementMaximumMbit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="managementReservationMbit")
    def management_reservation_mbit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "managementReservationMbit"))

    @management_reservation_mbit.setter
    def management_reservation_mbit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ace027e097e405bd714a6c511a77af5387eac3e0a23f88e6d29f15f461c4796)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "managementReservationMbit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="managementShareCount")
    def management_share_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "managementShareCount"))

    @management_share_count.setter
    def management_share_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de38124f91e4291078a80cc9fcad249f8207a25a2e6aa4640189092cd42c698d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "managementShareCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="managementShareLevel")
    def management_share_level(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "managementShareLevel"))

    @management_share_level.setter
    def management_share_level(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87f2312bcd1abd5cb57d16c928575743152efe59952fcdf30934b10025aaabd8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "managementShareLevel", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxMtu")
    def max_mtu(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxMtu"))

    @max_mtu.setter
    def max_mtu(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d00e4c4ff44a132de11dbf87e198faa3221397f2b8391301b2a80d9e99756dd4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxMtu", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="multicastFilteringMode")
    def multicast_filtering_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "multicastFilteringMode"))

    @multicast_filtering_mode.setter
    def multicast_filtering_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__854dff79864e7fb232aed1a354caed9790baf917ce019aa6e14ef78858bc32a8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "multicastFilteringMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a72851d10fa900a6bde57893bc869eee6cf9465e3b38b97400756f4e907be078)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="netflowActiveFlowTimeout")
    def netflow_active_flow_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "netflowActiveFlowTimeout"))

    @netflow_active_flow_timeout.setter
    def netflow_active_flow_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9355fdb140e559870616d54c6538adf9caf830a5cad0f87091cb47ee9e0cf415)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "netflowActiveFlowTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="netflowCollectorIpAddress")
    def netflow_collector_ip_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "netflowCollectorIpAddress"))

    @netflow_collector_ip_address.setter
    def netflow_collector_ip_address(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b973e3d39e79b4bba82c5a84b38566fe7600ce452fa88f1e55ab5fb58ad0f782)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "netflowCollectorIpAddress", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="netflowCollectorPort")
    def netflow_collector_port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "netflowCollectorPort"))

    @netflow_collector_port.setter
    def netflow_collector_port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b608c433c417bd1f3390b273fc26a3be56076b187446e0e436954d3f2f2b5c2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "netflowCollectorPort", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__21a03c034eb8841e53e401185e569927b527169a890d22f2f4d4312fab93885b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "netflowEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="netflowIdleFlowTimeout")
    def netflow_idle_flow_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "netflowIdleFlowTimeout"))

    @netflow_idle_flow_timeout.setter
    def netflow_idle_flow_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36333df7a63112e2aa34c827ae6bc78bd8c112b2164a848ca633b36fdf4ac4b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "netflowIdleFlowTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="netflowInternalFlowsOnly")
    def netflow_internal_flows_only(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "netflowInternalFlowsOnly"))

    @netflow_internal_flows_only.setter
    def netflow_internal_flows_only(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe0ddaf04ec6770ae6e14d4ec4539bf6fec4965aaa1e5c24107d336ed443f1ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "netflowInternalFlowsOnly", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="netflowObservationDomainId")
    def netflow_observation_domain_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "netflowObservationDomainId"))

    @netflow_observation_domain_id.setter
    def netflow_observation_domain_id(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ca00af1ab837acebdc2a0d449adf84d630b3a157f8b86ec0518e63b87164521)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "netflowObservationDomainId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="netflowSamplingRate")
    def netflow_sampling_rate(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "netflowSamplingRate"))

    @netflow_sampling_rate.setter
    def netflow_sampling_rate(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c60de2f67fdc987b92e91fb8d815fe8b853036f089524ed8e37c3b47d19085d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "netflowSamplingRate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="networkResourceControlEnabled")
    def network_resource_control_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "networkResourceControlEnabled"))

    @network_resource_control_enabled.setter
    def network_resource_control_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e57d53718704f1c7e2a552657d5b79ebff8538da807f0d3322f759f028267a37)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "networkResourceControlEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="networkResourceControlVersion")
    def network_resource_control_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "networkResourceControlVersion"))

    @network_resource_control_version.setter
    def network_resource_control_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a6491d5a36511ec75dd905aaffe277a454e27ecee61c8b30cc80111ab5fcd4ef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "networkResourceControlVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="nfsMaximumMbit")
    def nfs_maximum_mbit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "nfsMaximumMbit"))

    @nfs_maximum_mbit.setter
    def nfs_maximum_mbit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e5f4d42fd9e56d34372c4e65b44c94775f7261d5a5a4bb4d5fc014d81d7f3fe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nfsMaximumMbit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="nfsReservationMbit")
    def nfs_reservation_mbit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "nfsReservationMbit"))

    @nfs_reservation_mbit.setter
    def nfs_reservation_mbit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a0ef828e9298c7924ebb1bbd7dd08ea7390373d08ebeb80bfb73d3ddf416654)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nfsReservationMbit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="nfsShareCount")
    def nfs_share_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "nfsShareCount"))

    @nfs_share_count.setter
    def nfs_share_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14933169a9e17ca8d1a49b49f1c644a85690b80d337ac9274ff369b22377c68d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nfsShareCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="nfsShareLevel")
    def nfs_share_level(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nfsShareLevel"))

    @nfs_share_level.setter
    def nfs_share_level(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d813aab8077118caefeaa00b4e43b77f4bfac595c50124bfc93e4a48e4943419)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nfsShareLevel", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__14fc4b7b003020e34431d48e256f0ba7cccfd9a41d0de952e65b076cac2e82be)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "notifySwitches", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="portPrivateSecondaryVlanId")
    def port_private_secondary_vlan_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "portPrivateSecondaryVlanId"))

    @port_private_secondary_vlan_id.setter
    def port_private_secondary_vlan_id(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f9ad71ae248252fe2cb7bba47332022876083f853072672577479ffb467ffb01)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "portPrivateSecondaryVlanId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="standbyUplinks")
    def standby_uplinks(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "standbyUplinks"))

    @standby_uplinks.setter
    def standby_uplinks(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e993d066310e833b2670294cab72e01013f03914d851ec95e1666870a4cdcaa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "standbyUplinks", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f79d51bd730760271d0155cfc4d42f208822e4627ccf1aca78cfcf94c06bb09e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="teamingPolicy")
    def teaming_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "teamingPolicy"))

    @teaming_policy.setter
    def teaming_policy(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e77dc6afec2dac692c44ccd6682baf62ad05c677da816ed4791a25cbf590745)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "teamingPolicy", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__309a6926ba36e3ee185009202f9b3e2642464ce15e59f781e0716906f1f3fa5a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "txUplink", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uplinks")
    def uplinks(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "uplinks"))

    @uplinks.setter
    def uplinks(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7591233a4c75a2b1c4dbbbd7039685c8082a04817be254f78d7d3431b17f345e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uplinks", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vdpMaximumMbit")
    def vdp_maximum_mbit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "vdpMaximumMbit"))

    @vdp_maximum_mbit.setter
    def vdp_maximum_mbit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__340b7bdd667a0fd556dbe43e2d6a5e4f0be9ca8b66abb002e22371006836025f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vdpMaximumMbit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vdpReservationMbit")
    def vdp_reservation_mbit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "vdpReservationMbit"))

    @vdp_reservation_mbit.setter
    def vdp_reservation_mbit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__469b929037704d57f865e1b86d1b9c0fe6570471b3e9eba507fd07f9369c8f18)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vdpReservationMbit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vdpShareCount")
    def vdp_share_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "vdpShareCount"))

    @vdp_share_count.setter
    def vdp_share_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a0d1f1e212de2113c0b45b8341eed912996e8c6438410c04e61be6a728ecb3f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vdpShareCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vdpShareLevel")
    def vdp_share_level(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vdpShareLevel"))

    @vdp_share_level.setter
    def vdp_share_level(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea263d370f646fe63f9f2cda740a92a3adc9bb2c2a0a28d8162dc3267d5a39c2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vdpShareLevel", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @version.setter
    def version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76b6a3272897b37ab31baab67bddf24776a9d14ac257e594dada082d7db51db1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "version", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="virtualmachineMaximumMbit")
    def virtualmachine_maximum_mbit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "virtualmachineMaximumMbit"))

    @virtualmachine_maximum_mbit.setter
    def virtualmachine_maximum_mbit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c2ea66402c35dd295d687ffd6b35df4a99bc51a30f383acc80c088d37f473edb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "virtualmachineMaximumMbit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="virtualmachineReservationMbit")
    def virtualmachine_reservation_mbit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "virtualmachineReservationMbit"))

    @virtualmachine_reservation_mbit.setter
    def virtualmachine_reservation_mbit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74a7e8527ab3449cc84ba438f98da3364320dfa8c9d41d56856e5a5e2eb74dcf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "virtualmachineReservationMbit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="virtualmachineShareCount")
    def virtualmachine_share_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "virtualmachineShareCount"))

    @virtualmachine_share_count.setter
    def virtualmachine_share_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a822cb55b469bea10c9a2632c84a83e0b791beb4e535ceeeb2f3d27a48610c9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "virtualmachineShareCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="virtualmachineShareLevel")
    def virtualmachine_share_level(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "virtualmachineShareLevel"))

    @virtualmachine_share_level.setter
    def virtualmachine_share_level(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__953b0bb848fb30d61655ca7ff4d7f45c6e5c08e8caee8f40879e889c4036aed2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "virtualmachineShareLevel", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vlanId")
    def vlan_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "vlanId"))

    @vlan_id.setter
    def vlan_id(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23353a43ee1d7376378409daa25e4a5231429b08ec84d443331afc44f135b246)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vlanId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vmotionMaximumMbit")
    def vmotion_maximum_mbit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "vmotionMaximumMbit"))

    @vmotion_maximum_mbit.setter
    def vmotion_maximum_mbit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e587a78d057e7191308b8058b89918df16f00633d2d67e247c5809493194652)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vmotionMaximumMbit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vmotionReservationMbit")
    def vmotion_reservation_mbit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "vmotionReservationMbit"))

    @vmotion_reservation_mbit.setter
    def vmotion_reservation_mbit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__472126d8f4c90260506bccec261b15220af07e6e26826ef7b9c0bd4de7ae902b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vmotionReservationMbit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vmotionShareCount")
    def vmotion_share_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "vmotionShareCount"))

    @vmotion_share_count.setter
    def vmotion_share_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72a0845251b13a7f2145429bed322f584078ce348695fd0de50edc94bf8319dd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vmotionShareCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vmotionShareLevel")
    def vmotion_share_level(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vmotionShareLevel"))

    @vmotion_share_level.setter
    def vmotion_share_level(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05f9b906292d11572f7716a1c8263f5311a6784460a232261ba21d64bdeea9ab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vmotionShareLevel", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vsanMaximumMbit")
    def vsan_maximum_mbit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "vsanMaximumMbit"))

    @vsan_maximum_mbit.setter
    def vsan_maximum_mbit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d121fe9f9b68e42204a87d2ce15548998d58523539cedaf4acfb9728a18b69a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vsanMaximumMbit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vsanReservationMbit")
    def vsan_reservation_mbit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "vsanReservationMbit"))

    @vsan_reservation_mbit.setter
    def vsan_reservation_mbit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0c5f9d1c64f85f4541ad6d1213ca23192fb506c0c240a908c822993aec49e35)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vsanReservationMbit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vsanShareCount")
    def vsan_share_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "vsanShareCount"))

    @vsan_share_count.setter
    def vsan_share_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dcc7166faca340d33fae632558df44d1b2b51ffa317086055ca3deb6d511bc78)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vsanShareCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vsanShareLevel")
    def vsan_share_level(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vsanShareLevel"))

    @vsan_share_level.setter
    def vsan_share_level(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__248487444b2b37bf3a5c1e4d0f6f5c270c5e79fc0553020eec6dd93563f06e91)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vsanShareLevel", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.distributedVirtualSwitch.DistributedVirtualSwitchConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "datacenter_id": "datacenterId",
        "name": "name",
        "active_uplinks": "activeUplinks",
        "allow_forged_transmits": "allowForgedTransmits",
        "allow_mac_changes": "allowMacChanges",
        "allow_promiscuous": "allowPromiscuous",
        "backupnfc_maximum_mbit": "backupnfcMaximumMbit",
        "backupnfc_reservation_mbit": "backupnfcReservationMbit",
        "backupnfc_share_count": "backupnfcShareCount",
        "backupnfc_share_level": "backupnfcShareLevel",
        "block_all_ports": "blockAllPorts",
        "check_beacon": "checkBeacon",
        "contact_detail": "contactDetail",
        "contact_name": "contactName",
        "custom_attributes": "customAttributes",
        "description": "description",
        "directpath_gen2_allowed": "directpathGen2Allowed",
        "egress_shaping_average_bandwidth": "egressShapingAverageBandwidth",
        "egress_shaping_burst_size": "egressShapingBurstSize",
        "egress_shaping_enabled": "egressShapingEnabled",
        "egress_shaping_peak_bandwidth": "egressShapingPeakBandwidth",
        "failback": "failback",
        "faulttolerance_maximum_mbit": "faulttoleranceMaximumMbit",
        "faulttolerance_reservation_mbit": "faulttoleranceReservationMbit",
        "faulttolerance_share_count": "faulttoleranceShareCount",
        "faulttolerance_share_level": "faulttoleranceShareLevel",
        "folder": "folder",
        "hbr_maximum_mbit": "hbrMaximumMbit",
        "hbr_reservation_mbit": "hbrReservationMbit",
        "hbr_share_count": "hbrShareCount",
        "hbr_share_level": "hbrShareLevel",
        "host": "host",
        "id": "id",
        "ignore_other_pvlan_mappings": "ignoreOtherPvlanMappings",
        "ingress_shaping_average_bandwidth": "ingressShapingAverageBandwidth",
        "ingress_shaping_burst_size": "ingressShapingBurstSize",
        "ingress_shaping_enabled": "ingressShapingEnabled",
        "ingress_shaping_peak_bandwidth": "ingressShapingPeakBandwidth",
        "ipv4_address": "ipv4Address",
        "iscsi_maximum_mbit": "iscsiMaximumMbit",
        "iscsi_reservation_mbit": "iscsiReservationMbit",
        "iscsi_share_count": "iscsiShareCount",
        "iscsi_share_level": "iscsiShareLevel",
        "lacp_api_version": "lacpApiVersion",
        "lacp_enabled": "lacpEnabled",
        "lacp_mode": "lacpMode",
        "link_discovery_operation": "linkDiscoveryOperation",
        "link_discovery_protocol": "linkDiscoveryProtocol",
        "management_maximum_mbit": "managementMaximumMbit",
        "management_reservation_mbit": "managementReservationMbit",
        "management_share_count": "managementShareCount",
        "management_share_level": "managementShareLevel",
        "max_mtu": "maxMtu",
        "multicast_filtering_mode": "multicastFilteringMode",
        "netflow_active_flow_timeout": "netflowActiveFlowTimeout",
        "netflow_collector_ip_address": "netflowCollectorIpAddress",
        "netflow_collector_port": "netflowCollectorPort",
        "netflow_enabled": "netflowEnabled",
        "netflow_idle_flow_timeout": "netflowIdleFlowTimeout",
        "netflow_internal_flows_only": "netflowInternalFlowsOnly",
        "netflow_observation_domain_id": "netflowObservationDomainId",
        "netflow_sampling_rate": "netflowSamplingRate",
        "network_resource_control_enabled": "networkResourceControlEnabled",
        "network_resource_control_version": "networkResourceControlVersion",
        "nfs_maximum_mbit": "nfsMaximumMbit",
        "nfs_reservation_mbit": "nfsReservationMbit",
        "nfs_share_count": "nfsShareCount",
        "nfs_share_level": "nfsShareLevel",
        "notify_switches": "notifySwitches",
        "port_private_secondary_vlan_id": "portPrivateSecondaryVlanId",
        "pvlan_mapping": "pvlanMapping",
        "standby_uplinks": "standbyUplinks",
        "tags": "tags",
        "teaming_policy": "teamingPolicy",
        "tx_uplink": "txUplink",
        "uplinks": "uplinks",
        "vdp_maximum_mbit": "vdpMaximumMbit",
        "vdp_reservation_mbit": "vdpReservationMbit",
        "vdp_share_count": "vdpShareCount",
        "vdp_share_level": "vdpShareLevel",
        "version": "version",
        "virtualmachine_maximum_mbit": "virtualmachineMaximumMbit",
        "virtualmachine_reservation_mbit": "virtualmachineReservationMbit",
        "virtualmachine_share_count": "virtualmachineShareCount",
        "virtualmachine_share_level": "virtualmachineShareLevel",
        "vlan_id": "vlanId",
        "vlan_range": "vlanRange",
        "vmotion_maximum_mbit": "vmotionMaximumMbit",
        "vmotion_reservation_mbit": "vmotionReservationMbit",
        "vmotion_share_count": "vmotionShareCount",
        "vmotion_share_level": "vmotionShareLevel",
        "vsan_maximum_mbit": "vsanMaximumMbit",
        "vsan_reservation_mbit": "vsanReservationMbit",
        "vsan_share_count": "vsanShareCount",
        "vsan_share_level": "vsanShareLevel",
    },
)
class DistributedVirtualSwitchConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        datacenter_id: builtins.str,
        name: builtins.str,
        active_uplinks: typing.Optional[typing.Sequence[builtins.str]] = None,
        allow_forged_transmits: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_mac_changes: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_promiscuous: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        backupnfc_maximum_mbit: typing.Optional[jsii.Number] = None,
        backupnfc_reservation_mbit: typing.Optional[jsii.Number] = None,
        backupnfc_share_count: typing.Optional[jsii.Number] = None,
        backupnfc_share_level: typing.Optional[builtins.str] = None,
        block_all_ports: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        check_beacon: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        contact_detail: typing.Optional[builtins.str] = None,
        contact_name: typing.Optional[builtins.str] = None,
        custom_attributes: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        directpath_gen2_allowed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        egress_shaping_average_bandwidth: typing.Optional[jsii.Number] = None,
        egress_shaping_burst_size: typing.Optional[jsii.Number] = None,
        egress_shaping_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        egress_shaping_peak_bandwidth: typing.Optional[jsii.Number] = None,
        failback: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        faulttolerance_maximum_mbit: typing.Optional[jsii.Number] = None,
        faulttolerance_reservation_mbit: typing.Optional[jsii.Number] = None,
        faulttolerance_share_count: typing.Optional[jsii.Number] = None,
        faulttolerance_share_level: typing.Optional[builtins.str] = None,
        folder: typing.Optional[builtins.str] = None,
        hbr_maximum_mbit: typing.Optional[jsii.Number] = None,
        hbr_reservation_mbit: typing.Optional[jsii.Number] = None,
        hbr_share_count: typing.Optional[jsii.Number] = None,
        hbr_share_level: typing.Optional[builtins.str] = None,
        host: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DistributedVirtualSwitchHost", typing.Dict[builtins.str, typing.Any]]]]] = None,
        id: typing.Optional[builtins.str] = None,
        ignore_other_pvlan_mappings: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ingress_shaping_average_bandwidth: typing.Optional[jsii.Number] = None,
        ingress_shaping_burst_size: typing.Optional[jsii.Number] = None,
        ingress_shaping_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ingress_shaping_peak_bandwidth: typing.Optional[jsii.Number] = None,
        ipv4_address: typing.Optional[builtins.str] = None,
        iscsi_maximum_mbit: typing.Optional[jsii.Number] = None,
        iscsi_reservation_mbit: typing.Optional[jsii.Number] = None,
        iscsi_share_count: typing.Optional[jsii.Number] = None,
        iscsi_share_level: typing.Optional[builtins.str] = None,
        lacp_api_version: typing.Optional[builtins.str] = None,
        lacp_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        lacp_mode: typing.Optional[builtins.str] = None,
        link_discovery_operation: typing.Optional[builtins.str] = None,
        link_discovery_protocol: typing.Optional[builtins.str] = None,
        management_maximum_mbit: typing.Optional[jsii.Number] = None,
        management_reservation_mbit: typing.Optional[jsii.Number] = None,
        management_share_count: typing.Optional[jsii.Number] = None,
        management_share_level: typing.Optional[builtins.str] = None,
        max_mtu: typing.Optional[jsii.Number] = None,
        multicast_filtering_mode: typing.Optional[builtins.str] = None,
        netflow_active_flow_timeout: typing.Optional[jsii.Number] = None,
        netflow_collector_ip_address: typing.Optional[builtins.str] = None,
        netflow_collector_port: typing.Optional[jsii.Number] = None,
        netflow_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        netflow_idle_flow_timeout: typing.Optional[jsii.Number] = None,
        netflow_internal_flows_only: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        netflow_observation_domain_id: typing.Optional[jsii.Number] = None,
        netflow_sampling_rate: typing.Optional[jsii.Number] = None,
        network_resource_control_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        network_resource_control_version: typing.Optional[builtins.str] = None,
        nfs_maximum_mbit: typing.Optional[jsii.Number] = None,
        nfs_reservation_mbit: typing.Optional[jsii.Number] = None,
        nfs_share_count: typing.Optional[jsii.Number] = None,
        nfs_share_level: typing.Optional[builtins.str] = None,
        notify_switches: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        port_private_secondary_vlan_id: typing.Optional[jsii.Number] = None,
        pvlan_mapping: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DistributedVirtualSwitchPvlanMapping", typing.Dict[builtins.str, typing.Any]]]]] = None,
        standby_uplinks: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        teaming_policy: typing.Optional[builtins.str] = None,
        tx_uplink: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        uplinks: typing.Optional[typing.Sequence[builtins.str]] = None,
        vdp_maximum_mbit: typing.Optional[jsii.Number] = None,
        vdp_reservation_mbit: typing.Optional[jsii.Number] = None,
        vdp_share_count: typing.Optional[jsii.Number] = None,
        vdp_share_level: typing.Optional[builtins.str] = None,
        version: typing.Optional[builtins.str] = None,
        virtualmachine_maximum_mbit: typing.Optional[jsii.Number] = None,
        virtualmachine_reservation_mbit: typing.Optional[jsii.Number] = None,
        virtualmachine_share_count: typing.Optional[jsii.Number] = None,
        virtualmachine_share_level: typing.Optional[builtins.str] = None,
        vlan_id: typing.Optional[jsii.Number] = None,
        vlan_range: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DistributedVirtualSwitchVlanRange", typing.Dict[builtins.str, typing.Any]]]]] = None,
        vmotion_maximum_mbit: typing.Optional[jsii.Number] = None,
        vmotion_reservation_mbit: typing.Optional[jsii.Number] = None,
        vmotion_share_count: typing.Optional[jsii.Number] = None,
        vmotion_share_level: typing.Optional[builtins.str] = None,
        vsan_maximum_mbit: typing.Optional[jsii.Number] = None,
        vsan_reservation_mbit: typing.Optional[jsii.Number] = None,
        vsan_share_count: typing.Optional[jsii.Number] = None,
        vsan_share_level: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param datacenter_id: The ID of the datacenter to create this virtual switch in. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#datacenter_id DistributedVirtualSwitch#datacenter_id}
        :param name: The name for the DVS. Must be unique in the folder that it is being created in. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#name DistributedVirtualSwitch#name}
        :param active_uplinks: List of active uplinks used for load balancing, matching the names of the uplinks assigned in the DVS. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#active_uplinks DistributedVirtualSwitch#active_uplinks}
        :param allow_forged_transmits: Controls whether or not the virtual network adapter is allowed to send network traffic with a different MAC address than that of its own. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#allow_forged_transmits DistributedVirtualSwitch#allow_forged_transmits}
        :param allow_mac_changes: Controls whether or not the Media Access Control (MAC) address can be changed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#allow_mac_changes DistributedVirtualSwitch#allow_mac_changes}
        :param allow_promiscuous: Enable promiscuous mode on the network. This flag indicates whether or not all traffic is seen on a given port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#allow_promiscuous DistributedVirtualSwitch#allow_promiscuous}
        :param backupnfc_maximum_mbit: The maximum allowed usage for the backupNfc traffic class, in Mbits/sec. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#backupnfc_maximum_mbit DistributedVirtualSwitch#backupnfc_maximum_mbit}
        :param backupnfc_reservation_mbit: The amount of guaranteed bandwidth for the backupNfc traffic class, in Mbits/sec. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#backupnfc_reservation_mbit DistributedVirtualSwitch#backupnfc_reservation_mbit}
        :param backupnfc_share_count: The amount of shares to allocate to the backupNfc traffic class for a custom share level. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#backupnfc_share_count DistributedVirtualSwitch#backupnfc_share_count}
        :param backupnfc_share_level: The allocation level for the backupNfc traffic class. Can be one of high, low, normal, or custom. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#backupnfc_share_level DistributedVirtualSwitch#backupnfc_share_level}
        :param block_all_ports: Indicates whether to block all ports by default. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#block_all_ports DistributedVirtualSwitch#block_all_ports}
        :param check_beacon: Enable beacon probing on the ports this policy applies to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#check_beacon DistributedVirtualSwitch#check_beacon}
        :param contact_detail: The contact detail for this DVS. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#contact_detail DistributedVirtualSwitch#contact_detail}
        :param contact_name: The contact name for this DVS. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#contact_name DistributedVirtualSwitch#contact_name}
        :param custom_attributes: A list of custom attributes to set on this resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#custom_attributes DistributedVirtualSwitch#custom_attributes}
        :param description: The description of the DVS. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#description DistributedVirtualSwitch#description}
        :param directpath_gen2_allowed: Allow VMDirectPath Gen2 on the ports this policy applies to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#directpath_gen2_allowed DistributedVirtualSwitch#directpath_gen2_allowed}
        :param egress_shaping_average_bandwidth: The average egress bandwidth in bits per second if egress shaping is enabled on the port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#egress_shaping_average_bandwidth DistributedVirtualSwitch#egress_shaping_average_bandwidth}
        :param egress_shaping_burst_size: The maximum egress burst size allowed in bytes if egress shaping is enabled on the port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#egress_shaping_burst_size DistributedVirtualSwitch#egress_shaping_burst_size}
        :param egress_shaping_enabled: True if the traffic shaper is enabled for egress traffic on the port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#egress_shaping_enabled DistributedVirtualSwitch#egress_shaping_enabled}
        :param egress_shaping_peak_bandwidth: The peak egress bandwidth during bursts in bits per second if egress traffic shaping is enabled on the port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#egress_shaping_peak_bandwidth DistributedVirtualSwitch#egress_shaping_peak_bandwidth}
        :param failback: If true, the teaming policy will re-activate failed interfaces higher in precedence when they come back up. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#failback DistributedVirtualSwitch#failback}
        :param faulttolerance_maximum_mbit: The maximum allowed usage for the faultTolerance traffic class, in Mbits/sec. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#faulttolerance_maximum_mbit DistributedVirtualSwitch#faulttolerance_maximum_mbit}
        :param faulttolerance_reservation_mbit: The amount of guaranteed bandwidth for the faultTolerance traffic class, in Mbits/sec. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#faulttolerance_reservation_mbit DistributedVirtualSwitch#faulttolerance_reservation_mbit}
        :param faulttolerance_share_count: The amount of shares to allocate to the faultTolerance traffic class for a custom share level. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#faulttolerance_share_count DistributedVirtualSwitch#faulttolerance_share_count}
        :param faulttolerance_share_level: The allocation level for the faultTolerance traffic class. Can be one of high, low, normal, or custom. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#faulttolerance_share_level DistributedVirtualSwitch#faulttolerance_share_level}
        :param folder: The folder to create this virtual switch in, relative to the datacenter. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#folder DistributedVirtualSwitch#folder}
        :param hbr_maximum_mbit: The maximum allowed usage for the hbr traffic class, in Mbits/sec. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#hbr_maximum_mbit DistributedVirtualSwitch#hbr_maximum_mbit}
        :param hbr_reservation_mbit: The amount of guaranteed bandwidth for the hbr traffic class, in Mbits/sec. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#hbr_reservation_mbit DistributedVirtualSwitch#hbr_reservation_mbit}
        :param hbr_share_count: The amount of shares to allocate to the hbr traffic class for a custom share level. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#hbr_share_count DistributedVirtualSwitch#hbr_share_count}
        :param hbr_share_level: The allocation level for the hbr traffic class. Can be one of high, low, normal, or custom. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#hbr_share_level DistributedVirtualSwitch#hbr_share_level}
        :param host: host block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#host DistributedVirtualSwitch#host}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#id DistributedVirtualSwitch#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param ignore_other_pvlan_mappings: Whether to ignore existing PVLAN mappings not managed by this resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#ignore_other_pvlan_mappings DistributedVirtualSwitch#ignore_other_pvlan_mappings}
        :param ingress_shaping_average_bandwidth: The average ingress bandwidth in bits per second if ingress shaping is enabled on the port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#ingress_shaping_average_bandwidth DistributedVirtualSwitch#ingress_shaping_average_bandwidth}
        :param ingress_shaping_burst_size: The maximum ingress burst size allowed in bytes if ingress shaping is enabled on the port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#ingress_shaping_burst_size DistributedVirtualSwitch#ingress_shaping_burst_size}
        :param ingress_shaping_enabled: True if the traffic shaper is enabled for ingress traffic on the port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#ingress_shaping_enabled DistributedVirtualSwitch#ingress_shaping_enabled}
        :param ingress_shaping_peak_bandwidth: The peak ingress bandwidth during bursts in bits per second if ingress traffic shaping is enabled on the port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#ingress_shaping_peak_bandwidth DistributedVirtualSwitch#ingress_shaping_peak_bandwidth}
        :param ipv4_address: The IPv4 address of the switch. This can be used to see the DVS as a unique device with NetFlow. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#ipv4_address DistributedVirtualSwitch#ipv4_address}
        :param iscsi_maximum_mbit: The maximum allowed usage for the iSCSI traffic class, in Mbits/sec. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#iscsi_maximum_mbit DistributedVirtualSwitch#iscsi_maximum_mbit}
        :param iscsi_reservation_mbit: The amount of guaranteed bandwidth for the iSCSI traffic class, in Mbits/sec. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#iscsi_reservation_mbit DistributedVirtualSwitch#iscsi_reservation_mbit}
        :param iscsi_share_count: The amount of shares to allocate to the iSCSI traffic class for a custom share level. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#iscsi_share_count DistributedVirtualSwitch#iscsi_share_count}
        :param iscsi_share_level: The allocation level for the iSCSI traffic class. Can be one of high, low, normal, or custom. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#iscsi_share_level DistributedVirtualSwitch#iscsi_share_level}
        :param lacp_api_version: The Link Aggregation Control Protocol group version in the switch. Can be one of singleLag or multipleLag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#lacp_api_version DistributedVirtualSwitch#lacp_api_version}
        :param lacp_enabled: Whether or not to enable LACP on all uplink ports. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#lacp_enabled DistributedVirtualSwitch#lacp_enabled}
        :param lacp_mode: The uplink LACP mode to use. Can be one of active or passive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#lacp_mode DistributedVirtualSwitch#lacp_mode}
        :param link_discovery_operation: Whether to advertise or listen for link discovery. Valid values are advertise, both, listen, and none. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#link_discovery_operation DistributedVirtualSwitch#link_discovery_operation}
        :param link_discovery_protocol: The discovery protocol type. Valid values are cdp and lldp. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#link_discovery_protocol DistributedVirtualSwitch#link_discovery_protocol}
        :param management_maximum_mbit: The maximum allowed usage for the management traffic class, in Mbits/sec. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#management_maximum_mbit DistributedVirtualSwitch#management_maximum_mbit}
        :param management_reservation_mbit: The amount of guaranteed bandwidth for the management traffic class, in Mbits/sec. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#management_reservation_mbit DistributedVirtualSwitch#management_reservation_mbit}
        :param management_share_count: The amount of shares to allocate to the management traffic class for a custom share level. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#management_share_count DistributedVirtualSwitch#management_share_count}
        :param management_share_level: The allocation level for the management traffic class. Can be one of high, low, normal, or custom. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#management_share_level DistributedVirtualSwitch#management_share_level}
        :param max_mtu: The maximum MTU on the switch. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#max_mtu DistributedVirtualSwitch#max_mtu}
        :param multicast_filtering_mode: The multicast filtering mode on the switch. Can be one of legacyFiltering, or snooping. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#multicast_filtering_mode DistributedVirtualSwitch#multicast_filtering_mode}
        :param netflow_active_flow_timeout: The number of seconds after which active flows are forced to be exported to the collector. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#netflow_active_flow_timeout DistributedVirtualSwitch#netflow_active_flow_timeout}
        :param netflow_collector_ip_address: IP address for the netflow collector, using IPv4 or IPv6. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#netflow_collector_ip_address DistributedVirtualSwitch#netflow_collector_ip_address}
        :param netflow_collector_port: The port for the netflow collector. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#netflow_collector_port DistributedVirtualSwitch#netflow_collector_port}
        :param netflow_enabled: Indicates whether to enable netflow on all ports. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#netflow_enabled DistributedVirtualSwitch#netflow_enabled}
        :param netflow_idle_flow_timeout: The number of seconds after which idle flows are forced to be exported to the collector. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#netflow_idle_flow_timeout DistributedVirtualSwitch#netflow_idle_flow_timeout}
        :param netflow_internal_flows_only: Whether to limit analysis to traffic that has both source and destination served by the same host. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#netflow_internal_flows_only DistributedVirtualSwitch#netflow_internal_flows_only}
        :param netflow_observation_domain_id: The observation Domain ID for the netflow collector. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#netflow_observation_domain_id DistributedVirtualSwitch#netflow_observation_domain_id}
        :param netflow_sampling_rate: The ratio of total number of packets to the number of packets analyzed. Set to 0 to disable sampling, meaning that all packets are analyzed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#netflow_sampling_rate DistributedVirtualSwitch#netflow_sampling_rate}
        :param network_resource_control_enabled: Whether or not to enable network resource control, enabling advanced traffic shaping and resource control features. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#network_resource_control_enabled DistributedVirtualSwitch#network_resource_control_enabled}
        :param network_resource_control_version: The network I/O control version to use. Can be one of version2 or version3. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#network_resource_control_version DistributedVirtualSwitch#network_resource_control_version}
        :param nfs_maximum_mbit: The maximum allowed usage for the nfs traffic class, in Mbits/sec. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#nfs_maximum_mbit DistributedVirtualSwitch#nfs_maximum_mbit}
        :param nfs_reservation_mbit: The amount of guaranteed bandwidth for the nfs traffic class, in Mbits/sec. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#nfs_reservation_mbit DistributedVirtualSwitch#nfs_reservation_mbit}
        :param nfs_share_count: The amount of shares to allocate to the nfs traffic class for a custom share level. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#nfs_share_count DistributedVirtualSwitch#nfs_share_count}
        :param nfs_share_level: The allocation level for the nfs traffic class. Can be one of high, low, normal, or custom. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#nfs_share_level DistributedVirtualSwitch#nfs_share_level}
        :param notify_switches: If true, the teaming policy will notify the broadcast network of a NIC failover, triggering cache updates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#notify_switches DistributedVirtualSwitch#notify_switches}
        :param port_private_secondary_vlan_id: The secondary VLAN ID for this port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#port_private_secondary_vlan_id DistributedVirtualSwitch#port_private_secondary_vlan_id}
        :param pvlan_mapping: pvlan_mapping block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#pvlan_mapping DistributedVirtualSwitch#pvlan_mapping}
        :param standby_uplinks: List of standby uplinks used for load balancing, matching the names of the uplinks assigned in the DVS. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#standby_uplinks DistributedVirtualSwitch#standby_uplinks}
        :param tags: A list of tag IDs to apply to this object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#tags DistributedVirtualSwitch#tags}
        :param teaming_policy: The network adapter teaming policy. Can be one of loadbalance_ip, loadbalance_srcmac, loadbalance_srcid, failover_explicit, or loadbalance_loadbased. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#teaming_policy DistributedVirtualSwitch#teaming_policy}
        :param tx_uplink: If true, a copy of packets sent to the switch will always be forwarded to an uplink in addition to the regular packet forwarded done by the switch. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#tx_uplink DistributedVirtualSwitch#tx_uplink}
        :param uplinks: A list of uplink ports. The contents of this list control both the uplink count and names of the uplinks on the DVS across hosts. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#uplinks DistributedVirtualSwitch#uplinks}
        :param vdp_maximum_mbit: The maximum allowed usage for the vdp traffic class, in Mbits/sec. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#vdp_maximum_mbit DistributedVirtualSwitch#vdp_maximum_mbit}
        :param vdp_reservation_mbit: The amount of guaranteed bandwidth for the vdp traffic class, in Mbits/sec. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#vdp_reservation_mbit DistributedVirtualSwitch#vdp_reservation_mbit}
        :param vdp_share_count: The amount of shares to allocate to the vdp traffic class for a custom share level. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#vdp_share_count DistributedVirtualSwitch#vdp_share_count}
        :param vdp_share_level: The allocation level for the vdp traffic class. Can be one of high, low, normal, or custom. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#vdp_share_level DistributedVirtualSwitch#vdp_share_level}
        :param version: The version of this virtual switch. Allowed versions are 8.0.3, 8.0.0, 7.0.3, 7.0.2, 7.0.0, 6.6.0, 6.5.0, 6.0.0, 5.5.0, 5.1.0, and 5.0.0. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#version DistributedVirtualSwitch#version}
        :param virtualmachine_maximum_mbit: The maximum allowed usage for the virtualMachine traffic class, in Mbits/sec. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#virtualmachine_maximum_mbit DistributedVirtualSwitch#virtualmachine_maximum_mbit}
        :param virtualmachine_reservation_mbit: The amount of guaranteed bandwidth for the virtualMachine traffic class, in Mbits/sec. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#virtualmachine_reservation_mbit DistributedVirtualSwitch#virtualmachine_reservation_mbit}
        :param virtualmachine_share_count: The amount of shares to allocate to the virtualMachine traffic class for a custom share level. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#virtualmachine_share_count DistributedVirtualSwitch#virtualmachine_share_count}
        :param virtualmachine_share_level: The allocation level for the virtualMachine traffic class. Can be one of high, low, normal, or custom. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#virtualmachine_share_level DistributedVirtualSwitch#virtualmachine_share_level}
        :param vlan_id: The VLAN ID for single VLAN mode. 0 denotes no VLAN. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#vlan_id DistributedVirtualSwitch#vlan_id}
        :param vlan_range: vlan_range block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#vlan_range DistributedVirtualSwitch#vlan_range}
        :param vmotion_maximum_mbit: The maximum allowed usage for the vmotion traffic class, in Mbits/sec. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#vmotion_maximum_mbit DistributedVirtualSwitch#vmotion_maximum_mbit}
        :param vmotion_reservation_mbit: The amount of guaranteed bandwidth for the vmotion traffic class, in Mbits/sec. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#vmotion_reservation_mbit DistributedVirtualSwitch#vmotion_reservation_mbit}
        :param vmotion_share_count: The amount of shares to allocate to the vmotion traffic class for a custom share level. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#vmotion_share_count DistributedVirtualSwitch#vmotion_share_count}
        :param vmotion_share_level: The allocation level for the vmotion traffic class. Can be one of high, low, normal, or custom. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#vmotion_share_level DistributedVirtualSwitch#vmotion_share_level}
        :param vsan_maximum_mbit: The maximum allowed usage for the vsan traffic class, in Mbits/sec. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#vsan_maximum_mbit DistributedVirtualSwitch#vsan_maximum_mbit}
        :param vsan_reservation_mbit: The amount of guaranteed bandwidth for the vsan traffic class, in Mbits/sec. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#vsan_reservation_mbit DistributedVirtualSwitch#vsan_reservation_mbit}
        :param vsan_share_count: The amount of shares to allocate to the vsan traffic class for a custom share level. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#vsan_share_count DistributedVirtualSwitch#vsan_share_count}
        :param vsan_share_level: The allocation level for the vsan traffic class. Can be one of high, low, normal, or custom. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#vsan_share_level DistributedVirtualSwitch#vsan_share_level}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d221cf0e7e0221e763389d961f3179ab704d1265320c36c1cb0672ee983c2da3)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument datacenter_id", value=datacenter_id, expected_type=type_hints["datacenter_id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument active_uplinks", value=active_uplinks, expected_type=type_hints["active_uplinks"])
            check_type(argname="argument allow_forged_transmits", value=allow_forged_transmits, expected_type=type_hints["allow_forged_transmits"])
            check_type(argname="argument allow_mac_changes", value=allow_mac_changes, expected_type=type_hints["allow_mac_changes"])
            check_type(argname="argument allow_promiscuous", value=allow_promiscuous, expected_type=type_hints["allow_promiscuous"])
            check_type(argname="argument backupnfc_maximum_mbit", value=backupnfc_maximum_mbit, expected_type=type_hints["backupnfc_maximum_mbit"])
            check_type(argname="argument backupnfc_reservation_mbit", value=backupnfc_reservation_mbit, expected_type=type_hints["backupnfc_reservation_mbit"])
            check_type(argname="argument backupnfc_share_count", value=backupnfc_share_count, expected_type=type_hints["backupnfc_share_count"])
            check_type(argname="argument backupnfc_share_level", value=backupnfc_share_level, expected_type=type_hints["backupnfc_share_level"])
            check_type(argname="argument block_all_ports", value=block_all_ports, expected_type=type_hints["block_all_ports"])
            check_type(argname="argument check_beacon", value=check_beacon, expected_type=type_hints["check_beacon"])
            check_type(argname="argument contact_detail", value=contact_detail, expected_type=type_hints["contact_detail"])
            check_type(argname="argument contact_name", value=contact_name, expected_type=type_hints["contact_name"])
            check_type(argname="argument custom_attributes", value=custom_attributes, expected_type=type_hints["custom_attributes"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument directpath_gen2_allowed", value=directpath_gen2_allowed, expected_type=type_hints["directpath_gen2_allowed"])
            check_type(argname="argument egress_shaping_average_bandwidth", value=egress_shaping_average_bandwidth, expected_type=type_hints["egress_shaping_average_bandwidth"])
            check_type(argname="argument egress_shaping_burst_size", value=egress_shaping_burst_size, expected_type=type_hints["egress_shaping_burst_size"])
            check_type(argname="argument egress_shaping_enabled", value=egress_shaping_enabled, expected_type=type_hints["egress_shaping_enabled"])
            check_type(argname="argument egress_shaping_peak_bandwidth", value=egress_shaping_peak_bandwidth, expected_type=type_hints["egress_shaping_peak_bandwidth"])
            check_type(argname="argument failback", value=failback, expected_type=type_hints["failback"])
            check_type(argname="argument faulttolerance_maximum_mbit", value=faulttolerance_maximum_mbit, expected_type=type_hints["faulttolerance_maximum_mbit"])
            check_type(argname="argument faulttolerance_reservation_mbit", value=faulttolerance_reservation_mbit, expected_type=type_hints["faulttolerance_reservation_mbit"])
            check_type(argname="argument faulttolerance_share_count", value=faulttolerance_share_count, expected_type=type_hints["faulttolerance_share_count"])
            check_type(argname="argument faulttolerance_share_level", value=faulttolerance_share_level, expected_type=type_hints["faulttolerance_share_level"])
            check_type(argname="argument folder", value=folder, expected_type=type_hints["folder"])
            check_type(argname="argument hbr_maximum_mbit", value=hbr_maximum_mbit, expected_type=type_hints["hbr_maximum_mbit"])
            check_type(argname="argument hbr_reservation_mbit", value=hbr_reservation_mbit, expected_type=type_hints["hbr_reservation_mbit"])
            check_type(argname="argument hbr_share_count", value=hbr_share_count, expected_type=type_hints["hbr_share_count"])
            check_type(argname="argument hbr_share_level", value=hbr_share_level, expected_type=type_hints["hbr_share_level"])
            check_type(argname="argument host", value=host, expected_type=type_hints["host"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument ignore_other_pvlan_mappings", value=ignore_other_pvlan_mappings, expected_type=type_hints["ignore_other_pvlan_mappings"])
            check_type(argname="argument ingress_shaping_average_bandwidth", value=ingress_shaping_average_bandwidth, expected_type=type_hints["ingress_shaping_average_bandwidth"])
            check_type(argname="argument ingress_shaping_burst_size", value=ingress_shaping_burst_size, expected_type=type_hints["ingress_shaping_burst_size"])
            check_type(argname="argument ingress_shaping_enabled", value=ingress_shaping_enabled, expected_type=type_hints["ingress_shaping_enabled"])
            check_type(argname="argument ingress_shaping_peak_bandwidth", value=ingress_shaping_peak_bandwidth, expected_type=type_hints["ingress_shaping_peak_bandwidth"])
            check_type(argname="argument ipv4_address", value=ipv4_address, expected_type=type_hints["ipv4_address"])
            check_type(argname="argument iscsi_maximum_mbit", value=iscsi_maximum_mbit, expected_type=type_hints["iscsi_maximum_mbit"])
            check_type(argname="argument iscsi_reservation_mbit", value=iscsi_reservation_mbit, expected_type=type_hints["iscsi_reservation_mbit"])
            check_type(argname="argument iscsi_share_count", value=iscsi_share_count, expected_type=type_hints["iscsi_share_count"])
            check_type(argname="argument iscsi_share_level", value=iscsi_share_level, expected_type=type_hints["iscsi_share_level"])
            check_type(argname="argument lacp_api_version", value=lacp_api_version, expected_type=type_hints["lacp_api_version"])
            check_type(argname="argument lacp_enabled", value=lacp_enabled, expected_type=type_hints["lacp_enabled"])
            check_type(argname="argument lacp_mode", value=lacp_mode, expected_type=type_hints["lacp_mode"])
            check_type(argname="argument link_discovery_operation", value=link_discovery_operation, expected_type=type_hints["link_discovery_operation"])
            check_type(argname="argument link_discovery_protocol", value=link_discovery_protocol, expected_type=type_hints["link_discovery_protocol"])
            check_type(argname="argument management_maximum_mbit", value=management_maximum_mbit, expected_type=type_hints["management_maximum_mbit"])
            check_type(argname="argument management_reservation_mbit", value=management_reservation_mbit, expected_type=type_hints["management_reservation_mbit"])
            check_type(argname="argument management_share_count", value=management_share_count, expected_type=type_hints["management_share_count"])
            check_type(argname="argument management_share_level", value=management_share_level, expected_type=type_hints["management_share_level"])
            check_type(argname="argument max_mtu", value=max_mtu, expected_type=type_hints["max_mtu"])
            check_type(argname="argument multicast_filtering_mode", value=multicast_filtering_mode, expected_type=type_hints["multicast_filtering_mode"])
            check_type(argname="argument netflow_active_flow_timeout", value=netflow_active_flow_timeout, expected_type=type_hints["netflow_active_flow_timeout"])
            check_type(argname="argument netflow_collector_ip_address", value=netflow_collector_ip_address, expected_type=type_hints["netflow_collector_ip_address"])
            check_type(argname="argument netflow_collector_port", value=netflow_collector_port, expected_type=type_hints["netflow_collector_port"])
            check_type(argname="argument netflow_enabled", value=netflow_enabled, expected_type=type_hints["netflow_enabled"])
            check_type(argname="argument netflow_idle_flow_timeout", value=netflow_idle_flow_timeout, expected_type=type_hints["netflow_idle_flow_timeout"])
            check_type(argname="argument netflow_internal_flows_only", value=netflow_internal_flows_only, expected_type=type_hints["netflow_internal_flows_only"])
            check_type(argname="argument netflow_observation_domain_id", value=netflow_observation_domain_id, expected_type=type_hints["netflow_observation_domain_id"])
            check_type(argname="argument netflow_sampling_rate", value=netflow_sampling_rate, expected_type=type_hints["netflow_sampling_rate"])
            check_type(argname="argument network_resource_control_enabled", value=network_resource_control_enabled, expected_type=type_hints["network_resource_control_enabled"])
            check_type(argname="argument network_resource_control_version", value=network_resource_control_version, expected_type=type_hints["network_resource_control_version"])
            check_type(argname="argument nfs_maximum_mbit", value=nfs_maximum_mbit, expected_type=type_hints["nfs_maximum_mbit"])
            check_type(argname="argument nfs_reservation_mbit", value=nfs_reservation_mbit, expected_type=type_hints["nfs_reservation_mbit"])
            check_type(argname="argument nfs_share_count", value=nfs_share_count, expected_type=type_hints["nfs_share_count"])
            check_type(argname="argument nfs_share_level", value=nfs_share_level, expected_type=type_hints["nfs_share_level"])
            check_type(argname="argument notify_switches", value=notify_switches, expected_type=type_hints["notify_switches"])
            check_type(argname="argument port_private_secondary_vlan_id", value=port_private_secondary_vlan_id, expected_type=type_hints["port_private_secondary_vlan_id"])
            check_type(argname="argument pvlan_mapping", value=pvlan_mapping, expected_type=type_hints["pvlan_mapping"])
            check_type(argname="argument standby_uplinks", value=standby_uplinks, expected_type=type_hints["standby_uplinks"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument teaming_policy", value=teaming_policy, expected_type=type_hints["teaming_policy"])
            check_type(argname="argument tx_uplink", value=tx_uplink, expected_type=type_hints["tx_uplink"])
            check_type(argname="argument uplinks", value=uplinks, expected_type=type_hints["uplinks"])
            check_type(argname="argument vdp_maximum_mbit", value=vdp_maximum_mbit, expected_type=type_hints["vdp_maximum_mbit"])
            check_type(argname="argument vdp_reservation_mbit", value=vdp_reservation_mbit, expected_type=type_hints["vdp_reservation_mbit"])
            check_type(argname="argument vdp_share_count", value=vdp_share_count, expected_type=type_hints["vdp_share_count"])
            check_type(argname="argument vdp_share_level", value=vdp_share_level, expected_type=type_hints["vdp_share_level"])
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
            check_type(argname="argument virtualmachine_maximum_mbit", value=virtualmachine_maximum_mbit, expected_type=type_hints["virtualmachine_maximum_mbit"])
            check_type(argname="argument virtualmachine_reservation_mbit", value=virtualmachine_reservation_mbit, expected_type=type_hints["virtualmachine_reservation_mbit"])
            check_type(argname="argument virtualmachine_share_count", value=virtualmachine_share_count, expected_type=type_hints["virtualmachine_share_count"])
            check_type(argname="argument virtualmachine_share_level", value=virtualmachine_share_level, expected_type=type_hints["virtualmachine_share_level"])
            check_type(argname="argument vlan_id", value=vlan_id, expected_type=type_hints["vlan_id"])
            check_type(argname="argument vlan_range", value=vlan_range, expected_type=type_hints["vlan_range"])
            check_type(argname="argument vmotion_maximum_mbit", value=vmotion_maximum_mbit, expected_type=type_hints["vmotion_maximum_mbit"])
            check_type(argname="argument vmotion_reservation_mbit", value=vmotion_reservation_mbit, expected_type=type_hints["vmotion_reservation_mbit"])
            check_type(argname="argument vmotion_share_count", value=vmotion_share_count, expected_type=type_hints["vmotion_share_count"])
            check_type(argname="argument vmotion_share_level", value=vmotion_share_level, expected_type=type_hints["vmotion_share_level"])
            check_type(argname="argument vsan_maximum_mbit", value=vsan_maximum_mbit, expected_type=type_hints["vsan_maximum_mbit"])
            check_type(argname="argument vsan_reservation_mbit", value=vsan_reservation_mbit, expected_type=type_hints["vsan_reservation_mbit"])
            check_type(argname="argument vsan_share_count", value=vsan_share_count, expected_type=type_hints["vsan_share_count"])
            check_type(argname="argument vsan_share_level", value=vsan_share_level, expected_type=type_hints["vsan_share_level"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "datacenter_id": datacenter_id,
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
        if backupnfc_maximum_mbit is not None:
            self._values["backupnfc_maximum_mbit"] = backupnfc_maximum_mbit
        if backupnfc_reservation_mbit is not None:
            self._values["backupnfc_reservation_mbit"] = backupnfc_reservation_mbit
        if backupnfc_share_count is not None:
            self._values["backupnfc_share_count"] = backupnfc_share_count
        if backupnfc_share_level is not None:
            self._values["backupnfc_share_level"] = backupnfc_share_level
        if block_all_ports is not None:
            self._values["block_all_ports"] = block_all_ports
        if check_beacon is not None:
            self._values["check_beacon"] = check_beacon
        if contact_detail is not None:
            self._values["contact_detail"] = contact_detail
        if contact_name is not None:
            self._values["contact_name"] = contact_name
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
        if faulttolerance_maximum_mbit is not None:
            self._values["faulttolerance_maximum_mbit"] = faulttolerance_maximum_mbit
        if faulttolerance_reservation_mbit is not None:
            self._values["faulttolerance_reservation_mbit"] = faulttolerance_reservation_mbit
        if faulttolerance_share_count is not None:
            self._values["faulttolerance_share_count"] = faulttolerance_share_count
        if faulttolerance_share_level is not None:
            self._values["faulttolerance_share_level"] = faulttolerance_share_level
        if folder is not None:
            self._values["folder"] = folder
        if hbr_maximum_mbit is not None:
            self._values["hbr_maximum_mbit"] = hbr_maximum_mbit
        if hbr_reservation_mbit is not None:
            self._values["hbr_reservation_mbit"] = hbr_reservation_mbit
        if hbr_share_count is not None:
            self._values["hbr_share_count"] = hbr_share_count
        if hbr_share_level is not None:
            self._values["hbr_share_level"] = hbr_share_level
        if host is not None:
            self._values["host"] = host
        if id is not None:
            self._values["id"] = id
        if ignore_other_pvlan_mappings is not None:
            self._values["ignore_other_pvlan_mappings"] = ignore_other_pvlan_mappings
        if ingress_shaping_average_bandwidth is not None:
            self._values["ingress_shaping_average_bandwidth"] = ingress_shaping_average_bandwidth
        if ingress_shaping_burst_size is not None:
            self._values["ingress_shaping_burst_size"] = ingress_shaping_burst_size
        if ingress_shaping_enabled is not None:
            self._values["ingress_shaping_enabled"] = ingress_shaping_enabled
        if ingress_shaping_peak_bandwidth is not None:
            self._values["ingress_shaping_peak_bandwidth"] = ingress_shaping_peak_bandwidth
        if ipv4_address is not None:
            self._values["ipv4_address"] = ipv4_address
        if iscsi_maximum_mbit is not None:
            self._values["iscsi_maximum_mbit"] = iscsi_maximum_mbit
        if iscsi_reservation_mbit is not None:
            self._values["iscsi_reservation_mbit"] = iscsi_reservation_mbit
        if iscsi_share_count is not None:
            self._values["iscsi_share_count"] = iscsi_share_count
        if iscsi_share_level is not None:
            self._values["iscsi_share_level"] = iscsi_share_level
        if lacp_api_version is not None:
            self._values["lacp_api_version"] = lacp_api_version
        if lacp_enabled is not None:
            self._values["lacp_enabled"] = lacp_enabled
        if lacp_mode is not None:
            self._values["lacp_mode"] = lacp_mode
        if link_discovery_operation is not None:
            self._values["link_discovery_operation"] = link_discovery_operation
        if link_discovery_protocol is not None:
            self._values["link_discovery_protocol"] = link_discovery_protocol
        if management_maximum_mbit is not None:
            self._values["management_maximum_mbit"] = management_maximum_mbit
        if management_reservation_mbit is not None:
            self._values["management_reservation_mbit"] = management_reservation_mbit
        if management_share_count is not None:
            self._values["management_share_count"] = management_share_count
        if management_share_level is not None:
            self._values["management_share_level"] = management_share_level
        if max_mtu is not None:
            self._values["max_mtu"] = max_mtu
        if multicast_filtering_mode is not None:
            self._values["multicast_filtering_mode"] = multicast_filtering_mode
        if netflow_active_flow_timeout is not None:
            self._values["netflow_active_flow_timeout"] = netflow_active_flow_timeout
        if netflow_collector_ip_address is not None:
            self._values["netflow_collector_ip_address"] = netflow_collector_ip_address
        if netflow_collector_port is not None:
            self._values["netflow_collector_port"] = netflow_collector_port
        if netflow_enabled is not None:
            self._values["netflow_enabled"] = netflow_enabled
        if netflow_idle_flow_timeout is not None:
            self._values["netflow_idle_flow_timeout"] = netflow_idle_flow_timeout
        if netflow_internal_flows_only is not None:
            self._values["netflow_internal_flows_only"] = netflow_internal_flows_only
        if netflow_observation_domain_id is not None:
            self._values["netflow_observation_domain_id"] = netflow_observation_domain_id
        if netflow_sampling_rate is not None:
            self._values["netflow_sampling_rate"] = netflow_sampling_rate
        if network_resource_control_enabled is not None:
            self._values["network_resource_control_enabled"] = network_resource_control_enabled
        if network_resource_control_version is not None:
            self._values["network_resource_control_version"] = network_resource_control_version
        if nfs_maximum_mbit is not None:
            self._values["nfs_maximum_mbit"] = nfs_maximum_mbit
        if nfs_reservation_mbit is not None:
            self._values["nfs_reservation_mbit"] = nfs_reservation_mbit
        if nfs_share_count is not None:
            self._values["nfs_share_count"] = nfs_share_count
        if nfs_share_level is not None:
            self._values["nfs_share_level"] = nfs_share_level
        if notify_switches is not None:
            self._values["notify_switches"] = notify_switches
        if port_private_secondary_vlan_id is not None:
            self._values["port_private_secondary_vlan_id"] = port_private_secondary_vlan_id
        if pvlan_mapping is not None:
            self._values["pvlan_mapping"] = pvlan_mapping
        if standby_uplinks is not None:
            self._values["standby_uplinks"] = standby_uplinks
        if tags is not None:
            self._values["tags"] = tags
        if teaming_policy is not None:
            self._values["teaming_policy"] = teaming_policy
        if tx_uplink is not None:
            self._values["tx_uplink"] = tx_uplink
        if uplinks is not None:
            self._values["uplinks"] = uplinks
        if vdp_maximum_mbit is not None:
            self._values["vdp_maximum_mbit"] = vdp_maximum_mbit
        if vdp_reservation_mbit is not None:
            self._values["vdp_reservation_mbit"] = vdp_reservation_mbit
        if vdp_share_count is not None:
            self._values["vdp_share_count"] = vdp_share_count
        if vdp_share_level is not None:
            self._values["vdp_share_level"] = vdp_share_level
        if version is not None:
            self._values["version"] = version
        if virtualmachine_maximum_mbit is not None:
            self._values["virtualmachine_maximum_mbit"] = virtualmachine_maximum_mbit
        if virtualmachine_reservation_mbit is not None:
            self._values["virtualmachine_reservation_mbit"] = virtualmachine_reservation_mbit
        if virtualmachine_share_count is not None:
            self._values["virtualmachine_share_count"] = virtualmachine_share_count
        if virtualmachine_share_level is not None:
            self._values["virtualmachine_share_level"] = virtualmachine_share_level
        if vlan_id is not None:
            self._values["vlan_id"] = vlan_id
        if vlan_range is not None:
            self._values["vlan_range"] = vlan_range
        if vmotion_maximum_mbit is not None:
            self._values["vmotion_maximum_mbit"] = vmotion_maximum_mbit
        if vmotion_reservation_mbit is not None:
            self._values["vmotion_reservation_mbit"] = vmotion_reservation_mbit
        if vmotion_share_count is not None:
            self._values["vmotion_share_count"] = vmotion_share_count
        if vmotion_share_level is not None:
            self._values["vmotion_share_level"] = vmotion_share_level
        if vsan_maximum_mbit is not None:
            self._values["vsan_maximum_mbit"] = vsan_maximum_mbit
        if vsan_reservation_mbit is not None:
            self._values["vsan_reservation_mbit"] = vsan_reservation_mbit
        if vsan_share_count is not None:
            self._values["vsan_share_count"] = vsan_share_count
        if vsan_share_level is not None:
            self._values["vsan_share_level"] = vsan_share_level

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
    def datacenter_id(self) -> builtins.str:
        '''The ID of the datacenter to create this virtual switch in.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#datacenter_id DistributedVirtualSwitch#datacenter_id}
        '''
        result = self._values.get("datacenter_id")
        assert result is not None, "Required property 'datacenter_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name for the DVS. Must be unique in the folder that it is being created in.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#name DistributedVirtualSwitch#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def active_uplinks(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of active uplinks used for load balancing, matching the names of the uplinks assigned in the DVS.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#active_uplinks DistributedVirtualSwitch#active_uplinks}
        '''
        result = self._values.get("active_uplinks")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def allow_forged_transmits(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Controls whether or not the virtual network adapter is allowed to send network traffic with a different MAC address than that of its own.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#allow_forged_transmits DistributedVirtualSwitch#allow_forged_transmits}
        '''
        result = self._values.get("allow_forged_transmits")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def allow_mac_changes(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Controls whether or not the Media Access Control (MAC) address can be changed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#allow_mac_changes DistributedVirtualSwitch#allow_mac_changes}
        '''
        result = self._values.get("allow_mac_changes")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def allow_promiscuous(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable promiscuous mode on the network.

        This flag indicates whether or not all traffic is seen on a given port.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#allow_promiscuous DistributedVirtualSwitch#allow_promiscuous}
        '''
        result = self._values.get("allow_promiscuous")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def backupnfc_maximum_mbit(self) -> typing.Optional[jsii.Number]:
        '''The maximum allowed usage for the backupNfc traffic class, in Mbits/sec.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#backupnfc_maximum_mbit DistributedVirtualSwitch#backupnfc_maximum_mbit}
        '''
        result = self._values.get("backupnfc_maximum_mbit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def backupnfc_reservation_mbit(self) -> typing.Optional[jsii.Number]:
        '''The amount of guaranteed bandwidth for the backupNfc traffic class, in Mbits/sec.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#backupnfc_reservation_mbit DistributedVirtualSwitch#backupnfc_reservation_mbit}
        '''
        result = self._values.get("backupnfc_reservation_mbit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def backupnfc_share_count(self) -> typing.Optional[jsii.Number]:
        '''The amount of shares to allocate to the backupNfc traffic class for a custom share level.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#backupnfc_share_count DistributedVirtualSwitch#backupnfc_share_count}
        '''
        result = self._values.get("backupnfc_share_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def backupnfc_share_level(self) -> typing.Optional[builtins.str]:
        '''The allocation level for the backupNfc traffic class. Can be one of high, low, normal, or custom.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#backupnfc_share_level DistributedVirtualSwitch#backupnfc_share_level}
        '''
        result = self._values.get("backupnfc_share_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def block_all_ports(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Indicates whether to block all ports by default.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#block_all_ports DistributedVirtualSwitch#block_all_ports}
        '''
        result = self._values.get("block_all_ports")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def check_beacon(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable beacon probing on the ports this policy applies to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#check_beacon DistributedVirtualSwitch#check_beacon}
        '''
        result = self._values.get("check_beacon")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def contact_detail(self) -> typing.Optional[builtins.str]:
        '''The contact detail for this DVS.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#contact_detail DistributedVirtualSwitch#contact_detail}
        '''
        result = self._values.get("contact_detail")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def contact_name(self) -> typing.Optional[builtins.str]:
        '''The contact name for this DVS.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#contact_name DistributedVirtualSwitch#contact_name}
        '''
        result = self._values.get("contact_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_attributes(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''A list of custom attributes to set on this resource.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#custom_attributes DistributedVirtualSwitch#custom_attributes}
        '''
        result = self._values.get("custom_attributes")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The description of the DVS.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#description DistributedVirtualSwitch#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def directpath_gen2_allowed(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Allow VMDirectPath Gen2 on the ports this policy applies to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#directpath_gen2_allowed DistributedVirtualSwitch#directpath_gen2_allowed}
        '''
        result = self._values.get("directpath_gen2_allowed")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def egress_shaping_average_bandwidth(self) -> typing.Optional[jsii.Number]:
        '''The average egress bandwidth in bits per second if egress shaping is enabled on the port.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#egress_shaping_average_bandwidth DistributedVirtualSwitch#egress_shaping_average_bandwidth}
        '''
        result = self._values.get("egress_shaping_average_bandwidth")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def egress_shaping_burst_size(self) -> typing.Optional[jsii.Number]:
        '''The maximum egress burst size allowed in bytes if egress shaping is enabled on the port.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#egress_shaping_burst_size DistributedVirtualSwitch#egress_shaping_burst_size}
        '''
        result = self._values.get("egress_shaping_burst_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def egress_shaping_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''True if the traffic shaper is enabled for egress traffic on the port.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#egress_shaping_enabled DistributedVirtualSwitch#egress_shaping_enabled}
        '''
        result = self._values.get("egress_shaping_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def egress_shaping_peak_bandwidth(self) -> typing.Optional[jsii.Number]:
        '''The peak egress bandwidth during bursts in bits per second if egress traffic shaping is enabled on the port.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#egress_shaping_peak_bandwidth DistributedVirtualSwitch#egress_shaping_peak_bandwidth}
        '''
        result = self._values.get("egress_shaping_peak_bandwidth")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def failback(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If true, the teaming policy will re-activate failed interfaces higher in precedence when they come back up.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#failback DistributedVirtualSwitch#failback}
        '''
        result = self._values.get("failback")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def faulttolerance_maximum_mbit(self) -> typing.Optional[jsii.Number]:
        '''The maximum allowed usage for the faultTolerance traffic class, in Mbits/sec.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#faulttolerance_maximum_mbit DistributedVirtualSwitch#faulttolerance_maximum_mbit}
        '''
        result = self._values.get("faulttolerance_maximum_mbit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def faulttolerance_reservation_mbit(self) -> typing.Optional[jsii.Number]:
        '''The amount of guaranteed bandwidth for the faultTolerance traffic class, in Mbits/sec.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#faulttolerance_reservation_mbit DistributedVirtualSwitch#faulttolerance_reservation_mbit}
        '''
        result = self._values.get("faulttolerance_reservation_mbit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def faulttolerance_share_count(self) -> typing.Optional[jsii.Number]:
        '''The amount of shares to allocate to the faultTolerance traffic class for a custom share level.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#faulttolerance_share_count DistributedVirtualSwitch#faulttolerance_share_count}
        '''
        result = self._values.get("faulttolerance_share_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def faulttolerance_share_level(self) -> typing.Optional[builtins.str]:
        '''The allocation level for the faultTolerance traffic class. Can be one of high, low, normal, or custom.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#faulttolerance_share_level DistributedVirtualSwitch#faulttolerance_share_level}
        '''
        result = self._values.get("faulttolerance_share_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def folder(self) -> typing.Optional[builtins.str]:
        '''The folder to create this virtual switch in, relative to the datacenter.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#folder DistributedVirtualSwitch#folder}
        '''
        result = self._values.get("folder")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def hbr_maximum_mbit(self) -> typing.Optional[jsii.Number]:
        '''The maximum allowed usage for the hbr traffic class, in Mbits/sec.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#hbr_maximum_mbit DistributedVirtualSwitch#hbr_maximum_mbit}
        '''
        result = self._values.get("hbr_maximum_mbit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def hbr_reservation_mbit(self) -> typing.Optional[jsii.Number]:
        '''The amount of guaranteed bandwidth for the hbr traffic class, in Mbits/sec.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#hbr_reservation_mbit DistributedVirtualSwitch#hbr_reservation_mbit}
        '''
        result = self._values.get("hbr_reservation_mbit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def hbr_share_count(self) -> typing.Optional[jsii.Number]:
        '''The amount of shares to allocate to the hbr traffic class for a custom share level.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#hbr_share_count DistributedVirtualSwitch#hbr_share_count}
        '''
        result = self._values.get("hbr_share_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def hbr_share_level(self) -> typing.Optional[builtins.str]:
        '''The allocation level for the hbr traffic class. Can be one of high, low, normal, or custom.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#hbr_share_level DistributedVirtualSwitch#hbr_share_level}
        '''
        result = self._values.get("hbr_share_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def host(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DistributedVirtualSwitchHost"]]]:
        '''host block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#host DistributedVirtualSwitch#host}
        '''
        result = self._values.get("host")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DistributedVirtualSwitchHost"]]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#id DistributedVirtualSwitch#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ignore_other_pvlan_mappings(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether to ignore existing PVLAN mappings not managed by this resource.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#ignore_other_pvlan_mappings DistributedVirtualSwitch#ignore_other_pvlan_mappings}
        '''
        result = self._values.get("ignore_other_pvlan_mappings")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def ingress_shaping_average_bandwidth(self) -> typing.Optional[jsii.Number]:
        '''The average ingress bandwidth in bits per second if ingress shaping is enabled on the port.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#ingress_shaping_average_bandwidth DistributedVirtualSwitch#ingress_shaping_average_bandwidth}
        '''
        result = self._values.get("ingress_shaping_average_bandwidth")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ingress_shaping_burst_size(self) -> typing.Optional[jsii.Number]:
        '''The maximum ingress burst size allowed in bytes if ingress shaping is enabled on the port.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#ingress_shaping_burst_size DistributedVirtualSwitch#ingress_shaping_burst_size}
        '''
        result = self._values.get("ingress_shaping_burst_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ingress_shaping_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''True if the traffic shaper is enabled for ingress traffic on the port.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#ingress_shaping_enabled DistributedVirtualSwitch#ingress_shaping_enabled}
        '''
        result = self._values.get("ingress_shaping_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def ingress_shaping_peak_bandwidth(self) -> typing.Optional[jsii.Number]:
        '''The peak ingress bandwidth during bursts in bits per second if ingress traffic shaping is enabled on the port.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#ingress_shaping_peak_bandwidth DistributedVirtualSwitch#ingress_shaping_peak_bandwidth}
        '''
        result = self._values.get("ingress_shaping_peak_bandwidth")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ipv4_address(self) -> typing.Optional[builtins.str]:
        '''The IPv4 address of the switch.

        This can be used to see the DVS as a unique device with NetFlow.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#ipv4_address DistributedVirtualSwitch#ipv4_address}
        '''
        result = self._values.get("ipv4_address")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def iscsi_maximum_mbit(self) -> typing.Optional[jsii.Number]:
        '''The maximum allowed usage for the iSCSI traffic class, in Mbits/sec.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#iscsi_maximum_mbit DistributedVirtualSwitch#iscsi_maximum_mbit}
        '''
        result = self._values.get("iscsi_maximum_mbit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def iscsi_reservation_mbit(self) -> typing.Optional[jsii.Number]:
        '''The amount of guaranteed bandwidth for the iSCSI traffic class, in Mbits/sec.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#iscsi_reservation_mbit DistributedVirtualSwitch#iscsi_reservation_mbit}
        '''
        result = self._values.get("iscsi_reservation_mbit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def iscsi_share_count(self) -> typing.Optional[jsii.Number]:
        '''The amount of shares to allocate to the iSCSI traffic class for a custom share level.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#iscsi_share_count DistributedVirtualSwitch#iscsi_share_count}
        '''
        result = self._values.get("iscsi_share_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def iscsi_share_level(self) -> typing.Optional[builtins.str]:
        '''The allocation level for the iSCSI traffic class. Can be one of high, low, normal, or custom.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#iscsi_share_level DistributedVirtualSwitch#iscsi_share_level}
        '''
        result = self._values.get("iscsi_share_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lacp_api_version(self) -> typing.Optional[builtins.str]:
        '''The Link Aggregation Control Protocol group version in the switch. Can be one of singleLag or multipleLag.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#lacp_api_version DistributedVirtualSwitch#lacp_api_version}
        '''
        result = self._values.get("lacp_api_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lacp_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether or not to enable LACP on all uplink ports.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#lacp_enabled DistributedVirtualSwitch#lacp_enabled}
        '''
        result = self._values.get("lacp_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def lacp_mode(self) -> typing.Optional[builtins.str]:
        '''The uplink LACP mode to use. Can be one of active or passive.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#lacp_mode DistributedVirtualSwitch#lacp_mode}
        '''
        result = self._values.get("lacp_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def link_discovery_operation(self) -> typing.Optional[builtins.str]:
        '''Whether to advertise or listen for link discovery. Valid values are advertise, both, listen, and none.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#link_discovery_operation DistributedVirtualSwitch#link_discovery_operation}
        '''
        result = self._values.get("link_discovery_operation")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def link_discovery_protocol(self) -> typing.Optional[builtins.str]:
        '''The discovery protocol type. Valid values are cdp and lldp.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#link_discovery_protocol DistributedVirtualSwitch#link_discovery_protocol}
        '''
        result = self._values.get("link_discovery_protocol")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def management_maximum_mbit(self) -> typing.Optional[jsii.Number]:
        '''The maximum allowed usage for the management traffic class, in Mbits/sec.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#management_maximum_mbit DistributedVirtualSwitch#management_maximum_mbit}
        '''
        result = self._values.get("management_maximum_mbit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def management_reservation_mbit(self) -> typing.Optional[jsii.Number]:
        '''The amount of guaranteed bandwidth for the management traffic class, in Mbits/sec.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#management_reservation_mbit DistributedVirtualSwitch#management_reservation_mbit}
        '''
        result = self._values.get("management_reservation_mbit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def management_share_count(self) -> typing.Optional[jsii.Number]:
        '''The amount of shares to allocate to the management traffic class for a custom share level.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#management_share_count DistributedVirtualSwitch#management_share_count}
        '''
        result = self._values.get("management_share_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def management_share_level(self) -> typing.Optional[builtins.str]:
        '''The allocation level for the management traffic class. Can be one of high, low, normal, or custom.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#management_share_level DistributedVirtualSwitch#management_share_level}
        '''
        result = self._values.get("management_share_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_mtu(self) -> typing.Optional[jsii.Number]:
        '''The maximum MTU on the switch.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#max_mtu DistributedVirtualSwitch#max_mtu}
        '''
        result = self._values.get("max_mtu")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def multicast_filtering_mode(self) -> typing.Optional[builtins.str]:
        '''The multicast filtering mode on the switch. Can be one of legacyFiltering, or snooping.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#multicast_filtering_mode DistributedVirtualSwitch#multicast_filtering_mode}
        '''
        result = self._values.get("multicast_filtering_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def netflow_active_flow_timeout(self) -> typing.Optional[jsii.Number]:
        '''The number of seconds after which active flows are forced to be exported to the collector.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#netflow_active_flow_timeout DistributedVirtualSwitch#netflow_active_flow_timeout}
        '''
        result = self._values.get("netflow_active_flow_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def netflow_collector_ip_address(self) -> typing.Optional[builtins.str]:
        '''IP address for the netflow collector, using IPv4 or IPv6.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#netflow_collector_ip_address DistributedVirtualSwitch#netflow_collector_ip_address}
        '''
        result = self._values.get("netflow_collector_ip_address")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def netflow_collector_port(self) -> typing.Optional[jsii.Number]:
        '''The port for the netflow collector.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#netflow_collector_port DistributedVirtualSwitch#netflow_collector_port}
        '''
        result = self._values.get("netflow_collector_port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def netflow_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Indicates whether to enable netflow on all ports.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#netflow_enabled DistributedVirtualSwitch#netflow_enabled}
        '''
        result = self._values.get("netflow_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def netflow_idle_flow_timeout(self) -> typing.Optional[jsii.Number]:
        '''The number of seconds after which idle flows are forced to be exported to the collector.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#netflow_idle_flow_timeout DistributedVirtualSwitch#netflow_idle_flow_timeout}
        '''
        result = self._values.get("netflow_idle_flow_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def netflow_internal_flows_only(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether to limit analysis to traffic that has both source and destination served by the same host.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#netflow_internal_flows_only DistributedVirtualSwitch#netflow_internal_flows_only}
        '''
        result = self._values.get("netflow_internal_flows_only")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def netflow_observation_domain_id(self) -> typing.Optional[jsii.Number]:
        '''The observation Domain ID for the netflow collector.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#netflow_observation_domain_id DistributedVirtualSwitch#netflow_observation_domain_id}
        '''
        result = self._values.get("netflow_observation_domain_id")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def netflow_sampling_rate(self) -> typing.Optional[jsii.Number]:
        '''The ratio of total number of packets to the number of packets analyzed.

        Set to 0 to disable sampling, meaning that all packets are analyzed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#netflow_sampling_rate DistributedVirtualSwitch#netflow_sampling_rate}
        '''
        result = self._values.get("netflow_sampling_rate")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def network_resource_control_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether or not to enable network resource control, enabling advanced traffic shaping and resource control features.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#network_resource_control_enabled DistributedVirtualSwitch#network_resource_control_enabled}
        '''
        result = self._values.get("network_resource_control_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def network_resource_control_version(self) -> typing.Optional[builtins.str]:
        '''The network I/O control version to use. Can be one of version2 or version3.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#network_resource_control_version DistributedVirtualSwitch#network_resource_control_version}
        '''
        result = self._values.get("network_resource_control_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def nfs_maximum_mbit(self) -> typing.Optional[jsii.Number]:
        '''The maximum allowed usage for the nfs traffic class, in Mbits/sec.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#nfs_maximum_mbit DistributedVirtualSwitch#nfs_maximum_mbit}
        '''
        result = self._values.get("nfs_maximum_mbit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def nfs_reservation_mbit(self) -> typing.Optional[jsii.Number]:
        '''The amount of guaranteed bandwidth for the nfs traffic class, in Mbits/sec.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#nfs_reservation_mbit DistributedVirtualSwitch#nfs_reservation_mbit}
        '''
        result = self._values.get("nfs_reservation_mbit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def nfs_share_count(self) -> typing.Optional[jsii.Number]:
        '''The amount of shares to allocate to the nfs traffic class for a custom share level.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#nfs_share_count DistributedVirtualSwitch#nfs_share_count}
        '''
        result = self._values.get("nfs_share_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def nfs_share_level(self) -> typing.Optional[builtins.str]:
        '''The allocation level for the nfs traffic class. Can be one of high, low, normal, or custom.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#nfs_share_level DistributedVirtualSwitch#nfs_share_level}
        '''
        result = self._values.get("nfs_share_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def notify_switches(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If true, the teaming policy will notify the broadcast network of a NIC failover, triggering cache updates.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#notify_switches DistributedVirtualSwitch#notify_switches}
        '''
        result = self._values.get("notify_switches")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def port_private_secondary_vlan_id(self) -> typing.Optional[jsii.Number]:
        '''The secondary VLAN ID for this port.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#port_private_secondary_vlan_id DistributedVirtualSwitch#port_private_secondary_vlan_id}
        '''
        result = self._values.get("port_private_secondary_vlan_id")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def pvlan_mapping(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DistributedVirtualSwitchPvlanMapping"]]]:
        '''pvlan_mapping block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#pvlan_mapping DistributedVirtualSwitch#pvlan_mapping}
        '''
        result = self._values.get("pvlan_mapping")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DistributedVirtualSwitchPvlanMapping"]]], result)

    @builtins.property
    def standby_uplinks(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of standby uplinks used for load balancing, matching the names of the uplinks assigned in the DVS.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#standby_uplinks DistributedVirtualSwitch#standby_uplinks}
        '''
        result = self._values.get("standby_uplinks")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of tag IDs to apply to this object.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#tags DistributedVirtualSwitch#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def teaming_policy(self) -> typing.Optional[builtins.str]:
        '''The network adapter teaming policy. Can be one of loadbalance_ip, loadbalance_srcmac, loadbalance_srcid, failover_explicit, or loadbalance_loadbased.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#teaming_policy DistributedVirtualSwitch#teaming_policy}
        '''
        result = self._values.get("teaming_policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tx_uplink(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If true, a copy of packets sent to the switch will always be forwarded to an uplink in addition to the regular packet forwarded done by the switch.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#tx_uplink DistributedVirtualSwitch#tx_uplink}
        '''
        result = self._values.get("tx_uplink")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def uplinks(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of uplink ports.

        The contents of this list control both the uplink count and names of the uplinks on the DVS across hosts.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#uplinks DistributedVirtualSwitch#uplinks}
        '''
        result = self._values.get("uplinks")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def vdp_maximum_mbit(self) -> typing.Optional[jsii.Number]:
        '''The maximum allowed usage for the vdp traffic class, in Mbits/sec.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#vdp_maximum_mbit DistributedVirtualSwitch#vdp_maximum_mbit}
        '''
        result = self._values.get("vdp_maximum_mbit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def vdp_reservation_mbit(self) -> typing.Optional[jsii.Number]:
        '''The amount of guaranteed bandwidth for the vdp traffic class, in Mbits/sec.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#vdp_reservation_mbit DistributedVirtualSwitch#vdp_reservation_mbit}
        '''
        result = self._values.get("vdp_reservation_mbit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def vdp_share_count(self) -> typing.Optional[jsii.Number]:
        '''The amount of shares to allocate to the vdp traffic class for a custom share level.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#vdp_share_count DistributedVirtualSwitch#vdp_share_count}
        '''
        result = self._values.get("vdp_share_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def vdp_share_level(self) -> typing.Optional[builtins.str]:
        '''The allocation level for the vdp traffic class. Can be one of high, low, normal, or custom.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#vdp_share_level DistributedVirtualSwitch#vdp_share_level}
        '''
        result = self._values.get("vdp_share_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''The version of this virtual switch.

        Allowed versions are 8.0.3, 8.0.0, 7.0.3, 7.0.2, 7.0.0, 6.6.0, 6.5.0, 6.0.0, 5.5.0, 5.1.0, and 5.0.0.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#version DistributedVirtualSwitch#version}
        '''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def virtualmachine_maximum_mbit(self) -> typing.Optional[jsii.Number]:
        '''The maximum allowed usage for the virtualMachine traffic class, in Mbits/sec.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#virtualmachine_maximum_mbit DistributedVirtualSwitch#virtualmachine_maximum_mbit}
        '''
        result = self._values.get("virtualmachine_maximum_mbit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def virtualmachine_reservation_mbit(self) -> typing.Optional[jsii.Number]:
        '''The amount of guaranteed bandwidth for the virtualMachine traffic class, in Mbits/sec.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#virtualmachine_reservation_mbit DistributedVirtualSwitch#virtualmachine_reservation_mbit}
        '''
        result = self._values.get("virtualmachine_reservation_mbit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def virtualmachine_share_count(self) -> typing.Optional[jsii.Number]:
        '''The amount of shares to allocate to the virtualMachine traffic class for a custom share level.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#virtualmachine_share_count DistributedVirtualSwitch#virtualmachine_share_count}
        '''
        result = self._values.get("virtualmachine_share_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def virtualmachine_share_level(self) -> typing.Optional[builtins.str]:
        '''The allocation level for the virtualMachine traffic class. Can be one of high, low, normal, or custom.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#virtualmachine_share_level DistributedVirtualSwitch#virtualmachine_share_level}
        '''
        result = self._values.get("virtualmachine_share_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vlan_id(self) -> typing.Optional[jsii.Number]:
        '''The VLAN ID for single VLAN mode. 0 denotes no VLAN.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#vlan_id DistributedVirtualSwitch#vlan_id}
        '''
        result = self._values.get("vlan_id")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def vlan_range(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DistributedVirtualSwitchVlanRange"]]]:
        '''vlan_range block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#vlan_range DistributedVirtualSwitch#vlan_range}
        '''
        result = self._values.get("vlan_range")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DistributedVirtualSwitchVlanRange"]]], result)

    @builtins.property
    def vmotion_maximum_mbit(self) -> typing.Optional[jsii.Number]:
        '''The maximum allowed usage for the vmotion traffic class, in Mbits/sec.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#vmotion_maximum_mbit DistributedVirtualSwitch#vmotion_maximum_mbit}
        '''
        result = self._values.get("vmotion_maximum_mbit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def vmotion_reservation_mbit(self) -> typing.Optional[jsii.Number]:
        '''The amount of guaranteed bandwidth for the vmotion traffic class, in Mbits/sec.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#vmotion_reservation_mbit DistributedVirtualSwitch#vmotion_reservation_mbit}
        '''
        result = self._values.get("vmotion_reservation_mbit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def vmotion_share_count(self) -> typing.Optional[jsii.Number]:
        '''The amount of shares to allocate to the vmotion traffic class for a custom share level.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#vmotion_share_count DistributedVirtualSwitch#vmotion_share_count}
        '''
        result = self._values.get("vmotion_share_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def vmotion_share_level(self) -> typing.Optional[builtins.str]:
        '''The allocation level for the vmotion traffic class. Can be one of high, low, normal, or custom.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#vmotion_share_level DistributedVirtualSwitch#vmotion_share_level}
        '''
        result = self._values.get("vmotion_share_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vsan_maximum_mbit(self) -> typing.Optional[jsii.Number]:
        '''The maximum allowed usage for the vsan traffic class, in Mbits/sec.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#vsan_maximum_mbit DistributedVirtualSwitch#vsan_maximum_mbit}
        '''
        result = self._values.get("vsan_maximum_mbit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def vsan_reservation_mbit(self) -> typing.Optional[jsii.Number]:
        '''The amount of guaranteed bandwidth for the vsan traffic class, in Mbits/sec.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#vsan_reservation_mbit DistributedVirtualSwitch#vsan_reservation_mbit}
        '''
        result = self._values.get("vsan_reservation_mbit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def vsan_share_count(self) -> typing.Optional[jsii.Number]:
        '''The amount of shares to allocate to the vsan traffic class for a custom share level.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#vsan_share_count DistributedVirtualSwitch#vsan_share_count}
        '''
        result = self._values.get("vsan_share_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def vsan_share_level(self) -> typing.Optional[builtins.str]:
        '''The allocation level for the vsan traffic class. Can be one of high, low, normal, or custom.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#vsan_share_level DistributedVirtualSwitch#vsan_share_level}
        '''
        result = self._values.get("vsan_share_level")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DistributedVirtualSwitchConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.distributedVirtualSwitch.DistributedVirtualSwitchHost",
    jsii_struct_bases=[],
    name_mapping={"host_system_id": "hostSystemId", "devices": "devices"},
)
class DistributedVirtualSwitchHost:
    def __init__(
        self,
        *,
        host_system_id: builtins.str,
        devices: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param host_system_id: The managed object ID of the host this specification applies to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#host_system_id DistributedVirtualSwitch#host_system_id}
        :param devices: Name of the physical NIC to be added to the proxy switch. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#devices DistributedVirtualSwitch#devices}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee65e3cd1edf40872e66241d6050076b5bed73899d0959ae8042a1200c7c8684)
            check_type(argname="argument host_system_id", value=host_system_id, expected_type=type_hints["host_system_id"])
            check_type(argname="argument devices", value=devices, expected_type=type_hints["devices"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "host_system_id": host_system_id,
        }
        if devices is not None:
            self._values["devices"] = devices

    @builtins.property
    def host_system_id(self) -> builtins.str:
        '''The managed object ID of the host this specification applies to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#host_system_id DistributedVirtualSwitch#host_system_id}
        '''
        result = self._values.get("host_system_id")
        assert result is not None, "Required property 'host_system_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def devices(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Name of the physical NIC to be added to the proxy switch.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#devices DistributedVirtualSwitch#devices}
        '''
        result = self._values.get("devices")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DistributedVirtualSwitchHost(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DistributedVirtualSwitchHostList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.distributedVirtualSwitch.DistributedVirtualSwitchHostList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c2ca350ecf2b1a68eb572edacb032dbe025712e1e1235f3f6f15fcf37315affb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "DistributedVirtualSwitchHostOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4a98c23576a1a4821f16d87f44b98844a9619749d11f24aea75d5c355f30825)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DistributedVirtualSwitchHostOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83ef6346bf91cba0c347e3e5006d8f30a23874090894ffdd806c44d281c171c5)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a98ab7f512cbe524c66c01f82b9fa7da01d90856062ababc49f94efd61ce39e7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f9a17794e3b8f0aa115fd6233a48dec490f7bb8da3fd644afcfc95705b5d7c07)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DistributedVirtualSwitchHost]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DistributedVirtualSwitchHost]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DistributedVirtualSwitchHost]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f5539e646b76cc18d958d9702b71b0190662454ae6ec1dc68c38e6c145b07be8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DistributedVirtualSwitchHostOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.distributedVirtualSwitch.DistributedVirtualSwitchHostOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a7b2131299bb25cbaf90de3c840cc6219f09ab51e2dcdbfada2c74aeacfd84a5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetDevices")
    def reset_devices(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDevices", []))

    @builtins.property
    @jsii.member(jsii_name="devicesInput")
    def devices_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "devicesInput"))

    @builtins.property
    @jsii.member(jsii_name="hostSystemIdInput")
    def host_system_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostSystemIdInput"))

    @builtins.property
    @jsii.member(jsii_name="devices")
    def devices(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "devices"))

    @devices.setter
    def devices(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc01d92780d6ed46664e3dfe9899767373093866d04864a87a5713eccc8ce9d6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "devices", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="hostSystemId")
    def host_system_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostSystemId"))

    @host_system_id.setter
    def host_system_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f14bb72bb110a208d2dc136e6f56011550d4bd5fc1c3366b5ddf559871b0205)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hostSystemId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DistributedVirtualSwitchHost]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DistributedVirtualSwitchHost]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DistributedVirtualSwitchHost]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1533a83454e4f6a7f490ecbf0fd3a0671f0b07fc415de54f0c04a7888e27a774)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.distributedVirtualSwitch.DistributedVirtualSwitchPvlanMapping",
    jsii_struct_bases=[],
    name_mapping={
        "primary_vlan_id": "primaryVlanId",
        "pvlan_type": "pvlanType",
        "secondary_vlan_id": "secondaryVlanId",
    },
)
class DistributedVirtualSwitchPvlanMapping:
    def __init__(
        self,
        *,
        primary_vlan_id: jsii.Number,
        pvlan_type: builtins.str,
        secondary_vlan_id: jsii.Number,
    ) -> None:
        '''
        :param primary_vlan_id: The primary VLAN ID. The VLAN IDs of 0 and 4095 are reserved and cannot be used in this property. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#primary_vlan_id DistributedVirtualSwitch#primary_vlan_id}
        :param pvlan_type: The private VLAN type. Valid values are promiscuous, community and isolated. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#pvlan_type DistributedVirtualSwitch#pvlan_type}
        :param secondary_vlan_id: The secondary VLAN ID. The VLAN IDs of 0 and 4095 are reserved and cannot be used in this property. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#secondary_vlan_id DistributedVirtualSwitch#secondary_vlan_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__607798e58a7e82c3f6905605856f4f82024d02b647570120071193922867f321)
            check_type(argname="argument primary_vlan_id", value=primary_vlan_id, expected_type=type_hints["primary_vlan_id"])
            check_type(argname="argument pvlan_type", value=pvlan_type, expected_type=type_hints["pvlan_type"])
            check_type(argname="argument secondary_vlan_id", value=secondary_vlan_id, expected_type=type_hints["secondary_vlan_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "primary_vlan_id": primary_vlan_id,
            "pvlan_type": pvlan_type,
            "secondary_vlan_id": secondary_vlan_id,
        }

    @builtins.property
    def primary_vlan_id(self) -> jsii.Number:
        '''The primary VLAN ID.

        The VLAN IDs of 0 and 4095 are reserved and cannot be used in this property.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#primary_vlan_id DistributedVirtualSwitch#primary_vlan_id}
        '''
        result = self._values.get("primary_vlan_id")
        assert result is not None, "Required property 'primary_vlan_id' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def pvlan_type(self) -> builtins.str:
        '''The private VLAN type. Valid values are promiscuous, community and isolated.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#pvlan_type DistributedVirtualSwitch#pvlan_type}
        '''
        result = self._values.get("pvlan_type")
        assert result is not None, "Required property 'pvlan_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def secondary_vlan_id(self) -> jsii.Number:
        '''The secondary VLAN ID.

        The VLAN IDs of 0 and 4095 are reserved and cannot be used in this property.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#secondary_vlan_id DistributedVirtualSwitch#secondary_vlan_id}
        '''
        result = self._values.get("secondary_vlan_id")
        assert result is not None, "Required property 'secondary_vlan_id' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DistributedVirtualSwitchPvlanMapping(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DistributedVirtualSwitchPvlanMappingList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.distributedVirtualSwitch.DistributedVirtualSwitchPvlanMappingList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9633e232ca5efa949d041e13cb50380072b41d8e516b3c34e9501b8a70efe9c9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DistributedVirtualSwitchPvlanMappingOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__616c2cad4b4dd709db5d06dc67fb34d763454023a99b903a85a7cf4b26ec02de)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DistributedVirtualSwitchPvlanMappingOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c9b201cee44832de6df9ad400cd6102462cc7408dd03e0fdc31a825fc415354)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b78e35831d9ea8934664b0ab64c817ac75fa6d51af8981c7a0ec4f925da9a592)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e31b728664a07c5a172c481516e7d04d8dc06efe938d126de20622b65516757c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DistributedVirtualSwitchPvlanMapping]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DistributedVirtualSwitchPvlanMapping]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DistributedVirtualSwitchPvlanMapping]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79c26f507975e70f2e014f374a86069f3faf4c8b93f999a32e6061101dbfeadc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DistributedVirtualSwitchPvlanMappingOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.distributedVirtualSwitch.DistributedVirtualSwitchPvlanMappingOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2c40e757daa771cf49eaac2c670134bf66588592f78d571e2e2fad7827e8008e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

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
    @jsii.member(jsii_name="primaryVlanId")
    def primary_vlan_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "primaryVlanId"))

    @primary_vlan_id.setter
    def primary_vlan_id(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__442e0c63ebdfc6c1fb9adb1f0d9d48820fb196b25aab879c6773ac1eb5fd7127)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "primaryVlanId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pvlanType")
    def pvlan_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pvlanType"))

    @pvlan_type.setter
    def pvlan_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a62e713d860039b4a683b4200f75e611eb5259b7234dbb71dd2378d9ed9f950)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pvlanType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="secondaryVlanId")
    def secondary_vlan_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "secondaryVlanId"))

    @secondary_vlan_id.setter
    def secondary_vlan_id(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d5f134d55d634e72d6e0b1cfd0018517e7e3d57a72099c6dd01104ea8d60532)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secondaryVlanId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DistributedVirtualSwitchPvlanMapping]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DistributedVirtualSwitchPvlanMapping]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DistributedVirtualSwitchPvlanMapping]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f228ad8f536000aef78d6de7e1c8ad4633f024e93d5a07d91501c68f8a0b674)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.distributedVirtualSwitch.DistributedVirtualSwitchVlanRange",
    jsii_struct_bases=[],
    name_mapping={"max_vlan": "maxVlan", "min_vlan": "minVlan"},
)
class DistributedVirtualSwitchVlanRange:
    def __init__(self, *, max_vlan: jsii.Number, min_vlan: jsii.Number) -> None:
        '''
        :param max_vlan: The minimum VLAN to use in the range. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#max_vlan DistributedVirtualSwitch#max_vlan}
        :param min_vlan: The minimum VLAN to use in the range. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#min_vlan DistributedVirtualSwitch#min_vlan}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0b8ce7b1676170d43394f4349278d540566243208c7258a614b695397d10deb)
            check_type(argname="argument max_vlan", value=max_vlan, expected_type=type_hints["max_vlan"])
            check_type(argname="argument min_vlan", value=min_vlan, expected_type=type_hints["min_vlan"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "max_vlan": max_vlan,
            "min_vlan": min_vlan,
        }

    @builtins.property
    def max_vlan(self) -> jsii.Number:
        '''The minimum VLAN to use in the range.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#max_vlan DistributedVirtualSwitch#max_vlan}
        '''
        result = self._values.get("max_vlan")
        assert result is not None, "Required property 'max_vlan' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def min_vlan(self) -> jsii.Number:
        '''The minimum VLAN to use in the range.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/distributed_virtual_switch#min_vlan DistributedVirtualSwitch#min_vlan}
        '''
        result = self._values.get("min_vlan")
        assert result is not None, "Required property 'min_vlan' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DistributedVirtualSwitchVlanRange(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DistributedVirtualSwitchVlanRangeList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.distributedVirtualSwitch.DistributedVirtualSwitchVlanRangeList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__706ed5236148e90be8bd2c42c0abbf3af30ca17ddabb097c2d26314470078a55)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DistributedVirtualSwitchVlanRangeOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bbc57f4695b47b7269ccfa528847786d0deb75533a98390bc31baf276660929e)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DistributedVirtualSwitchVlanRangeOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f9a4ce58a4614d633dc2105e93fefb7324c9eeeba83136732a6bef9951e5266c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__144a3ba4a7b29c518ead5246f922101a10968112bbb7e0a8d58cbfb997da0b1a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f50b1231c8f4c7b2a44b8a56cb95e77ad2dadc4075e3c8d4005f290805b6450a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DistributedVirtualSwitchVlanRange]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DistributedVirtualSwitchVlanRange]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DistributedVirtualSwitchVlanRange]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc7ceb0e60233b3b55b179f5f5199e8aa95ef76ee8101a1987dde8b70c2d7199)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DistributedVirtualSwitchVlanRangeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.distributedVirtualSwitch.DistributedVirtualSwitchVlanRangeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c9fba82aa46503338d97f8b53622ea8c00144d0ebc3a1595843f3120626d3f9d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__97529cdd0f7a06f684c4a78a43cd5c7c7c738e7fa8b5ce41a770edb9c40a887c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxVlan", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minVlan")
    def min_vlan(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minVlan"))

    @min_vlan.setter
    def min_vlan(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3afc3f9bc3e3deac57f2fdd4986fba0eeae97dd390e95071857604bee772d90)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minVlan", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DistributedVirtualSwitchVlanRange]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DistributedVirtualSwitchVlanRange]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DistributedVirtualSwitchVlanRange]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__54d74da89535a727db3b49e02af459b31517636e1d5043b6a78af5b0a9d99abd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DistributedVirtualSwitch",
    "DistributedVirtualSwitchConfig",
    "DistributedVirtualSwitchHost",
    "DistributedVirtualSwitchHostList",
    "DistributedVirtualSwitchHostOutputReference",
    "DistributedVirtualSwitchPvlanMapping",
    "DistributedVirtualSwitchPvlanMappingList",
    "DistributedVirtualSwitchPvlanMappingOutputReference",
    "DistributedVirtualSwitchVlanRange",
    "DistributedVirtualSwitchVlanRangeList",
    "DistributedVirtualSwitchVlanRangeOutputReference",
]

publication.publish()

def _typecheckingstub__5d3687ae93fa4b327b751d3748a3385265380d804ecaf8116c5d4895cce67f53(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    datacenter_id: builtins.str,
    name: builtins.str,
    active_uplinks: typing.Optional[typing.Sequence[builtins.str]] = None,
    allow_forged_transmits: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_mac_changes: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_promiscuous: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    backupnfc_maximum_mbit: typing.Optional[jsii.Number] = None,
    backupnfc_reservation_mbit: typing.Optional[jsii.Number] = None,
    backupnfc_share_count: typing.Optional[jsii.Number] = None,
    backupnfc_share_level: typing.Optional[builtins.str] = None,
    block_all_ports: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    check_beacon: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    contact_detail: typing.Optional[builtins.str] = None,
    contact_name: typing.Optional[builtins.str] = None,
    custom_attributes: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    description: typing.Optional[builtins.str] = None,
    directpath_gen2_allowed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    egress_shaping_average_bandwidth: typing.Optional[jsii.Number] = None,
    egress_shaping_burst_size: typing.Optional[jsii.Number] = None,
    egress_shaping_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    egress_shaping_peak_bandwidth: typing.Optional[jsii.Number] = None,
    failback: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    faulttolerance_maximum_mbit: typing.Optional[jsii.Number] = None,
    faulttolerance_reservation_mbit: typing.Optional[jsii.Number] = None,
    faulttolerance_share_count: typing.Optional[jsii.Number] = None,
    faulttolerance_share_level: typing.Optional[builtins.str] = None,
    folder: typing.Optional[builtins.str] = None,
    hbr_maximum_mbit: typing.Optional[jsii.Number] = None,
    hbr_reservation_mbit: typing.Optional[jsii.Number] = None,
    hbr_share_count: typing.Optional[jsii.Number] = None,
    hbr_share_level: typing.Optional[builtins.str] = None,
    host: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DistributedVirtualSwitchHost, typing.Dict[builtins.str, typing.Any]]]]] = None,
    id: typing.Optional[builtins.str] = None,
    ignore_other_pvlan_mappings: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ingress_shaping_average_bandwidth: typing.Optional[jsii.Number] = None,
    ingress_shaping_burst_size: typing.Optional[jsii.Number] = None,
    ingress_shaping_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ingress_shaping_peak_bandwidth: typing.Optional[jsii.Number] = None,
    ipv4_address: typing.Optional[builtins.str] = None,
    iscsi_maximum_mbit: typing.Optional[jsii.Number] = None,
    iscsi_reservation_mbit: typing.Optional[jsii.Number] = None,
    iscsi_share_count: typing.Optional[jsii.Number] = None,
    iscsi_share_level: typing.Optional[builtins.str] = None,
    lacp_api_version: typing.Optional[builtins.str] = None,
    lacp_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    lacp_mode: typing.Optional[builtins.str] = None,
    link_discovery_operation: typing.Optional[builtins.str] = None,
    link_discovery_protocol: typing.Optional[builtins.str] = None,
    management_maximum_mbit: typing.Optional[jsii.Number] = None,
    management_reservation_mbit: typing.Optional[jsii.Number] = None,
    management_share_count: typing.Optional[jsii.Number] = None,
    management_share_level: typing.Optional[builtins.str] = None,
    max_mtu: typing.Optional[jsii.Number] = None,
    multicast_filtering_mode: typing.Optional[builtins.str] = None,
    netflow_active_flow_timeout: typing.Optional[jsii.Number] = None,
    netflow_collector_ip_address: typing.Optional[builtins.str] = None,
    netflow_collector_port: typing.Optional[jsii.Number] = None,
    netflow_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    netflow_idle_flow_timeout: typing.Optional[jsii.Number] = None,
    netflow_internal_flows_only: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    netflow_observation_domain_id: typing.Optional[jsii.Number] = None,
    netflow_sampling_rate: typing.Optional[jsii.Number] = None,
    network_resource_control_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    network_resource_control_version: typing.Optional[builtins.str] = None,
    nfs_maximum_mbit: typing.Optional[jsii.Number] = None,
    nfs_reservation_mbit: typing.Optional[jsii.Number] = None,
    nfs_share_count: typing.Optional[jsii.Number] = None,
    nfs_share_level: typing.Optional[builtins.str] = None,
    notify_switches: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    port_private_secondary_vlan_id: typing.Optional[jsii.Number] = None,
    pvlan_mapping: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DistributedVirtualSwitchPvlanMapping, typing.Dict[builtins.str, typing.Any]]]]] = None,
    standby_uplinks: typing.Optional[typing.Sequence[builtins.str]] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    teaming_policy: typing.Optional[builtins.str] = None,
    tx_uplink: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    uplinks: typing.Optional[typing.Sequence[builtins.str]] = None,
    vdp_maximum_mbit: typing.Optional[jsii.Number] = None,
    vdp_reservation_mbit: typing.Optional[jsii.Number] = None,
    vdp_share_count: typing.Optional[jsii.Number] = None,
    vdp_share_level: typing.Optional[builtins.str] = None,
    version: typing.Optional[builtins.str] = None,
    virtualmachine_maximum_mbit: typing.Optional[jsii.Number] = None,
    virtualmachine_reservation_mbit: typing.Optional[jsii.Number] = None,
    virtualmachine_share_count: typing.Optional[jsii.Number] = None,
    virtualmachine_share_level: typing.Optional[builtins.str] = None,
    vlan_id: typing.Optional[jsii.Number] = None,
    vlan_range: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DistributedVirtualSwitchVlanRange, typing.Dict[builtins.str, typing.Any]]]]] = None,
    vmotion_maximum_mbit: typing.Optional[jsii.Number] = None,
    vmotion_reservation_mbit: typing.Optional[jsii.Number] = None,
    vmotion_share_count: typing.Optional[jsii.Number] = None,
    vmotion_share_level: typing.Optional[builtins.str] = None,
    vsan_maximum_mbit: typing.Optional[jsii.Number] = None,
    vsan_reservation_mbit: typing.Optional[jsii.Number] = None,
    vsan_share_count: typing.Optional[jsii.Number] = None,
    vsan_share_level: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__acf0e4939da365843266edb7c5f140f619eb17b2d2cb57d1dc7436ea76aa25f3(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06231c32da6a95236e80fae43caebdb912880c03d94d5a2090c603aedbd30456(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DistributedVirtualSwitchHost, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4301a2a6098e670a5913de0dcb2409f8cf429b0c10eaf0c2a12020425308b10(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DistributedVirtualSwitchPvlanMapping, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0442724c46e2564d8880a14e12e303c7cc18a25114a6055cae762736dcebec1d(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DistributedVirtualSwitchVlanRange, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a11636edf7599cd231cfae9eabc7a5ad724a2ee3b8df5b72944066c5b027ec0(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a77d17fea7873f83c93e2ee4a9f097dd1b0ef0f318ee95f0216c2a08b62dd702(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62cff42b489d3b659fbfe250c68deeda5209269d0a60898698d99235e83132b0(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19ec6bc7dfad7447c16a5f5d4bf10e58a80b01313d8319f9a1f16854492f17ed(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3de15ae2deb3f787864c74e1948a2e944d5adc0fb4d9b607f8a3119a0ead07b0(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88799553a38cc4ae4d5e73cebad4ba19d14a8acf71db614203ecd382158a5356(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18cf2c9757a0e1f79c4543d26e7cd27b20403365cc429957417003838a1f9f22(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b0de7511e2934739946da54300ebc617fdd5d62e7f0b0ecc70e09b331324c44(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47c902b3d9dd46cd632e62446b22a713cde27eade1c08839719ec8079a4cae61(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__32cdc019d8e5294c3dbdfbed5d23c4b51c15fb8cd7821ae747953dbba452cc11(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc86333573b5c81f77240ea7453ccba60b9c5cda55957afd5d2657f4500a1752(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f05155ffd3db7a93266d4cee9558cd2246a8ee8b755cffddb56b9b3534dfa590(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68cc5c938c5c12d82822a3fcbeb0aaa521d379ca0c94c021a4863c7e8ff7c0e9(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7fc2ee53e164c6a9339c5d9c1eac181c3a90f022cd34235843b23a8aa931929a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4aa311214ee0c24675140418dd909f62f86b85c0c8815f66fcee3a5c716d3fe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0cdc3f5c16ebeaf67bde53a8baf6d34c4af65953c68e52f183b40e1c7af570f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5bc318b970c83c5752f3427a3394c78da3d70f7b4bc5db29261a83473a87bda9(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84b40c48a12f4382ff480ba07da558780c38fca8301d5c6796b13a10a9d72ec1(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d99b8a1edd7752d5edd3e93d7e620a032593e3450b66103155a93808d974996(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1296b8d14d8d346ac5b99307800fc50ec32fd47a3292ae2be2da918f302b8365(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c7a9618c95ab3d424c32a460b3cf4f3b0532543ae6aad6a5b44a376fc7fd4cf(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19fc98d55c27a4fbf34a3549cd0bd640a77205dab1ced47b441be8248d3e5b01(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07e402c60c29e7ad5e19b2706ab1d25ae4796efda84be045981803a05fdc1ec0(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1f53e5cd29a0ed2f8157a7832810f6e62ae0186e1f97edf692f9ace3250a2c2(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e6ed6fbfe9a8bfde6417f05ec7827ec6358de9772b89d9dec94b295f307f403(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37e9e4091e3b7e6b0fddd0c4d11e9f303ad9f63947c896d3404408b19e7877c7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0446d12bad820a458775fef7e65e7e53151505d3d82da0f712fba25aec154943(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8605f368855445ec3d30dfac468a2c234705f36726c0ea94786da0bdf9d63e9(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49609ae0c56d799730f26c199fb988a56a14a5cdc42627f5df596d4524fdb229(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a3d52c246c0ad6f23f1097ff3d595837ea7b517c87b8686b28903e29c787ce44(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f3a21a553235bd4518b257010851b242a626c8c0fc5bc9cd97507a831ff725f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a77a70509529aaed3964131e434d235bd7e589ce306eb93f0ceb5bbf06379bf(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__775d0f97776e8b352a968f4c9bd5c0ca37ce69029133f80c028ff797e4501387(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7615157cfa880dc077a08b9b7a8e42f897a46c1efdc5d465774390b6a40fd88(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__785d331ae9cf7f75e78219ddeadf3fe3c62a2e470597ca94cadf8174e4a185a3(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be7524a2298f48a71060cfc97c2c2b0e8cd6dd194495bd7ff8e58094c1055035(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d590d1e3701df1771de802df354fb4aaa4a7c45a5970cb086698434f57c7779(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba6fa135913b8e9a7bc7c361e9d21e4d378e2819c101c319fe2618932d80cf4b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7a338d7831974a6f7856d700f67d4322dd7b50b0ffbe05adc97e255e78aaa3e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1fb832b7743bed78b3b660a6d4a046d84be984db542bf4a987ed15b643a6fa0(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e875a9234718732930ed986b929d3243dfc8dba6759676b10f1f77989046f162(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f209afb7bc11e1a5d7c541f0389f73aebc3d9ff455551579549618255ba611da(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__231f468379c197e7ed84f3afc2a271cccd573e22a5bddff3b0bf3b9eb42b6b0f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de9d2f4b1b43ca24e46cbe947a07c94304d548131478588327c619c07624a0bf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb8c7af4a25698ea936a3b07dca71b52ccee76e6a995b9cccaac4d37b603e7cb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14304848776145b12155292fa345388c5be98448282d9672113dd3be9f1fb92e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8042501a86a08d321e2d042521e18fbf65e2feb0da68bbf5e5d644086da5ea48(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ace027e097e405bd714a6c511a77af5387eac3e0a23f88e6d29f15f461c4796(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de38124f91e4291078a80cc9fcad249f8207a25a2e6aa4640189092cd42c698d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87f2312bcd1abd5cb57d16c928575743152efe59952fcdf30934b10025aaabd8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d00e4c4ff44a132de11dbf87e198faa3221397f2b8391301b2a80d9e99756dd4(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__854dff79864e7fb232aed1a354caed9790baf917ce019aa6e14ef78858bc32a8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a72851d10fa900a6bde57893bc869eee6cf9465e3b38b97400756f4e907be078(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9355fdb140e559870616d54c6538adf9caf830a5cad0f87091cb47ee9e0cf415(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b973e3d39e79b4bba82c5a84b38566fe7600ce452fa88f1e55ab5fb58ad0f782(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b608c433c417bd1f3390b273fc26a3be56076b187446e0e436954d3f2f2b5c2(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21a03c034eb8841e53e401185e569927b527169a890d22f2f4d4312fab93885b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36333df7a63112e2aa34c827ae6bc78bd8c112b2164a848ca633b36fdf4ac4b7(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe0ddaf04ec6770ae6e14d4ec4539bf6fec4965aaa1e5c24107d336ed443f1ff(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ca00af1ab837acebdc2a0d449adf84d630b3a157f8b86ec0518e63b87164521(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c60de2f67fdc987b92e91fb8d815fe8b853036f089524ed8e37c3b47d19085d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e57d53718704f1c7e2a552657d5b79ebff8538da807f0d3322f759f028267a37(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6491d5a36511ec75dd905aaffe277a454e27ecee61c8b30cc80111ab5fcd4ef(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e5f4d42fd9e56d34372c4e65b44c94775f7261d5a5a4bb4d5fc014d81d7f3fe(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a0ef828e9298c7924ebb1bbd7dd08ea7390373d08ebeb80bfb73d3ddf416654(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14933169a9e17ca8d1a49b49f1c644a85690b80d337ac9274ff369b22377c68d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d813aab8077118caefeaa00b4e43b77f4bfac595c50124bfc93e4a48e4943419(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14fc4b7b003020e34431d48e256f0ba7cccfd9a41d0de952e65b076cac2e82be(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9ad71ae248252fe2cb7bba47332022876083f853072672577479ffb467ffb01(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e993d066310e833b2670294cab72e01013f03914d851ec95e1666870a4cdcaa(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f79d51bd730760271d0155cfc4d42f208822e4627ccf1aca78cfcf94c06bb09e(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e77dc6afec2dac692c44ccd6682baf62ad05c677da816ed4791a25cbf590745(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__309a6926ba36e3ee185009202f9b3e2642464ce15e59f781e0716906f1f3fa5a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7591233a4c75a2b1c4dbbbd7039685c8082a04817be254f78d7d3431b17f345e(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__340b7bdd667a0fd556dbe43e2d6a5e4f0be9ca8b66abb002e22371006836025f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__469b929037704d57f865e1b86d1b9c0fe6570471b3e9eba507fd07f9369c8f18(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a0d1f1e212de2113c0b45b8341eed912996e8c6438410c04e61be6a728ecb3f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea263d370f646fe63f9f2cda740a92a3adc9bb2c2a0a28d8162dc3267d5a39c2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76b6a3272897b37ab31baab67bddf24776a9d14ac257e594dada082d7db51db1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2ea66402c35dd295d687ffd6b35df4a99bc51a30f383acc80c088d37f473edb(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74a7e8527ab3449cc84ba438f98da3364320dfa8c9d41d56856e5a5e2eb74dcf(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a822cb55b469bea10c9a2632c84a83e0b791beb4e535ceeeb2f3d27a48610c9(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__953b0bb848fb30d61655ca7ff4d7f45c6e5c08e8caee8f40879e889c4036aed2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23353a43ee1d7376378409daa25e4a5231429b08ec84d443331afc44f135b246(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e587a78d057e7191308b8058b89918df16f00633d2d67e247c5809493194652(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__472126d8f4c90260506bccec261b15220af07e6e26826ef7b9c0bd4de7ae902b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72a0845251b13a7f2145429bed322f584078ce348695fd0de50edc94bf8319dd(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05f9b906292d11572f7716a1c8263f5311a6784460a232261ba21d64bdeea9ab(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d121fe9f9b68e42204a87d2ce15548998d58523539cedaf4acfb9728a18b69a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0c5f9d1c64f85f4541ad6d1213ca23192fb506c0c240a908c822993aec49e35(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dcc7166faca340d33fae632558df44d1b2b51ffa317086055ca3deb6d511bc78(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__248487444b2b37bf3a5c1e4d0f6f5c270c5e79fc0553020eec6dd93563f06e91(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d221cf0e7e0221e763389d961f3179ab704d1265320c36c1cb0672ee983c2da3(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    datacenter_id: builtins.str,
    name: builtins.str,
    active_uplinks: typing.Optional[typing.Sequence[builtins.str]] = None,
    allow_forged_transmits: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_mac_changes: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_promiscuous: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    backupnfc_maximum_mbit: typing.Optional[jsii.Number] = None,
    backupnfc_reservation_mbit: typing.Optional[jsii.Number] = None,
    backupnfc_share_count: typing.Optional[jsii.Number] = None,
    backupnfc_share_level: typing.Optional[builtins.str] = None,
    block_all_ports: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    check_beacon: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    contact_detail: typing.Optional[builtins.str] = None,
    contact_name: typing.Optional[builtins.str] = None,
    custom_attributes: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    description: typing.Optional[builtins.str] = None,
    directpath_gen2_allowed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    egress_shaping_average_bandwidth: typing.Optional[jsii.Number] = None,
    egress_shaping_burst_size: typing.Optional[jsii.Number] = None,
    egress_shaping_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    egress_shaping_peak_bandwidth: typing.Optional[jsii.Number] = None,
    failback: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    faulttolerance_maximum_mbit: typing.Optional[jsii.Number] = None,
    faulttolerance_reservation_mbit: typing.Optional[jsii.Number] = None,
    faulttolerance_share_count: typing.Optional[jsii.Number] = None,
    faulttolerance_share_level: typing.Optional[builtins.str] = None,
    folder: typing.Optional[builtins.str] = None,
    hbr_maximum_mbit: typing.Optional[jsii.Number] = None,
    hbr_reservation_mbit: typing.Optional[jsii.Number] = None,
    hbr_share_count: typing.Optional[jsii.Number] = None,
    hbr_share_level: typing.Optional[builtins.str] = None,
    host: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DistributedVirtualSwitchHost, typing.Dict[builtins.str, typing.Any]]]]] = None,
    id: typing.Optional[builtins.str] = None,
    ignore_other_pvlan_mappings: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ingress_shaping_average_bandwidth: typing.Optional[jsii.Number] = None,
    ingress_shaping_burst_size: typing.Optional[jsii.Number] = None,
    ingress_shaping_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ingress_shaping_peak_bandwidth: typing.Optional[jsii.Number] = None,
    ipv4_address: typing.Optional[builtins.str] = None,
    iscsi_maximum_mbit: typing.Optional[jsii.Number] = None,
    iscsi_reservation_mbit: typing.Optional[jsii.Number] = None,
    iscsi_share_count: typing.Optional[jsii.Number] = None,
    iscsi_share_level: typing.Optional[builtins.str] = None,
    lacp_api_version: typing.Optional[builtins.str] = None,
    lacp_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    lacp_mode: typing.Optional[builtins.str] = None,
    link_discovery_operation: typing.Optional[builtins.str] = None,
    link_discovery_protocol: typing.Optional[builtins.str] = None,
    management_maximum_mbit: typing.Optional[jsii.Number] = None,
    management_reservation_mbit: typing.Optional[jsii.Number] = None,
    management_share_count: typing.Optional[jsii.Number] = None,
    management_share_level: typing.Optional[builtins.str] = None,
    max_mtu: typing.Optional[jsii.Number] = None,
    multicast_filtering_mode: typing.Optional[builtins.str] = None,
    netflow_active_flow_timeout: typing.Optional[jsii.Number] = None,
    netflow_collector_ip_address: typing.Optional[builtins.str] = None,
    netflow_collector_port: typing.Optional[jsii.Number] = None,
    netflow_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    netflow_idle_flow_timeout: typing.Optional[jsii.Number] = None,
    netflow_internal_flows_only: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    netflow_observation_domain_id: typing.Optional[jsii.Number] = None,
    netflow_sampling_rate: typing.Optional[jsii.Number] = None,
    network_resource_control_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    network_resource_control_version: typing.Optional[builtins.str] = None,
    nfs_maximum_mbit: typing.Optional[jsii.Number] = None,
    nfs_reservation_mbit: typing.Optional[jsii.Number] = None,
    nfs_share_count: typing.Optional[jsii.Number] = None,
    nfs_share_level: typing.Optional[builtins.str] = None,
    notify_switches: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    port_private_secondary_vlan_id: typing.Optional[jsii.Number] = None,
    pvlan_mapping: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DistributedVirtualSwitchPvlanMapping, typing.Dict[builtins.str, typing.Any]]]]] = None,
    standby_uplinks: typing.Optional[typing.Sequence[builtins.str]] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    teaming_policy: typing.Optional[builtins.str] = None,
    tx_uplink: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    uplinks: typing.Optional[typing.Sequence[builtins.str]] = None,
    vdp_maximum_mbit: typing.Optional[jsii.Number] = None,
    vdp_reservation_mbit: typing.Optional[jsii.Number] = None,
    vdp_share_count: typing.Optional[jsii.Number] = None,
    vdp_share_level: typing.Optional[builtins.str] = None,
    version: typing.Optional[builtins.str] = None,
    virtualmachine_maximum_mbit: typing.Optional[jsii.Number] = None,
    virtualmachine_reservation_mbit: typing.Optional[jsii.Number] = None,
    virtualmachine_share_count: typing.Optional[jsii.Number] = None,
    virtualmachine_share_level: typing.Optional[builtins.str] = None,
    vlan_id: typing.Optional[jsii.Number] = None,
    vlan_range: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DistributedVirtualSwitchVlanRange, typing.Dict[builtins.str, typing.Any]]]]] = None,
    vmotion_maximum_mbit: typing.Optional[jsii.Number] = None,
    vmotion_reservation_mbit: typing.Optional[jsii.Number] = None,
    vmotion_share_count: typing.Optional[jsii.Number] = None,
    vmotion_share_level: typing.Optional[builtins.str] = None,
    vsan_maximum_mbit: typing.Optional[jsii.Number] = None,
    vsan_reservation_mbit: typing.Optional[jsii.Number] = None,
    vsan_share_count: typing.Optional[jsii.Number] = None,
    vsan_share_level: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee65e3cd1edf40872e66241d6050076b5bed73899d0959ae8042a1200c7c8684(
    *,
    host_system_id: builtins.str,
    devices: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2ca350ecf2b1a68eb572edacb032dbe025712e1e1235f3f6f15fcf37315affb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4a98c23576a1a4821f16d87f44b98844a9619749d11f24aea75d5c355f30825(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83ef6346bf91cba0c347e3e5006d8f30a23874090894ffdd806c44d281c171c5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a98ab7f512cbe524c66c01f82b9fa7da01d90856062ababc49f94efd61ce39e7(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9a17794e3b8f0aa115fd6233a48dec490f7bb8da3fd644afcfc95705b5d7c07(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5539e646b76cc18d958d9702b71b0190662454ae6ec1dc68c38e6c145b07be8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DistributedVirtualSwitchHost]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7b2131299bb25cbaf90de3c840cc6219f09ab51e2dcdbfada2c74aeacfd84a5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc01d92780d6ed46664e3dfe9899767373093866d04864a87a5713eccc8ce9d6(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f14bb72bb110a208d2dc136e6f56011550d4bd5fc1c3366b5ddf559871b0205(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1533a83454e4f6a7f490ecbf0fd3a0671f0b07fc415de54f0c04a7888e27a774(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DistributedVirtualSwitchHost]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__607798e58a7e82c3f6905605856f4f82024d02b647570120071193922867f321(
    *,
    primary_vlan_id: jsii.Number,
    pvlan_type: builtins.str,
    secondary_vlan_id: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9633e232ca5efa949d041e13cb50380072b41d8e516b3c34e9501b8a70efe9c9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__616c2cad4b4dd709db5d06dc67fb34d763454023a99b903a85a7cf4b26ec02de(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c9b201cee44832de6df9ad400cd6102462cc7408dd03e0fdc31a825fc415354(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b78e35831d9ea8934664b0ab64c817ac75fa6d51af8981c7a0ec4f925da9a592(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e31b728664a07c5a172c481516e7d04d8dc06efe938d126de20622b65516757c(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79c26f507975e70f2e014f374a86069f3faf4c8b93f999a32e6061101dbfeadc(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DistributedVirtualSwitchPvlanMapping]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c40e757daa771cf49eaac2c670134bf66588592f78d571e2e2fad7827e8008e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__442e0c63ebdfc6c1fb9adb1f0d9d48820fb196b25aab879c6773ac1eb5fd7127(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a62e713d860039b4a683b4200f75e611eb5259b7234dbb71dd2378d9ed9f950(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d5f134d55d634e72d6e0b1cfd0018517e7e3d57a72099c6dd01104ea8d60532(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f228ad8f536000aef78d6de7e1c8ad4633f024e93d5a07d91501c68f8a0b674(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DistributedVirtualSwitchPvlanMapping]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0b8ce7b1676170d43394f4349278d540566243208c7258a614b695397d10deb(
    *,
    max_vlan: jsii.Number,
    min_vlan: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__706ed5236148e90be8bd2c42c0abbf3af30ca17ddabb097c2d26314470078a55(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bbc57f4695b47b7269ccfa528847786d0deb75533a98390bc31baf276660929e(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9a4ce58a4614d633dc2105e93fefb7324c9eeeba83136732a6bef9951e5266c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__144a3ba4a7b29c518ead5246f922101a10968112bbb7e0a8d58cbfb997da0b1a(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f50b1231c8f4c7b2a44b8a56cb95e77ad2dadc4075e3c8d4005f290805b6450a(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc7ceb0e60233b3b55b179f5f5199e8aa95ef76ee8101a1987dde8b70c2d7199(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DistributedVirtualSwitchVlanRange]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9fba82aa46503338d97f8b53622ea8c00144d0ebc3a1595843f3120626d3f9d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97529cdd0f7a06f684c4a78a43cd5c7c7c738e7fa8b5ce41a770edb9c40a887c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3afc3f9bc3e3deac57f2fdd4986fba0eeae97dd390e95071857604bee772d90(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54d74da89535a727db3b49e02af459b31517636e1d5043b6a78af5b0a9d99abd(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DistributedVirtualSwitchVlanRange]],
) -> None:
    """Type checking stubs"""
    pass
