r'''
# `vsphere_virtual_machine`

Refer to the Terraform Registry for docs: [`vsphere_virtual_machine`](https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine).
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


class VirtualMachine(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.virtualMachine.VirtualMachine",
):
    '''Represents a {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine vsphere_virtual_machine}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        resource_pool_id: builtins.str,
        alternate_guest_name: typing.Optional[builtins.str] = None,
        annotation: typing.Optional[builtins.str] = None,
        boot_delay: typing.Optional[jsii.Number] = None,
        boot_retry_delay: typing.Optional[jsii.Number] = None,
        boot_retry_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        cdrom: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["VirtualMachineCdrom", typing.Dict[builtins.str, typing.Any]]]]] = None,
        clone: typing.Optional[typing.Union["VirtualMachineClone", typing.Dict[builtins.str, typing.Any]]] = None,
        cpu_hot_add_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        cpu_hot_remove_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        cpu_limit: typing.Optional[jsii.Number] = None,
        cpu_performance_counters_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        cpu_reservation: typing.Optional[jsii.Number] = None,
        cpu_share_count: typing.Optional[jsii.Number] = None,
        cpu_share_level: typing.Optional[builtins.str] = None,
        custom_attributes: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        datacenter_id: typing.Optional[builtins.str] = None,
        datastore_cluster_id: typing.Optional[builtins.str] = None,
        datastore_id: typing.Optional[builtins.str] = None,
        disk: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["VirtualMachineDisk", typing.Dict[builtins.str, typing.Any]]]]] = None,
        efi_secure_boot_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enable_disk_uuid: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enable_logging: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ept_rvi_mode: typing.Optional[builtins.str] = None,
        extra_config: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        extra_config_reboot_required: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        firmware: typing.Optional[builtins.str] = None,
        folder: typing.Optional[builtins.str] = None,
        force_power_off: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        guest_id: typing.Optional[builtins.str] = None,
        hardware_version: typing.Optional[jsii.Number] = None,
        host_system_id: typing.Optional[builtins.str] = None,
        hv_mode: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        ide_controller_count: typing.Optional[jsii.Number] = None,
        ignored_guest_ips: typing.Optional[typing.Sequence[builtins.str]] = None,
        latency_sensitivity: typing.Optional[builtins.str] = None,
        memory: typing.Optional[jsii.Number] = None,
        memory_hot_add_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        memory_limit: typing.Optional[jsii.Number] = None,
        memory_reservation: typing.Optional[jsii.Number] = None,
        memory_reservation_locked_to_max: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        memory_share_count: typing.Optional[jsii.Number] = None,
        memory_share_level: typing.Optional[builtins.str] = None,
        migrate_wait_timeout: typing.Optional[jsii.Number] = None,
        nested_hv_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        network_interface: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["VirtualMachineNetworkInterface", typing.Dict[builtins.str, typing.Any]]]]] = None,
        num_cores_per_socket: typing.Optional[jsii.Number] = None,
        num_cpus: typing.Optional[jsii.Number] = None,
        nvme_controller_count: typing.Optional[jsii.Number] = None,
        ovf_deploy: typing.Optional[typing.Union["VirtualMachineOvfDeploy", typing.Dict[builtins.str, typing.Any]]] = None,
        pci_device_id: typing.Optional[typing.Sequence[builtins.str]] = None,
        poweron_timeout: typing.Optional[jsii.Number] = None,
        replace_trigger: typing.Optional[builtins.str] = None,
        run_tools_scripts_after_power_on: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        run_tools_scripts_after_resume: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        run_tools_scripts_before_guest_reboot: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        run_tools_scripts_before_guest_shutdown: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        run_tools_scripts_before_guest_standby: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        sata_controller_count: typing.Optional[jsii.Number] = None,
        scsi_bus_sharing: typing.Optional[builtins.str] = None,
        scsi_controller_count: typing.Optional[jsii.Number] = None,
        scsi_type: typing.Optional[builtins.str] = None,
        shutdown_wait_timeout: typing.Optional[jsii.Number] = None,
        storage_policy_id: typing.Optional[builtins.str] = None,
        swap_placement_policy: typing.Optional[builtins.str] = None,
        sync_time_with_host: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        sync_time_with_host_periodically: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        tools_upgrade_policy: typing.Optional[builtins.str] = None,
        vapp: typing.Optional[typing.Union["VirtualMachineVapp", typing.Dict[builtins.str, typing.Any]]] = None,
        vbs_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        vtpm: typing.Optional[typing.Union["VirtualMachineVtpm", typing.Dict[builtins.str, typing.Any]]] = None,
        vvtd_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        wait_for_guest_ip_timeout: typing.Optional[jsii.Number] = None,
        wait_for_guest_net_routable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        wait_for_guest_net_timeout: typing.Optional[jsii.Number] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine vsphere_virtual_machine} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: The name of this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#name VirtualMachine#name}
        :param resource_pool_id: The ID of a resource pool to put the virtual machine in. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#resource_pool_id VirtualMachine#resource_pool_id}
        :param alternate_guest_name: The guest name for the operating system when guest_id is otherGuest or otherGuest64. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#alternate_guest_name VirtualMachine#alternate_guest_name}
        :param annotation: User-provided description of the virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#annotation VirtualMachine#annotation}
        :param boot_delay: The number of milliseconds to wait before starting the boot sequence. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#boot_delay VirtualMachine#boot_delay}
        :param boot_retry_delay: The number of milliseconds to wait before retrying the boot sequence. This only valid if boot_retry_enabled is true. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#boot_retry_delay VirtualMachine#boot_retry_delay}
        :param boot_retry_enabled: If set to true, a virtual machine that fails to boot will try again after the delay defined in boot_retry_delay. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#boot_retry_enabled VirtualMachine#boot_retry_enabled}
        :param cdrom: cdrom block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#cdrom VirtualMachine#cdrom}
        :param clone: clone block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#clone VirtualMachine#clone}
        :param cpu_hot_add_enabled: Allow CPUs to be added to this virtual machine while it is running. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#cpu_hot_add_enabled VirtualMachine#cpu_hot_add_enabled}
        :param cpu_hot_remove_enabled: Allow CPUs to be added to this virtual machine while it is running. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#cpu_hot_remove_enabled VirtualMachine#cpu_hot_remove_enabled}
        :param cpu_limit: The maximum amount of memory (in MB) or CPU (in MHz) that this virtual machine can consume, regardless of available resources. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#cpu_limit VirtualMachine#cpu_limit}
        :param cpu_performance_counters_enabled: Enable CPU performance counters on this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#cpu_performance_counters_enabled VirtualMachine#cpu_performance_counters_enabled}
        :param cpu_reservation: The amount of memory (in MB) or CPU (in MHz) that this virtual machine is guaranteed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#cpu_reservation VirtualMachine#cpu_reservation}
        :param cpu_share_count: The amount of shares to allocate to cpu for a custom share level. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#cpu_share_count VirtualMachine#cpu_share_count}
        :param cpu_share_level: The allocation level for cpu resources. Can be one of high, low, normal, or custom. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#cpu_share_level VirtualMachine#cpu_share_level}
        :param custom_attributes: A list of custom attributes to set on this resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#custom_attributes VirtualMachine#custom_attributes}
        :param datacenter_id: The ID of the datacenter where the VM is to be created. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#datacenter_id VirtualMachine#datacenter_id}
        :param datastore_cluster_id: The ID of a datastore cluster to put the virtual machine in. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#datastore_cluster_id VirtualMachine#datastore_cluster_id}
        :param datastore_id: The ID of the virtual machine's datastore. The virtual machine configuration is placed here, along with any virtual disks that are created without datastores. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#datastore_id VirtualMachine#datastore_id}
        :param disk: disk block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#disk VirtualMachine#disk}
        :param efi_secure_boot_enabled: When the boot type set in firmware is efi, this enables EFI secure boot. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#efi_secure_boot_enabled VirtualMachine#efi_secure_boot_enabled}
        :param enable_disk_uuid: Expose the UUIDs of attached virtual disks to the virtual machine, allowing access to them in the guest. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#enable_disk_uuid VirtualMachine#enable_disk_uuid}
        :param enable_logging: Enable logging on this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#enable_logging VirtualMachine#enable_logging}
        :param ept_rvi_mode: The EPT/RVI (hardware memory virtualization) setting for this virtual machine. Can be one of automatic, on, or off. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#ept_rvi_mode VirtualMachine#ept_rvi_mode}
        :param extra_config: Extra configuration data for this virtual machine. Can be used to supply advanced parameters not normally in configuration, such as instance metadata, or configuration data for OVF images. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#extra_config VirtualMachine#extra_config}
        :param extra_config_reboot_required: Allow the virtual machine to be rebooted when a change to ``extra_config`` occurs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#extra_config_reboot_required VirtualMachine#extra_config_reboot_required}
        :param firmware: The firmware interface to use on the virtual machine. Can be one of bios or efi. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#firmware VirtualMachine#firmware}
        :param folder: The name of the folder to locate the virtual machine in. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#folder VirtualMachine#folder}
        :param force_power_off: Set to true to force power-off a virtual machine if a graceful guest shutdown failed for a necessary operation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#force_power_off VirtualMachine#force_power_off}
        :param guest_id: The guest ID for the operating system. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#guest_id VirtualMachine#guest_id}
        :param hardware_version: The hardware version for the virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#hardware_version VirtualMachine#hardware_version}
        :param host_system_id: The ID of an optional host system to pin the virtual machine to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#host_system_id VirtualMachine#host_system_id}
        :param hv_mode: The (non-nested) hardware virtualization setting for this virtual machine. Can be one of hvAuto, hvOn, or hvOff. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#hv_mode VirtualMachine#hv_mode}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#id VirtualMachine#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param ide_controller_count: The number of IDE controllers that Terraform manages on this virtual machine. This directly affects the amount of disks you can add to the virtual machine and the maximum disk unit number. Note that lowering this value does not remove controllers. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#ide_controller_count VirtualMachine#ide_controller_count}
        :param ignored_guest_ips: List of IP addresses and CIDR networks to ignore while waiting for an IP. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#ignored_guest_ips VirtualMachine#ignored_guest_ips}
        :param latency_sensitivity: Controls the scheduling delay of the virtual machine. Use a higher sensitivity for applications that require lower latency, such as VOIP, media player applications, or applications that require frequent access to mouse or keyboard devices. Can be one of low, normal, medium, or high. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#latency_sensitivity VirtualMachine#latency_sensitivity}
        :param memory: The size of the virtual machine's memory, in MB. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#memory VirtualMachine#memory}
        :param memory_hot_add_enabled: Allow memory to be added to this virtual machine while it is running. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#memory_hot_add_enabled VirtualMachine#memory_hot_add_enabled}
        :param memory_limit: The maximum amount of memory (in MB) or CPU (in MHz) that this virtual machine can consume, regardless of available resources. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#memory_limit VirtualMachine#memory_limit}
        :param memory_reservation: The amount of memory (in MB) or CPU (in MHz) that this virtual machine is guaranteed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#memory_reservation VirtualMachine#memory_reservation}
        :param memory_reservation_locked_to_max: If set true, memory resource reservation for this virtual machine will always be equal to the virtual machine's memory size;increases in memory size will be rejected when a corresponding reservation increase is not possible. This feature may only be enabled if it is currently possible to reserve all of the virtual machine's memory. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#memory_reservation_locked_to_max VirtualMachine#memory_reservation_locked_to_max}
        :param memory_share_count: The amount of shares to allocate to memory for a custom share level. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#memory_share_count VirtualMachine#memory_share_count}
        :param memory_share_level: The allocation level for memory resources. Can be one of high, low, normal, or custom. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#memory_share_level VirtualMachine#memory_share_level}
        :param migrate_wait_timeout: The amount of time, in minutes, to wait for a vMotion operation to complete before failing. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#migrate_wait_timeout VirtualMachine#migrate_wait_timeout}
        :param nested_hv_enabled: Enable nested hardware virtualization on this virtual machine, facilitating nested virtualization in the guest. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#nested_hv_enabled VirtualMachine#nested_hv_enabled}
        :param network_interface: network_interface block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#network_interface VirtualMachine#network_interface}
        :param num_cores_per_socket: The number of cores to distribute amongst the CPUs in this virtual machine. If specified, the value supplied to num_cpus must be evenly divisible by this value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#num_cores_per_socket VirtualMachine#num_cores_per_socket}
        :param num_cpus: The number of virtual processors to assign to this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#num_cpus VirtualMachine#num_cpus}
        :param nvme_controller_count: The number of NVMe controllers that Terraform manages on this virtual machine. This directly affects the amount of disks you can add to the virtual machine and the maximum disk unit number. Note that lowering this value does not remove controllers. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#nvme_controller_count VirtualMachine#nvme_controller_count}
        :param ovf_deploy: ovf_deploy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#ovf_deploy VirtualMachine#ovf_deploy}
        :param pci_device_id: A list of PCI passthrough devices. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#pci_device_id VirtualMachine#pci_device_id}
        :param poweron_timeout: The amount of time, in seconds, that we will be trying to power on a VM. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#poweron_timeout VirtualMachine#poweron_timeout}
        :param replace_trigger: Triggers replacement of resource whenever it changes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#replace_trigger VirtualMachine#replace_trigger}
        :param run_tools_scripts_after_power_on: Enable the run of scripts after virtual machine power-on when VMware Tools is installed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#run_tools_scripts_after_power_on VirtualMachine#run_tools_scripts_after_power_on}
        :param run_tools_scripts_after_resume: Enable the run of scripts after virtual machine resume when when VMware Tools is installed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#run_tools_scripts_after_resume VirtualMachine#run_tools_scripts_after_resume}
        :param run_tools_scripts_before_guest_reboot: Enable the run of scripts before guest operating system reboot when VMware Tools is installed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#run_tools_scripts_before_guest_reboot VirtualMachine#run_tools_scripts_before_guest_reboot}
        :param run_tools_scripts_before_guest_shutdown: Enable the run of scripts before guest operating system shutdown when VMware Tools is installed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#run_tools_scripts_before_guest_shutdown VirtualMachine#run_tools_scripts_before_guest_shutdown}
        :param run_tools_scripts_before_guest_standby: Enable the run of scripts before guest operating system standby when VMware Tools is installed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#run_tools_scripts_before_guest_standby VirtualMachine#run_tools_scripts_before_guest_standby}
        :param sata_controller_count: The number of SATA controllers that Terraform manages on this virtual machine. This directly affects the amount of disks you can add to the virtual machine and the maximum disk unit number. Note that lowering this value does not remove controllers. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#sata_controller_count VirtualMachine#sata_controller_count}
        :param scsi_bus_sharing: Mode for sharing the SCSI bus. The modes are physicalSharing, virtualSharing, and noSharing. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#scsi_bus_sharing VirtualMachine#scsi_bus_sharing}
        :param scsi_controller_count: The number of SCSI controllers that Terraform manages on this virtual machine. This directly affects the amount of disks you can add to the virtual machine and the maximum disk unit number. Note that lowering this value does not remove controllers. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#scsi_controller_count VirtualMachine#scsi_controller_count}
        :param scsi_type: The type of SCSI bus this virtual machine will have. Can be one of lsilogic, lsilogic-sas or pvscsi. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#scsi_type VirtualMachine#scsi_type}
        :param shutdown_wait_timeout: The amount of time, in minutes, to wait for shutdown when making necessary updates to the virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#shutdown_wait_timeout VirtualMachine#shutdown_wait_timeout}
        :param storage_policy_id: The ID of the storage policy to assign to the virtual machine home directory. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#storage_policy_id VirtualMachine#storage_policy_id}
        :param swap_placement_policy: The swap file placement policy for this virtual machine. Can be one of inherit, hostLocal, or vmDirectory. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#swap_placement_policy VirtualMachine#swap_placement_policy}
        :param sync_time_with_host: Enable guest clock synchronization with the host. On vSphere 7.0 U1 and above, with only this setting the clock is synchronized on startup and resume. Requires VMware Tools to be installed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#sync_time_with_host VirtualMachine#sync_time_with_host}
        :param sync_time_with_host_periodically: Enable periodic clock synchronization with the host. Supported only on vSphere 7.0 U1 and above. On prior versions setting ``sync_time_with_host`` is enough for periodic synchronization. Requires VMware Tools to be installed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#sync_time_with_host_periodically VirtualMachine#sync_time_with_host_periodically}
        :param tags: A list of tag IDs to apply to this object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#tags VirtualMachine#tags}
        :param tools_upgrade_policy: Set the upgrade policy for VMware Tools. Can be one of ``manual`` or ``upgradeAtPowerCycle``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#tools_upgrade_policy VirtualMachine#tools_upgrade_policy}
        :param vapp: vapp block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#vapp VirtualMachine#vapp}
        :param vbs_enabled: Flag to specify if Virtualization-based security is enabled for this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#vbs_enabled VirtualMachine#vbs_enabled}
        :param vtpm: vtpm block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#vtpm VirtualMachine#vtpm}
        :param vvtd_enabled: Flag to specify if I/O MMU virtualization, also called Intel Virtualization Technology for Directed I/O (VT-d) and AMD I/O Virtualization (AMD-Vi or IOMMU), is enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#vvtd_enabled VirtualMachine#vvtd_enabled}
        :param wait_for_guest_ip_timeout: The amount of time, in minutes, to wait for an available IP address on this virtual machine. A value less than 1 disables the waiter. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#wait_for_guest_ip_timeout VirtualMachine#wait_for_guest_ip_timeout}
        :param wait_for_guest_net_routable: Controls whether or not the guest network waiter waits for a routable address. When false, the waiter does not wait for a default gateway, nor are IP addresses checked against any discovered default gateways as part of its success criteria. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#wait_for_guest_net_routable VirtualMachine#wait_for_guest_net_routable}
        :param wait_for_guest_net_timeout: The amount of time, in minutes, to wait for an available IP address on this virtual machine. A value less than 1 disables the waiter. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#wait_for_guest_net_timeout VirtualMachine#wait_for_guest_net_timeout}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d1beefa1ea634ee7a9f7d3716ff2c4e22d4abd84d0eba1f0ba9e3f7df6382c0)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = VirtualMachineConfig(
            name=name,
            resource_pool_id=resource_pool_id,
            alternate_guest_name=alternate_guest_name,
            annotation=annotation,
            boot_delay=boot_delay,
            boot_retry_delay=boot_retry_delay,
            boot_retry_enabled=boot_retry_enabled,
            cdrom=cdrom,
            clone=clone,
            cpu_hot_add_enabled=cpu_hot_add_enabled,
            cpu_hot_remove_enabled=cpu_hot_remove_enabled,
            cpu_limit=cpu_limit,
            cpu_performance_counters_enabled=cpu_performance_counters_enabled,
            cpu_reservation=cpu_reservation,
            cpu_share_count=cpu_share_count,
            cpu_share_level=cpu_share_level,
            custom_attributes=custom_attributes,
            datacenter_id=datacenter_id,
            datastore_cluster_id=datastore_cluster_id,
            datastore_id=datastore_id,
            disk=disk,
            efi_secure_boot_enabled=efi_secure_boot_enabled,
            enable_disk_uuid=enable_disk_uuid,
            enable_logging=enable_logging,
            ept_rvi_mode=ept_rvi_mode,
            extra_config=extra_config,
            extra_config_reboot_required=extra_config_reboot_required,
            firmware=firmware,
            folder=folder,
            force_power_off=force_power_off,
            guest_id=guest_id,
            hardware_version=hardware_version,
            host_system_id=host_system_id,
            hv_mode=hv_mode,
            id=id,
            ide_controller_count=ide_controller_count,
            ignored_guest_ips=ignored_guest_ips,
            latency_sensitivity=latency_sensitivity,
            memory=memory,
            memory_hot_add_enabled=memory_hot_add_enabled,
            memory_limit=memory_limit,
            memory_reservation=memory_reservation,
            memory_reservation_locked_to_max=memory_reservation_locked_to_max,
            memory_share_count=memory_share_count,
            memory_share_level=memory_share_level,
            migrate_wait_timeout=migrate_wait_timeout,
            nested_hv_enabled=nested_hv_enabled,
            network_interface=network_interface,
            num_cores_per_socket=num_cores_per_socket,
            num_cpus=num_cpus,
            nvme_controller_count=nvme_controller_count,
            ovf_deploy=ovf_deploy,
            pci_device_id=pci_device_id,
            poweron_timeout=poweron_timeout,
            replace_trigger=replace_trigger,
            run_tools_scripts_after_power_on=run_tools_scripts_after_power_on,
            run_tools_scripts_after_resume=run_tools_scripts_after_resume,
            run_tools_scripts_before_guest_reboot=run_tools_scripts_before_guest_reboot,
            run_tools_scripts_before_guest_shutdown=run_tools_scripts_before_guest_shutdown,
            run_tools_scripts_before_guest_standby=run_tools_scripts_before_guest_standby,
            sata_controller_count=sata_controller_count,
            scsi_bus_sharing=scsi_bus_sharing,
            scsi_controller_count=scsi_controller_count,
            scsi_type=scsi_type,
            shutdown_wait_timeout=shutdown_wait_timeout,
            storage_policy_id=storage_policy_id,
            swap_placement_policy=swap_placement_policy,
            sync_time_with_host=sync_time_with_host,
            sync_time_with_host_periodically=sync_time_with_host_periodically,
            tags=tags,
            tools_upgrade_policy=tools_upgrade_policy,
            vapp=vapp,
            vbs_enabled=vbs_enabled,
            vtpm=vtpm,
            vvtd_enabled=vvtd_enabled,
            wait_for_guest_ip_timeout=wait_for_guest_ip_timeout,
            wait_for_guest_net_routable=wait_for_guest_net_routable,
            wait_for_guest_net_timeout=wait_for_guest_net_timeout,
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
        '''Generates CDKTF code for importing a VirtualMachine resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the VirtualMachine to import.
        :param import_from_id: The id of the existing VirtualMachine that should be imported. Refer to the {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the VirtualMachine to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4d4d6c1bb222ae6efdd4bad6633ef9b17d5f522ae4bc2ba6ef57539eeb38002)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putCdrom")
    def put_cdrom(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["VirtualMachineCdrom", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1fcf134354c29061d7e4fb0169e7e7a20912c1a5b880bbdb2a4bb5ea01aada40)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putCdrom", [value]))

    @jsii.member(jsii_name="putClone")
    def put_clone(
        self,
        *,
        template_uuid: builtins.str,
        customization_spec: typing.Optional[typing.Union["VirtualMachineCloneCustomizationSpec", typing.Dict[builtins.str, typing.Any]]] = None,
        customize: typing.Optional[typing.Union["VirtualMachineCloneCustomize", typing.Dict[builtins.str, typing.Any]]] = None,
        linked_clone: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ovf_network_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        ovf_storage_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        timeout: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param template_uuid: The UUID of the source virtual machine or template. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#template_uuid VirtualMachine#template_uuid}
        :param customization_spec: customization_spec block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#customization_spec VirtualMachine#customization_spec}
        :param customize: customize block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#customize VirtualMachine#customize}
        :param linked_clone: Whether or not to create a linked clone when cloning. When this option is used, the source VM must have a single snapshot associated with it. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#linked_clone VirtualMachine#linked_clone}
        :param ovf_network_map: Mapping of ovf networks to the networks to use in vSphere. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#ovf_network_map VirtualMachine#ovf_network_map}
        :param ovf_storage_map: Mapping of ovf storage to the datastores to use in vSphere. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#ovf_storage_map VirtualMachine#ovf_storage_map}
        :param timeout: The timeout, in minutes, to wait for the virtual machine clone to complete. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#timeout VirtualMachine#timeout}
        '''
        value = VirtualMachineClone(
            template_uuid=template_uuid,
            customization_spec=customization_spec,
            customize=customize,
            linked_clone=linked_clone,
            ovf_network_map=ovf_network_map,
            ovf_storage_map=ovf_storage_map,
            timeout=timeout,
        )

        return typing.cast(None, jsii.invoke(self, "putClone", [value]))

    @jsii.member(jsii_name="putDisk")
    def put_disk(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["VirtualMachineDisk", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58fa4cc37d9bb816590e73256a903ca0d1eac1a1c25ba6b1e3602ac1de5d11b1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putDisk", [value]))

    @jsii.member(jsii_name="putNetworkInterface")
    def put_network_interface(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["VirtualMachineNetworkInterface", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ddfc29ea46f37ba23bc6d587142d3c2870f4795bc2ea5998d42291c8cd0db10a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putNetworkInterface", [value]))

    @jsii.member(jsii_name="putOvfDeploy")
    def put_ovf_deploy(
        self,
        *,
        allow_unverified_ssl_cert: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        deployment_option: typing.Optional[builtins.str] = None,
        disk_provisioning: typing.Optional[builtins.str] = None,
        enable_hidden_properties: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ip_allocation_policy: typing.Optional[builtins.str] = None,
        ip_protocol: typing.Optional[builtins.str] = None,
        local_ovf_path: typing.Optional[builtins.str] = None,
        ovf_network_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        remote_ovf_url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param allow_unverified_ssl_cert: Allow unverified ssl certificates while deploying ovf/ova from url. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#allow_unverified_ssl_cert VirtualMachine#allow_unverified_ssl_cert}
        :param deployment_option: The Deployment option to be chosen. If empty, the default option is used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#deployment_option VirtualMachine#deployment_option}
        :param disk_provisioning: An optional disk provisioning. If set, all the disks in the deployed ovf will have the same specified disk type (e.g., thin provisioned). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#disk_provisioning VirtualMachine#disk_provisioning}
        :param enable_hidden_properties: Allow properties with ovf:userConfigurable=false to be set. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#enable_hidden_properties VirtualMachine#enable_hidden_properties}
        :param ip_allocation_policy: The IP allocation policy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#ip_allocation_policy VirtualMachine#ip_allocation_policy}
        :param ip_protocol: The IP protocol. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#ip_protocol VirtualMachine#ip_protocol}
        :param local_ovf_path: The absolute path to the ovf/ova file in the local system. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#local_ovf_path VirtualMachine#local_ovf_path}
        :param ovf_network_map: The mapping of name of network identifiers from the ovf descriptor to network UUID in the VI infrastructure. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#ovf_network_map VirtualMachine#ovf_network_map}
        :param remote_ovf_url: URL to the remote ovf/ova file to be deployed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#remote_ovf_url VirtualMachine#remote_ovf_url}
        '''
        value = VirtualMachineOvfDeploy(
            allow_unverified_ssl_cert=allow_unverified_ssl_cert,
            deployment_option=deployment_option,
            disk_provisioning=disk_provisioning,
            enable_hidden_properties=enable_hidden_properties,
            ip_allocation_policy=ip_allocation_policy,
            ip_protocol=ip_protocol,
            local_ovf_path=local_ovf_path,
            ovf_network_map=ovf_network_map,
            remote_ovf_url=remote_ovf_url,
        )

        return typing.cast(None, jsii.invoke(self, "putOvfDeploy", [value]))

    @jsii.member(jsii_name="putVapp")
    def put_vapp(
        self,
        *,
        properties: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param properties: A map of customizable vApp properties and their values. Allows customization of VMs cloned from OVF templates which have customizable vApp properties. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#properties VirtualMachine#properties}
        '''
        value = VirtualMachineVapp(properties=properties)

        return typing.cast(None, jsii.invoke(self, "putVapp", [value]))

    @jsii.member(jsii_name="putVtpm")
    def put_vtpm(self, *, version: typing.Optional[builtins.str] = None) -> None:
        '''
        :param version: The version of the TPM device. Default is 2.0. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#version VirtualMachine#version}
        '''
        value = VirtualMachineVtpm(version=version)

        return typing.cast(None, jsii.invoke(self, "putVtpm", [value]))

    @jsii.member(jsii_name="resetAlternateGuestName")
    def reset_alternate_guest_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlternateGuestName", []))

    @jsii.member(jsii_name="resetAnnotation")
    def reset_annotation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAnnotation", []))

    @jsii.member(jsii_name="resetBootDelay")
    def reset_boot_delay(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBootDelay", []))

    @jsii.member(jsii_name="resetBootRetryDelay")
    def reset_boot_retry_delay(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBootRetryDelay", []))

    @jsii.member(jsii_name="resetBootRetryEnabled")
    def reset_boot_retry_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBootRetryEnabled", []))

    @jsii.member(jsii_name="resetCdrom")
    def reset_cdrom(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCdrom", []))

    @jsii.member(jsii_name="resetClone")
    def reset_clone(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClone", []))

    @jsii.member(jsii_name="resetCpuHotAddEnabled")
    def reset_cpu_hot_add_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCpuHotAddEnabled", []))

    @jsii.member(jsii_name="resetCpuHotRemoveEnabled")
    def reset_cpu_hot_remove_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCpuHotRemoveEnabled", []))

    @jsii.member(jsii_name="resetCpuLimit")
    def reset_cpu_limit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCpuLimit", []))

    @jsii.member(jsii_name="resetCpuPerformanceCountersEnabled")
    def reset_cpu_performance_counters_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCpuPerformanceCountersEnabled", []))

    @jsii.member(jsii_name="resetCpuReservation")
    def reset_cpu_reservation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCpuReservation", []))

    @jsii.member(jsii_name="resetCpuShareCount")
    def reset_cpu_share_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCpuShareCount", []))

    @jsii.member(jsii_name="resetCpuShareLevel")
    def reset_cpu_share_level(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCpuShareLevel", []))

    @jsii.member(jsii_name="resetCustomAttributes")
    def reset_custom_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomAttributes", []))

    @jsii.member(jsii_name="resetDatacenterId")
    def reset_datacenter_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatacenterId", []))

    @jsii.member(jsii_name="resetDatastoreClusterId")
    def reset_datastore_cluster_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatastoreClusterId", []))

    @jsii.member(jsii_name="resetDatastoreId")
    def reset_datastore_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatastoreId", []))

    @jsii.member(jsii_name="resetDisk")
    def reset_disk(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisk", []))

    @jsii.member(jsii_name="resetEfiSecureBootEnabled")
    def reset_efi_secure_boot_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEfiSecureBootEnabled", []))

    @jsii.member(jsii_name="resetEnableDiskUuid")
    def reset_enable_disk_uuid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableDiskUuid", []))

    @jsii.member(jsii_name="resetEnableLogging")
    def reset_enable_logging(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableLogging", []))

    @jsii.member(jsii_name="resetEptRviMode")
    def reset_ept_rvi_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEptRviMode", []))

    @jsii.member(jsii_name="resetExtraConfig")
    def reset_extra_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExtraConfig", []))

    @jsii.member(jsii_name="resetExtraConfigRebootRequired")
    def reset_extra_config_reboot_required(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExtraConfigRebootRequired", []))

    @jsii.member(jsii_name="resetFirmware")
    def reset_firmware(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFirmware", []))

    @jsii.member(jsii_name="resetFolder")
    def reset_folder(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFolder", []))

    @jsii.member(jsii_name="resetForcePowerOff")
    def reset_force_power_off(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForcePowerOff", []))

    @jsii.member(jsii_name="resetGuestId")
    def reset_guest_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGuestId", []))

    @jsii.member(jsii_name="resetHardwareVersion")
    def reset_hardware_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHardwareVersion", []))

    @jsii.member(jsii_name="resetHostSystemId")
    def reset_host_system_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHostSystemId", []))

    @jsii.member(jsii_name="resetHvMode")
    def reset_hv_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHvMode", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIdeControllerCount")
    def reset_ide_controller_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdeControllerCount", []))

    @jsii.member(jsii_name="resetIgnoredGuestIps")
    def reset_ignored_guest_ips(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIgnoredGuestIps", []))

    @jsii.member(jsii_name="resetLatencySensitivity")
    def reset_latency_sensitivity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLatencySensitivity", []))

    @jsii.member(jsii_name="resetMemory")
    def reset_memory(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMemory", []))

    @jsii.member(jsii_name="resetMemoryHotAddEnabled")
    def reset_memory_hot_add_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMemoryHotAddEnabled", []))

    @jsii.member(jsii_name="resetMemoryLimit")
    def reset_memory_limit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMemoryLimit", []))

    @jsii.member(jsii_name="resetMemoryReservation")
    def reset_memory_reservation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMemoryReservation", []))

    @jsii.member(jsii_name="resetMemoryReservationLockedToMax")
    def reset_memory_reservation_locked_to_max(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMemoryReservationLockedToMax", []))

    @jsii.member(jsii_name="resetMemoryShareCount")
    def reset_memory_share_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMemoryShareCount", []))

    @jsii.member(jsii_name="resetMemoryShareLevel")
    def reset_memory_share_level(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMemoryShareLevel", []))

    @jsii.member(jsii_name="resetMigrateWaitTimeout")
    def reset_migrate_wait_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMigrateWaitTimeout", []))

    @jsii.member(jsii_name="resetNestedHvEnabled")
    def reset_nested_hv_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNestedHvEnabled", []))

    @jsii.member(jsii_name="resetNetworkInterface")
    def reset_network_interface(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworkInterface", []))

    @jsii.member(jsii_name="resetNumCoresPerSocket")
    def reset_num_cores_per_socket(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNumCoresPerSocket", []))

    @jsii.member(jsii_name="resetNumCpus")
    def reset_num_cpus(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNumCpus", []))

    @jsii.member(jsii_name="resetNvmeControllerCount")
    def reset_nvme_controller_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNvmeControllerCount", []))

    @jsii.member(jsii_name="resetOvfDeploy")
    def reset_ovf_deploy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOvfDeploy", []))

    @jsii.member(jsii_name="resetPciDeviceId")
    def reset_pci_device_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPciDeviceId", []))

    @jsii.member(jsii_name="resetPoweronTimeout")
    def reset_poweron_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPoweronTimeout", []))

    @jsii.member(jsii_name="resetReplaceTrigger")
    def reset_replace_trigger(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReplaceTrigger", []))

    @jsii.member(jsii_name="resetRunToolsScriptsAfterPowerOn")
    def reset_run_tools_scripts_after_power_on(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRunToolsScriptsAfterPowerOn", []))

    @jsii.member(jsii_name="resetRunToolsScriptsAfterResume")
    def reset_run_tools_scripts_after_resume(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRunToolsScriptsAfterResume", []))

    @jsii.member(jsii_name="resetRunToolsScriptsBeforeGuestReboot")
    def reset_run_tools_scripts_before_guest_reboot(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRunToolsScriptsBeforeGuestReboot", []))

    @jsii.member(jsii_name="resetRunToolsScriptsBeforeGuestShutdown")
    def reset_run_tools_scripts_before_guest_shutdown(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRunToolsScriptsBeforeGuestShutdown", []))

    @jsii.member(jsii_name="resetRunToolsScriptsBeforeGuestStandby")
    def reset_run_tools_scripts_before_guest_standby(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRunToolsScriptsBeforeGuestStandby", []))

    @jsii.member(jsii_name="resetSataControllerCount")
    def reset_sata_controller_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSataControllerCount", []))

    @jsii.member(jsii_name="resetScsiBusSharing")
    def reset_scsi_bus_sharing(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScsiBusSharing", []))

    @jsii.member(jsii_name="resetScsiControllerCount")
    def reset_scsi_controller_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScsiControllerCount", []))

    @jsii.member(jsii_name="resetScsiType")
    def reset_scsi_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScsiType", []))

    @jsii.member(jsii_name="resetShutdownWaitTimeout")
    def reset_shutdown_wait_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetShutdownWaitTimeout", []))

    @jsii.member(jsii_name="resetStoragePolicyId")
    def reset_storage_policy_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStoragePolicyId", []))

    @jsii.member(jsii_name="resetSwapPlacementPolicy")
    def reset_swap_placement_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSwapPlacementPolicy", []))

    @jsii.member(jsii_name="resetSyncTimeWithHost")
    def reset_sync_time_with_host(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSyncTimeWithHost", []))

    @jsii.member(jsii_name="resetSyncTimeWithHostPeriodically")
    def reset_sync_time_with_host_periodically(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSyncTimeWithHostPeriodically", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetToolsUpgradePolicy")
    def reset_tools_upgrade_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetToolsUpgradePolicy", []))

    @jsii.member(jsii_name="resetVapp")
    def reset_vapp(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVapp", []))

    @jsii.member(jsii_name="resetVbsEnabled")
    def reset_vbs_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVbsEnabled", []))

    @jsii.member(jsii_name="resetVtpm")
    def reset_vtpm(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVtpm", []))

    @jsii.member(jsii_name="resetVvtdEnabled")
    def reset_vvtd_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVvtdEnabled", []))

    @jsii.member(jsii_name="resetWaitForGuestIpTimeout")
    def reset_wait_for_guest_ip_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWaitForGuestIpTimeout", []))

    @jsii.member(jsii_name="resetWaitForGuestNetRoutable")
    def reset_wait_for_guest_net_routable(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWaitForGuestNetRoutable", []))

    @jsii.member(jsii_name="resetWaitForGuestNetTimeout")
    def reset_wait_for_guest_net_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWaitForGuestNetTimeout", []))

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
    @jsii.member(jsii_name="cdrom")
    def cdrom(self) -> "VirtualMachineCdromList":
        return typing.cast("VirtualMachineCdromList", jsii.get(self, "cdrom"))

    @builtins.property
    @jsii.member(jsii_name="changeVersion")
    def change_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "changeVersion"))

    @builtins.property
    @jsii.member(jsii_name="clone")
    def clone(self) -> "VirtualMachineCloneOutputReference":
        return typing.cast("VirtualMachineCloneOutputReference", jsii.get(self, "clone"))

    @builtins.property
    @jsii.member(jsii_name="defaultIpAddress")
    def default_ip_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultIpAddress"))

    @builtins.property
    @jsii.member(jsii_name="disk")
    def disk(self) -> "VirtualMachineDiskList":
        return typing.cast("VirtualMachineDiskList", jsii.get(self, "disk"))

    @builtins.property
    @jsii.member(jsii_name="guestIpAddresses")
    def guest_ip_addresses(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "guestIpAddresses"))

    @builtins.property
    @jsii.member(jsii_name="imported")
    def imported(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "imported"))

    @builtins.property
    @jsii.member(jsii_name="moid")
    def moid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "moid"))

    @builtins.property
    @jsii.member(jsii_name="networkInterface")
    def network_interface(self) -> "VirtualMachineNetworkInterfaceList":
        return typing.cast("VirtualMachineNetworkInterfaceList", jsii.get(self, "networkInterface"))

    @builtins.property
    @jsii.member(jsii_name="ovfDeploy")
    def ovf_deploy(self) -> "VirtualMachineOvfDeployOutputReference":
        return typing.cast("VirtualMachineOvfDeployOutputReference", jsii.get(self, "ovfDeploy"))

    @builtins.property
    @jsii.member(jsii_name="powerState")
    def power_state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "powerState"))

    @builtins.property
    @jsii.member(jsii_name="rebootRequired")
    def reboot_required(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "rebootRequired"))

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @builtins.property
    @jsii.member(jsii_name="vapp")
    def vapp(self) -> "VirtualMachineVappOutputReference":
        return typing.cast("VirtualMachineVappOutputReference", jsii.get(self, "vapp"))

    @builtins.property
    @jsii.member(jsii_name="vappTransport")
    def vapp_transport(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "vappTransport"))

    @builtins.property
    @jsii.member(jsii_name="vmwareToolsStatus")
    def vmware_tools_status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vmwareToolsStatus"))

    @builtins.property
    @jsii.member(jsii_name="vmxPath")
    def vmx_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vmxPath"))

    @builtins.property
    @jsii.member(jsii_name="vtpm")
    def vtpm(self) -> "VirtualMachineVtpmOutputReference":
        return typing.cast("VirtualMachineVtpmOutputReference", jsii.get(self, "vtpm"))

    @builtins.property
    @jsii.member(jsii_name="alternateGuestNameInput")
    def alternate_guest_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "alternateGuestNameInput"))

    @builtins.property
    @jsii.member(jsii_name="annotationInput")
    def annotation_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "annotationInput"))

    @builtins.property
    @jsii.member(jsii_name="bootDelayInput")
    def boot_delay_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "bootDelayInput"))

    @builtins.property
    @jsii.member(jsii_name="bootRetryDelayInput")
    def boot_retry_delay_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "bootRetryDelayInput"))

    @builtins.property
    @jsii.member(jsii_name="bootRetryEnabledInput")
    def boot_retry_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "bootRetryEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="cdromInput")
    def cdrom_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VirtualMachineCdrom"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VirtualMachineCdrom"]]], jsii.get(self, "cdromInput"))

    @builtins.property
    @jsii.member(jsii_name="cloneInput")
    def clone_input(self) -> typing.Optional["VirtualMachineClone"]:
        return typing.cast(typing.Optional["VirtualMachineClone"], jsii.get(self, "cloneInput"))

    @builtins.property
    @jsii.member(jsii_name="cpuHotAddEnabledInput")
    def cpu_hot_add_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "cpuHotAddEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="cpuHotRemoveEnabledInput")
    def cpu_hot_remove_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "cpuHotRemoveEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="cpuLimitInput")
    def cpu_limit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "cpuLimitInput"))

    @builtins.property
    @jsii.member(jsii_name="cpuPerformanceCountersEnabledInput")
    def cpu_performance_counters_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "cpuPerformanceCountersEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="cpuReservationInput")
    def cpu_reservation_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "cpuReservationInput"))

    @builtins.property
    @jsii.member(jsii_name="cpuShareCountInput")
    def cpu_share_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "cpuShareCountInput"))

    @builtins.property
    @jsii.member(jsii_name="cpuShareLevelInput")
    def cpu_share_level_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cpuShareLevelInput"))

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
    @jsii.member(jsii_name="datastoreClusterIdInput")
    def datastore_cluster_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "datastoreClusterIdInput"))

    @builtins.property
    @jsii.member(jsii_name="datastoreIdInput")
    def datastore_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "datastoreIdInput"))

    @builtins.property
    @jsii.member(jsii_name="diskInput")
    def disk_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VirtualMachineDisk"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VirtualMachineDisk"]]], jsii.get(self, "diskInput"))

    @builtins.property
    @jsii.member(jsii_name="efiSecureBootEnabledInput")
    def efi_secure_boot_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "efiSecureBootEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="enableDiskUuidInput")
    def enable_disk_uuid_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enableDiskUuidInput"))

    @builtins.property
    @jsii.member(jsii_name="enableLoggingInput")
    def enable_logging_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enableLoggingInput"))

    @builtins.property
    @jsii.member(jsii_name="eptRviModeInput")
    def ept_rvi_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "eptRviModeInput"))

    @builtins.property
    @jsii.member(jsii_name="extraConfigInput")
    def extra_config_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "extraConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="extraConfigRebootRequiredInput")
    def extra_config_reboot_required_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "extraConfigRebootRequiredInput"))

    @builtins.property
    @jsii.member(jsii_name="firmwareInput")
    def firmware_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "firmwareInput"))

    @builtins.property
    @jsii.member(jsii_name="folderInput")
    def folder_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "folderInput"))

    @builtins.property
    @jsii.member(jsii_name="forcePowerOffInput")
    def force_power_off_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "forcePowerOffInput"))

    @builtins.property
    @jsii.member(jsii_name="guestIdInput")
    def guest_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "guestIdInput"))

    @builtins.property
    @jsii.member(jsii_name="hardwareVersionInput")
    def hardware_version_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "hardwareVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="hostSystemIdInput")
    def host_system_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostSystemIdInput"))

    @builtins.property
    @jsii.member(jsii_name="hvModeInput")
    def hv_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hvModeInput"))

    @builtins.property
    @jsii.member(jsii_name="ideControllerCountInput")
    def ide_controller_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ideControllerCountInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="ignoredGuestIpsInput")
    def ignored_guest_ips_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "ignoredGuestIpsInput"))

    @builtins.property
    @jsii.member(jsii_name="latencySensitivityInput")
    def latency_sensitivity_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "latencySensitivityInput"))

    @builtins.property
    @jsii.member(jsii_name="memoryHotAddEnabledInput")
    def memory_hot_add_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "memoryHotAddEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="memoryInput")
    def memory_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "memoryInput"))

    @builtins.property
    @jsii.member(jsii_name="memoryLimitInput")
    def memory_limit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "memoryLimitInput"))

    @builtins.property
    @jsii.member(jsii_name="memoryReservationInput")
    def memory_reservation_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "memoryReservationInput"))

    @builtins.property
    @jsii.member(jsii_name="memoryReservationLockedToMaxInput")
    def memory_reservation_locked_to_max_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "memoryReservationLockedToMaxInput"))

    @builtins.property
    @jsii.member(jsii_name="memoryShareCountInput")
    def memory_share_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "memoryShareCountInput"))

    @builtins.property
    @jsii.member(jsii_name="memoryShareLevelInput")
    def memory_share_level_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "memoryShareLevelInput"))

    @builtins.property
    @jsii.member(jsii_name="migrateWaitTimeoutInput")
    def migrate_wait_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "migrateWaitTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="nestedHvEnabledInput")
    def nested_hv_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "nestedHvEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="networkInterfaceInput")
    def network_interface_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VirtualMachineNetworkInterface"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VirtualMachineNetworkInterface"]]], jsii.get(self, "networkInterfaceInput"))

    @builtins.property
    @jsii.member(jsii_name="numCoresPerSocketInput")
    def num_cores_per_socket_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "numCoresPerSocketInput"))

    @builtins.property
    @jsii.member(jsii_name="numCpusInput")
    def num_cpus_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "numCpusInput"))

    @builtins.property
    @jsii.member(jsii_name="nvmeControllerCountInput")
    def nvme_controller_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "nvmeControllerCountInput"))

    @builtins.property
    @jsii.member(jsii_name="ovfDeployInput")
    def ovf_deploy_input(self) -> typing.Optional["VirtualMachineOvfDeploy"]:
        return typing.cast(typing.Optional["VirtualMachineOvfDeploy"], jsii.get(self, "ovfDeployInput"))

    @builtins.property
    @jsii.member(jsii_name="pciDeviceIdInput")
    def pci_device_id_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "pciDeviceIdInput"))

    @builtins.property
    @jsii.member(jsii_name="poweronTimeoutInput")
    def poweron_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "poweronTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="replaceTriggerInput")
    def replace_trigger_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "replaceTriggerInput"))

    @builtins.property
    @jsii.member(jsii_name="resourcePoolIdInput")
    def resource_pool_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourcePoolIdInput"))

    @builtins.property
    @jsii.member(jsii_name="runToolsScriptsAfterPowerOnInput")
    def run_tools_scripts_after_power_on_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "runToolsScriptsAfterPowerOnInput"))

    @builtins.property
    @jsii.member(jsii_name="runToolsScriptsAfterResumeInput")
    def run_tools_scripts_after_resume_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "runToolsScriptsAfterResumeInput"))

    @builtins.property
    @jsii.member(jsii_name="runToolsScriptsBeforeGuestRebootInput")
    def run_tools_scripts_before_guest_reboot_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "runToolsScriptsBeforeGuestRebootInput"))

    @builtins.property
    @jsii.member(jsii_name="runToolsScriptsBeforeGuestShutdownInput")
    def run_tools_scripts_before_guest_shutdown_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "runToolsScriptsBeforeGuestShutdownInput"))

    @builtins.property
    @jsii.member(jsii_name="runToolsScriptsBeforeGuestStandbyInput")
    def run_tools_scripts_before_guest_standby_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "runToolsScriptsBeforeGuestStandbyInput"))

    @builtins.property
    @jsii.member(jsii_name="sataControllerCountInput")
    def sata_controller_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "sataControllerCountInput"))

    @builtins.property
    @jsii.member(jsii_name="scsiBusSharingInput")
    def scsi_bus_sharing_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "scsiBusSharingInput"))

    @builtins.property
    @jsii.member(jsii_name="scsiControllerCountInput")
    def scsi_controller_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "scsiControllerCountInput"))

    @builtins.property
    @jsii.member(jsii_name="scsiTypeInput")
    def scsi_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "scsiTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="shutdownWaitTimeoutInput")
    def shutdown_wait_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "shutdownWaitTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="storagePolicyIdInput")
    def storage_policy_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "storagePolicyIdInput"))

    @builtins.property
    @jsii.member(jsii_name="swapPlacementPolicyInput")
    def swap_placement_policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "swapPlacementPolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="syncTimeWithHostInput")
    def sync_time_with_host_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "syncTimeWithHostInput"))

    @builtins.property
    @jsii.member(jsii_name="syncTimeWithHostPeriodicallyInput")
    def sync_time_with_host_periodically_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "syncTimeWithHostPeriodicallyInput"))

    @builtins.property
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property
    @jsii.member(jsii_name="toolsUpgradePolicyInput")
    def tools_upgrade_policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "toolsUpgradePolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="vappInput")
    def vapp_input(self) -> typing.Optional["VirtualMachineVapp"]:
        return typing.cast(typing.Optional["VirtualMachineVapp"], jsii.get(self, "vappInput"))

    @builtins.property
    @jsii.member(jsii_name="vbsEnabledInput")
    def vbs_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "vbsEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="vtpmInput")
    def vtpm_input(self) -> typing.Optional["VirtualMachineVtpm"]:
        return typing.cast(typing.Optional["VirtualMachineVtpm"], jsii.get(self, "vtpmInput"))

    @builtins.property
    @jsii.member(jsii_name="vvtdEnabledInput")
    def vvtd_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "vvtdEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="waitForGuestIpTimeoutInput")
    def wait_for_guest_ip_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "waitForGuestIpTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="waitForGuestNetRoutableInput")
    def wait_for_guest_net_routable_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "waitForGuestNetRoutableInput"))

    @builtins.property
    @jsii.member(jsii_name="waitForGuestNetTimeoutInput")
    def wait_for_guest_net_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "waitForGuestNetTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="alternateGuestName")
    def alternate_guest_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "alternateGuestName"))

    @alternate_guest_name.setter
    def alternate_guest_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ba5330706b1bf9965a56bf13579f5d837be248be307e77c6e722597a6e7b7f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alternateGuestName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="annotation")
    def annotation(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "annotation"))

    @annotation.setter
    def annotation(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a425e252ab02e685c4d67700ee811861319ed71e70adbf7183def42d28f87c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "annotation", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bootDelay")
    def boot_delay(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "bootDelay"))

    @boot_delay.setter
    def boot_delay(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b7e4dc7554f41f8c7e1483c8ef6742cf3d145ebed1167f7c6304ee136be408f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bootDelay", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bootRetryDelay")
    def boot_retry_delay(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "bootRetryDelay"))

    @boot_retry_delay.setter
    def boot_retry_delay(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bfc28b95f319370cc2c9b97e530fd9813c44a3678abfe74ab012b68d0a857403)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bootRetryDelay", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bootRetryEnabled")
    def boot_retry_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "bootRetryEnabled"))

    @boot_retry_enabled.setter
    def boot_retry_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f070fffa27a92511e0ce48fe3894cbc0a5500f631b3e4a25596c1409b122807f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bootRetryEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cpuHotAddEnabled")
    def cpu_hot_add_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "cpuHotAddEnabled"))

    @cpu_hot_add_enabled.setter
    def cpu_hot_add_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a55d59ce35d1defed15c6308994aa202a6c026768ed0a06322c1c94f114d5315)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cpuHotAddEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cpuHotRemoveEnabled")
    def cpu_hot_remove_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "cpuHotRemoveEnabled"))

    @cpu_hot_remove_enabled.setter
    def cpu_hot_remove_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58c3cc3a5dd3056677931e9b57925eff86b759f6dbe4926b7e7ec4b093b2d21f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cpuHotRemoveEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cpuLimit")
    def cpu_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cpuLimit"))

    @cpu_limit.setter
    def cpu_limit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2867b6768f65aa7fa89499268307d8a7e5283ab2ec89d629ac8474e2fab4c09)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cpuLimit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cpuPerformanceCountersEnabled")
    def cpu_performance_counters_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "cpuPerformanceCountersEnabled"))

    @cpu_performance_counters_enabled.setter
    def cpu_performance_counters_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5db22cc3248cb2d8ae0eaeb8f16c6bc33de67cc8a933528e52d1c523e138402)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cpuPerformanceCountersEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cpuReservation")
    def cpu_reservation(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cpuReservation"))

    @cpu_reservation.setter
    def cpu_reservation(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13afb1bed41b4bba1425acfabec583bc9bbe65d5d87a4812d0f57babaa274074)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cpuReservation", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cpuShareCount")
    def cpu_share_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cpuShareCount"))

    @cpu_share_count.setter
    def cpu_share_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aec048d2721e51416f7f9ddbea45b8a0342af9ea5c4e52d630c43ad2ee5e5531)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cpuShareCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cpuShareLevel")
    def cpu_share_level(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cpuShareLevel"))

    @cpu_share_level.setter
    def cpu_share_level(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9277e65b9386aab8fc2c4fbe351a5fe6cdc61c0b6caccf9925fb6b10803a681e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cpuShareLevel", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__da78df638e192682f8fa2155fc457957ad2886f26938892439be719a107c9479)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customAttributes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="datacenterId")
    def datacenter_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "datacenterId"))

    @datacenter_id.setter
    def datacenter_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6260a7ca67a70b82d7217c115d27e51edd256ff22c91992665d7e5253e20328b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "datacenterId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="datastoreClusterId")
    def datastore_cluster_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "datastoreClusterId"))

    @datastore_cluster_id.setter
    def datastore_cluster_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61ef44ac89d0f83f459f4591cefa392f4d24526ff6d9f4647de6643f8565c1bf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "datastoreClusterId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="datastoreId")
    def datastore_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "datastoreId"))

    @datastore_id.setter
    def datastore_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b8985bd72fba6490f3496fe95b96309036d2af442ddf4c3f7642752403f88ad3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "datastoreId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="efiSecureBootEnabled")
    def efi_secure_boot_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "efiSecureBootEnabled"))

    @efi_secure_boot_enabled.setter
    def efi_secure_boot_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e696cc23cd23d5332b48dbcd23a23c7e80a5933752803021177c7d033cff53b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "efiSecureBootEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enableDiskUuid")
    def enable_disk_uuid(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enableDiskUuid"))

    @enable_disk_uuid.setter
    def enable_disk_uuid(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d646503fc240fc209be7c84b9b8d248ef6d78e8f83d32d9e8a20dabc2498f57)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableDiskUuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enableLogging")
    def enable_logging(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enableLogging"))

    @enable_logging.setter
    def enable_logging(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__129838cac8713bebbb80ee8a05bebb726d26c113aad1c048c77d1becee692c94)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableLogging", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="eptRviMode")
    def ept_rvi_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "eptRviMode"))

    @ept_rvi_mode.setter
    def ept_rvi_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e04d68724056ae077046c133d22f7fcb40b0f0678b58549f9b78f3fb972a5e17)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "eptRviMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="extraConfig")
    def extra_config(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "extraConfig"))

    @extra_config.setter
    def extra_config(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db7f92fb8b53e5ec7cc29a32efcf58684c45c39632f9f42ccdf8ff4e1ad99903)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "extraConfig", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="extraConfigRebootRequired")
    def extra_config_reboot_required(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "extraConfigRebootRequired"))

    @extra_config_reboot_required.setter
    def extra_config_reboot_required(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__827eb4d007aa4580496441537568311b0d50a24f974c31676a9bfd4eca76f4a7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "extraConfigRebootRequired", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="firmware")
    def firmware(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "firmware"))

    @firmware.setter
    def firmware(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0354f581946a03f855a296e0e04332e97efa24527f993d7b553d49a6aade821d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "firmware", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="folder")
    def folder(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "folder"))

    @folder.setter
    def folder(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__41327995595bcd41649699b070e20b7987840b64da32b876d8803cb5d354f972)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "folder", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="forcePowerOff")
    def force_power_off(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "forcePowerOff"))

    @force_power_off.setter
    def force_power_off(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3620ada25c8f6fe96462ea3d4866056ea5cb356a6637a543315942ac9f49f20f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "forcePowerOff", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="guestId")
    def guest_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "guestId"))

    @guest_id.setter
    def guest_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a269783ceb28e05a70d58fb9a334e07557ad35e824c6d0de9b9dda6f216fbc3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "guestId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="hardwareVersion")
    def hardware_version(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "hardwareVersion"))

    @hardware_version.setter
    def hardware_version(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05ffc72f401b81bc54167cecde0d59efce6e5378a142f3fc443904d1318335f0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hardwareVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="hostSystemId")
    def host_system_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostSystemId"))

    @host_system_id.setter
    def host_system_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e454e386bc47a0784d25fa88a5c2059301cf7a107918937e0a4c7cbc3d933bb9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hostSystemId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="hvMode")
    def hv_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hvMode"))

    @hv_mode.setter
    def hv_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15f0b302e4ffd0ae9a8572de2afb5049ac7e8dc804fedbb346b1afdc41e91296)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hvMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eac110862722a9f858da985925cc26cccf7c84fab53026b73dfc14fa676a5b6e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ideControllerCount")
    def ide_controller_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ideControllerCount"))

    @ide_controller_count.setter
    def ide_controller_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5c00bd1c76ba4593b9af25ed5b6f7552d1b3c126c386387428ca468fde5a7eb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ideControllerCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ignoredGuestIps")
    def ignored_guest_ips(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "ignoredGuestIps"))

    @ignored_guest_ips.setter
    def ignored_guest_ips(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d25fec1f5441117d24961df885f3c030027acfaf06815bc2e329fe63b360ccf3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ignoredGuestIps", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="latencySensitivity")
    def latency_sensitivity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "latencySensitivity"))

    @latency_sensitivity.setter
    def latency_sensitivity(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a9db60fad9259067f72a0b794ceb75b246794d6bde61ba8117bc264eaa2c5a7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "latencySensitivity", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="memory")
    def memory(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "memory"))

    @memory.setter
    def memory(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f5daa3eb21983bb678d72dd777cf238cffc5d108d4194100f8a5a233e06d077)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "memory", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="memoryHotAddEnabled")
    def memory_hot_add_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "memoryHotAddEnabled"))

    @memory_hot_add_enabled.setter
    def memory_hot_add_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e71691b3c7a290af103e2228d8048a23cb3d443369a30867ceda6f8fea6ffe22)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "memoryHotAddEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="memoryLimit")
    def memory_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "memoryLimit"))

    @memory_limit.setter
    def memory_limit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__720d90a5bb4db23b62315c9b6e6395aa8f341cd7c97e2487bb22bf09fc5a799d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "memoryLimit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="memoryReservation")
    def memory_reservation(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "memoryReservation"))

    @memory_reservation.setter
    def memory_reservation(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07adffd6f2750f3daa8c3d011c00c65bf52472d7c2accd5a3473a573735055e0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "memoryReservation", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="memoryReservationLockedToMax")
    def memory_reservation_locked_to_max(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "memoryReservationLockedToMax"))

    @memory_reservation_locked_to_max.setter
    def memory_reservation_locked_to_max(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e69ca2b2fdfb904ad4bbf82bdfa98450307b052de6835b8e92ebeb8915e7494b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "memoryReservationLockedToMax", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="memoryShareCount")
    def memory_share_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "memoryShareCount"))

    @memory_share_count.setter
    def memory_share_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2803b3e6d763cb91ad7db58806318cb4f5c219b3ca2905572da8a5c23377601f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "memoryShareCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="memoryShareLevel")
    def memory_share_level(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "memoryShareLevel"))

    @memory_share_level.setter
    def memory_share_level(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f8a8daccba8c1143b215685c560c890936e8aeefc730a4874a5a4e7ff9ddec57)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "memoryShareLevel", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="migrateWaitTimeout")
    def migrate_wait_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "migrateWaitTimeout"))

    @migrate_wait_timeout.setter
    def migrate_wait_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1aed230e1a0ba99924292a0f6f56f89b03417d9f80c2cfe7d3f8298bbb0e424b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "migrateWaitTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6ca57f2dfe7833c6b11e6beb69cbdd32ecc390a2780eed2fcb7693e35ef7b2f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="nestedHvEnabled")
    def nested_hv_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "nestedHvEnabled"))

    @nested_hv_enabled.setter
    def nested_hv_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e722deb0ded51bc305f34a4a6d762971a1c1d18ae93ff6fd8922bbe0fe72b43)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nestedHvEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="numCoresPerSocket")
    def num_cores_per_socket(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numCoresPerSocket"))

    @num_cores_per_socket.setter
    def num_cores_per_socket(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f60f8cd4e3b1fad5f0b427d7c8941d92fdb47d20f5923dfb24805bb6a808c88)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "numCoresPerSocket", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="numCpus")
    def num_cpus(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numCpus"))

    @num_cpus.setter
    def num_cpus(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__793d0cff2c3d7cb8c7e08e825d7d9bd91064987c5a43abc1f6cdb82a022bbed5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "numCpus", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="nvmeControllerCount")
    def nvme_controller_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "nvmeControllerCount"))

    @nvme_controller_count.setter
    def nvme_controller_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0da05056b45fb7f8dd0088c9ebb962cc9a0f1bdab9131405afb9a3ff0c0e81b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nvmeControllerCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pciDeviceId")
    def pci_device_id(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "pciDeviceId"))

    @pci_device_id.setter
    def pci_device_id(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e6ed5237d069a9f34f8d01143f3048925ce3cbcb43810e80e7ea128d46951ad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pciDeviceId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="poweronTimeout")
    def poweron_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "poweronTimeout"))

    @poweron_timeout.setter
    def poweron_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__50a52787fb5a9ed86cf7df6e46b142b67287b023519785ac33f5cd15ff3d3b71)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "poweronTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="replaceTrigger")
    def replace_trigger(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "replaceTrigger"))

    @replace_trigger.setter
    def replace_trigger(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__345a4f39fe904c3351766e38b06027bdb8ebbc4338d5e6a13d5f622c57878ae7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "replaceTrigger", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="resourcePoolId")
    def resource_pool_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourcePoolId"))

    @resource_pool_id.setter
    def resource_pool_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae7da94511492519e1e921c8e49f66e8a88a3439f2e3be2eff5635f38da8d494)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resourcePoolId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="runToolsScriptsAfterPowerOn")
    def run_tools_scripts_after_power_on(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "runToolsScriptsAfterPowerOn"))

    @run_tools_scripts_after_power_on.setter
    def run_tools_scripts_after_power_on(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f37a48968cd3df7669956ad3b7697b790c0cba9776cc3ddab6650490da3039c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "runToolsScriptsAfterPowerOn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="runToolsScriptsAfterResume")
    def run_tools_scripts_after_resume(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "runToolsScriptsAfterResume"))

    @run_tools_scripts_after_resume.setter
    def run_tools_scripts_after_resume(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef023fc8dbb7c4b49d2e0ed4ba489a690f05ea5e203499da4e8b2a7d62784987)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "runToolsScriptsAfterResume", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="runToolsScriptsBeforeGuestReboot")
    def run_tools_scripts_before_guest_reboot(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "runToolsScriptsBeforeGuestReboot"))

    @run_tools_scripts_before_guest_reboot.setter
    def run_tools_scripts_before_guest_reboot(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__69897ede9bc9831bedc9f4648be0447dc28eb70a4577beb7a723797b9e25bd4a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "runToolsScriptsBeforeGuestReboot", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="runToolsScriptsBeforeGuestShutdown")
    def run_tools_scripts_before_guest_shutdown(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "runToolsScriptsBeforeGuestShutdown"))

    @run_tools_scripts_before_guest_shutdown.setter
    def run_tools_scripts_before_guest_shutdown(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67e89a91b69dc10e7014912688cfb5102aad4449079d53897bf4cd15e0f6f2da)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "runToolsScriptsBeforeGuestShutdown", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="runToolsScriptsBeforeGuestStandby")
    def run_tools_scripts_before_guest_standby(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "runToolsScriptsBeforeGuestStandby"))

    @run_tools_scripts_before_guest_standby.setter
    def run_tools_scripts_before_guest_standby(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a109095a3083c8cdf5fd6d36447e8d521f8d65e8d003e325ccd5c022df4170c8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "runToolsScriptsBeforeGuestStandby", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sataControllerCount")
    def sata_controller_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "sataControllerCount"))

    @sata_controller_count.setter
    def sata_controller_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bbfbb2f31a1572191b3c0e07825c7f4563e2d53ee4efff1347f3c6bb45401d73)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sataControllerCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scsiBusSharing")
    def scsi_bus_sharing(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scsiBusSharing"))

    @scsi_bus_sharing.setter
    def scsi_bus_sharing(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72287081637ebd7d4c1c80b9d458f71c3b053cc61d6a2c5fbec5ca36a578e041)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scsiBusSharing", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scsiControllerCount")
    def scsi_controller_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "scsiControllerCount"))

    @scsi_controller_count.setter
    def scsi_controller_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__16dbe14cde4ddbce43d93e76a7df105e22bb3a0cd0c30e0afc6c0147b8c11d7a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scsiControllerCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scsiType")
    def scsi_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scsiType"))

    @scsi_type.setter
    def scsi_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d00bf341c47c273df5376b299f9f67dc4c6ff2c0a36b4d5140ccc110652b086)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scsiType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="shutdownWaitTimeout")
    def shutdown_wait_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "shutdownWaitTimeout"))

    @shutdown_wait_timeout.setter
    def shutdown_wait_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a4fd4c63ea830a7d8bd6ec3089f77bd77c87d2fb1d3d6076edd62e7fbecbb1d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "shutdownWaitTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="storagePolicyId")
    def storage_policy_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storagePolicyId"))

    @storage_policy_id.setter
    def storage_policy_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__636617ed770a4a086968d6bd0c1bd2b6a4255e9c0cded5dcc0f2b023e6c4e7cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "storagePolicyId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="swapPlacementPolicy")
    def swap_placement_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "swapPlacementPolicy"))

    @swap_placement_policy.setter
    def swap_placement_policy(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de1d3b83cae9c88a95d4e4e7a489b1ada03c2671d3d045cfd749a621c648fa0a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "swapPlacementPolicy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="syncTimeWithHost")
    def sync_time_with_host(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "syncTimeWithHost"))

    @sync_time_with_host.setter
    def sync_time_with_host(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5bf36f926d0426eef8510ad8be2cdc528b57e9b839d893f3c1ceb6473c2eaf4c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "syncTimeWithHost", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="syncTimeWithHostPeriodically")
    def sync_time_with_host_periodically(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "syncTimeWithHostPeriodically"))

    @sync_time_with_host_periodically.setter
    def sync_time_with_host_periodically(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__705b9a2255149661521697571135163ab95dfd7ba275dd2e44a4f0973cbe398e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "syncTimeWithHostPeriodically", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c6d1f5eb89924e796e8640f75235a5f134b3be3066d9d2b99090a342cd402e80)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="toolsUpgradePolicy")
    def tools_upgrade_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "toolsUpgradePolicy"))

    @tools_upgrade_policy.setter
    def tools_upgrade_policy(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5fb55dd2605b80afbdd6f1dfeea1cfc37a75538bf1a3952d722e510fe3555a5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "toolsUpgradePolicy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vbsEnabled")
    def vbs_enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "vbsEnabled"))

    @vbs_enabled.setter
    def vbs_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b7fece8c5dc5d778a776849995e38e7f30fc4e918d915c6a5dea0d27390994fa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vbsEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vvtdEnabled")
    def vvtd_enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "vvtdEnabled"))

    @vvtd_enabled.setter
    def vvtd_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eabfe61f73841c75a9c95cf6b54df2307b4259e76893d0b18df08811fac2557f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vvtdEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="waitForGuestIpTimeout")
    def wait_for_guest_ip_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "waitForGuestIpTimeout"))

    @wait_for_guest_ip_timeout.setter
    def wait_for_guest_ip_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d659b4207b24633382fd564a946924d6aa7052dd96ecf3371a18f0754aed6856)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "waitForGuestIpTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="waitForGuestNetRoutable")
    def wait_for_guest_net_routable(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "waitForGuestNetRoutable"))

    @wait_for_guest_net_routable.setter
    def wait_for_guest_net_routable(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__073ecab6b23708c92a289d888312aa17c27926ed0ae68c43b9e637727e9862f1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "waitForGuestNetRoutable", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="waitForGuestNetTimeout")
    def wait_for_guest_net_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "waitForGuestNetTimeout"))

    @wait_for_guest_net_timeout.setter
    def wait_for_guest_net_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a8413ab56184260d6d1d431ddf08a98493b146e1571ce108ca49c6c2ca22be6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "waitForGuestNetTimeout", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.virtualMachine.VirtualMachineCdrom",
    jsii_struct_bases=[],
    name_mapping={
        "client_device": "clientDevice",
        "datastore_id": "datastoreId",
        "path": "path",
    },
)
class VirtualMachineCdrom:
    def __init__(
        self,
        *,
        client_device: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        datastore_id: typing.Optional[builtins.str] = None,
        path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param client_device: Indicates whether the device should be mapped to a remote client device. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#client_device VirtualMachine#client_device}
        :param datastore_id: The datastore ID the ISO is located on. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#datastore_id VirtualMachine#datastore_id}
        :param path: The path to the ISO file on the datastore. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#path VirtualMachine#path}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db6c206832ac558dd3570c60f20393b92900d2195b60691c29dedb8c08333591)
            check_type(argname="argument client_device", value=client_device, expected_type=type_hints["client_device"])
            check_type(argname="argument datastore_id", value=datastore_id, expected_type=type_hints["datastore_id"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if client_device is not None:
            self._values["client_device"] = client_device
        if datastore_id is not None:
            self._values["datastore_id"] = datastore_id
        if path is not None:
            self._values["path"] = path

    @builtins.property
    def client_device(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Indicates whether the device should be mapped to a remote client device.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#client_device VirtualMachine#client_device}
        '''
        result = self._values.get("client_device")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def datastore_id(self) -> typing.Optional[builtins.str]:
        '''The datastore ID the ISO is located on.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#datastore_id VirtualMachine#datastore_id}
        '''
        result = self._values.get("datastore_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''The path to the ISO file on the datastore.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#path VirtualMachine#path}
        '''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VirtualMachineCdrom(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class VirtualMachineCdromList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.virtualMachine.VirtualMachineCdromList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__da099c8719c5562b667440a30667628f072388bbdbe288e9c21a2226c22994cb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "VirtualMachineCdromOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7a95734842c9148a4d1c948d643c535aab0cf67d607d74a5050823f9022af67)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("VirtualMachineCdromOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55a393dddf3b40a315f0d7d3d32327e0031a36eb42fe2002a701d2d7c4c4f6ae)
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
            type_hints = typing.get_type_hints(_typecheckingstub__937d6be279adb9a1e5c1ec7d82bd108319a6f43b06404263a41657d8c8f254c2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b4f83413ef2cdc08322e49d33dc1014edd837a1138feb647c9b6d080d628edaa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VirtualMachineCdrom]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VirtualMachineCdrom]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VirtualMachineCdrom]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ab986fb66af572482aaec81fb552041770b9afb55d4c5e7299f56f8acd2a9e5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class VirtualMachineCdromOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.virtualMachine.VirtualMachineCdromOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8b341cf6c0e3df967c4469230fdc8fb5f7dd3b34c6e70f580f9acff90fc811dd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetClientDevice")
    def reset_client_device(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClientDevice", []))

    @jsii.member(jsii_name="resetDatastoreId")
    def reset_datastore_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatastoreId", []))

    @jsii.member(jsii_name="resetPath")
    def reset_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPath", []))

    @builtins.property
    @jsii.member(jsii_name="deviceAddress")
    def device_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deviceAddress"))

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "key"))

    @builtins.property
    @jsii.member(jsii_name="clientDeviceInput")
    def client_device_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "clientDeviceInput"))

    @builtins.property
    @jsii.member(jsii_name="datastoreIdInput")
    def datastore_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "datastoreIdInput"))

    @builtins.property
    @jsii.member(jsii_name="pathInput")
    def path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pathInput"))

    @builtins.property
    @jsii.member(jsii_name="clientDevice")
    def client_device(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "clientDevice"))

    @client_device.setter
    def client_device(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4fa64659643c9868ee0c5a85471e433bf07d8359455c3c8790e10219dfd953cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientDevice", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="datastoreId")
    def datastore_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "datastoreId"))

    @datastore_id.setter
    def datastore_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4118cba22f708b5344cd83e26ea1725166fbbde7fdd67e2c0f545412b5b1414)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "datastoreId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @path.setter
    def path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ebd5ac9bc5fd966654f211e7c5ff35fd712c7a82398a1a477a5bdcfa63e28a5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "path", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VirtualMachineCdrom]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VirtualMachineCdrom]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VirtualMachineCdrom]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__077ab4575066b341ad5cfc8e3cc596196c332d69e22489be6d7585ab67ef482f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.virtualMachine.VirtualMachineClone",
    jsii_struct_bases=[],
    name_mapping={
        "template_uuid": "templateUuid",
        "customization_spec": "customizationSpec",
        "customize": "customize",
        "linked_clone": "linkedClone",
        "ovf_network_map": "ovfNetworkMap",
        "ovf_storage_map": "ovfStorageMap",
        "timeout": "timeout",
    },
)
class VirtualMachineClone:
    def __init__(
        self,
        *,
        template_uuid: builtins.str,
        customization_spec: typing.Optional[typing.Union["VirtualMachineCloneCustomizationSpec", typing.Dict[builtins.str, typing.Any]]] = None,
        customize: typing.Optional[typing.Union["VirtualMachineCloneCustomize", typing.Dict[builtins.str, typing.Any]]] = None,
        linked_clone: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ovf_network_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        ovf_storage_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        timeout: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param template_uuid: The UUID of the source virtual machine or template. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#template_uuid VirtualMachine#template_uuid}
        :param customization_spec: customization_spec block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#customization_spec VirtualMachine#customization_spec}
        :param customize: customize block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#customize VirtualMachine#customize}
        :param linked_clone: Whether or not to create a linked clone when cloning. When this option is used, the source VM must have a single snapshot associated with it. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#linked_clone VirtualMachine#linked_clone}
        :param ovf_network_map: Mapping of ovf networks to the networks to use in vSphere. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#ovf_network_map VirtualMachine#ovf_network_map}
        :param ovf_storage_map: Mapping of ovf storage to the datastores to use in vSphere. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#ovf_storage_map VirtualMachine#ovf_storage_map}
        :param timeout: The timeout, in minutes, to wait for the virtual machine clone to complete. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#timeout VirtualMachine#timeout}
        '''
        if isinstance(customization_spec, dict):
            customization_spec = VirtualMachineCloneCustomizationSpec(**customization_spec)
        if isinstance(customize, dict):
            customize = VirtualMachineCloneCustomize(**customize)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__293830fb9774d771f538120dcfa765be0b267765980eefe0dc73767ba0f8d9fc)
            check_type(argname="argument template_uuid", value=template_uuid, expected_type=type_hints["template_uuid"])
            check_type(argname="argument customization_spec", value=customization_spec, expected_type=type_hints["customization_spec"])
            check_type(argname="argument customize", value=customize, expected_type=type_hints["customize"])
            check_type(argname="argument linked_clone", value=linked_clone, expected_type=type_hints["linked_clone"])
            check_type(argname="argument ovf_network_map", value=ovf_network_map, expected_type=type_hints["ovf_network_map"])
            check_type(argname="argument ovf_storage_map", value=ovf_storage_map, expected_type=type_hints["ovf_storage_map"])
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "template_uuid": template_uuid,
        }
        if customization_spec is not None:
            self._values["customization_spec"] = customization_spec
        if customize is not None:
            self._values["customize"] = customize
        if linked_clone is not None:
            self._values["linked_clone"] = linked_clone
        if ovf_network_map is not None:
            self._values["ovf_network_map"] = ovf_network_map
        if ovf_storage_map is not None:
            self._values["ovf_storage_map"] = ovf_storage_map
        if timeout is not None:
            self._values["timeout"] = timeout

    @builtins.property
    def template_uuid(self) -> builtins.str:
        '''The UUID of the source virtual machine or template.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#template_uuid VirtualMachine#template_uuid}
        '''
        result = self._values.get("template_uuid")
        assert result is not None, "Required property 'template_uuid' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def customization_spec(
        self,
    ) -> typing.Optional["VirtualMachineCloneCustomizationSpec"]:
        '''customization_spec block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#customization_spec VirtualMachine#customization_spec}
        '''
        result = self._values.get("customization_spec")
        return typing.cast(typing.Optional["VirtualMachineCloneCustomizationSpec"], result)

    @builtins.property
    def customize(self) -> typing.Optional["VirtualMachineCloneCustomize"]:
        '''customize block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#customize VirtualMachine#customize}
        '''
        result = self._values.get("customize")
        return typing.cast(typing.Optional["VirtualMachineCloneCustomize"], result)

    @builtins.property
    def linked_clone(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether or not to create a linked clone when cloning.

        When this option is used, the source VM must have a single snapshot associated with it.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#linked_clone VirtualMachine#linked_clone}
        '''
        result = self._values.get("linked_clone")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def ovf_network_map(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Mapping of ovf networks to the networks to use in vSphere.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#ovf_network_map VirtualMachine#ovf_network_map}
        '''
        result = self._values.get("ovf_network_map")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def ovf_storage_map(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Mapping of ovf storage to the datastores to use in vSphere.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#ovf_storage_map VirtualMachine#ovf_storage_map}
        '''
        result = self._values.get("ovf_storage_map")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def timeout(self) -> typing.Optional[jsii.Number]:
        '''The timeout, in minutes, to wait for the virtual machine clone to complete.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#timeout VirtualMachine#timeout}
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VirtualMachineClone(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.virtualMachine.VirtualMachineCloneCustomizationSpec",
    jsii_struct_bases=[],
    name_mapping={"id": "id", "timeout": "timeout"},
)
class VirtualMachineCloneCustomizationSpec:
    def __init__(
        self,
        *,
        id: builtins.str,
        timeout: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param id: The unique identifier of the customization specification is its name and is unique per vCenter Server instance. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#id VirtualMachine#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param timeout: The amount of time, in minutes, to wait for guest OS customization to complete before returning with an error. Setting this value to 0 or a negative value skips the waiter. Default: 10. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#timeout VirtualMachine#timeout}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2114155cbd07283ebabb6160517744d3ca02bed7acce1ed8ff750110801694ba)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "id": id,
        }
        if timeout is not None:
            self._values["timeout"] = timeout

    @builtins.property
    def id(self) -> builtins.str:
        '''The unique identifier of the customization specification is its name and is unique per vCenter Server instance.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#id VirtualMachine#id}

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def timeout(self) -> typing.Optional[jsii.Number]:
        '''The amount of time, in minutes, to wait for guest OS customization to complete before returning with an error.

        Setting this value to 0 or a negative value skips the waiter. Default: 10.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#timeout VirtualMachine#timeout}
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VirtualMachineCloneCustomizationSpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class VirtualMachineCloneCustomizationSpecOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.virtualMachine.VirtualMachineCloneCustomizationSpecOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__677eddd7ffe1818393fb18badf2b0ae2fbb24bf8f212b0fc3c0a4731ed9e30a3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetTimeout")
    def reset_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeout", []))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutInput")
    def timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "timeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c2dbf13abb60268fe659973b3911e12bdb5feda266b41b01ea1700822e49193)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="timeout")
    def timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "timeout"))

    @timeout.setter
    def timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52b928a80f02abf621cf57c8aef5dbbb00a07f1123254dddc387057a530e026c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[VirtualMachineCloneCustomizationSpec]:
        return typing.cast(typing.Optional[VirtualMachineCloneCustomizationSpec], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[VirtualMachineCloneCustomizationSpec],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51ad427d15ce2ef0ecb05aac568c4d4a2685d44ba1940ddc59b82f359a7c0bc2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.virtualMachine.VirtualMachineCloneCustomize",
    jsii_struct_bases=[],
    name_mapping={
        "dns_server_list": "dnsServerList",
        "dns_suffix_list": "dnsSuffixList",
        "ipv4_gateway": "ipv4Gateway",
        "ipv6_gateway": "ipv6Gateway",
        "linux_options": "linuxOptions",
        "network_interface": "networkInterface",
        "timeout": "timeout",
        "windows_options": "windowsOptions",
        "windows_sysprep_text": "windowsSysprepText",
    },
)
class VirtualMachineCloneCustomize:
    def __init__(
        self,
        *,
        dns_server_list: typing.Optional[typing.Sequence[builtins.str]] = None,
        dns_suffix_list: typing.Optional[typing.Sequence[builtins.str]] = None,
        ipv4_gateway: typing.Optional[builtins.str] = None,
        ipv6_gateway: typing.Optional[builtins.str] = None,
        linux_options: typing.Optional[typing.Union["VirtualMachineCloneCustomizeLinuxOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        network_interface: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["VirtualMachineCloneCustomizeNetworkInterface", typing.Dict[builtins.str, typing.Any]]]]] = None,
        timeout: typing.Optional[jsii.Number] = None,
        windows_options: typing.Optional[typing.Union["VirtualMachineCloneCustomizeWindowsOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        windows_sysprep_text: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param dns_server_list: The list of DNS servers for a virtual network adapter with a static IP address. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#dns_server_list VirtualMachine#dns_server_list}
        :param dns_suffix_list: A list of DNS search domains to add to the DNS configuration on the virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#dns_suffix_list VirtualMachine#dns_suffix_list}
        :param ipv4_gateway: The IPv4 default gateway when using network_interface customization on the virtual machine. This address must be local to a static IPv4 address configured in an interface sub-resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#ipv4_gateway VirtualMachine#ipv4_gateway}
        :param ipv6_gateway: The IPv6 default gateway when using network_interface customization on the virtual machine. This address must be local to a static IPv4 address configured in an interface sub-resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#ipv6_gateway VirtualMachine#ipv6_gateway}
        :param linux_options: linux_options block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#linux_options VirtualMachine#linux_options}
        :param network_interface: network_interface block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#network_interface VirtualMachine#network_interface}
        :param timeout: The amount of time, in minutes, to wait for guest OS customization to complete before returning with an error. Setting this value to 0 or a negative value skips the waiter. Default: 10. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#timeout VirtualMachine#timeout}
        :param windows_options: windows_options block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#windows_options VirtualMachine#windows_options}
        :param windows_sysprep_text: Use this option to specify a windows sysprep file directly. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#windows_sysprep_text VirtualMachine#windows_sysprep_text}
        '''
        if isinstance(linux_options, dict):
            linux_options = VirtualMachineCloneCustomizeLinuxOptions(**linux_options)
        if isinstance(windows_options, dict):
            windows_options = VirtualMachineCloneCustomizeWindowsOptions(**windows_options)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d12c07cc841613da4f6fc2384f11a6e19de4bf27d3032cca2ed100c0b43f2b0)
            check_type(argname="argument dns_server_list", value=dns_server_list, expected_type=type_hints["dns_server_list"])
            check_type(argname="argument dns_suffix_list", value=dns_suffix_list, expected_type=type_hints["dns_suffix_list"])
            check_type(argname="argument ipv4_gateway", value=ipv4_gateway, expected_type=type_hints["ipv4_gateway"])
            check_type(argname="argument ipv6_gateway", value=ipv6_gateway, expected_type=type_hints["ipv6_gateway"])
            check_type(argname="argument linux_options", value=linux_options, expected_type=type_hints["linux_options"])
            check_type(argname="argument network_interface", value=network_interface, expected_type=type_hints["network_interface"])
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
            check_type(argname="argument windows_options", value=windows_options, expected_type=type_hints["windows_options"])
            check_type(argname="argument windows_sysprep_text", value=windows_sysprep_text, expected_type=type_hints["windows_sysprep_text"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if dns_server_list is not None:
            self._values["dns_server_list"] = dns_server_list
        if dns_suffix_list is not None:
            self._values["dns_suffix_list"] = dns_suffix_list
        if ipv4_gateway is not None:
            self._values["ipv4_gateway"] = ipv4_gateway
        if ipv6_gateway is not None:
            self._values["ipv6_gateway"] = ipv6_gateway
        if linux_options is not None:
            self._values["linux_options"] = linux_options
        if network_interface is not None:
            self._values["network_interface"] = network_interface
        if timeout is not None:
            self._values["timeout"] = timeout
        if windows_options is not None:
            self._values["windows_options"] = windows_options
        if windows_sysprep_text is not None:
            self._values["windows_sysprep_text"] = windows_sysprep_text

    @builtins.property
    def dns_server_list(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The list of DNS servers for a virtual network adapter with a static IP address.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#dns_server_list VirtualMachine#dns_server_list}
        '''
        result = self._values.get("dns_server_list")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def dns_suffix_list(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of DNS search domains to add to the DNS configuration on the virtual machine.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#dns_suffix_list VirtualMachine#dns_suffix_list}
        '''
        result = self._values.get("dns_suffix_list")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def ipv4_gateway(self) -> typing.Optional[builtins.str]:
        '''The IPv4 default gateway when using network_interface customization on the virtual machine.

        This address must be local to a static IPv4 address configured in an interface sub-resource.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#ipv4_gateway VirtualMachine#ipv4_gateway}
        '''
        result = self._values.get("ipv4_gateway")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ipv6_gateway(self) -> typing.Optional[builtins.str]:
        '''The IPv6 default gateway when using network_interface customization on the virtual machine.

        This address must be local to a static IPv4 address configured in an interface sub-resource.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#ipv6_gateway VirtualMachine#ipv6_gateway}
        '''
        result = self._values.get("ipv6_gateway")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def linux_options(
        self,
    ) -> typing.Optional["VirtualMachineCloneCustomizeLinuxOptions"]:
        '''linux_options block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#linux_options VirtualMachine#linux_options}
        '''
        result = self._values.get("linux_options")
        return typing.cast(typing.Optional["VirtualMachineCloneCustomizeLinuxOptions"], result)

    @builtins.property
    def network_interface(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VirtualMachineCloneCustomizeNetworkInterface"]]]:
        '''network_interface block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#network_interface VirtualMachine#network_interface}
        '''
        result = self._values.get("network_interface")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VirtualMachineCloneCustomizeNetworkInterface"]]], result)

    @builtins.property
    def timeout(self) -> typing.Optional[jsii.Number]:
        '''The amount of time, in minutes, to wait for guest OS customization to complete before returning with an error.

        Setting this value to 0 or a negative value skips the waiter. Default: 10.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#timeout VirtualMachine#timeout}
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def windows_options(
        self,
    ) -> typing.Optional["VirtualMachineCloneCustomizeWindowsOptions"]:
        '''windows_options block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#windows_options VirtualMachine#windows_options}
        '''
        result = self._values.get("windows_options")
        return typing.cast(typing.Optional["VirtualMachineCloneCustomizeWindowsOptions"], result)

    @builtins.property
    def windows_sysprep_text(self) -> typing.Optional[builtins.str]:
        '''Use this option to specify a windows sysprep file directly.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#windows_sysprep_text VirtualMachine#windows_sysprep_text}
        '''
        result = self._values.get("windows_sysprep_text")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VirtualMachineCloneCustomize(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.virtualMachine.VirtualMachineCloneCustomizeLinuxOptions",
    jsii_struct_bases=[],
    name_mapping={
        "domain": "domain",
        "host_name": "hostName",
        "hw_clock_utc": "hwClockUtc",
        "script_text": "scriptText",
        "time_zone": "timeZone",
    },
)
class VirtualMachineCloneCustomizeLinuxOptions:
    def __init__(
        self,
        *,
        domain: builtins.str,
        host_name: builtins.str,
        hw_clock_utc: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        script_text: typing.Optional[builtins.str] = None,
        time_zone: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param domain: The domain name for this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#domain VirtualMachine#domain}
        :param host_name: The hostname for this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#host_name VirtualMachine#host_name}
        :param hw_clock_utc: Specifies whether or not the hardware clock should be in UTC or not. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#hw_clock_utc VirtualMachine#hw_clock_utc}
        :param script_text: The customization script to run before and or after guest customization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#script_text VirtualMachine#script_text}
        :param time_zone: Customize the time zone on the VM. This should be a time zone-style entry, like America/Los_Angeles. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#time_zone VirtualMachine#time_zone}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1556122300d0463e6170c85145f524655221d1753b1ae06b0627cbf408520a50)
            check_type(argname="argument domain", value=domain, expected_type=type_hints["domain"])
            check_type(argname="argument host_name", value=host_name, expected_type=type_hints["host_name"])
            check_type(argname="argument hw_clock_utc", value=hw_clock_utc, expected_type=type_hints["hw_clock_utc"])
            check_type(argname="argument script_text", value=script_text, expected_type=type_hints["script_text"])
            check_type(argname="argument time_zone", value=time_zone, expected_type=type_hints["time_zone"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domain": domain,
            "host_name": host_name,
        }
        if hw_clock_utc is not None:
            self._values["hw_clock_utc"] = hw_clock_utc
        if script_text is not None:
            self._values["script_text"] = script_text
        if time_zone is not None:
            self._values["time_zone"] = time_zone

    @builtins.property
    def domain(self) -> builtins.str:
        '''The domain name for this virtual machine.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#domain VirtualMachine#domain}
        '''
        result = self._values.get("domain")
        assert result is not None, "Required property 'domain' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def host_name(self) -> builtins.str:
        '''The hostname for this virtual machine.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#host_name VirtualMachine#host_name}
        '''
        result = self._values.get("host_name")
        assert result is not None, "Required property 'host_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def hw_clock_utc(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Specifies whether or not the hardware clock should be in UTC or not.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#hw_clock_utc VirtualMachine#hw_clock_utc}
        '''
        result = self._values.get("hw_clock_utc")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def script_text(self) -> typing.Optional[builtins.str]:
        '''The customization script to run before and or after guest customization.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#script_text VirtualMachine#script_text}
        '''
        result = self._values.get("script_text")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def time_zone(self) -> typing.Optional[builtins.str]:
        '''Customize the time zone on the VM. This should be a time zone-style entry, like America/Los_Angeles.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#time_zone VirtualMachine#time_zone}
        '''
        result = self._values.get("time_zone")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VirtualMachineCloneCustomizeLinuxOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class VirtualMachineCloneCustomizeLinuxOptionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.virtualMachine.VirtualMachineCloneCustomizeLinuxOptionsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__713fae389811e3c67e0da9820c9b9770bdc5dbaebb0c7d60d0e6b6c0b701590f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetHwClockUtc")
    def reset_hw_clock_utc(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHwClockUtc", []))

    @jsii.member(jsii_name="resetScriptText")
    def reset_script_text(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScriptText", []))

    @jsii.member(jsii_name="resetTimeZone")
    def reset_time_zone(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeZone", []))

    @builtins.property
    @jsii.member(jsii_name="domainInput")
    def domain_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainInput"))

    @builtins.property
    @jsii.member(jsii_name="hostNameInput")
    def host_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostNameInput"))

    @builtins.property
    @jsii.member(jsii_name="hwClockUtcInput")
    def hw_clock_utc_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "hwClockUtcInput"))

    @builtins.property
    @jsii.member(jsii_name="scriptTextInput")
    def script_text_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "scriptTextInput"))

    @builtins.property
    @jsii.member(jsii_name="timeZoneInput")
    def time_zone_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "timeZoneInput"))

    @builtins.property
    @jsii.member(jsii_name="domain")
    def domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domain"))

    @domain.setter
    def domain(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9716db47d936e76a2b4d8404355302d934a211dc26863474d15e2ec3908b8c0e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "domain", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="hostName")
    def host_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostName"))

    @host_name.setter
    def host_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e6826c595a2a9e79747c5835281983f0d711faceb6d9cf712b45546d6958279)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hostName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="hwClockUtc")
    def hw_clock_utc(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "hwClockUtc"))

    @hw_clock_utc.setter
    def hw_clock_utc(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b57dc9030109236260fc5fd3e9286cd9c6beecac80f9650014dacbe56439f78)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hwClockUtc", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scriptText")
    def script_text(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scriptText"))

    @script_text.setter
    def script_text(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b252087ebe1e4eb7ff7c5bfe895738e28114418e31e2d8312eedefc10aa26e39)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scriptText", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="timeZone")
    def time_zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timeZone"))

    @time_zone.setter
    def time_zone(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__152ee819ddc4dd0546a70b2d88276025ba95051946d828b826532a62dac76694)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timeZone", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[VirtualMachineCloneCustomizeLinuxOptions]:
        return typing.cast(typing.Optional[VirtualMachineCloneCustomizeLinuxOptions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[VirtualMachineCloneCustomizeLinuxOptions],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb02b73e19dd8dcb1991020d74c4dfa534e9b321d1b97b1eca5dfda9459f1621)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.virtualMachine.VirtualMachineCloneCustomizeNetworkInterface",
    jsii_struct_bases=[],
    name_mapping={
        "dns_domain": "dnsDomain",
        "dns_server_list": "dnsServerList",
        "ipv4_address": "ipv4Address",
        "ipv4_netmask": "ipv4Netmask",
        "ipv6_address": "ipv6Address",
        "ipv6_netmask": "ipv6Netmask",
    },
)
class VirtualMachineCloneCustomizeNetworkInterface:
    def __init__(
        self,
        *,
        dns_domain: typing.Optional[builtins.str] = None,
        dns_server_list: typing.Optional[typing.Sequence[builtins.str]] = None,
        ipv4_address: typing.Optional[builtins.str] = None,
        ipv4_netmask: typing.Optional[jsii.Number] = None,
        ipv6_address: typing.Optional[builtins.str] = None,
        ipv6_netmask: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param dns_domain: A DNS search domain to add to the DNS configuration on the virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#dns_domain VirtualMachine#dns_domain}
        :param dns_server_list: Network-interface specific DNS settings for Windows operating systems. Ignored on Linux. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#dns_server_list VirtualMachine#dns_server_list}
        :param ipv4_address: The IPv4 address assigned to this network adapter. If left blank, DHCP is used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#ipv4_address VirtualMachine#ipv4_address}
        :param ipv4_netmask: The IPv4 CIDR netmask for the supplied IP address. Ignored if DHCP is selected. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#ipv4_netmask VirtualMachine#ipv4_netmask}
        :param ipv6_address: The IPv6 address assigned to this network adapter. If left blank, default auto-configuration is used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#ipv6_address VirtualMachine#ipv6_address}
        :param ipv6_netmask: The IPv6 CIDR netmask for the supplied IP address. Ignored if auto-configuration is selected. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#ipv6_netmask VirtualMachine#ipv6_netmask}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ff7104e6aeab39b8d3ec40b75330535bcacf136da04e3f12606a06d7720a6a5)
            check_type(argname="argument dns_domain", value=dns_domain, expected_type=type_hints["dns_domain"])
            check_type(argname="argument dns_server_list", value=dns_server_list, expected_type=type_hints["dns_server_list"])
            check_type(argname="argument ipv4_address", value=ipv4_address, expected_type=type_hints["ipv4_address"])
            check_type(argname="argument ipv4_netmask", value=ipv4_netmask, expected_type=type_hints["ipv4_netmask"])
            check_type(argname="argument ipv6_address", value=ipv6_address, expected_type=type_hints["ipv6_address"])
            check_type(argname="argument ipv6_netmask", value=ipv6_netmask, expected_type=type_hints["ipv6_netmask"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if dns_domain is not None:
            self._values["dns_domain"] = dns_domain
        if dns_server_list is not None:
            self._values["dns_server_list"] = dns_server_list
        if ipv4_address is not None:
            self._values["ipv4_address"] = ipv4_address
        if ipv4_netmask is not None:
            self._values["ipv4_netmask"] = ipv4_netmask
        if ipv6_address is not None:
            self._values["ipv6_address"] = ipv6_address
        if ipv6_netmask is not None:
            self._values["ipv6_netmask"] = ipv6_netmask

    @builtins.property
    def dns_domain(self) -> typing.Optional[builtins.str]:
        '''A DNS search domain to add to the DNS configuration on the virtual machine.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#dns_domain VirtualMachine#dns_domain}
        '''
        result = self._values.get("dns_domain")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dns_server_list(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Network-interface specific DNS settings for Windows operating systems. Ignored on Linux.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#dns_server_list VirtualMachine#dns_server_list}
        '''
        result = self._values.get("dns_server_list")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def ipv4_address(self) -> typing.Optional[builtins.str]:
        '''The IPv4 address assigned to this network adapter. If left blank, DHCP is used.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#ipv4_address VirtualMachine#ipv4_address}
        '''
        result = self._values.get("ipv4_address")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ipv4_netmask(self) -> typing.Optional[jsii.Number]:
        '''The IPv4 CIDR netmask for the supplied IP address. Ignored if DHCP is selected.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#ipv4_netmask VirtualMachine#ipv4_netmask}
        '''
        result = self._values.get("ipv4_netmask")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ipv6_address(self) -> typing.Optional[builtins.str]:
        '''The IPv6 address assigned to this network adapter. If left blank, default auto-configuration is used.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#ipv6_address VirtualMachine#ipv6_address}
        '''
        result = self._values.get("ipv6_address")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ipv6_netmask(self) -> typing.Optional[jsii.Number]:
        '''The IPv6 CIDR netmask for the supplied IP address. Ignored if auto-configuration is selected.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#ipv6_netmask VirtualMachine#ipv6_netmask}
        '''
        result = self._values.get("ipv6_netmask")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VirtualMachineCloneCustomizeNetworkInterface(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class VirtualMachineCloneCustomizeNetworkInterfaceList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.virtualMachine.VirtualMachineCloneCustomizeNetworkInterfaceList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__419d83219c0769a77112c0b0ef92b6f12c0331ac1c27fc52e4b86f41c0abfb92)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "VirtualMachineCloneCustomizeNetworkInterfaceOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76629be8cc0545366e2b2cdad872712ef364c3e08ecedb02d2f99b4f4b9cc834)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("VirtualMachineCloneCustomizeNetworkInterfaceOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a6ffbdd40086d07161f03187e615cb80180d22ca2ec4d15d0c628db38af290f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ede43286cf92c85dc9c3fc3f1ba711b8babe88d353e0d94098867de7e1dbb25c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__78faef14ff34646788b0c3def8fb13cf8381a3e85a15ae5dc688cae79ed764f0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VirtualMachineCloneCustomizeNetworkInterface]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VirtualMachineCloneCustomizeNetworkInterface]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VirtualMachineCloneCustomizeNetworkInterface]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6e04c95b3fe8254998fc705a41fb352b12724c7962eea88d8c5446f86cf88fd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class VirtualMachineCloneCustomizeNetworkInterfaceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.virtualMachine.VirtualMachineCloneCustomizeNetworkInterfaceOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ce0f8e6f5bb0b03ebdc6b4300c42152ab2caf4c641037e92607cf067d258ec33)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetDnsDomain")
    def reset_dns_domain(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDnsDomain", []))

    @jsii.member(jsii_name="resetDnsServerList")
    def reset_dns_server_list(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDnsServerList", []))

    @jsii.member(jsii_name="resetIpv4Address")
    def reset_ipv4_address(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpv4Address", []))

    @jsii.member(jsii_name="resetIpv4Netmask")
    def reset_ipv4_netmask(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpv4Netmask", []))

    @jsii.member(jsii_name="resetIpv6Address")
    def reset_ipv6_address(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpv6Address", []))

    @jsii.member(jsii_name="resetIpv6Netmask")
    def reset_ipv6_netmask(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpv6Netmask", []))

    @builtins.property
    @jsii.member(jsii_name="dnsDomainInput")
    def dns_domain_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dnsDomainInput"))

    @builtins.property
    @jsii.member(jsii_name="dnsServerListInput")
    def dns_server_list_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "dnsServerListInput"))

    @builtins.property
    @jsii.member(jsii_name="ipv4AddressInput")
    def ipv4_address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ipv4AddressInput"))

    @builtins.property
    @jsii.member(jsii_name="ipv4NetmaskInput")
    def ipv4_netmask_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ipv4NetmaskInput"))

    @builtins.property
    @jsii.member(jsii_name="ipv6AddressInput")
    def ipv6_address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ipv6AddressInput"))

    @builtins.property
    @jsii.member(jsii_name="ipv6NetmaskInput")
    def ipv6_netmask_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ipv6NetmaskInput"))

    @builtins.property
    @jsii.member(jsii_name="dnsDomain")
    def dns_domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dnsDomain"))

    @dns_domain.setter
    def dns_domain(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__53a6bffb68236b4fa14db6fb83a82e5c70e572949abc1dcb31acfba7c32e517c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dnsDomain", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dnsServerList")
    def dns_server_list(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "dnsServerList"))

    @dns_server_list.setter
    def dns_server_list(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__784602f584e8c41e594c33912147ed5af72a7e268961532ed4b7cd0b56c0c8ac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dnsServerList", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipv4Address")
    def ipv4_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipv4Address"))

    @ipv4_address.setter
    def ipv4_address(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d163140ef2f902d3d38224442e867475d9e50346a8ebc6abd3ddfda50df61103)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipv4Address", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipv4Netmask")
    def ipv4_netmask(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ipv4Netmask"))

    @ipv4_netmask.setter
    def ipv4_netmask(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__654f5b18184b000490aa6a9206e9c1d9b0580bbeb8f70ea411ad372388dca9b6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipv4Netmask", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipv6Address")
    def ipv6_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipv6Address"))

    @ipv6_address.setter
    def ipv6_address(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f7ece60636029850fd0026bffd0f03b3010b17583e006f687b3b9c43ce22551)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipv6Address", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipv6Netmask")
    def ipv6_netmask(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ipv6Netmask"))

    @ipv6_netmask.setter
    def ipv6_netmask(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b063422561b09ae5b600f7610307d847ab111d9158ce56a0c8a7808d5c667f0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipv6Netmask", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VirtualMachineCloneCustomizeNetworkInterface]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VirtualMachineCloneCustomizeNetworkInterface]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VirtualMachineCloneCustomizeNetworkInterface]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9cf99001d5d036203796d4abd754e34eadf7746f4dfa18358ad7cbf4bd886ba2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class VirtualMachineCloneCustomizeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.virtualMachine.VirtualMachineCloneCustomizeOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__550b4de40fdf14c7952747bdadb84bb8918bbe7a50bf68fba8670724cecc1dae)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putLinuxOptions")
    def put_linux_options(
        self,
        *,
        domain: builtins.str,
        host_name: builtins.str,
        hw_clock_utc: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        script_text: typing.Optional[builtins.str] = None,
        time_zone: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param domain: The domain name for this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#domain VirtualMachine#domain}
        :param host_name: The hostname for this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#host_name VirtualMachine#host_name}
        :param hw_clock_utc: Specifies whether or not the hardware clock should be in UTC or not. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#hw_clock_utc VirtualMachine#hw_clock_utc}
        :param script_text: The customization script to run before and or after guest customization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#script_text VirtualMachine#script_text}
        :param time_zone: Customize the time zone on the VM. This should be a time zone-style entry, like America/Los_Angeles. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#time_zone VirtualMachine#time_zone}
        '''
        value = VirtualMachineCloneCustomizeLinuxOptions(
            domain=domain,
            host_name=host_name,
            hw_clock_utc=hw_clock_utc,
            script_text=script_text,
            time_zone=time_zone,
        )

        return typing.cast(None, jsii.invoke(self, "putLinuxOptions", [value]))

    @jsii.member(jsii_name="putNetworkInterface")
    def put_network_interface(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VirtualMachineCloneCustomizeNetworkInterface, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a97aebd933299c6d522c492d366a140928e3ba24cfaed809da6f8dad02fffee2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putNetworkInterface", [value]))

    @jsii.member(jsii_name="putWindowsOptions")
    def put_windows_options(
        self,
        *,
        computer_name: builtins.str,
        admin_password: typing.Optional[builtins.str] = None,
        auto_logon: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        auto_logon_count: typing.Optional[jsii.Number] = None,
        domain_admin_password: typing.Optional[builtins.str] = None,
        domain_admin_user: typing.Optional[builtins.str] = None,
        domain_ou: typing.Optional[builtins.str] = None,
        full_name: typing.Optional[builtins.str] = None,
        join_domain: typing.Optional[builtins.str] = None,
        organization_name: typing.Optional[builtins.str] = None,
        product_key: typing.Optional[builtins.str] = None,
        run_once_command_list: typing.Optional[typing.Sequence[builtins.str]] = None,
        time_zone: typing.Optional[jsii.Number] = None,
        workgroup: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param computer_name: The host name for this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#computer_name VirtualMachine#computer_name}
        :param admin_password: The new administrator password for this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#admin_password VirtualMachine#admin_password}
        :param auto_logon: Specifies whether or not the VM automatically logs on as Administrator. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#auto_logon VirtualMachine#auto_logon}
        :param auto_logon_count: Specifies how many times the VM should auto-logon the Administrator account when auto_logon is true. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#auto_logon_count VirtualMachine#auto_logon_count}
        :param domain_admin_password: The password of the domain administrator used to join this virtual machine to the domain. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#domain_admin_password VirtualMachine#domain_admin_password}
        :param domain_admin_user: The user account of the domain administrator used to join this virtual machine to the domain. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#domain_admin_user VirtualMachine#domain_admin_user}
        :param domain_ou: The MachineObjectOU which specifies the full LDAP path name of the OU to which the virtual machine belongs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#domain_ou VirtualMachine#domain_ou}
        :param full_name: The full name of the user of this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#full_name VirtualMachine#full_name}
        :param join_domain: The domain that the virtual machine should join. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#join_domain VirtualMachine#join_domain}
        :param organization_name: The organization name this virtual machine is being installed for. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#organization_name VirtualMachine#organization_name}
        :param product_key: The product key for this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#product_key VirtualMachine#product_key}
        :param run_once_command_list: A list of commands to run at first user logon, after guest customization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#run_once_command_list VirtualMachine#run_once_command_list}
        :param time_zone: The new time zone for the virtual machine. This is a sysprep-dictated timezone code. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#time_zone VirtualMachine#time_zone}
        :param workgroup: The workgroup for this virtual machine if not joining a domain. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#workgroup VirtualMachine#workgroup}
        '''
        value = VirtualMachineCloneCustomizeWindowsOptions(
            computer_name=computer_name,
            admin_password=admin_password,
            auto_logon=auto_logon,
            auto_logon_count=auto_logon_count,
            domain_admin_password=domain_admin_password,
            domain_admin_user=domain_admin_user,
            domain_ou=domain_ou,
            full_name=full_name,
            join_domain=join_domain,
            organization_name=organization_name,
            product_key=product_key,
            run_once_command_list=run_once_command_list,
            time_zone=time_zone,
            workgroup=workgroup,
        )

        return typing.cast(None, jsii.invoke(self, "putWindowsOptions", [value]))

    @jsii.member(jsii_name="resetDnsServerList")
    def reset_dns_server_list(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDnsServerList", []))

    @jsii.member(jsii_name="resetDnsSuffixList")
    def reset_dns_suffix_list(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDnsSuffixList", []))

    @jsii.member(jsii_name="resetIpv4Gateway")
    def reset_ipv4_gateway(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpv4Gateway", []))

    @jsii.member(jsii_name="resetIpv6Gateway")
    def reset_ipv6_gateway(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpv6Gateway", []))

    @jsii.member(jsii_name="resetLinuxOptions")
    def reset_linux_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLinuxOptions", []))

    @jsii.member(jsii_name="resetNetworkInterface")
    def reset_network_interface(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworkInterface", []))

    @jsii.member(jsii_name="resetTimeout")
    def reset_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeout", []))

    @jsii.member(jsii_name="resetWindowsOptions")
    def reset_windows_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWindowsOptions", []))

    @jsii.member(jsii_name="resetWindowsSysprepText")
    def reset_windows_sysprep_text(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWindowsSysprepText", []))

    @builtins.property
    @jsii.member(jsii_name="linuxOptions")
    def linux_options(self) -> VirtualMachineCloneCustomizeLinuxOptionsOutputReference:
        return typing.cast(VirtualMachineCloneCustomizeLinuxOptionsOutputReference, jsii.get(self, "linuxOptions"))

    @builtins.property
    @jsii.member(jsii_name="networkInterface")
    def network_interface(self) -> VirtualMachineCloneCustomizeNetworkInterfaceList:
        return typing.cast(VirtualMachineCloneCustomizeNetworkInterfaceList, jsii.get(self, "networkInterface"))

    @builtins.property
    @jsii.member(jsii_name="windowsOptions")
    def windows_options(
        self,
    ) -> "VirtualMachineCloneCustomizeWindowsOptionsOutputReference":
        return typing.cast("VirtualMachineCloneCustomizeWindowsOptionsOutputReference", jsii.get(self, "windowsOptions"))

    @builtins.property
    @jsii.member(jsii_name="dnsServerListInput")
    def dns_server_list_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "dnsServerListInput"))

    @builtins.property
    @jsii.member(jsii_name="dnsSuffixListInput")
    def dns_suffix_list_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "dnsSuffixListInput"))

    @builtins.property
    @jsii.member(jsii_name="ipv4GatewayInput")
    def ipv4_gateway_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ipv4GatewayInput"))

    @builtins.property
    @jsii.member(jsii_name="ipv6GatewayInput")
    def ipv6_gateway_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ipv6GatewayInput"))

    @builtins.property
    @jsii.member(jsii_name="linuxOptionsInput")
    def linux_options_input(
        self,
    ) -> typing.Optional[VirtualMachineCloneCustomizeLinuxOptions]:
        return typing.cast(typing.Optional[VirtualMachineCloneCustomizeLinuxOptions], jsii.get(self, "linuxOptionsInput"))

    @builtins.property
    @jsii.member(jsii_name="networkInterfaceInput")
    def network_interface_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VirtualMachineCloneCustomizeNetworkInterface]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VirtualMachineCloneCustomizeNetworkInterface]]], jsii.get(self, "networkInterfaceInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutInput")
    def timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "timeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="windowsOptionsInput")
    def windows_options_input(
        self,
    ) -> typing.Optional["VirtualMachineCloneCustomizeWindowsOptions"]:
        return typing.cast(typing.Optional["VirtualMachineCloneCustomizeWindowsOptions"], jsii.get(self, "windowsOptionsInput"))

    @builtins.property
    @jsii.member(jsii_name="windowsSysprepTextInput")
    def windows_sysprep_text_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "windowsSysprepTextInput"))

    @builtins.property
    @jsii.member(jsii_name="dnsServerList")
    def dns_server_list(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "dnsServerList"))

    @dns_server_list.setter
    def dns_server_list(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f2d8f459c62a0206e87c311971a51e1b92ebc6fd8d833acadb1632619a38401)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dnsServerList", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dnsSuffixList")
    def dns_suffix_list(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "dnsSuffixList"))

    @dns_suffix_list.setter
    def dns_suffix_list(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db58206829516f1a7cb009bc9db17265ad956509bb1b13434e3b9f507ab2667c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dnsSuffixList", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipv4Gateway")
    def ipv4_gateway(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipv4Gateway"))

    @ipv4_gateway.setter
    def ipv4_gateway(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47a59106bc86d61b198c10021f02e025d5724993c79186eda6b9a16c483c51d5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipv4Gateway", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipv6Gateway")
    def ipv6_gateway(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipv6Gateway"))

    @ipv6_gateway.setter
    def ipv6_gateway(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b70d2895b12fe284f1e524387dd86d3c69f6c1e6c74ed0125100d270dd04967)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipv6Gateway", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="timeout")
    def timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "timeout"))

    @timeout.setter
    def timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3247656088c58a5e08f290d700e1f9782a8e34413b4e1b42a668fdcd817cb03)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="windowsSysprepText")
    def windows_sysprep_text(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "windowsSysprepText"))

    @windows_sysprep_text.setter
    def windows_sysprep_text(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a1440619beeabd405172dad469fc9fa69760e50b26dab6a0aa351b3d9628624)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "windowsSysprepText", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[VirtualMachineCloneCustomize]:
        return typing.cast(typing.Optional[VirtualMachineCloneCustomize], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[VirtualMachineCloneCustomize],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3aa25279ab32ed95b31423fdeb8b7556fa89893489451fa2d5d1f9ad78c07b5a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.virtualMachine.VirtualMachineCloneCustomizeWindowsOptions",
    jsii_struct_bases=[],
    name_mapping={
        "computer_name": "computerName",
        "admin_password": "adminPassword",
        "auto_logon": "autoLogon",
        "auto_logon_count": "autoLogonCount",
        "domain_admin_password": "domainAdminPassword",
        "domain_admin_user": "domainAdminUser",
        "domain_ou": "domainOu",
        "full_name": "fullName",
        "join_domain": "joinDomain",
        "organization_name": "organizationName",
        "product_key": "productKey",
        "run_once_command_list": "runOnceCommandList",
        "time_zone": "timeZone",
        "workgroup": "workgroup",
    },
)
class VirtualMachineCloneCustomizeWindowsOptions:
    def __init__(
        self,
        *,
        computer_name: builtins.str,
        admin_password: typing.Optional[builtins.str] = None,
        auto_logon: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        auto_logon_count: typing.Optional[jsii.Number] = None,
        domain_admin_password: typing.Optional[builtins.str] = None,
        domain_admin_user: typing.Optional[builtins.str] = None,
        domain_ou: typing.Optional[builtins.str] = None,
        full_name: typing.Optional[builtins.str] = None,
        join_domain: typing.Optional[builtins.str] = None,
        organization_name: typing.Optional[builtins.str] = None,
        product_key: typing.Optional[builtins.str] = None,
        run_once_command_list: typing.Optional[typing.Sequence[builtins.str]] = None,
        time_zone: typing.Optional[jsii.Number] = None,
        workgroup: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param computer_name: The host name for this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#computer_name VirtualMachine#computer_name}
        :param admin_password: The new administrator password for this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#admin_password VirtualMachine#admin_password}
        :param auto_logon: Specifies whether or not the VM automatically logs on as Administrator. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#auto_logon VirtualMachine#auto_logon}
        :param auto_logon_count: Specifies how many times the VM should auto-logon the Administrator account when auto_logon is true. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#auto_logon_count VirtualMachine#auto_logon_count}
        :param domain_admin_password: The password of the domain administrator used to join this virtual machine to the domain. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#domain_admin_password VirtualMachine#domain_admin_password}
        :param domain_admin_user: The user account of the domain administrator used to join this virtual machine to the domain. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#domain_admin_user VirtualMachine#domain_admin_user}
        :param domain_ou: The MachineObjectOU which specifies the full LDAP path name of the OU to which the virtual machine belongs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#domain_ou VirtualMachine#domain_ou}
        :param full_name: The full name of the user of this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#full_name VirtualMachine#full_name}
        :param join_domain: The domain that the virtual machine should join. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#join_domain VirtualMachine#join_domain}
        :param organization_name: The organization name this virtual machine is being installed for. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#organization_name VirtualMachine#organization_name}
        :param product_key: The product key for this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#product_key VirtualMachine#product_key}
        :param run_once_command_list: A list of commands to run at first user logon, after guest customization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#run_once_command_list VirtualMachine#run_once_command_list}
        :param time_zone: The new time zone for the virtual machine. This is a sysprep-dictated timezone code. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#time_zone VirtualMachine#time_zone}
        :param workgroup: The workgroup for this virtual machine if not joining a domain. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#workgroup VirtualMachine#workgroup}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0116db1b8b0ee4c2f9b0cc48bf9326f3b94a46fcbe940de46f0b06efb5248ed)
            check_type(argname="argument computer_name", value=computer_name, expected_type=type_hints["computer_name"])
            check_type(argname="argument admin_password", value=admin_password, expected_type=type_hints["admin_password"])
            check_type(argname="argument auto_logon", value=auto_logon, expected_type=type_hints["auto_logon"])
            check_type(argname="argument auto_logon_count", value=auto_logon_count, expected_type=type_hints["auto_logon_count"])
            check_type(argname="argument domain_admin_password", value=domain_admin_password, expected_type=type_hints["domain_admin_password"])
            check_type(argname="argument domain_admin_user", value=domain_admin_user, expected_type=type_hints["domain_admin_user"])
            check_type(argname="argument domain_ou", value=domain_ou, expected_type=type_hints["domain_ou"])
            check_type(argname="argument full_name", value=full_name, expected_type=type_hints["full_name"])
            check_type(argname="argument join_domain", value=join_domain, expected_type=type_hints["join_domain"])
            check_type(argname="argument organization_name", value=organization_name, expected_type=type_hints["organization_name"])
            check_type(argname="argument product_key", value=product_key, expected_type=type_hints["product_key"])
            check_type(argname="argument run_once_command_list", value=run_once_command_list, expected_type=type_hints["run_once_command_list"])
            check_type(argname="argument time_zone", value=time_zone, expected_type=type_hints["time_zone"])
            check_type(argname="argument workgroup", value=workgroup, expected_type=type_hints["workgroup"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "computer_name": computer_name,
        }
        if admin_password is not None:
            self._values["admin_password"] = admin_password
        if auto_logon is not None:
            self._values["auto_logon"] = auto_logon
        if auto_logon_count is not None:
            self._values["auto_logon_count"] = auto_logon_count
        if domain_admin_password is not None:
            self._values["domain_admin_password"] = domain_admin_password
        if domain_admin_user is not None:
            self._values["domain_admin_user"] = domain_admin_user
        if domain_ou is not None:
            self._values["domain_ou"] = domain_ou
        if full_name is not None:
            self._values["full_name"] = full_name
        if join_domain is not None:
            self._values["join_domain"] = join_domain
        if organization_name is not None:
            self._values["organization_name"] = organization_name
        if product_key is not None:
            self._values["product_key"] = product_key
        if run_once_command_list is not None:
            self._values["run_once_command_list"] = run_once_command_list
        if time_zone is not None:
            self._values["time_zone"] = time_zone
        if workgroup is not None:
            self._values["workgroup"] = workgroup

    @builtins.property
    def computer_name(self) -> builtins.str:
        '''The host name for this virtual machine.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#computer_name VirtualMachine#computer_name}
        '''
        result = self._values.get("computer_name")
        assert result is not None, "Required property 'computer_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def admin_password(self) -> typing.Optional[builtins.str]:
        '''The new administrator password for this virtual machine.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#admin_password VirtualMachine#admin_password}
        '''
        result = self._values.get("admin_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auto_logon(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Specifies whether or not the VM automatically logs on as Administrator.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#auto_logon VirtualMachine#auto_logon}
        '''
        result = self._values.get("auto_logon")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def auto_logon_count(self) -> typing.Optional[jsii.Number]:
        '''Specifies how many times the VM should auto-logon the Administrator account when auto_logon is true.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#auto_logon_count VirtualMachine#auto_logon_count}
        '''
        result = self._values.get("auto_logon_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def domain_admin_password(self) -> typing.Optional[builtins.str]:
        '''The password of the domain administrator used to join this virtual machine to the domain.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#domain_admin_password VirtualMachine#domain_admin_password}
        '''
        result = self._values.get("domain_admin_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def domain_admin_user(self) -> typing.Optional[builtins.str]:
        '''The user account of the domain administrator used to join this virtual machine to the domain.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#domain_admin_user VirtualMachine#domain_admin_user}
        '''
        result = self._values.get("domain_admin_user")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def domain_ou(self) -> typing.Optional[builtins.str]:
        '''The MachineObjectOU which specifies the full LDAP path name of the OU to which the virtual machine belongs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#domain_ou VirtualMachine#domain_ou}
        '''
        result = self._values.get("domain_ou")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def full_name(self) -> typing.Optional[builtins.str]:
        '''The full name of the user of this virtual machine.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#full_name VirtualMachine#full_name}
        '''
        result = self._values.get("full_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def join_domain(self) -> typing.Optional[builtins.str]:
        '''The domain that the virtual machine should join.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#join_domain VirtualMachine#join_domain}
        '''
        result = self._values.get("join_domain")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def organization_name(self) -> typing.Optional[builtins.str]:
        '''The organization name this virtual machine is being installed for.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#organization_name VirtualMachine#organization_name}
        '''
        result = self._values.get("organization_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def product_key(self) -> typing.Optional[builtins.str]:
        '''The product key for this virtual machine.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#product_key VirtualMachine#product_key}
        '''
        result = self._values.get("product_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def run_once_command_list(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of commands to run at first user logon, after guest customization.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#run_once_command_list VirtualMachine#run_once_command_list}
        '''
        result = self._values.get("run_once_command_list")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def time_zone(self) -> typing.Optional[jsii.Number]:
        '''The new time zone for the virtual machine. This is a sysprep-dictated timezone code.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#time_zone VirtualMachine#time_zone}
        '''
        result = self._values.get("time_zone")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def workgroup(self) -> typing.Optional[builtins.str]:
        '''The workgroup for this virtual machine if not joining a domain.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#workgroup VirtualMachine#workgroup}
        '''
        result = self._values.get("workgroup")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VirtualMachineCloneCustomizeWindowsOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class VirtualMachineCloneCustomizeWindowsOptionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.virtualMachine.VirtualMachineCloneCustomizeWindowsOptionsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0403c4cea7f349747a50360f4b07352e3fbf217f7ccfba7209a39c2528a3e1c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAdminPassword")
    def reset_admin_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdminPassword", []))

    @jsii.member(jsii_name="resetAutoLogon")
    def reset_auto_logon(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoLogon", []))

    @jsii.member(jsii_name="resetAutoLogonCount")
    def reset_auto_logon_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoLogonCount", []))

    @jsii.member(jsii_name="resetDomainAdminPassword")
    def reset_domain_admin_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDomainAdminPassword", []))

    @jsii.member(jsii_name="resetDomainAdminUser")
    def reset_domain_admin_user(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDomainAdminUser", []))

    @jsii.member(jsii_name="resetDomainOu")
    def reset_domain_ou(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDomainOu", []))

    @jsii.member(jsii_name="resetFullName")
    def reset_full_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFullName", []))

    @jsii.member(jsii_name="resetJoinDomain")
    def reset_join_domain(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJoinDomain", []))

    @jsii.member(jsii_name="resetOrganizationName")
    def reset_organization_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOrganizationName", []))

    @jsii.member(jsii_name="resetProductKey")
    def reset_product_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProductKey", []))

    @jsii.member(jsii_name="resetRunOnceCommandList")
    def reset_run_once_command_list(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRunOnceCommandList", []))

    @jsii.member(jsii_name="resetTimeZone")
    def reset_time_zone(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeZone", []))

    @jsii.member(jsii_name="resetWorkgroup")
    def reset_workgroup(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkgroup", []))

    @builtins.property
    @jsii.member(jsii_name="adminPasswordInput")
    def admin_password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "adminPasswordInput"))

    @builtins.property
    @jsii.member(jsii_name="autoLogonCountInput")
    def auto_logon_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "autoLogonCountInput"))

    @builtins.property
    @jsii.member(jsii_name="autoLogonInput")
    def auto_logon_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "autoLogonInput"))

    @builtins.property
    @jsii.member(jsii_name="computerNameInput")
    def computer_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "computerNameInput"))

    @builtins.property
    @jsii.member(jsii_name="domainAdminPasswordInput")
    def domain_admin_password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainAdminPasswordInput"))

    @builtins.property
    @jsii.member(jsii_name="domainAdminUserInput")
    def domain_admin_user_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainAdminUserInput"))

    @builtins.property
    @jsii.member(jsii_name="domainOuInput")
    def domain_ou_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainOuInput"))

    @builtins.property
    @jsii.member(jsii_name="fullNameInput")
    def full_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fullNameInput"))

    @builtins.property
    @jsii.member(jsii_name="joinDomainInput")
    def join_domain_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "joinDomainInput"))

    @builtins.property
    @jsii.member(jsii_name="organizationNameInput")
    def organization_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "organizationNameInput"))

    @builtins.property
    @jsii.member(jsii_name="productKeyInput")
    def product_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "productKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="runOnceCommandListInput")
    def run_once_command_list_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "runOnceCommandListInput"))

    @builtins.property
    @jsii.member(jsii_name="timeZoneInput")
    def time_zone_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "timeZoneInput"))

    @builtins.property
    @jsii.member(jsii_name="workgroupInput")
    def workgroup_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workgroupInput"))

    @builtins.property
    @jsii.member(jsii_name="adminPassword")
    def admin_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "adminPassword"))

    @admin_password.setter
    def admin_password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80dab348356470c231eddfacd268a463a821a12339ebb341ee8685e9047dbe21)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "adminPassword", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="autoLogon")
    def auto_logon(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "autoLogon"))

    @auto_logon.setter
    def auto_logon(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47f7463ebaa207ff911bd9e0a3d02972a153558c1502633bd91230b99f9b39d2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoLogon", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="autoLogonCount")
    def auto_logon_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "autoLogonCount"))

    @auto_logon_count.setter
    def auto_logon_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__820d2a592b375270ef1d11d8b0f359a912e9d4a153d8e9bb9f3f2e5054024a81)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoLogonCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="computerName")
    def computer_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "computerName"))

    @computer_name.setter
    def computer_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07686288e01e19393a29e9bcb71b5b8771e7493483caae78a2e6507a97fdc3b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "computerName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="domainAdminPassword")
    def domain_admin_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domainAdminPassword"))

    @domain_admin_password.setter
    def domain_admin_password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6f5a20f194da7993f787bde2a9a31b03837bde2bcbac51b52b536fdaccd68d5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "domainAdminPassword", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="domainAdminUser")
    def domain_admin_user(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domainAdminUser"))

    @domain_admin_user.setter
    def domain_admin_user(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4305a675f73e2444be3da59d88da0a47c045785c268386019951b27d338b6db7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "domainAdminUser", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="domainOu")
    def domain_ou(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domainOu"))

    @domain_ou.setter
    def domain_ou(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ebce476ec2b4b3eb00e2261a1262e3cff012e08e29aad1c150d1d6e627efecef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "domainOu", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="fullName")
    def full_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fullName"))

    @full_name.setter
    def full_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__406f436a55ac6ed534f0eee3741772a0f8346ea84b7958f68a3b52254ce442e9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fullName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="joinDomain")
    def join_domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "joinDomain"))

    @join_domain.setter
    def join_domain(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e903fa90cec789bec27ae55dad3e1c7040d517eca9c5d6dd932bd0bbab3c989)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "joinDomain", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="organizationName")
    def organization_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "organizationName"))

    @organization_name.setter
    def organization_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9034fa1b2b110e029f53ce151a7c9891ecbb87dab1c32a04a5a2ecb12612bc44)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "organizationName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="productKey")
    def product_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "productKey"))

    @product_key.setter
    def product_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e01747404ea0013dfaf0b6091286ad98ed7742ff3549819ef254771bfc1fbad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "productKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="runOnceCommandList")
    def run_once_command_list(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "runOnceCommandList"))

    @run_once_command_list.setter
    def run_once_command_list(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3b15f1b0384933ffa48d88c8009f7526059d1d0c8bb92fc1dc8a80fb7184830)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "runOnceCommandList", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="timeZone")
    def time_zone(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "timeZone"))

    @time_zone.setter
    def time_zone(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ebf0c99b035559c01e66ad560ffecfef4faf04cb9044e09a60eb023668d81f78)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timeZone", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workgroup")
    def workgroup(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workgroup"))

    @workgroup.setter
    def workgroup(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf0e26cafbcdf978a76eb4933d3cb156c144162a2fe2c1124ab50ee179f51348)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workgroup", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[VirtualMachineCloneCustomizeWindowsOptions]:
        return typing.cast(typing.Optional[VirtualMachineCloneCustomizeWindowsOptions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[VirtualMachineCloneCustomizeWindowsOptions],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d4ae348e08133789c5279adc2ab586c3bc53390e76b7ee9c608cd95af2954cf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class VirtualMachineCloneOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.virtualMachine.VirtualMachineCloneOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22a23434afdd0bfa57c789686afac7c1e04394f88236c9c2c3602bbd38ae2aca)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putCustomizationSpec")
    def put_customization_spec(
        self,
        *,
        id: builtins.str,
        timeout: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param id: The unique identifier of the customization specification is its name and is unique per vCenter Server instance. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#id VirtualMachine#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param timeout: The amount of time, in minutes, to wait for guest OS customization to complete before returning with an error. Setting this value to 0 or a negative value skips the waiter. Default: 10. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#timeout VirtualMachine#timeout}
        '''
        value = VirtualMachineCloneCustomizationSpec(id=id, timeout=timeout)

        return typing.cast(None, jsii.invoke(self, "putCustomizationSpec", [value]))

    @jsii.member(jsii_name="putCustomize")
    def put_customize(
        self,
        *,
        dns_server_list: typing.Optional[typing.Sequence[builtins.str]] = None,
        dns_suffix_list: typing.Optional[typing.Sequence[builtins.str]] = None,
        ipv4_gateway: typing.Optional[builtins.str] = None,
        ipv6_gateway: typing.Optional[builtins.str] = None,
        linux_options: typing.Optional[typing.Union[VirtualMachineCloneCustomizeLinuxOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        network_interface: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VirtualMachineCloneCustomizeNetworkInterface, typing.Dict[builtins.str, typing.Any]]]]] = None,
        timeout: typing.Optional[jsii.Number] = None,
        windows_options: typing.Optional[typing.Union[VirtualMachineCloneCustomizeWindowsOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        windows_sysprep_text: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param dns_server_list: The list of DNS servers for a virtual network adapter with a static IP address. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#dns_server_list VirtualMachine#dns_server_list}
        :param dns_suffix_list: A list of DNS search domains to add to the DNS configuration on the virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#dns_suffix_list VirtualMachine#dns_suffix_list}
        :param ipv4_gateway: The IPv4 default gateway when using network_interface customization on the virtual machine. This address must be local to a static IPv4 address configured in an interface sub-resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#ipv4_gateway VirtualMachine#ipv4_gateway}
        :param ipv6_gateway: The IPv6 default gateway when using network_interface customization on the virtual machine. This address must be local to a static IPv4 address configured in an interface sub-resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#ipv6_gateway VirtualMachine#ipv6_gateway}
        :param linux_options: linux_options block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#linux_options VirtualMachine#linux_options}
        :param network_interface: network_interface block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#network_interface VirtualMachine#network_interface}
        :param timeout: The amount of time, in minutes, to wait for guest OS customization to complete before returning with an error. Setting this value to 0 or a negative value skips the waiter. Default: 10. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#timeout VirtualMachine#timeout}
        :param windows_options: windows_options block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#windows_options VirtualMachine#windows_options}
        :param windows_sysprep_text: Use this option to specify a windows sysprep file directly. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#windows_sysprep_text VirtualMachine#windows_sysprep_text}
        '''
        value = VirtualMachineCloneCustomize(
            dns_server_list=dns_server_list,
            dns_suffix_list=dns_suffix_list,
            ipv4_gateway=ipv4_gateway,
            ipv6_gateway=ipv6_gateway,
            linux_options=linux_options,
            network_interface=network_interface,
            timeout=timeout,
            windows_options=windows_options,
            windows_sysprep_text=windows_sysprep_text,
        )

        return typing.cast(None, jsii.invoke(self, "putCustomize", [value]))

    @jsii.member(jsii_name="resetCustomizationSpec")
    def reset_customization_spec(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomizationSpec", []))

    @jsii.member(jsii_name="resetCustomize")
    def reset_customize(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomize", []))

    @jsii.member(jsii_name="resetLinkedClone")
    def reset_linked_clone(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLinkedClone", []))

    @jsii.member(jsii_name="resetOvfNetworkMap")
    def reset_ovf_network_map(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOvfNetworkMap", []))

    @jsii.member(jsii_name="resetOvfStorageMap")
    def reset_ovf_storage_map(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOvfStorageMap", []))

    @jsii.member(jsii_name="resetTimeout")
    def reset_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeout", []))

    @builtins.property
    @jsii.member(jsii_name="customizationSpec")
    def customization_spec(self) -> VirtualMachineCloneCustomizationSpecOutputReference:
        return typing.cast(VirtualMachineCloneCustomizationSpecOutputReference, jsii.get(self, "customizationSpec"))

    @builtins.property
    @jsii.member(jsii_name="customize")
    def customize(self) -> VirtualMachineCloneCustomizeOutputReference:
        return typing.cast(VirtualMachineCloneCustomizeOutputReference, jsii.get(self, "customize"))

    @builtins.property
    @jsii.member(jsii_name="customizationSpecInput")
    def customization_spec_input(
        self,
    ) -> typing.Optional[VirtualMachineCloneCustomizationSpec]:
        return typing.cast(typing.Optional[VirtualMachineCloneCustomizationSpec], jsii.get(self, "customizationSpecInput"))

    @builtins.property
    @jsii.member(jsii_name="customizeInput")
    def customize_input(self) -> typing.Optional[VirtualMachineCloneCustomize]:
        return typing.cast(typing.Optional[VirtualMachineCloneCustomize], jsii.get(self, "customizeInput"))

    @builtins.property
    @jsii.member(jsii_name="linkedCloneInput")
    def linked_clone_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "linkedCloneInput"))

    @builtins.property
    @jsii.member(jsii_name="ovfNetworkMapInput")
    def ovf_network_map_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "ovfNetworkMapInput"))

    @builtins.property
    @jsii.member(jsii_name="ovfStorageMapInput")
    def ovf_storage_map_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "ovfStorageMapInput"))

    @builtins.property
    @jsii.member(jsii_name="templateUuidInput")
    def template_uuid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "templateUuidInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutInput")
    def timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "timeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="linkedClone")
    def linked_clone(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "linkedClone"))

    @linked_clone.setter
    def linked_clone(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c485edd657ef5fe7b5e3ce4eeb8e1343b72bc3605ffbaf3460f3ecde54ff6cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "linkedClone", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ovfNetworkMap")
    def ovf_network_map(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "ovfNetworkMap"))

    @ovf_network_map.setter
    def ovf_network_map(
        self,
        value: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__edc06ce38e17e728527c1c3d71e1249e42412e1743d51e14d3bd8707186174d7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ovfNetworkMap", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ovfStorageMap")
    def ovf_storage_map(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "ovfStorageMap"))

    @ovf_storage_map.setter
    def ovf_storage_map(
        self,
        value: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5bec349910d07d3fde80822069fc2aeee6947a24d21197c0b173fa843fcc3f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ovfStorageMap", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="templateUuid")
    def template_uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "templateUuid"))

    @template_uuid.setter
    def template_uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8f7448e1f97d3870b1bb201c7a661eeea22f6d2c5ec301e08f8c8cfb431f21f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "templateUuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="timeout")
    def timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "timeout"))

    @timeout.setter
    def timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__228673e59a6569fc60cf65a2b5c7b31f5f52ee9eb06c5034e0e0711f202b498c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[VirtualMachineClone]:
        return typing.cast(typing.Optional[VirtualMachineClone], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[VirtualMachineClone]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0774638501660981959ca52aaeacc6b1297d43c5e42de7b0bb64d36430107808)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.virtualMachine.VirtualMachineConfig",
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
        "resource_pool_id": "resourcePoolId",
        "alternate_guest_name": "alternateGuestName",
        "annotation": "annotation",
        "boot_delay": "bootDelay",
        "boot_retry_delay": "bootRetryDelay",
        "boot_retry_enabled": "bootRetryEnabled",
        "cdrom": "cdrom",
        "clone": "clone",
        "cpu_hot_add_enabled": "cpuHotAddEnabled",
        "cpu_hot_remove_enabled": "cpuHotRemoveEnabled",
        "cpu_limit": "cpuLimit",
        "cpu_performance_counters_enabled": "cpuPerformanceCountersEnabled",
        "cpu_reservation": "cpuReservation",
        "cpu_share_count": "cpuShareCount",
        "cpu_share_level": "cpuShareLevel",
        "custom_attributes": "customAttributes",
        "datacenter_id": "datacenterId",
        "datastore_cluster_id": "datastoreClusterId",
        "datastore_id": "datastoreId",
        "disk": "disk",
        "efi_secure_boot_enabled": "efiSecureBootEnabled",
        "enable_disk_uuid": "enableDiskUuid",
        "enable_logging": "enableLogging",
        "ept_rvi_mode": "eptRviMode",
        "extra_config": "extraConfig",
        "extra_config_reboot_required": "extraConfigRebootRequired",
        "firmware": "firmware",
        "folder": "folder",
        "force_power_off": "forcePowerOff",
        "guest_id": "guestId",
        "hardware_version": "hardwareVersion",
        "host_system_id": "hostSystemId",
        "hv_mode": "hvMode",
        "id": "id",
        "ide_controller_count": "ideControllerCount",
        "ignored_guest_ips": "ignoredGuestIps",
        "latency_sensitivity": "latencySensitivity",
        "memory": "memory",
        "memory_hot_add_enabled": "memoryHotAddEnabled",
        "memory_limit": "memoryLimit",
        "memory_reservation": "memoryReservation",
        "memory_reservation_locked_to_max": "memoryReservationLockedToMax",
        "memory_share_count": "memoryShareCount",
        "memory_share_level": "memoryShareLevel",
        "migrate_wait_timeout": "migrateWaitTimeout",
        "nested_hv_enabled": "nestedHvEnabled",
        "network_interface": "networkInterface",
        "num_cores_per_socket": "numCoresPerSocket",
        "num_cpus": "numCpus",
        "nvme_controller_count": "nvmeControllerCount",
        "ovf_deploy": "ovfDeploy",
        "pci_device_id": "pciDeviceId",
        "poweron_timeout": "poweronTimeout",
        "replace_trigger": "replaceTrigger",
        "run_tools_scripts_after_power_on": "runToolsScriptsAfterPowerOn",
        "run_tools_scripts_after_resume": "runToolsScriptsAfterResume",
        "run_tools_scripts_before_guest_reboot": "runToolsScriptsBeforeGuestReboot",
        "run_tools_scripts_before_guest_shutdown": "runToolsScriptsBeforeGuestShutdown",
        "run_tools_scripts_before_guest_standby": "runToolsScriptsBeforeGuestStandby",
        "sata_controller_count": "sataControllerCount",
        "scsi_bus_sharing": "scsiBusSharing",
        "scsi_controller_count": "scsiControllerCount",
        "scsi_type": "scsiType",
        "shutdown_wait_timeout": "shutdownWaitTimeout",
        "storage_policy_id": "storagePolicyId",
        "swap_placement_policy": "swapPlacementPolicy",
        "sync_time_with_host": "syncTimeWithHost",
        "sync_time_with_host_periodically": "syncTimeWithHostPeriodically",
        "tags": "tags",
        "tools_upgrade_policy": "toolsUpgradePolicy",
        "vapp": "vapp",
        "vbs_enabled": "vbsEnabled",
        "vtpm": "vtpm",
        "vvtd_enabled": "vvtdEnabled",
        "wait_for_guest_ip_timeout": "waitForGuestIpTimeout",
        "wait_for_guest_net_routable": "waitForGuestNetRoutable",
        "wait_for_guest_net_timeout": "waitForGuestNetTimeout",
    },
)
class VirtualMachineConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        resource_pool_id: builtins.str,
        alternate_guest_name: typing.Optional[builtins.str] = None,
        annotation: typing.Optional[builtins.str] = None,
        boot_delay: typing.Optional[jsii.Number] = None,
        boot_retry_delay: typing.Optional[jsii.Number] = None,
        boot_retry_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        cdrom: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VirtualMachineCdrom, typing.Dict[builtins.str, typing.Any]]]]] = None,
        clone: typing.Optional[typing.Union[VirtualMachineClone, typing.Dict[builtins.str, typing.Any]]] = None,
        cpu_hot_add_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        cpu_hot_remove_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        cpu_limit: typing.Optional[jsii.Number] = None,
        cpu_performance_counters_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        cpu_reservation: typing.Optional[jsii.Number] = None,
        cpu_share_count: typing.Optional[jsii.Number] = None,
        cpu_share_level: typing.Optional[builtins.str] = None,
        custom_attributes: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        datacenter_id: typing.Optional[builtins.str] = None,
        datastore_cluster_id: typing.Optional[builtins.str] = None,
        datastore_id: typing.Optional[builtins.str] = None,
        disk: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["VirtualMachineDisk", typing.Dict[builtins.str, typing.Any]]]]] = None,
        efi_secure_boot_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enable_disk_uuid: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enable_logging: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ept_rvi_mode: typing.Optional[builtins.str] = None,
        extra_config: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        extra_config_reboot_required: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        firmware: typing.Optional[builtins.str] = None,
        folder: typing.Optional[builtins.str] = None,
        force_power_off: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        guest_id: typing.Optional[builtins.str] = None,
        hardware_version: typing.Optional[jsii.Number] = None,
        host_system_id: typing.Optional[builtins.str] = None,
        hv_mode: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        ide_controller_count: typing.Optional[jsii.Number] = None,
        ignored_guest_ips: typing.Optional[typing.Sequence[builtins.str]] = None,
        latency_sensitivity: typing.Optional[builtins.str] = None,
        memory: typing.Optional[jsii.Number] = None,
        memory_hot_add_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        memory_limit: typing.Optional[jsii.Number] = None,
        memory_reservation: typing.Optional[jsii.Number] = None,
        memory_reservation_locked_to_max: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        memory_share_count: typing.Optional[jsii.Number] = None,
        memory_share_level: typing.Optional[builtins.str] = None,
        migrate_wait_timeout: typing.Optional[jsii.Number] = None,
        nested_hv_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        network_interface: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["VirtualMachineNetworkInterface", typing.Dict[builtins.str, typing.Any]]]]] = None,
        num_cores_per_socket: typing.Optional[jsii.Number] = None,
        num_cpus: typing.Optional[jsii.Number] = None,
        nvme_controller_count: typing.Optional[jsii.Number] = None,
        ovf_deploy: typing.Optional[typing.Union["VirtualMachineOvfDeploy", typing.Dict[builtins.str, typing.Any]]] = None,
        pci_device_id: typing.Optional[typing.Sequence[builtins.str]] = None,
        poweron_timeout: typing.Optional[jsii.Number] = None,
        replace_trigger: typing.Optional[builtins.str] = None,
        run_tools_scripts_after_power_on: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        run_tools_scripts_after_resume: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        run_tools_scripts_before_guest_reboot: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        run_tools_scripts_before_guest_shutdown: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        run_tools_scripts_before_guest_standby: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        sata_controller_count: typing.Optional[jsii.Number] = None,
        scsi_bus_sharing: typing.Optional[builtins.str] = None,
        scsi_controller_count: typing.Optional[jsii.Number] = None,
        scsi_type: typing.Optional[builtins.str] = None,
        shutdown_wait_timeout: typing.Optional[jsii.Number] = None,
        storage_policy_id: typing.Optional[builtins.str] = None,
        swap_placement_policy: typing.Optional[builtins.str] = None,
        sync_time_with_host: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        sync_time_with_host_periodically: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        tools_upgrade_policy: typing.Optional[builtins.str] = None,
        vapp: typing.Optional[typing.Union["VirtualMachineVapp", typing.Dict[builtins.str, typing.Any]]] = None,
        vbs_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        vtpm: typing.Optional[typing.Union["VirtualMachineVtpm", typing.Dict[builtins.str, typing.Any]]] = None,
        vvtd_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        wait_for_guest_ip_timeout: typing.Optional[jsii.Number] = None,
        wait_for_guest_net_routable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        wait_for_guest_net_timeout: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: The name of this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#name VirtualMachine#name}
        :param resource_pool_id: The ID of a resource pool to put the virtual machine in. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#resource_pool_id VirtualMachine#resource_pool_id}
        :param alternate_guest_name: The guest name for the operating system when guest_id is otherGuest or otherGuest64. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#alternate_guest_name VirtualMachine#alternate_guest_name}
        :param annotation: User-provided description of the virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#annotation VirtualMachine#annotation}
        :param boot_delay: The number of milliseconds to wait before starting the boot sequence. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#boot_delay VirtualMachine#boot_delay}
        :param boot_retry_delay: The number of milliseconds to wait before retrying the boot sequence. This only valid if boot_retry_enabled is true. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#boot_retry_delay VirtualMachine#boot_retry_delay}
        :param boot_retry_enabled: If set to true, a virtual machine that fails to boot will try again after the delay defined in boot_retry_delay. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#boot_retry_enabled VirtualMachine#boot_retry_enabled}
        :param cdrom: cdrom block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#cdrom VirtualMachine#cdrom}
        :param clone: clone block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#clone VirtualMachine#clone}
        :param cpu_hot_add_enabled: Allow CPUs to be added to this virtual machine while it is running. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#cpu_hot_add_enabled VirtualMachine#cpu_hot_add_enabled}
        :param cpu_hot_remove_enabled: Allow CPUs to be added to this virtual machine while it is running. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#cpu_hot_remove_enabled VirtualMachine#cpu_hot_remove_enabled}
        :param cpu_limit: The maximum amount of memory (in MB) or CPU (in MHz) that this virtual machine can consume, regardless of available resources. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#cpu_limit VirtualMachine#cpu_limit}
        :param cpu_performance_counters_enabled: Enable CPU performance counters on this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#cpu_performance_counters_enabled VirtualMachine#cpu_performance_counters_enabled}
        :param cpu_reservation: The amount of memory (in MB) or CPU (in MHz) that this virtual machine is guaranteed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#cpu_reservation VirtualMachine#cpu_reservation}
        :param cpu_share_count: The amount of shares to allocate to cpu for a custom share level. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#cpu_share_count VirtualMachine#cpu_share_count}
        :param cpu_share_level: The allocation level for cpu resources. Can be one of high, low, normal, or custom. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#cpu_share_level VirtualMachine#cpu_share_level}
        :param custom_attributes: A list of custom attributes to set on this resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#custom_attributes VirtualMachine#custom_attributes}
        :param datacenter_id: The ID of the datacenter where the VM is to be created. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#datacenter_id VirtualMachine#datacenter_id}
        :param datastore_cluster_id: The ID of a datastore cluster to put the virtual machine in. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#datastore_cluster_id VirtualMachine#datastore_cluster_id}
        :param datastore_id: The ID of the virtual machine's datastore. The virtual machine configuration is placed here, along with any virtual disks that are created without datastores. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#datastore_id VirtualMachine#datastore_id}
        :param disk: disk block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#disk VirtualMachine#disk}
        :param efi_secure_boot_enabled: When the boot type set in firmware is efi, this enables EFI secure boot. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#efi_secure_boot_enabled VirtualMachine#efi_secure_boot_enabled}
        :param enable_disk_uuid: Expose the UUIDs of attached virtual disks to the virtual machine, allowing access to them in the guest. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#enable_disk_uuid VirtualMachine#enable_disk_uuid}
        :param enable_logging: Enable logging on this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#enable_logging VirtualMachine#enable_logging}
        :param ept_rvi_mode: The EPT/RVI (hardware memory virtualization) setting for this virtual machine. Can be one of automatic, on, or off. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#ept_rvi_mode VirtualMachine#ept_rvi_mode}
        :param extra_config: Extra configuration data for this virtual machine. Can be used to supply advanced parameters not normally in configuration, such as instance metadata, or configuration data for OVF images. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#extra_config VirtualMachine#extra_config}
        :param extra_config_reboot_required: Allow the virtual machine to be rebooted when a change to ``extra_config`` occurs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#extra_config_reboot_required VirtualMachine#extra_config_reboot_required}
        :param firmware: The firmware interface to use on the virtual machine. Can be one of bios or efi. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#firmware VirtualMachine#firmware}
        :param folder: The name of the folder to locate the virtual machine in. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#folder VirtualMachine#folder}
        :param force_power_off: Set to true to force power-off a virtual machine if a graceful guest shutdown failed for a necessary operation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#force_power_off VirtualMachine#force_power_off}
        :param guest_id: The guest ID for the operating system. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#guest_id VirtualMachine#guest_id}
        :param hardware_version: The hardware version for the virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#hardware_version VirtualMachine#hardware_version}
        :param host_system_id: The ID of an optional host system to pin the virtual machine to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#host_system_id VirtualMachine#host_system_id}
        :param hv_mode: The (non-nested) hardware virtualization setting for this virtual machine. Can be one of hvAuto, hvOn, or hvOff. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#hv_mode VirtualMachine#hv_mode}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#id VirtualMachine#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param ide_controller_count: The number of IDE controllers that Terraform manages on this virtual machine. This directly affects the amount of disks you can add to the virtual machine and the maximum disk unit number. Note that lowering this value does not remove controllers. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#ide_controller_count VirtualMachine#ide_controller_count}
        :param ignored_guest_ips: List of IP addresses and CIDR networks to ignore while waiting for an IP. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#ignored_guest_ips VirtualMachine#ignored_guest_ips}
        :param latency_sensitivity: Controls the scheduling delay of the virtual machine. Use a higher sensitivity for applications that require lower latency, such as VOIP, media player applications, or applications that require frequent access to mouse or keyboard devices. Can be one of low, normal, medium, or high. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#latency_sensitivity VirtualMachine#latency_sensitivity}
        :param memory: The size of the virtual machine's memory, in MB. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#memory VirtualMachine#memory}
        :param memory_hot_add_enabled: Allow memory to be added to this virtual machine while it is running. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#memory_hot_add_enabled VirtualMachine#memory_hot_add_enabled}
        :param memory_limit: The maximum amount of memory (in MB) or CPU (in MHz) that this virtual machine can consume, regardless of available resources. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#memory_limit VirtualMachine#memory_limit}
        :param memory_reservation: The amount of memory (in MB) or CPU (in MHz) that this virtual machine is guaranteed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#memory_reservation VirtualMachine#memory_reservation}
        :param memory_reservation_locked_to_max: If set true, memory resource reservation for this virtual machine will always be equal to the virtual machine's memory size;increases in memory size will be rejected when a corresponding reservation increase is not possible. This feature may only be enabled if it is currently possible to reserve all of the virtual machine's memory. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#memory_reservation_locked_to_max VirtualMachine#memory_reservation_locked_to_max}
        :param memory_share_count: The amount of shares to allocate to memory for a custom share level. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#memory_share_count VirtualMachine#memory_share_count}
        :param memory_share_level: The allocation level for memory resources. Can be one of high, low, normal, or custom. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#memory_share_level VirtualMachine#memory_share_level}
        :param migrate_wait_timeout: The amount of time, in minutes, to wait for a vMotion operation to complete before failing. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#migrate_wait_timeout VirtualMachine#migrate_wait_timeout}
        :param nested_hv_enabled: Enable nested hardware virtualization on this virtual machine, facilitating nested virtualization in the guest. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#nested_hv_enabled VirtualMachine#nested_hv_enabled}
        :param network_interface: network_interface block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#network_interface VirtualMachine#network_interface}
        :param num_cores_per_socket: The number of cores to distribute amongst the CPUs in this virtual machine. If specified, the value supplied to num_cpus must be evenly divisible by this value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#num_cores_per_socket VirtualMachine#num_cores_per_socket}
        :param num_cpus: The number of virtual processors to assign to this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#num_cpus VirtualMachine#num_cpus}
        :param nvme_controller_count: The number of NVMe controllers that Terraform manages on this virtual machine. This directly affects the amount of disks you can add to the virtual machine and the maximum disk unit number. Note that lowering this value does not remove controllers. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#nvme_controller_count VirtualMachine#nvme_controller_count}
        :param ovf_deploy: ovf_deploy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#ovf_deploy VirtualMachine#ovf_deploy}
        :param pci_device_id: A list of PCI passthrough devices. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#pci_device_id VirtualMachine#pci_device_id}
        :param poweron_timeout: The amount of time, in seconds, that we will be trying to power on a VM. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#poweron_timeout VirtualMachine#poweron_timeout}
        :param replace_trigger: Triggers replacement of resource whenever it changes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#replace_trigger VirtualMachine#replace_trigger}
        :param run_tools_scripts_after_power_on: Enable the run of scripts after virtual machine power-on when VMware Tools is installed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#run_tools_scripts_after_power_on VirtualMachine#run_tools_scripts_after_power_on}
        :param run_tools_scripts_after_resume: Enable the run of scripts after virtual machine resume when when VMware Tools is installed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#run_tools_scripts_after_resume VirtualMachine#run_tools_scripts_after_resume}
        :param run_tools_scripts_before_guest_reboot: Enable the run of scripts before guest operating system reboot when VMware Tools is installed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#run_tools_scripts_before_guest_reboot VirtualMachine#run_tools_scripts_before_guest_reboot}
        :param run_tools_scripts_before_guest_shutdown: Enable the run of scripts before guest operating system shutdown when VMware Tools is installed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#run_tools_scripts_before_guest_shutdown VirtualMachine#run_tools_scripts_before_guest_shutdown}
        :param run_tools_scripts_before_guest_standby: Enable the run of scripts before guest operating system standby when VMware Tools is installed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#run_tools_scripts_before_guest_standby VirtualMachine#run_tools_scripts_before_guest_standby}
        :param sata_controller_count: The number of SATA controllers that Terraform manages on this virtual machine. This directly affects the amount of disks you can add to the virtual machine and the maximum disk unit number. Note that lowering this value does not remove controllers. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#sata_controller_count VirtualMachine#sata_controller_count}
        :param scsi_bus_sharing: Mode for sharing the SCSI bus. The modes are physicalSharing, virtualSharing, and noSharing. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#scsi_bus_sharing VirtualMachine#scsi_bus_sharing}
        :param scsi_controller_count: The number of SCSI controllers that Terraform manages on this virtual machine. This directly affects the amount of disks you can add to the virtual machine and the maximum disk unit number. Note that lowering this value does not remove controllers. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#scsi_controller_count VirtualMachine#scsi_controller_count}
        :param scsi_type: The type of SCSI bus this virtual machine will have. Can be one of lsilogic, lsilogic-sas or pvscsi. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#scsi_type VirtualMachine#scsi_type}
        :param shutdown_wait_timeout: The amount of time, in minutes, to wait for shutdown when making necessary updates to the virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#shutdown_wait_timeout VirtualMachine#shutdown_wait_timeout}
        :param storage_policy_id: The ID of the storage policy to assign to the virtual machine home directory. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#storage_policy_id VirtualMachine#storage_policy_id}
        :param swap_placement_policy: The swap file placement policy for this virtual machine. Can be one of inherit, hostLocal, or vmDirectory. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#swap_placement_policy VirtualMachine#swap_placement_policy}
        :param sync_time_with_host: Enable guest clock synchronization with the host. On vSphere 7.0 U1 and above, with only this setting the clock is synchronized on startup and resume. Requires VMware Tools to be installed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#sync_time_with_host VirtualMachine#sync_time_with_host}
        :param sync_time_with_host_periodically: Enable periodic clock synchronization with the host. Supported only on vSphere 7.0 U1 and above. On prior versions setting ``sync_time_with_host`` is enough for periodic synchronization. Requires VMware Tools to be installed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#sync_time_with_host_periodically VirtualMachine#sync_time_with_host_periodically}
        :param tags: A list of tag IDs to apply to this object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#tags VirtualMachine#tags}
        :param tools_upgrade_policy: Set the upgrade policy for VMware Tools. Can be one of ``manual`` or ``upgradeAtPowerCycle``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#tools_upgrade_policy VirtualMachine#tools_upgrade_policy}
        :param vapp: vapp block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#vapp VirtualMachine#vapp}
        :param vbs_enabled: Flag to specify if Virtualization-based security is enabled for this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#vbs_enabled VirtualMachine#vbs_enabled}
        :param vtpm: vtpm block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#vtpm VirtualMachine#vtpm}
        :param vvtd_enabled: Flag to specify if I/O MMU virtualization, also called Intel Virtualization Technology for Directed I/O (VT-d) and AMD I/O Virtualization (AMD-Vi or IOMMU), is enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#vvtd_enabled VirtualMachine#vvtd_enabled}
        :param wait_for_guest_ip_timeout: The amount of time, in minutes, to wait for an available IP address on this virtual machine. A value less than 1 disables the waiter. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#wait_for_guest_ip_timeout VirtualMachine#wait_for_guest_ip_timeout}
        :param wait_for_guest_net_routable: Controls whether or not the guest network waiter waits for a routable address. When false, the waiter does not wait for a default gateway, nor are IP addresses checked against any discovered default gateways as part of its success criteria. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#wait_for_guest_net_routable VirtualMachine#wait_for_guest_net_routable}
        :param wait_for_guest_net_timeout: The amount of time, in minutes, to wait for an available IP address on this virtual machine. A value less than 1 disables the waiter. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#wait_for_guest_net_timeout VirtualMachine#wait_for_guest_net_timeout}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(clone, dict):
            clone = VirtualMachineClone(**clone)
        if isinstance(ovf_deploy, dict):
            ovf_deploy = VirtualMachineOvfDeploy(**ovf_deploy)
        if isinstance(vapp, dict):
            vapp = VirtualMachineVapp(**vapp)
        if isinstance(vtpm, dict):
            vtpm = VirtualMachineVtpm(**vtpm)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8cb994aacc5d8d8695d7507f4c95addbd577e3dfee85f804d3a5554ec9b5f9b1)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument resource_pool_id", value=resource_pool_id, expected_type=type_hints["resource_pool_id"])
            check_type(argname="argument alternate_guest_name", value=alternate_guest_name, expected_type=type_hints["alternate_guest_name"])
            check_type(argname="argument annotation", value=annotation, expected_type=type_hints["annotation"])
            check_type(argname="argument boot_delay", value=boot_delay, expected_type=type_hints["boot_delay"])
            check_type(argname="argument boot_retry_delay", value=boot_retry_delay, expected_type=type_hints["boot_retry_delay"])
            check_type(argname="argument boot_retry_enabled", value=boot_retry_enabled, expected_type=type_hints["boot_retry_enabled"])
            check_type(argname="argument cdrom", value=cdrom, expected_type=type_hints["cdrom"])
            check_type(argname="argument clone", value=clone, expected_type=type_hints["clone"])
            check_type(argname="argument cpu_hot_add_enabled", value=cpu_hot_add_enabled, expected_type=type_hints["cpu_hot_add_enabled"])
            check_type(argname="argument cpu_hot_remove_enabled", value=cpu_hot_remove_enabled, expected_type=type_hints["cpu_hot_remove_enabled"])
            check_type(argname="argument cpu_limit", value=cpu_limit, expected_type=type_hints["cpu_limit"])
            check_type(argname="argument cpu_performance_counters_enabled", value=cpu_performance_counters_enabled, expected_type=type_hints["cpu_performance_counters_enabled"])
            check_type(argname="argument cpu_reservation", value=cpu_reservation, expected_type=type_hints["cpu_reservation"])
            check_type(argname="argument cpu_share_count", value=cpu_share_count, expected_type=type_hints["cpu_share_count"])
            check_type(argname="argument cpu_share_level", value=cpu_share_level, expected_type=type_hints["cpu_share_level"])
            check_type(argname="argument custom_attributes", value=custom_attributes, expected_type=type_hints["custom_attributes"])
            check_type(argname="argument datacenter_id", value=datacenter_id, expected_type=type_hints["datacenter_id"])
            check_type(argname="argument datastore_cluster_id", value=datastore_cluster_id, expected_type=type_hints["datastore_cluster_id"])
            check_type(argname="argument datastore_id", value=datastore_id, expected_type=type_hints["datastore_id"])
            check_type(argname="argument disk", value=disk, expected_type=type_hints["disk"])
            check_type(argname="argument efi_secure_boot_enabled", value=efi_secure_boot_enabled, expected_type=type_hints["efi_secure_boot_enabled"])
            check_type(argname="argument enable_disk_uuid", value=enable_disk_uuid, expected_type=type_hints["enable_disk_uuid"])
            check_type(argname="argument enable_logging", value=enable_logging, expected_type=type_hints["enable_logging"])
            check_type(argname="argument ept_rvi_mode", value=ept_rvi_mode, expected_type=type_hints["ept_rvi_mode"])
            check_type(argname="argument extra_config", value=extra_config, expected_type=type_hints["extra_config"])
            check_type(argname="argument extra_config_reboot_required", value=extra_config_reboot_required, expected_type=type_hints["extra_config_reboot_required"])
            check_type(argname="argument firmware", value=firmware, expected_type=type_hints["firmware"])
            check_type(argname="argument folder", value=folder, expected_type=type_hints["folder"])
            check_type(argname="argument force_power_off", value=force_power_off, expected_type=type_hints["force_power_off"])
            check_type(argname="argument guest_id", value=guest_id, expected_type=type_hints["guest_id"])
            check_type(argname="argument hardware_version", value=hardware_version, expected_type=type_hints["hardware_version"])
            check_type(argname="argument host_system_id", value=host_system_id, expected_type=type_hints["host_system_id"])
            check_type(argname="argument hv_mode", value=hv_mode, expected_type=type_hints["hv_mode"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument ide_controller_count", value=ide_controller_count, expected_type=type_hints["ide_controller_count"])
            check_type(argname="argument ignored_guest_ips", value=ignored_guest_ips, expected_type=type_hints["ignored_guest_ips"])
            check_type(argname="argument latency_sensitivity", value=latency_sensitivity, expected_type=type_hints["latency_sensitivity"])
            check_type(argname="argument memory", value=memory, expected_type=type_hints["memory"])
            check_type(argname="argument memory_hot_add_enabled", value=memory_hot_add_enabled, expected_type=type_hints["memory_hot_add_enabled"])
            check_type(argname="argument memory_limit", value=memory_limit, expected_type=type_hints["memory_limit"])
            check_type(argname="argument memory_reservation", value=memory_reservation, expected_type=type_hints["memory_reservation"])
            check_type(argname="argument memory_reservation_locked_to_max", value=memory_reservation_locked_to_max, expected_type=type_hints["memory_reservation_locked_to_max"])
            check_type(argname="argument memory_share_count", value=memory_share_count, expected_type=type_hints["memory_share_count"])
            check_type(argname="argument memory_share_level", value=memory_share_level, expected_type=type_hints["memory_share_level"])
            check_type(argname="argument migrate_wait_timeout", value=migrate_wait_timeout, expected_type=type_hints["migrate_wait_timeout"])
            check_type(argname="argument nested_hv_enabled", value=nested_hv_enabled, expected_type=type_hints["nested_hv_enabled"])
            check_type(argname="argument network_interface", value=network_interface, expected_type=type_hints["network_interface"])
            check_type(argname="argument num_cores_per_socket", value=num_cores_per_socket, expected_type=type_hints["num_cores_per_socket"])
            check_type(argname="argument num_cpus", value=num_cpus, expected_type=type_hints["num_cpus"])
            check_type(argname="argument nvme_controller_count", value=nvme_controller_count, expected_type=type_hints["nvme_controller_count"])
            check_type(argname="argument ovf_deploy", value=ovf_deploy, expected_type=type_hints["ovf_deploy"])
            check_type(argname="argument pci_device_id", value=pci_device_id, expected_type=type_hints["pci_device_id"])
            check_type(argname="argument poweron_timeout", value=poweron_timeout, expected_type=type_hints["poweron_timeout"])
            check_type(argname="argument replace_trigger", value=replace_trigger, expected_type=type_hints["replace_trigger"])
            check_type(argname="argument run_tools_scripts_after_power_on", value=run_tools_scripts_after_power_on, expected_type=type_hints["run_tools_scripts_after_power_on"])
            check_type(argname="argument run_tools_scripts_after_resume", value=run_tools_scripts_after_resume, expected_type=type_hints["run_tools_scripts_after_resume"])
            check_type(argname="argument run_tools_scripts_before_guest_reboot", value=run_tools_scripts_before_guest_reboot, expected_type=type_hints["run_tools_scripts_before_guest_reboot"])
            check_type(argname="argument run_tools_scripts_before_guest_shutdown", value=run_tools_scripts_before_guest_shutdown, expected_type=type_hints["run_tools_scripts_before_guest_shutdown"])
            check_type(argname="argument run_tools_scripts_before_guest_standby", value=run_tools_scripts_before_guest_standby, expected_type=type_hints["run_tools_scripts_before_guest_standby"])
            check_type(argname="argument sata_controller_count", value=sata_controller_count, expected_type=type_hints["sata_controller_count"])
            check_type(argname="argument scsi_bus_sharing", value=scsi_bus_sharing, expected_type=type_hints["scsi_bus_sharing"])
            check_type(argname="argument scsi_controller_count", value=scsi_controller_count, expected_type=type_hints["scsi_controller_count"])
            check_type(argname="argument scsi_type", value=scsi_type, expected_type=type_hints["scsi_type"])
            check_type(argname="argument shutdown_wait_timeout", value=shutdown_wait_timeout, expected_type=type_hints["shutdown_wait_timeout"])
            check_type(argname="argument storage_policy_id", value=storage_policy_id, expected_type=type_hints["storage_policy_id"])
            check_type(argname="argument swap_placement_policy", value=swap_placement_policy, expected_type=type_hints["swap_placement_policy"])
            check_type(argname="argument sync_time_with_host", value=sync_time_with_host, expected_type=type_hints["sync_time_with_host"])
            check_type(argname="argument sync_time_with_host_periodically", value=sync_time_with_host_periodically, expected_type=type_hints["sync_time_with_host_periodically"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument tools_upgrade_policy", value=tools_upgrade_policy, expected_type=type_hints["tools_upgrade_policy"])
            check_type(argname="argument vapp", value=vapp, expected_type=type_hints["vapp"])
            check_type(argname="argument vbs_enabled", value=vbs_enabled, expected_type=type_hints["vbs_enabled"])
            check_type(argname="argument vtpm", value=vtpm, expected_type=type_hints["vtpm"])
            check_type(argname="argument vvtd_enabled", value=vvtd_enabled, expected_type=type_hints["vvtd_enabled"])
            check_type(argname="argument wait_for_guest_ip_timeout", value=wait_for_guest_ip_timeout, expected_type=type_hints["wait_for_guest_ip_timeout"])
            check_type(argname="argument wait_for_guest_net_routable", value=wait_for_guest_net_routable, expected_type=type_hints["wait_for_guest_net_routable"])
            check_type(argname="argument wait_for_guest_net_timeout", value=wait_for_guest_net_timeout, expected_type=type_hints["wait_for_guest_net_timeout"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "resource_pool_id": resource_pool_id,
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
        if alternate_guest_name is not None:
            self._values["alternate_guest_name"] = alternate_guest_name
        if annotation is not None:
            self._values["annotation"] = annotation
        if boot_delay is not None:
            self._values["boot_delay"] = boot_delay
        if boot_retry_delay is not None:
            self._values["boot_retry_delay"] = boot_retry_delay
        if boot_retry_enabled is not None:
            self._values["boot_retry_enabled"] = boot_retry_enabled
        if cdrom is not None:
            self._values["cdrom"] = cdrom
        if clone is not None:
            self._values["clone"] = clone
        if cpu_hot_add_enabled is not None:
            self._values["cpu_hot_add_enabled"] = cpu_hot_add_enabled
        if cpu_hot_remove_enabled is not None:
            self._values["cpu_hot_remove_enabled"] = cpu_hot_remove_enabled
        if cpu_limit is not None:
            self._values["cpu_limit"] = cpu_limit
        if cpu_performance_counters_enabled is not None:
            self._values["cpu_performance_counters_enabled"] = cpu_performance_counters_enabled
        if cpu_reservation is not None:
            self._values["cpu_reservation"] = cpu_reservation
        if cpu_share_count is not None:
            self._values["cpu_share_count"] = cpu_share_count
        if cpu_share_level is not None:
            self._values["cpu_share_level"] = cpu_share_level
        if custom_attributes is not None:
            self._values["custom_attributes"] = custom_attributes
        if datacenter_id is not None:
            self._values["datacenter_id"] = datacenter_id
        if datastore_cluster_id is not None:
            self._values["datastore_cluster_id"] = datastore_cluster_id
        if datastore_id is not None:
            self._values["datastore_id"] = datastore_id
        if disk is not None:
            self._values["disk"] = disk
        if efi_secure_boot_enabled is not None:
            self._values["efi_secure_boot_enabled"] = efi_secure_boot_enabled
        if enable_disk_uuid is not None:
            self._values["enable_disk_uuid"] = enable_disk_uuid
        if enable_logging is not None:
            self._values["enable_logging"] = enable_logging
        if ept_rvi_mode is not None:
            self._values["ept_rvi_mode"] = ept_rvi_mode
        if extra_config is not None:
            self._values["extra_config"] = extra_config
        if extra_config_reboot_required is not None:
            self._values["extra_config_reboot_required"] = extra_config_reboot_required
        if firmware is not None:
            self._values["firmware"] = firmware
        if folder is not None:
            self._values["folder"] = folder
        if force_power_off is not None:
            self._values["force_power_off"] = force_power_off
        if guest_id is not None:
            self._values["guest_id"] = guest_id
        if hardware_version is not None:
            self._values["hardware_version"] = hardware_version
        if host_system_id is not None:
            self._values["host_system_id"] = host_system_id
        if hv_mode is not None:
            self._values["hv_mode"] = hv_mode
        if id is not None:
            self._values["id"] = id
        if ide_controller_count is not None:
            self._values["ide_controller_count"] = ide_controller_count
        if ignored_guest_ips is not None:
            self._values["ignored_guest_ips"] = ignored_guest_ips
        if latency_sensitivity is not None:
            self._values["latency_sensitivity"] = latency_sensitivity
        if memory is not None:
            self._values["memory"] = memory
        if memory_hot_add_enabled is not None:
            self._values["memory_hot_add_enabled"] = memory_hot_add_enabled
        if memory_limit is not None:
            self._values["memory_limit"] = memory_limit
        if memory_reservation is not None:
            self._values["memory_reservation"] = memory_reservation
        if memory_reservation_locked_to_max is not None:
            self._values["memory_reservation_locked_to_max"] = memory_reservation_locked_to_max
        if memory_share_count is not None:
            self._values["memory_share_count"] = memory_share_count
        if memory_share_level is not None:
            self._values["memory_share_level"] = memory_share_level
        if migrate_wait_timeout is not None:
            self._values["migrate_wait_timeout"] = migrate_wait_timeout
        if nested_hv_enabled is not None:
            self._values["nested_hv_enabled"] = nested_hv_enabled
        if network_interface is not None:
            self._values["network_interface"] = network_interface
        if num_cores_per_socket is not None:
            self._values["num_cores_per_socket"] = num_cores_per_socket
        if num_cpus is not None:
            self._values["num_cpus"] = num_cpus
        if nvme_controller_count is not None:
            self._values["nvme_controller_count"] = nvme_controller_count
        if ovf_deploy is not None:
            self._values["ovf_deploy"] = ovf_deploy
        if pci_device_id is not None:
            self._values["pci_device_id"] = pci_device_id
        if poweron_timeout is not None:
            self._values["poweron_timeout"] = poweron_timeout
        if replace_trigger is not None:
            self._values["replace_trigger"] = replace_trigger
        if run_tools_scripts_after_power_on is not None:
            self._values["run_tools_scripts_after_power_on"] = run_tools_scripts_after_power_on
        if run_tools_scripts_after_resume is not None:
            self._values["run_tools_scripts_after_resume"] = run_tools_scripts_after_resume
        if run_tools_scripts_before_guest_reboot is not None:
            self._values["run_tools_scripts_before_guest_reboot"] = run_tools_scripts_before_guest_reboot
        if run_tools_scripts_before_guest_shutdown is not None:
            self._values["run_tools_scripts_before_guest_shutdown"] = run_tools_scripts_before_guest_shutdown
        if run_tools_scripts_before_guest_standby is not None:
            self._values["run_tools_scripts_before_guest_standby"] = run_tools_scripts_before_guest_standby
        if sata_controller_count is not None:
            self._values["sata_controller_count"] = sata_controller_count
        if scsi_bus_sharing is not None:
            self._values["scsi_bus_sharing"] = scsi_bus_sharing
        if scsi_controller_count is not None:
            self._values["scsi_controller_count"] = scsi_controller_count
        if scsi_type is not None:
            self._values["scsi_type"] = scsi_type
        if shutdown_wait_timeout is not None:
            self._values["shutdown_wait_timeout"] = shutdown_wait_timeout
        if storage_policy_id is not None:
            self._values["storage_policy_id"] = storage_policy_id
        if swap_placement_policy is not None:
            self._values["swap_placement_policy"] = swap_placement_policy
        if sync_time_with_host is not None:
            self._values["sync_time_with_host"] = sync_time_with_host
        if sync_time_with_host_periodically is not None:
            self._values["sync_time_with_host_periodically"] = sync_time_with_host_periodically
        if tags is not None:
            self._values["tags"] = tags
        if tools_upgrade_policy is not None:
            self._values["tools_upgrade_policy"] = tools_upgrade_policy
        if vapp is not None:
            self._values["vapp"] = vapp
        if vbs_enabled is not None:
            self._values["vbs_enabled"] = vbs_enabled
        if vtpm is not None:
            self._values["vtpm"] = vtpm
        if vvtd_enabled is not None:
            self._values["vvtd_enabled"] = vvtd_enabled
        if wait_for_guest_ip_timeout is not None:
            self._values["wait_for_guest_ip_timeout"] = wait_for_guest_ip_timeout
        if wait_for_guest_net_routable is not None:
            self._values["wait_for_guest_net_routable"] = wait_for_guest_net_routable
        if wait_for_guest_net_timeout is not None:
            self._values["wait_for_guest_net_timeout"] = wait_for_guest_net_timeout

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
        '''The name of this virtual machine.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#name VirtualMachine#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def resource_pool_id(self) -> builtins.str:
        '''The ID of a resource pool to put the virtual machine in.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#resource_pool_id VirtualMachine#resource_pool_id}
        '''
        result = self._values.get("resource_pool_id")
        assert result is not None, "Required property 'resource_pool_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def alternate_guest_name(self) -> typing.Optional[builtins.str]:
        '''The guest name for the operating system when guest_id is otherGuest or otherGuest64.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#alternate_guest_name VirtualMachine#alternate_guest_name}
        '''
        result = self._values.get("alternate_guest_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def annotation(self) -> typing.Optional[builtins.str]:
        '''User-provided description of the virtual machine.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#annotation VirtualMachine#annotation}
        '''
        result = self._values.get("annotation")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def boot_delay(self) -> typing.Optional[jsii.Number]:
        '''The number of milliseconds to wait before starting the boot sequence.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#boot_delay VirtualMachine#boot_delay}
        '''
        result = self._values.get("boot_delay")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def boot_retry_delay(self) -> typing.Optional[jsii.Number]:
        '''The number of milliseconds to wait before retrying the boot sequence. This only valid if boot_retry_enabled is true.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#boot_retry_delay VirtualMachine#boot_retry_delay}
        '''
        result = self._values.get("boot_retry_delay")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def boot_retry_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If set to true, a virtual machine that fails to boot will try again after the delay defined in boot_retry_delay.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#boot_retry_enabled VirtualMachine#boot_retry_enabled}
        '''
        result = self._values.get("boot_retry_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def cdrom(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VirtualMachineCdrom]]]:
        '''cdrom block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#cdrom VirtualMachine#cdrom}
        '''
        result = self._values.get("cdrom")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VirtualMachineCdrom]]], result)

    @builtins.property
    def clone(self) -> typing.Optional[VirtualMachineClone]:
        '''clone block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#clone VirtualMachine#clone}
        '''
        result = self._values.get("clone")
        return typing.cast(typing.Optional[VirtualMachineClone], result)

    @builtins.property
    def cpu_hot_add_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Allow CPUs to be added to this virtual machine while it is running.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#cpu_hot_add_enabled VirtualMachine#cpu_hot_add_enabled}
        '''
        result = self._values.get("cpu_hot_add_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def cpu_hot_remove_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Allow CPUs to be added to this virtual machine while it is running.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#cpu_hot_remove_enabled VirtualMachine#cpu_hot_remove_enabled}
        '''
        result = self._values.get("cpu_hot_remove_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def cpu_limit(self) -> typing.Optional[jsii.Number]:
        '''The maximum amount of memory (in MB) or CPU (in MHz) that this virtual machine can consume, regardless of available resources.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#cpu_limit VirtualMachine#cpu_limit}
        '''
        result = self._values.get("cpu_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def cpu_performance_counters_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable CPU performance counters on this virtual machine.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#cpu_performance_counters_enabled VirtualMachine#cpu_performance_counters_enabled}
        '''
        result = self._values.get("cpu_performance_counters_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def cpu_reservation(self) -> typing.Optional[jsii.Number]:
        '''The amount of memory (in MB) or CPU (in MHz) that this virtual machine is guaranteed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#cpu_reservation VirtualMachine#cpu_reservation}
        '''
        result = self._values.get("cpu_reservation")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def cpu_share_count(self) -> typing.Optional[jsii.Number]:
        '''The amount of shares to allocate to cpu for a custom share level.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#cpu_share_count VirtualMachine#cpu_share_count}
        '''
        result = self._values.get("cpu_share_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def cpu_share_level(self) -> typing.Optional[builtins.str]:
        '''The allocation level for cpu resources. Can be one of high, low, normal, or custom.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#cpu_share_level VirtualMachine#cpu_share_level}
        '''
        result = self._values.get("cpu_share_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_attributes(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''A list of custom attributes to set on this resource.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#custom_attributes VirtualMachine#custom_attributes}
        '''
        result = self._values.get("custom_attributes")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def datacenter_id(self) -> typing.Optional[builtins.str]:
        '''The ID of the datacenter where the VM is to be created.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#datacenter_id VirtualMachine#datacenter_id}
        '''
        result = self._values.get("datacenter_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def datastore_cluster_id(self) -> typing.Optional[builtins.str]:
        '''The ID of a datastore cluster to put the virtual machine in.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#datastore_cluster_id VirtualMachine#datastore_cluster_id}
        '''
        result = self._values.get("datastore_cluster_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def datastore_id(self) -> typing.Optional[builtins.str]:
        '''The ID of the virtual machine's datastore.

        The virtual machine configuration is placed here, along with any virtual disks that are created without datastores.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#datastore_id VirtualMachine#datastore_id}
        '''
        result = self._values.get("datastore_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disk(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VirtualMachineDisk"]]]:
        '''disk block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#disk VirtualMachine#disk}
        '''
        result = self._values.get("disk")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VirtualMachineDisk"]]], result)

    @builtins.property
    def efi_secure_boot_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''When the boot type set in firmware is efi, this enables EFI secure boot.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#efi_secure_boot_enabled VirtualMachine#efi_secure_boot_enabled}
        '''
        result = self._values.get("efi_secure_boot_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def enable_disk_uuid(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Expose the UUIDs of attached virtual disks to the virtual machine, allowing access to them in the guest.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#enable_disk_uuid VirtualMachine#enable_disk_uuid}
        '''
        result = self._values.get("enable_disk_uuid")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def enable_logging(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable logging on this virtual machine.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#enable_logging VirtualMachine#enable_logging}
        '''
        result = self._values.get("enable_logging")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def ept_rvi_mode(self) -> typing.Optional[builtins.str]:
        '''The EPT/RVI (hardware memory virtualization) setting for this virtual machine. Can be one of automatic, on, or off.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#ept_rvi_mode VirtualMachine#ept_rvi_mode}
        '''
        result = self._values.get("ept_rvi_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def extra_config(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Extra configuration data for this virtual machine.

        Can be used to supply advanced parameters not normally in configuration, such as instance metadata, or configuration data for OVF images.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#extra_config VirtualMachine#extra_config}
        '''
        result = self._values.get("extra_config")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def extra_config_reboot_required(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Allow the virtual machine to be rebooted when a change to ``extra_config`` occurs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#extra_config_reboot_required VirtualMachine#extra_config_reboot_required}
        '''
        result = self._values.get("extra_config_reboot_required")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def firmware(self) -> typing.Optional[builtins.str]:
        '''The firmware interface to use on the virtual machine. Can be one of bios or efi.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#firmware VirtualMachine#firmware}
        '''
        result = self._values.get("firmware")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def folder(self) -> typing.Optional[builtins.str]:
        '''The name of the folder to locate the virtual machine in.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#folder VirtualMachine#folder}
        '''
        result = self._values.get("folder")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def force_power_off(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Set to true to force power-off a virtual machine if a graceful guest shutdown failed for a necessary operation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#force_power_off VirtualMachine#force_power_off}
        '''
        result = self._values.get("force_power_off")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def guest_id(self) -> typing.Optional[builtins.str]:
        '''The guest ID for the operating system.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#guest_id VirtualMachine#guest_id}
        '''
        result = self._values.get("guest_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def hardware_version(self) -> typing.Optional[jsii.Number]:
        '''The hardware version for the virtual machine.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#hardware_version VirtualMachine#hardware_version}
        '''
        result = self._values.get("hardware_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def host_system_id(self) -> typing.Optional[builtins.str]:
        '''The ID of an optional host system to pin the virtual machine to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#host_system_id VirtualMachine#host_system_id}
        '''
        result = self._values.get("host_system_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def hv_mode(self) -> typing.Optional[builtins.str]:
        '''The (non-nested) hardware virtualization setting for this virtual machine. Can be one of hvAuto, hvOn, or hvOff.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#hv_mode VirtualMachine#hv_mode}
        '''
        result = self._values.get("hv_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#id VirtualMachine#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ide_controller_count(self) -> typing.Optional[jsii.Number]:
        '''The number of IDE controllers that Terraform manages on this virtual machine.

        This directly affects the amount of disks you can add to the virtual machine and the maximum disk unit number. Note that lowering this value does not remove controllers.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#ide_controller_count VirtualMachine#ide_controller_count}
        '''
        result = self._values.get("ide_controller_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ignored_guest_ips(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of IP addresses and CIDR networks to ignore while waiting for an IP.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#ignored_guest_ips VirtualMachine#ignored_guest_ips}
        '''
        result = self._values.get("ignored_guest_ips")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def latency_sensitivity(self) -> typing.Optional[builtins.str]:
        '''Controls the scheduling delay of the virtual machine.

        Use a higher sensitivity for applications that require lower latency, such as VOIP, media player applications, or applications that require frequent access to mouse or keyboard devices. Can be one of low, normal, medium, or high.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#latency_sensitivity VirtualMachine#latency_sensitivity}
        '''
        result = self._values.get("latency_sensitivity")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def memory(self) -> typing.Optional[jsii.Number]:
        '''The size of the virtual machine's memory, in MB.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#memory VirtualMachine#memory}
        '''
        result = self._values.get("memory")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def memory_hot_add_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Allow memory to be added to this virtual machine while it is running.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#memory_hot_add_enabled VirtualMachine#memory_hot_add_enabled}
        '''
        result = self._values.get("memory_hot_add_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def memory_limit(self) -> typing.Optional[jsii.Number]:
        '''The maximum amount of memory (in MB) or CPU (in MHz) that this virtual machine can consume, regardless of available resources.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#memory_limit VirtualMachine#memory_limit}
        '''
        result = self._values.get("memory_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def memory_reservation(self) -> typing.Optional[jsii.Number]:
        '''The amount of memory (in MB) or CPU (in MHz) that this virtual machine is guaranteed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#memory_reservation VirtualMachine#memory_reservation}
        '''
        result = self._values.get("memory_reservation")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def memory_reservation_locked_to_max(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If set true, memory resource reservation for this virtual machine will always be equal to the virtual machine's memory size;increases in memory size will be rejected when a corresponding reservation increase is not possible. This feature may only be enabled if it is currently possible to reserve all of the virtual machine's memory.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#memory_reservation_locked_to_max VirtualMachine#memory_reservation_locked_to_max}
        '''
        result = self._values.get("memory_reservation_locked_to_max")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def memory_share_count(self) -> typing.Optional[jsii.Number]:
        '''The amount of shares to allocate to memory for a custom share level.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#memory_share_count VirtualMachine#memory_share_count}
        '''
        result = self._values.get("memory_share_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def memory_share_level(self) -> typing.Optional[builtins.str]:
        '''The allocation level for memory resources. Can be one of high, low, normal, or custom.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#memory_share_level VirtualMachine#memory_share_level}
        '''
        result = self._values.get("memory_share_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def migrate_wait_timeout(self) -> typing.Optional[jsii.Number]:
        '''The amount of time, in minutes, to wait for a vMotion operation to complete before failing.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#migrate_wait_timeout VirtualMachine#migrate_wait_timeout}
        '''
        result = self._values.get("migrate_wait_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def nested_hv_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable nested hardware virtualization on this virtual machine, facilitating nested virtualization in the guest.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#nested_hv_enabled VirtualMachine#nested_hv_enabled}
        '''
        result = self._values.get("nested_hv_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def network_interface(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VirtualMachineNetworkInterface"]]]:
        '''network_interface block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#network_interface VirtualMachine#network_interface}
        '''
        result = self._values.get("network_interface")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VirtualMachineNetworkInterface"]]], result)

    @builtins.property
    def num_cores_per_socket(self) -> typing.Optional[jsii.Number]:
        '''The number of cores to distribute amongst the CPUs in this virtual machine.

        If specified, the value supplied to num_cpus must be evenly divisible by this value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#num_cores_per_socket VirtualMachine#num_cores_per_socket}
        '''
        result = self._values.get("num_cores_per_socket")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def num_cpus(self) -> typing.Optional[jsii.Number]:
        '''The number of virtual processors to assign to this virtual machine.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#num_cpus VirtualMachine#num_cpus}
        '''
        result = self._values.get("num_cpus")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def nvme_controller_count(self) -> typing.Optional[jsii.Number]:
        '''The number of NVMe controllers that Terraform manages on this virtual machine.

        This directly affects the amount of disks you can add to the virtual machine and the maximum disk unit number. Note that lowering this value does not remove controllers.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#nvme_controller_count VirtualMachine#nvme_controller_count}
        '''
        result = self._values.get("nvme_controller_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ovf_deploy(self) -> typing.Optional["VirtualMachineOvfDeploy"]:
        '''ovf_deploy block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#ovf_deploy VirtualMachine#ovf_deploy}
        '''
        result = self._values.get("ovf_deploy")
        return typing.cast(typing.Optional["VirtualMachineOvfDeploy"], result)

    @builtins.property
    def pci_device_id(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of PCI passthrough devices.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#pci_device_id VirtualMachine#pci_device_id}
        '''
        result = self._values.get("pci_device_id")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def poweron_timeout(self) -> typing.Optional[jsii.Number]:
        '''The amount of time, in seconds, that we will be trying to power on a VM.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#poweron_timeout VirtualMachine#poweron_timeout}
        '''
        result = self._values.get("poweron_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def replace_trigger(self) -> typing.Optional[builtins.str]:
        '''Triggers replacement of resource whenever it changes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#replace_trigger VirtualMachine#replace_trigger}
        '''
        result = self._values.get("replace_trigger")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def run_tools_scripts_after_power_on(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable the run of scripts after virtual machine power-on when VMware Tools is installed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#run_tools_scripts_after_power_on VirtualMachine#run_tools_scripts_after_power_on}
        '''
        result = self._values.get("run_tools_scripts_after_power_on")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def run_tools_scripts_after_resume(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable the run of scripts after virtual machine resume when when VMware Tools is installed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#run_tools_scripts_after_resume VirtualMachine#run_tools_scripts_after_resume}
        '''
        result = self._values.get("run_tools_scripts_after_resume")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def run_tools_scripts_before_guest_reboot(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable the run of scripts before guest operating system reboot when VMware Tools is installed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#run_tools_scripts_before_guest_reboot VirtualMachine#run_tools_scripts_before_guest_reboot}
        '''
        result = self._values.get("run_tools_scripts_before_guest_reboot")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def run_tools_scripts_before_guest_shutdown(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable the run of scripts before guest operating system shutdown when VMware Tools is installed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#run_tools_scripts_before_guest_shutdown VirtualMachine#run_tools_scripts_before_guest_shutdown}
        '''
        result = self._values.get("run_tools_scripts_before_guest_shutdown")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def run_tools_scripts_before_guest_standby(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable the run of scripts before guest operating system standby when VMware Tools is installed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#run_tools_scripts_before_guest_standby VirtualMachine#run_tools_scripts_before_guest_standby}
        '''
        result = self._values.get("run_tools_scripts_before_guest_standby")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def sata_controller_count(self) -> typing.Optional[jsii.Number]:
        '''The number of SATA controllers that Terraform manages on this virtual machine.

        This directly affects the amount of disks you can add to the virtual machine and the maximum disk unit number. Note that lowering this value does not remove controllers.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#sata_controller_count VirtualMachine#sata_controller_count}
        '''
        result = self._values.get("sata_controller_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def scsi_bus_sharing(self) -> typing.Optional[builtins.str]:
        '''Mode for sharing the SCSI bus. The modes are physicalSharing, virtualSharing, and noSharing.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#scsi_bus_sharing VirtualMachine#scsi_bus_sharing}
        '''
        result = self._values.get("scsi_bus_sharing")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def scsi_controller_count(self) -> typing.Optional[jsii.Number]:
        '''The number of SCSI controllers that Terraform manages on this virtual machine.

        This directly affects the amount of disks you can add to the virtual machine and the maximum disk unit number. Note that lowering this value does not remove controllers.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#scsi_controller_count VirtualMachine#scsi_controller_count}
        '''
        result = self._values.get("scsi_controller_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def scsi_type(self) -> typing.Optional[builtins.str]:
        '''The type of SCSI bus this virtual machine will have. Can be one of lsilogic, lsilogic-sas or pvscsi.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#scsi_type VirtualMachine#scsi_type}
        '''
        result = self._values.get("scsi_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def shutdown_wait_timeout(self) -> typing.Optional[jsii.Number]:
        '''The amount of time, in minutes, to wait for shutdown when making necessary updates to the virtual machine.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#shutdown_wait_timeout VirtualMachine#shutdown_wait_timeout}
        '''
        result = self._values.get("shutdown_wait_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def storage_policy_id(self) -> typing.Optional[builtins.str]:
        '''The ID of the storage policy to assign to the virtual machine home directory.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#storage_policy_id VirtualMachine#storage_policy_id}
        '''
        result = self._values.get("storage_policy_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def swap_placement_policy(self) -> typing.Optional[builtins.str]:
        '''The swap file placement policy for this virtual machine. Can be one of inherit, hostLocal, or vmDirectory.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#swap_placement_policy VirtualMachine#swap_placement_policy}
        '''
        result = self._values.get("swap_placement_policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sync_time_with_host(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable guest clock synchronization with the host.

        On vSphere 7.0 U1 and above, with only this setting the clock is synchronized on startup and resume. Requires VMware Tools to be installed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#sync_time_with_host VirtualMachine#sync_time_with_host}
        '''
        result = self._values.get("sync_time_with_host")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def sync_time_with_host_periodically(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable periodic clock synchronization with the host.

        Supported only on vSphere 7.0 U1 and above. On prior versions setting ``sync_time_with_host`` is enough for periodic synchronization. Requires VMware Tools to be installed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#sync_time_with_host_periodically VirtualMachine#sync_time_with_host_periodically}
        '''
        result = self._values.get("sync_time_with_host_periodically")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of tag IDs to apply to this object.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#tags VirtualMachine#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tools_upgrade_policy(self) -> typing.Optional[builtins.str]:
        '''Set the upgrade policy for VMware Tools. Can be one of ``manual`` or ``upgradeAtPowerCycle``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#tools_upgrade_policy VirtualMachine#tools_upgrade_policy}
        '''
        result = self._values.get("tools_upgrade_policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vapp(self) -> typing.Optional["VirtualMachineVapp"]:
        '''vapp block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#vapp VirtualMachine#vapp}
        '''
        result = self._values.get("vapp")
        return typing.cast(typing.Optional["VirtualMachineVapp"], result)

    @builtins.property
    def vbs_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Flag to specify if Virtualization-based security is enabled for this virtual machine.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#vbs_enabled VirtualMachine#vbs_enabled}
        '''
        result = self._values.get("vbs_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def vtpm(self) -> typing.Optional["VirtualMachineVtpm"]:
        '''vtpm block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#vtpm VirtualMachine#vtpm}
        '''
        result = self._values.get("vtpm")
        return typing.cast(typing.Optional["VirtualMachineVtpm"], result)

    @builtins.property
    def vvtd_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Flag to specify if I/O MMU virtualization, also called Intel Virtualization Technology for Directed I/O (VT-d) and AMD I/O Virtualization (AMD-Vi or IOMMU), is enabled.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#vvtd_enabled VirtualMachine#vvtd_enabled}
        '''
        result = self._values.get("vvtd_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def wait_for_guest_ip_timeout(self) -> typing.Optional[jsii.Number]:
        '''The amount of time, in minutes, to wait for an available IP address on this virtual machine.

        A value less than 1 disables the waiter.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#wait_for_guest_ip_timeout VirtualMachine#wait_for_guest_ip_timeout}
        '''
        result = self._values.get("wait_for_guest_ip_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def wait_for_guest_net_routable(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Controls whether or not the guest network waiter waits for a routable address.

        When false, the waiter does not wait for a default gateway, nor are IP addresses checked against any discovered default gateways as part of its success criteria.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#wait_for_guest_net_routable VirtualMachine#wait_for_guest_net_routable}
        '''
        result = self._values.get("wait_for_guest_net_routable")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def wait_for_guest_net_timeout(self) -> typing.Optional[jsii.Number]:
        '''The amount of time, in minutes, to wait for an available IP address on this virtual machine.

        A value less than 1 disables the waiter.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#wait_for_guest_net_timeout VirtualMachine#wait_for_guest_net_timeout}
        '''
        result = self._values.get("wait_for_guest_net_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VirtualMachineConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.virtualMachine.VirtualMachineDisk",
    jsii_struct_bases=[],
    name_mapping={
        "label": "label",
        "attach": "attach",
        "controller_type": "controllerType",
        "datastore_id": "datastoreId",
        "disk_mode": "diskMode",
        "disk_sharing": "diskSharing",
        "eagerly_scrub": "eagerlyScrub",
        "io_limit": "ioLimit",
        "io_reservation": "ioReservation",
        "io_share_count": "ioShareCount",
        "io_share_level": "ioShareLevel",
        "keep_on_remove": "keepOnRemove",
        "path": "path",
        "size": "size",
        "storage_policy_id": "storagePolicyId",
        "thin_provisioned": "thinProvisioned",
        "unit_number": "unitNumber",
        "write_through": "writeThrough",
    },
)
class VirtualMachineDisk:
    def __init__(
        self,
        *,
        label: builtins.str,
        attach: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        controller_type: typing.Optional[builtins.str] = None,
        datastore_id: typing.Optional[builtins.str] = None,
        disk_mode: typing.Optional[builtins.str] = None,
        disk_sharing: typing.Optional[builtins.str] = None,
        eagerly_scrub: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        io_limit: typing.Optional[jsii.Number] = None,
        io_reservation: typing.Optional[jsii.Number] = None,
        io_share_count: typing.Optional[jsii.Number] = None,
        io_share_level: typing.Optional[builtins.str] = None,
        keep_on_remove: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        path: typing.Optional[builtins.str] = None,
        size: typing.Optional[jsii.Number] = None,
        storage_policy_id: typing.Optional[builtins.str] = None,
        thin_provisioned: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        unit_number: typing.Optional[jsii.Number] = None,
        write_through: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param label: A unique label for this disk. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#label VirtualMachine#label}
        :param attach: If this is true, the disk is attached instead of created. Implies keep_on_remove. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#attach VirtualMachine#attach}
        :param controller_type: The type of controller the disk should be connected to. Must be 'scsi', 'sata', 'nvme', or 'ide'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#controller_type VirtualMachine#controller_type}
        :param datastore_id: The datastore ID for this virtual disk, if different than the virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#datastore_id VirtualMachine#datastore_id}
        :param disk_mode: The mode of this this virtual disk for purposes of writes and snapshotting. Can be one of append, independent_nonpersistent, independent_persistent, nonpersistent, persistent, or undoable. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#disk_mode VirtualMachine#disk_mode}
        :param disk_sharing: The sharing mode of this virtual disk. Can be one of sharingMultiWriter or sharingNone. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#disk_sharing VirtualMachine#disk_sharing}
        :param eagerly_scrub: The virtual disk file zeroing policy when thin_provision is not true. The default is false, which lazily-zeros the disk, speeding up thick-provisioned disk creation time. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#eagerly_scrub VirtualMachine#eagerly_scrub}
        :param io_limit: The upper limit of IOPS that this disk can use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#io_limit VirtualMachine#io_limit}
        :param io_reservation: The I/O guarantee that this disk has, in IOPS. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#io_reservation VirtualMachine#io_reservation}
        :param io_share_count: The share count for this disk when the share level is custom. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#io_share_count VirtualMachine#io_share_count}
        :param io_share_level: The share allocation level for this disk. Can be one of low, normal, high, or custom. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#io_share_level VirtualMachine#io_share_level}
        :param keep_on_remove: Set to true to keep the underlying VMDK file when removing this virtual disk from configuration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#keep_on_remove VirtualMachine#keep_on_remove}
        :param path: The full path of the virtual disk. This can only be provided if attach is set to true, otherwise it is a read-only value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#path VirtualMachine#path}
        :param size: The size of the disk, in GB. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#size VirtualMachine#size}
        :param storage_policy_id: The ID of the storage policy to assign to the virtual disk in VM. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#storage_policy_id VirtualMachine#storage_policy_id}
        :param thin_provisioned: If true, this disk is thin provisioned, with space for the file being allocated on an as-needed basis. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#thin_provisioned VirtualMachine#thin_provisioned}
        :param unit_number: The unique device number for this disk. This number determines where on the SCSI bus this device will be attached. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#unit_number VirtualMachine#unit_number}
        :param write_through: If true, writes for this disk are sent directly to the filesystem immediately instead of being buffered. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#write_through VirtualMachine#write_through}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aab91385a396cb5112f20f1e520ccf43242269bf1d54b0652fb3445b6aac8f5a)
            check_type(argname="argument label", value=label, expected_type=type_hints["label"])
            check_type(argname="argument attach", value=attach, expected_type=type_hints["attach"])
            check_type(argname="argument controller_type", value=controller_type, expected_type=type_hints["controller_type"])
            check_type(argname="argument datastore_id", value=datastore_id, expected_type=type_hints["datastore_id"])
            check_type(argname="argument disk_mode", value=disk_mode, expected_type=type_hints["disk_mode"])
            check_type(argname="argument disk_sharing", value=disk_sharing, expected_type=type_hints["disk_sharing"])
            check_type(argname="argument eagerly_scrub", value=eagerly_scrub, expected_type=type_hints["eagerly_scrub"])
            check_type(argname="argument io_limit", value=io_limit, expected_type=type_hints["io_limit"])
            check_type(argname="argument io_reservation", value=io_reservation, expected_type=type_hints["io_reservation"])
            check_type(argname="argument io_share_count", value=io_share_count, expected_type=type_hints["io_share_count"])
            check_type(argname="argument io_share_level", value=io_share_level, expected_type=type_hints["io_share_level"])
            check_type(argname="argument keep_on_remove", value=keep_on_remove, expected_type=type_hints["keep_on_remove"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument size", value=size, expected_type=type_hints["size"])
            check_type(argname="argument storage_policy_id", value=storage_policy_id, expected_type=type_hints["storage_policy_id"])
            check_type(argname="argument thin_provisioned", value=thin_provisioned, expected_type=type_hints["thin_provisioned"])
            check_type(argname="argument unit_number", value=unit_number, expected_type=type_hints["unit_number"])
            check_type(argname="argument write_through", value=write_through, expected_type=type_hints["write_through"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "label": label,
        }
        if attach is not None:
            self._values["attach"] = attach
        if controller_type is not None:
            self._values["controller_type"] = controller_type
        if datastore_id is not None:
            self._values["datastore_id"] = datastore_id
        if disk_mode is not None:
            self._values["disk_mode"] = disk_mode
        if disk_sharing is not None:
            self._values["disk_sharing"] = disk_sharing
        if eagerly_scrub is not None:
            self._values["eagerly_scrub"] = eagerly_scrub
        if io_limit is not None:
            self._values["io_limit"] = io_limit
        if io_reservation is not None:
            self._values["io_reservation"] = io_reservation
        if io_share_count is not None:
            self._values["io_share_count"] = io_share_count
        if io_share_level is not None:
            self._values["io_share_level"] = io_share_level
        if keep_on_remove is not None:
            self._values["keep_on_remove"] = keep_on_remove
        if path is not None:
            self._values["path"] = path
        if size is not None:
            self._values["size"] = size
        if storage_policy_id is not None:
            self._values["storage_policy_id"] = storage_policy_id
        if thin_provisioned is not None:
            self._values["thin_provisioned"] = thin_provisioned
        if unit_number is not None:
            self._values["unit_number"] = unit_number
        if write_through is not None:
            self._values["write_through"] = write_through

    @builtins.property
    def label(self) -> builtins.str:
        '''A unique label for this disk.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#label VirtualMachine#label}
        '''
        result = self._values.get("label")
        assert result is not None, "Required property 'label' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def attach(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If this is true, the disk is attached instead of created. Implies keep_on_remove.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#attach VirtualMachine#attach}
        '''
        result = self._values.get("attach")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def controller_type(self) -> typing.Optional[builtins.str]:
        '''The type of controller the disk should be connected to. Must be 'scsi', 'sata', 'nvme', or 'ide'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#controller_type VirtualMachine#controller_type}
        '''
        result = self._values.get("controller_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def datastore_id(self) -> typing.Optional[builtins.str]:
        '''The datastore ID for this virtual disk, if different than the virtual machine.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#datastore_id VirtualMachine#datastore_id}
        '''
        result = self._values.get("datastore_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disk_mode(self) -> typing.Optional[builtins.str]:
        '''The mode of this this virtual disk for purposes of writes and snapshotting.

        Can be one of append, independent_nonpersistent, independent_persistent, nonpersistent, persistent, or undoable.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#disk_mode VirtualMachine#disk_mode}
        '''
        result = self._values.get("disk_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disk_sharing(self) -> typing.Optional[builtins.str]:
        '''The sharing mode of this virtual disk. Can be one of sharingMultiWriter or sharingNone.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#disk_sharing VirtualMachine#disk_sharing}
        '''
        result = self._values.get("disk_sharing")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def eagerly_scrub(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''The virtual disk file zeroing policy when thin_provision is not true.

        The default is false, which lazily-zeros the disk, speeding up thick-provisioned disk creation time.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#eagerly_scrub VirtualMachine#eagerly_scrub}
        '''
        result = self._values.get("eagerly_scrub")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def io_limit(self) -> typing.Optional[jsii.Number]:
        '''The upper limit of IOPS that this disk can use.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#io_limit VirtualMachine#io_limit}
        '''
        result = self._values.get("io_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def io_reservation(self) -> typing.Optional[jsii.Number]:
        '''The I/O guarantee that this disk has, in IOPS.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#io_reservation VirtualMachine#io_reservation}
        '''
        result = self._values.get("io_reservation")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def io_share_count(self) -> typing.Optional[jsii.Number]:
        '''The share count for this disk when the share level is custom.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#io_share_count VirtualMachine#io_share_count}
        '''
        result = self._values.get("io_share_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def io_share_level(self) -> typing.Optional[builtins.str]:
        '''The share allocation level for this disk. Can be one of low, normal, high, or custom.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#io_share_level VirtualMachine#io_share_level}
        '''
        result = self._values.get("io_share_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def keep_on_remove(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Set to true to keep the underlying VMDK file when removing this virtual disk from configuration.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#keep_on_remove VirtualMachine#keep_on_remove}
        '''
        result = self._values.get("keep_on_remove")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''The full path of the virtual disk.

        This can only be provided if attach is set to true, otherwise it is a read-only value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#path VirtualMachine#path}
        '''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def size(self) -> typing.Optional[jsii.Number]:
        '''The size of the disk, in GB.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#size VirtualMachine#size}
        '''
        result = self._values.get("size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def storage_policy_id(self) -> typing.Optional[builtins.str]:
        '''The ID of the storage policy to assign to the virtual disk in VM.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#storage_policy_id VirtualMachine#storage_policy_id}
        '''
        result = self._values.get("storage_policy_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def thin_provisioned(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If true, this disk is thin provisioned, with space for the file being allocated on an as-needed basis.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#thin_provisioned VirtualMachine#thin_provisioned}
        '''
        result = self._values.get("thin_provisioned")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def unit_number(self) -> typing.Optional[jsii.Number]:
        '''The unique device number for this disk.

        This number determines where on the SCSI bus this device will be attached.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#unit_number VirtualMachine#unit_number}
        '''
        result = self._values.get("unit_number")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def write_through(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If true, writes for this disk are sent directly to the filesystem immediately instead of being buffered.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#write_through VirtualMachine#write_through}
        '''
        result = self._values.get("write_through")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VirtualMachineDisk(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class VirtualMachineDiskList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.virtualMachine.VirtualMachineDiskList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1ec46522bd19d3b0cfc98d651ba791e966992fde21f48bcef4dd434136073188)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "VirtualMachineDiskOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__706490de336664979021a45f48535b98a42b940b6fa4cebaa6380dde13150028)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("VirtualMachineDiskOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f8847e7c4b0ad8b1f413dbd4cff963b91ecc732a7d92203adfef2bf6ebe47e08)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c8a87cc61b2da5757cc23f0c0db555c29ed253846a57b8d846a14990fea02a2c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__625831c40dd33c47afca70458ecbf103582d92e17b408102c189063eda696a14)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VirtualMachineDisk]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VirtualMachineDisk]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VirtualMachineDisk]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14c9c36a725b6cd4b504579ccb53340639358c9a5f6a332ca28dbc0e38618491)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class VirtualMachineDiskOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.virtualMachine.VirtualMachineDiskOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4fa4f00f4801c110a9048fcd1a60c22a2d0756f06c670fa8d9237d74f3ba0fdd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetAttach")
    def reset_attach(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAttach", []))

    @jsii.member(jsii_name="resetControllerType")
    def reset_controller_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetControllerType", []))

    @jsii.member(jsii_name="resetDatastoreId")
    def reset_datastore_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatastoreId", []))

    @jsii.member(jsii_name="resetDiskMode")
    def reset_disk_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDiskMode", []))

    @jsii.member(jsii_name="resetDiskSharing")
    def reset_disk_sharing(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDiskSharing", []))

    @jsii.member(jsii_name="resetEagerlyScrub")
    def reset_eagerly_scrub(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEagerlyScrub", []))

    @jsii.member(jsii_name="resetIoLimit")
    def reset_io_limit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIoLimit", []))

    @jsii.member(jsii_name="resetIoReservation")
    def reset_io_reservation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIoReservation", []))

    @jsii.member(jsii_name="resetIoShareCount")
    def reset_io_share_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIoShareCount", []))

    @jsii.member(jsii_name="resetIoShareLevel")
    def reset_io_share_level(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIoShareLevel", []))

    @jsii.member(jsii_name="resetKeepOnRemove")
    def reset_keep_on_remove(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeepOnRemove", []))

    @jsii.member(jsii_name="resetPath")
    def reset_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPath", []))

    @jsii.member(jsii_name="resetSize")
    def reset_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSize", []))

    @jsii.member(jsii_name="resetStoragePolicyId")
    def reset_storage_policy_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStoragePolicyId", []))

    @jsii.member(jsii_name="resetThinProvisioned")
    def reset_thin_provisioned(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThinProvisioned", []))

    @jsii.member(jsii_name="resetUnitNumber")
    def reset_unit_number(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUnitNumber", []))

    @jsii.member(jsii_name="resetWriteThrough")
    def reset_write_through(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWriteThrough", []))

    @builtins.property
    @jsii.member(jsii_name="deviceAddress")
    def device_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deviceAddress"))

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "key"))

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @builtins.property
    @jsii.member(jsii_name="attachInput")
    def attach_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "attachInput"))

    @builtins.property
    @jsii.member(jsii_name="controllerTypeInput")
    def controller_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "controllerTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="datastoreIdInput")
    def datastore_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "datastoreIdInput"))

    @builtins.property
    @jsii.member(jsii_name="diskModeInput")
    def disk_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "diskModeInput"))

    @builtins.property
    @jsii.member(jsii_name="diskSharingInput")
    def disk_sharing_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "diskSharingInput"))

    @builtins.property
    @jsii.member(jsii_name="eagerlyScrubInput")
    def eagerly_scrub_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "eagerlyScrubInput"))

    @builtins.property
    @jsii.member(jsii_name="ioLimitInput")
    def io_limit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ioLimitInput"))

    @builtins.property
    @jsii.member(jsii_name="ioReservationInput")
    def io_reservation_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ioReservationInput"))

    @builtins.property
    @jsii.member(jsii_name="ioShareCountInput")
    def io_share_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ioShareCountInput"))

    @builtins.property
    @jsii.member(jsii_name="ioShareLevelInput")
    def io_share_level_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ioShareLevelInput"))

    @builtins.property
    @jsii.member(jsii_name="keepOnRemoveInput")
    def keep_on_remove_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "keepOnRemoveInput"))

    @builtins.property
    @jsii.member(jsii_name="labelInput")
    def label_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "labelInput"))

    @builtins.property
    @jsii.member(jsii_name="pathInput")
    def path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pathInput"))

    @builtins.property
    @jsii.member(jsii_name="sizeInput")
    def size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "sizeInput"))

    @builtins.property
    @jsii.member(jsii_name="storagePolicyIdInput")
    def storage_policy_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "storagePolicyIdInput"))

    @builtins.property
    @jsii.member(jsii_name="thinProvisionedInput")
    def thin_provisioned_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "thinProvisionedInput"))

    @builtins.property
    @jsii.member(jsii_name="unitNumberInput")
    def unit_number_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "unitNumberInput"))

    @builtins.property
    @jsii.member(jsii_name="writeThroughInput")
    def write_through_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "writeThroughInput"))

    @builtins.property
    @jsii.member(jsii_name="attach")
    def attach(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "attach"))

    @attach.setter
    def attach(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c6e726a90c6fe0e61f81e4ce41334d9e9dcd1f889985d7b6bceb149ff51bd8b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "attach", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="controllerType")
    def controller_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "controllerType"))

    @controller_type.setter
    def controller_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a3519b33978c4dfe433ce0ceca8964c7a8b6e83002bad1fdf49ecf485d8d996)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "controllerType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="datastoreId")
    def datastore_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "datastoreId"))

    @datastore_id.setter
    def datastore_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__adb270334a184e5492364a527757f2834c10ad0c0a4421c7dcbb763656b3423e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "datastoreId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="diskMode")
    def disk_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "diskMode"))

    @disk_mode.setter
    def disk_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d9e4c9a71910f35ce0cf97b72c11f7e9d56844c2d9b01dbe2860f0d458cc47b3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "diskMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="diskSharing")
    def disk_sharing(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "diskSharing"))

    @disk_sharing.setter
    def disk_sharing(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__518baaf34051f451f6a2abaf0935a95e3546730bd0dd9dab28a229c2fe4b4a52)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "diskSharing", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="eagerlyScrub")
    def eagerly_scrub(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "eagerlyScrub"))

    @eagerly_scrub.setter
    def eagerly_scrub(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5dc95b6cdfb2b74722337018873948d994ebcf41383f1dabcf93267bdd856811)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "eagerlyScrub", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ioLimit")
    def io_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ioLimit"))

    @io_limit.setter
    def io_limit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d49b9fef8343009871699ad470fa7fe5ee0bcfa587a8323c64615f2f96b806e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ioLimit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ioReservation")
    def io_reservation(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ioReservation"))

    @io_reservation.setter
    def io_reservation(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__258e5ba0e74db181d9cf2b26d19db13d466563830cf31783db81fb2bff92caea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ioReservation", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ioShareCount")
    def io_share_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ioShareCount"))

    @io_share_count.setter
    def io_share_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac522eaea7a607fce9d3184932d9bdf29a40cd238c4f57d9db59eb7fe9f3dcea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ioShareCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ioShareLevel")
    def io_share_level(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ioShareLevel"))

    @io_share_level.setter
    def io_share_level(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d83e1ac723313882532fe92111923e472b3a45c864fc8a9732f70fd1fb280fd1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ioShareLevel", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keepOnRemove")
    def keep_on_remove(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "keepOnRemove"))

    @keep_on_remove.setter
    def keep_on_remove(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__705629d04d737f5db6f394fc6362bdd48aaae503ebcbb4081b69ede6c493a8b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keepOnRemove", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="label")
    def label(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "label"))

    @label.setter
    def label(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7c8c8c6d970677f5fabe6c3c10db1169dc2a898efb43fdc6735de4fc1a78782)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "label", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @path.setter
    def path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3e3ddfce3dd83c51ade760fcdb82e702760974e13e4a325d20538f0dc814c76)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "path", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="size")
    def size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "size"))

    @size.setter
    def size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6437edb1f67aa1b093289fa52d2c959df29cde1a818515cc796beb4e3c59aa7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "size", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="storagePolicyId")
    def storage_policy_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storagePolicyId"))

    @storage_policy_id.setter
    def storage_policy_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a4f08f7db03e282de77ac2569b915b45ae785b58e503f682ea8ad6398cd680b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "storagePolicyId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="thinProvisioned")
    def thin_provisioned(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "thinProvisioned"))

    @thin_provisioned.setter
    def thin_provisioned(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f11d5676f6d47fc98b65c3611b03c7bbd5fb85f11b49f1162b5c70e2eb8a1c94)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "thinProvisioned", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="unitNumber")
    def unit_number(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "unitNumber"))

    @unit_number.setter
    def unit_number(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c355225b910fade253dd47433e76dca8cfbb2fddae10a491743d52b92ffc1c05)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "unitNumber", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="writeThrough")
    def write_through(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "writeThrough"))

    @write_through.setter
    def write_through(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c70aa33526b4a281f861455ec862161cc08a3451bcb37970d1f569a6a2c6fabc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "writeThrough", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VirtualMachineDisk]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VirtualMachineDisk]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VirtualMachineDisk]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47afbcdbafa332ae97ca39fa7c984b32614f3fb114bab38350a6a0d945a00518)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.virtualMachine.VirtualMachineNetworkInterface",
    jsii_struct_bases=[],
    name_mapping={
        "network_id": "networkId",
        "adapter_type": "adapterType",
        "bandwidth_limit": "bandwidthLimit",
        "bandwidth_reservation": "bandwidthReservation",
        "bandwidth_share_count": "bandwidthShareCount",
        "bandwidth_share_level": "bandwidthShareLevel",
        "mac_address": "macAddress",
        "ovf_mapping": "ovfMapping",
        "physical_function": "physicalFunction",
        "use_static_mac": "useStaticMac",
    },
)
class VirtualMachineNetworkInterface:
    def __init__(
        self,
        *,
        network_id: builtins.str,
        adapter_type: typing.Optional[builtins.str] = None,
        bandwidth_limit: typing.Optional[jsii.Number] = None,
        bandwidth_reservation: typing.Optional[jsii.Number] = None,
        bandwidth_share_count: typing.Optional[jsii.Number] = None,
        bandwidth_share_level: typing.Optional[builtins.str] = None,
        mac_address: typing.Optional[builtins.str] = None,
        ovf_mapping: typing.Optional[builtins.str] = None,
        physical_function: typing.Optional[builtins.str] = None,
        use_static_mac: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param network_id: The ID of the network to connect this network interface to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#network_id VirtualMachine#network_id}
        :param adapter_type: The controller type. Can be one of e1000, e1000e, sriov, vmxnet3, or vrdma. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#adapter_type VirtualMachine#adapter_type}
        :param bandwidth_limit: The upper bandwidth limit of this network interface, in Mbits/sec. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#bandwidth_limit VirtualMachine#bandwidth_limit}
        :param bandwidth_reservation: The bandwidth reservation of this network interface, in Mbits/sec. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#bandwidth_reservation VirtualMachine#bandwidth_reservation}
        :param bandwidth_share_count: The share count for this network interface when the share level is custom. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#bandwidth_share_count VirtualMachine#bandwidth_share_count}
        :param bandwidth_share_level: The bandwidth share allocation level for this interface. Can be one of low, normal, high, or custom. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#bandwidth_share_level VirtualMachine#bandwidth_share_level}
        :param mac_address: The MAC address of this network interface. Can only be manually set if use_static_mac is true. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#mac_address VirtualMachine#mac_address}
        :param ovf_mapping: Mapping of network interface to OVF network. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#ovf_mapping VirtualMachine#ovf_mapping}
        :param physical_function: The ID of the Physical SR-IOV NIC to attach to, e.g. '0000:d8:00.0'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#physical_function VirtualMachine#physical_function}
        :param use_static_mac: If true, the mac_address field is treated as a static MAC address and set accordingly. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#use_static_mac VirtualMachine#use_static_mac}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__708827f70ceb09045c7032f0814f5fb082a31ce8dd932846e8f9b8e775214313)
            check_type(argname="argument network_id", value=network_id, expected_type=type_hints["network_id"])
            check_type(argname="argument adapter_type", value=adapter_type, expected_type=type_hints["adapter_type"])
            check_type(argname="argument bandwidth_limit", value=bandwidth_limit, expected_type=type_hints["bandwidth_limit"])
            check_type(argname="argument bandwidth_reservation", value=bandwidth_reservation, expected_type=type_hints["bandwidth_reservation"])
            check_type(argname="argument bandwidth_share_count", value=bandwidth_share_count, expected_type=type_hints["bandwidth_share_count"])
            check_type(argname="argument bandwidth_share_level", value=bandwidth_share_level, expected_type=type_hints["bandwidth_share_level"])
            check_type(argname="argument mac_address", value=mac_address, expected_type=type_hints["mac_address"])
            check_type(argname="argument ovf_mapping", value=ovf_mapping, expected_type=type_hints["ovf_mapping"])
            check_type(argname="argument physical_function", value=physical_function, expected_type=type_hints["physical_function"])
            check_type(argname="argument use_static_mac", value=use_static_mac, expected_type=type_hints["use_static_mac"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "network_id": network_id,
        }
        if adapter_type is not None:
            self._values["adapter_type"] = adapter_type
        if bandwidth_limit is not None:
            self._values["bandwidth_limit"] = bandwidth_limit
        if bandwidth_reservation is not None:
            self._values["bandwidth_reservation"] = bandwidth_reservation
        if bandwidth_share_count is not None:
            self._values["bandwidth_share_count"] = bandwidth_share_count
        if bandwidth_share_level is not None:
            self._values["bandwidth_share_level"] = bandwidth_share_level
        if mac_address is not None:
            self._values["mac_address"] = mac_address
        if ovf_mapping is not None:
            self._values["ovf_mapping"] = ovf_mapping
        if physical_function is not None:
            self._values["physical_function"] = physical_function
        if use_static_mac is not None:
            self._values["use_static_mac"] = use_static_mac

    @builtins.property
    def network_id(self) -> builtins.str:
        '''The ID of the network to connect this network interface to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#network_id VirtualMachine#network_id}
        '''
        result = self._values.get("network_id")
        assert result is not None, "Required property 'network_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def adapter_type(self) -> typing.Optional[builtins.str]:
        '''The controller type. Can be one of e1000, e1000e, sriov, vmxnet3, or vrdma.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#adapter_type VirtualMachine#adapter_type}
        '''
        result = self._values.get("adapter_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bandwidth_limit(self) -> typing.Optional[jsii.Number]:
        '''The upper bandwidth limit of this network interface, in Mbits/sec.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#bandwidth_limit VirtualMachine#bandwidth_limit}
        '''
        result = self._values.get("bandwidth_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def bandwidth_reservation(self) -> typing.Optional[jsii.Number]:
        '''The bandwidth reservation of this network interface, in Mbits/sec.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#bandwidth_reservation VirtualMachine#bandwidth_reservation}
        '''
        result = self._values.get("bandwidth_reservation")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def bandwidth_share_count(self) -> typing.Optional[jsii.Number]:
        '''The share count for this network interface when the share level is custom.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#bandwidth_share_count VirtualMachine#bandwidth_share_count}
        '''
        result = self._values.get("bandwidth_share_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def bandwidth_share_level(self) -> typing.Optional[builtins.str]:
        '''The bandwidth share allocation level for this interface. Can be one of low, normal, high, or custom.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#bandwidth_share_level VirtualMachine#bandwidth_share_level}
        '''
        result = self._values.get("bandwidth_share_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mac_address(self) -> typing.Optional[builtins.str]:
        '''The MAC address of this network interface. Can only be manually set if use_static_mac is true.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#mac_address VirtualMachine#mac_address}
        '''
        result = self._values.get("mac_address")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ovf_mapping(self) -> typing.Optional[builtins.str]:
        '''Mapping of network interface to OVF network.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#ovf_mapping VirtualMachine#ovf_mapping}
        '''
        result = self._values.get("ovf_mapping")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def physical_function(self) -> typing.Optional[builtins.str]:
        '''The ID of the Physical SR-IOV NIC to attach to, e.g. '0000:d8:00.0'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#physical_function VirtualMachine#physical_function}
        '''
        result = self._values.get("physical_function")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def use_static_mac(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If true, the mac_address field is treated as a static MAC address and set accordingly.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#use_static_mac VirtualMachine#use_static_mac}
        '''
        result = self._values.get("use_static_mac")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VirtualMachineNetworkInterface(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class VirtualMachineNetworkInterfaceList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.virtualMachine.VirtualMachineNetworkInterfaceList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__93bf52d0931e15652116851792a0d574a0385b6ef33ab4fc47073e9c500a0620)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "VirtualMachineNetworkInterfaceOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce8141ee7f283564cd87d9898e638026927c5c7134e21605247891b903143c37)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("VirtualMachineNetworkInterfaceOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c4a689cc64a38da205b656835a2978762504159c9e38255d259652fcd031a5e5)
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
            type_hints = typing.get_type_hints(_typecheckingstub__92b00bbe88e295e71d3dc86f15fee437e70af29fe5182d3f8c41ae660cef0092)
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
            type_hints = typing.get_type_hints(_typecheckingstub__576f3b21ff7534a7e0b7c2958fde2915392135ca8407368a6641c3b15e42ae96)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VirtualMachineNetworkInterface]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VirtualMachineNetworkInterface]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VirtualMachineNetworkInterface]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9d17504496e6b9a6ac511be1d82cace9a26bf508b3afc77cce33c8bc34d9499)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class VirtualMachineNetworkInterfaceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.virtualMachine.VirtualMachineNetworkInterfaceOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b2a7ea257c8585573e4a070f96ac8ea16794b9c33ff624c2e7d46047cd8fc7ae)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetAdapterType")
    def reset_adapter_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdapterType", []))

    @jsii.member(jsii_name="resetBandwidthLimit")
    def reset_bandwidth_limit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBandwidthLimit", []))

    @jsii.member(jsii_name="resetBandwidthReservation")
    def reset_bandwidth_reservation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBandwidthReservation", []))

    @jsii.member(jsii_name="resetBandwidthShareCount")
    def reset_bandwidth_share_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBandwidthShareCount", []))

    @jsii.member(jsii_name="resetBandwidthShareLevel")
    def reset_bandwidth_share_level(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBandwidthShareLevel", []))

    @jsii.member(jsii_name="resetMacAddress")
    def reset_mac_address(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMacAddress", []))

    @jsii.member(jsii_name="resetOvfMapping")
    def reset_ovf_mapping(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOvfMapping", []))

    @jsii.member(jsii_name="resetPhysicalFunction")
    def reset_physical_function(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPhysicalFunction", []))

    @jsii.member(jsii_name="resetUseStaticMac")
    def reset_use_static_mac(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUseStaticMac", []))

    @builtins.property
    @jsii.member(jsii_name="deviceAddress")
    def device_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deviceAddress"))

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "key"))

    @builtins.property
    @jsii.member(jsii_name="adapterTypeInput")
    def adapter_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "adapterTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="bandwidthLimitInput")
    def bandwidth_limit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "bandwidthLimitInput"))

    @builtins.property
    @jsii.member(jsii_name="bandwidthReservationInput")
    def bandwidth_reservation_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "bandwidthReservationInput"))

    @builtins.property
    @jsii.member(jsii_name="bandwidthShareCountInput")
    def bandwidth_share_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "bandwidthShareCountInput"))

    @builtins.property
    @jsii.member(jsii_name="bandwidthShareLevelInput")
    def bandwidth_share_level_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bandwidthShareLevelInput"))

    @builtins.property
    @jsii.member(jsii_name="macAddressInput")
    def mac_address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "macAddressInput"))

    @builtins.property
    @jsii.member(jsii_name="networkIdInput")
    def network_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "networkIdInput"))

    @builtins.property
    @jsii.member(jsii_name="ovfMappingInput")
    def ovf_mapping_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ovfMappingInput"))

    @builtins.property
    @jsii.member(jsii_name="physicalFunctionInput")
    def physical_function_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "physicalFunctionInput"))

    @builtins.property
    @jsii.member(jsii_name="useStaticMacInput")
    def use_static_mac_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "useStaticMacInput"))

    @builtins.property
    @jsii.member(jsii_name="adapterType")
    def adapter_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "adapterType"))

    @adapter_type.setter
    def adapter_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c6ee69c722fa78cddb12c1da1be9638edd7a79b45cc6a9238f696cdda5fa25fc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "adapterType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bandwidthLimit")
    def bandwidth_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "bandwidthLimit"))

    @bandwidth_limit.setter
    def bandwidth_limit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a08753e4010b4fd96bba2bf085d04b7a600db7f515c0d812d6d21117d0779fdf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bandwidthLimit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bandwidthReservation")
    def bandwidth_reservation(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "bandwidthReservation"))

    @bandwidth_reservation.setter
    def bandwidth_reservation(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da5c094e0866b11dd17636b4fd087eae687934a13e07949cc8acd3e0b446721f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bandwidthReservation", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bandwidthShareCount")
    def bandwidth_share_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "bandwidthShareCount"))

    @bandwidth_share_count.setter
    def bandwidth_share_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dbe1197a94ad3d62675000cfe0c2ff00e24f58b180caaecc50f7460967fd5743)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bandwidthShareCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bandwidthShareLevel")
    def bandwidth_share_level(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bandwidthShareLevel"))

    @bandwidth_share_level.setter
    def bandwidth_share_level(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__78e35bbf20bcd27d84f977f6bb7f313432322f12cc4290d024179782956e6287)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bandwidthShareLevel", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="macAddress")
    def mac_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "macAddress"))

    @mac_address.setter
    def mac_address(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c189bb0f05e182d9c30c70dff4c54b92f52da0694861df9e40d4e9d794059063)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "macAddress", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="networkId")
    def network_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "networkId"))

    @network_id.setter
    def network_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__53ba6813cdec3d066e9d2a8eb7984f7904a2bc4153b582ca2d6f38692cbd0cce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "networkId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ovfMapping")
    def ovf_mapping(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ovfMapping"))

    @ovf_mapping.setter
    def ovf_mapping(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__98a47fcdd0a5d55d7aa2f90feee152e474c3d6249db79936719a123987ed8004)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ovfMapping", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="physicalFunction")
    def physical_function(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "physicalFunction"))

    @physical_function.setter
    def physical_function(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7631102d58877e10ceec0691bb27391024ac1a38731eebe1b17ac651f5eb4a44)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "physicalFunction", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="useStaticMac")
    def use_static_mac(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "useStaticMac"))

    @use_static_mac.setter
    def use_static_mac(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee6157e8ea1176893e5bed8539baa801319421842ce1012ed9a0368f8e66f0a5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "useStaticMac", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VirtualMachineNetworkInterface]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VirtualMachineNetworkInterface]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VirtualMachineNetworkInterface]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8943d1b454a29f03379b36de6136a6e3d752b6300bc50327af4ba57c969e1099)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.virtualMachine.VirtualMachineOvfDeploy",
    jsii_struct_bases=[],
    name_mapping={
        "allow_unverified_ssl_cert": "allowUnverifiedSslCert",
        "deployment_option": "deploymentOption",
        "disk_provisioning": "diskProvisioning",
        "enable_hidden_properties": "enableHiddenProperties",
        "ip_allocation_policy": "ipAllocationPolicy",
        "ip_protocol": "ipProtocol",
        "local_ovf_path": "localOvfPath",
        "ovf_network_map": "ovfNetworkMap",
        "remote_ovf_url": "remoteOvfUrl",
    },
)
class VirtualMachineOvfDeploy:
    def __init__(
        self,
        *,
        allow_unverified_ssl_cert: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        deployment_option: typing.Optional[builtins.str] = None,
        disk_provisioning: typing.Optional[builtins.str] = None,
        enable_hidden_properties: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ip_allocation_policy: typing.Optional[builtins.str] = None,
        ip_protocol: typing.Optional[builtins.str] = None,
        local_ovf_path: typing.Optional[builtins.str] = None,
        ovf_network_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        remote_ovf_url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param allow_unverified_ssl_cert: Allow unverified ssl certificates while deploying ovf/ova from url. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#allow_unverified_ssl_cert VirtualMachine#allow_unverified_ssl_cert}
        :param deployment_option: The Deployment option to be chosen. If empty, the default option is used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#deployment_option VirtualMachine#deployment_option}
        :param disk_provisioning: An optional disk provisioning. If set, all the disks in the deployed ovf will have the same specified disk type (e.g., thin provisioned). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#disk_provisioning VirtualMachine#disk_provisioning}
        :param enable_hidden_properties: Allow properties with ovf:userConfigurable=false to be set. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#enable_hidden_properties VirtualMachine#enable_hidden_properties}
        :param ip_allocation_policy: The IP allocation policy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#ip_allocation_policy VirtualMachine#ip_allocation_policy}
        :param ip_protocol: The IP protocol. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#ip_protocol VirtualMachine#ip_protocol}
        :param local_ovf_path: The absolute path to the ovf/ova file in the local system. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#local_ovf_path VirtualMachine#local_ovf_path}
        :param ovf_network_map: The mapping of name of network identifiers from the ovf descriptor to network UUID in the VI infrastructure. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#ovf_network_map VirtualMachine#ovf_network_map}
        :param remote_ovf_url: URL to the remote ovf/ova file to be deployed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#remote_ovf_url VirtualMachine#remote_ovf_url}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__54248ad14ab80cbc48fcba75d1cf7cb7806eb218318c8969b2e4ba9fce1cd891)
            check_type(argname="argument allow_unverified_ssl_cert", value=allow_unverified_ssl_cert, expected_type=type_hints["allow_unverified_ssl_cert"])
            check_type(argname="argument deployment_option", value=deployment_option, expected_type=type_hints["deployment_option"])
            check_type(argname="argument disk_provisioning", value=disk_provisioning, expected_type=type_hints["disk_provisioning"])
            check_type(argname="argument enable_hidden_properties", value=enable_hidden_properties, expected_type=type_hints["enable_hidden_properties"])
            check_type(argname="argument ip_allocation_policy", value=ip_allocation_policy, expected_type=type_hints["ip_allocation_policy"])
            check_type(argname="argument ip_protocol", value=ip_protocol, expected_type=type_hints["ip_protocol"])
            check_type(argname="argument local_ovf_path", value=local_ovf_path, expected_type=type_hints["local_ovf_path"])
            check_type(argname="argument ovf_network_map", value=ovf_network_map, expected_type=type_hints["ovf_network_map"])
            check_type(argname="argument remote_ovf_url", value=remote_ovf_url, expected_type=type_hints["remote_ovf_url"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if allow_unverified_ssl_cert is not None:
            self._values["allow_unverified_ssl_cert"] = allow_unverified_ssl_cert
        if deployment_option is not None:
            self._values["deployment_option"] = deployment_option
        if disk_provisioning is not None:
            self._values["disk_provisioning"] = disk_provisioning
        if enable_hidden_properties is not None:
            self._values["enable_hidden_properties"] = enable_hidden_properties
        if ip_allocation_policy is not None:
            self._values["ip_allocation_policy"] = ip_allocation_policy
        if ip_protocol is not None:
            self._values["ip_protocol"] = ip_protocol
        if local_ovf_path is not None:
            self._values["local_ovf_path"] = local_ovf_path
        if ovf_network_map is not None:
            self._values["ovf_network_map"] = ovf_network_map
        if remote_ovf_url is not None:
            self._values["remote_ovf_url"] = remote_ovf_url

    @builtins.property
    def allow_unverified_ssl_cert(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Allow unverified ssl certificates while deploying ovf/ova from url.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#allow_unverified_ssl_cert VirtualMachine#allow_unverified_ssl_cert}
        '''
        result = self._values.get("allow_unverified_ssl_cert")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def deployment_option(self) -> typing.Optional[builtins.str]:
        '''The Deployment option to be chosen. If empty, the default option is used.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#deployment_option VirtualMachine#deployment_option}
        '''
        result = self._values.get("deployment_option")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disk_provisioning(self) -> typing.Optional[builtins.str]:
        '''An optional disk provisioning.

        If set, all the disks in the deployed ovf will have the same specified disk type (e.g., thin provisioned).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#disk_provisioning VirtualMachine#disk_provisioning}
        '''
        result = self._values.get("disk_provisioning")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_hidden_properties(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Allow properties with ovf:userConfigurable=false to be set.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#enable_hidden_properties VirtualMachine#enable_hidden_properties}
        '''
        result = self._values.get("enable_hidden_properties")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def ip_allocation_policy(self) -> typing.Optional[builtins.str]:
        '''The IP allocation policy.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#ip_allocation_policy VirtualMachine#ip_allocation_policy}
        '''
        result = self._values.get("ip_allocation_policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ip_protocol(self) -> typing.Optional[builtins.str]:
        '''The IP protocol.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#ip_protocol VirtualMachine#ip_protocol}
        '''
        result = self._values.get("ip_protocol")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def local_ovf_path(self) -> typing.Optional[builtins.str]:
        '''The absolute path to the ovf/ova file in the local system.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#local_ovf_path VirtualMachine#local_ovf_path}
        '''
        result = self._values.get("local_ovf_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ovf_network_map(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''The mapping of name of network identifiers from the ovf descriptor to network UUID in the VI infrastructure.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#ovf_network_map VirtualMachine#ovf_network_map}
        '''
        result = self._values.get("ovf_network_map")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def remote_ovf_url(self) -> typing.Optional[builtins.str]:
        '''URL to the remote ovf/ova file to be deployed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#remote_ovf_url VirtualMachine#remote_ovf_url}
        '''
        result = self._values.get("remote_ovf_url")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VirtualMachineOvfDeploy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class VirtualMachineOvfDeployOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.virtualMachine.VirtualMachineOvfDeployOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__100441516de3f7c50670de0876c984cdaf1bda7b8af9c15fed7b86d65245c91a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAllowUnverifiedSslCert")
    def reset_allow_unverified_ssl_cert(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowUnverifiedSslCert", []))

    @jsii.member(jsii_name="resetDeploymentOption")
    def reset_deployment_option(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeploymentOption", []))

    @jsii.member(jsii_name="resetDiskProvisioning")
    def reset_disk_provisioning(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDiskProvisioning", []))

    @jsii.member(jsii_name="resetEnableHiddenProperties")
    def reset_enable_hidden_properties(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableHiddenProperties", []))

    @jsii.member(jsii_name="resetIpAllocationPolicy")
    def reset_ip_allocation_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpAllocationPolicy", []))

    @jsii.member(jsii_name="resetIpProtocol")
    def reset_ip_protocol(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpProtocol", []))

    @jsii.member(jsii_name="resetLocalOvfPath")
    def reset_local_ovf_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLocalOvfPath", []))

    @jsii.member(jsii_name="resetOvfNetworkMap")
    def reset_ovf_network_map(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOvfNetworkMap", []))

    @jsii.member(jsii_name="resetRemoteOvfUrl")
    def reset_remote_ovf_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRemoteOvfUrl", []))

    @builtins.property
    @jsii.member(jsii_name="allowUnverifiedSslCertInput")
    def allow_unverified_ssl_cert_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "allowUnverifiedSslCertInput"))

    @builtins.property
    @jsii.member(jsii_name="deploymentOptionInput")
    def deployment_option_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deploymentOptionInput"))

    @builtins.property
    @jsii.member(jsii_name="diskProvisioningInput")
    def disk_provisioning_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "diskProvisioningInput"))

    @builtins.property
    @jsii.member(jsii_name="enableHiddenPropertiesInput")
    def enable_hidden_properties_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enableHiddenPropertiesInput"))

    @builtins.property
    @jsii.member(jsii_name="ipAllocationPolicyInput")
    def ip_allocation_policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ipAllocationPolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="ipProtocolInput")
    def ip_protocol_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ipProtocolInput"))

    @builtins.property
    @jsii.member(jsii_name="localOvfPathInput")
    def local_ovf_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "localOvfPathInput"))

    @builtins.property
    @jsii.member(jsii_name="ovfNetworkMapInput")
    def ovf_network_map_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "ovfNetworkMapInput"))

    @builtins.property
    @jsii.member(jsii_name="remoteOvfUrlInput")
    def remote_ovf_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "remoteOvfUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="allowUnverifiedSslCert")
    def allow_unverified_ssl_cert(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "allowUnverifiedSslCert"))

    @allow_unverified_ssl_cert.setter
    def allow_unverified_ssl_cert(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8995d8f47a71c7917ef04df93875df645d3de536271f95c8ff62dedc69e8c28)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowUnverifiedSslCert", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="deploymentOption")
    def deployment_option(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deploymentOption"))

    @deployment_option.setter
    def deployment_option(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20a6267ae9e70c4280dd2f5a18fbf939c8da0360fa296d4e201856525d5b520e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deploymentOption", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="diskProvisioning")
    def disk_provisioning(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "diskProvisioning"))

    @disk_provisioning.setter
    def disk_provisioning(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73e4bb0fba00e63fe62bff40293b0b5d5c65013375a9ce5865fd0b775cee0e46)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "diskProvisioning", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enableHiddenProperties")
    def enable_hidden_properties(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enableHiddenProperties"))

    @enable_hidden_properties.setter
    def enable_hidden_properties(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3069bf30a1de2f004551da3f6966e78a1b3f3ec9d3aea181092b5053fa918109)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableHiddenProperties", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipAllocationPolicy")
    def ip_allocation_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipAllocationPolicy"))

    @ip_allocation_policy.setter
    def ip_allocation_policy(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6474c06f6d9a259a7744516c9fc13416fe9ebf843a1c1ba81ea0ba2dd95d0620)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipAllocationPolicy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipProtocol")
    def ip_protocol(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipProtocol"))

    @ip_protocol.setter
    def ip_protocol(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1e60dadb1a107d61b67238dc16bda3ce88e61f09f6f03bd6d8c69ee788a42f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipProtocol", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="localOvfPath")
    def local_ovf_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "localOvfPath"))

    @local_ovf_path.setter
    def local_ovf_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d9f85e43210389468d6fe4f057b1992ba79dbd5b30ae79f37725b5f19577d3e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "localOvfPath", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ovfNetworkMap")
    def ovf_network_map(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "ovfNetworkMap"))

    @ovf_network_map.setter
    def ovf_network_map(
        self,
        value: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bcfd25c9ce5ba2e2200901e6bd9c91ad41385372409ab75cf7db38b45a0bd5ab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ovfNetworkMap", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="remoteOvfUrl")
    def remote_ovf_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "remoteOvfUrl"))

    @remote_ovf_url.setter
    def remote_ovf_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec9d7dc3a2853c3909d1d1c018351ecbfd8dd8f8a71d37ab13d344cdf65eccc8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "remoteOvfUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[VirtualMachineOvfDeploy]:
        return typing.cast(typing.Optional[VirtualMachineOvfDeploy], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[VirtualMachineOvfDeploy]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5380d49cffc84748d26f05ab906105129174c67bf6781931661d9b63f322c37d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.virtualMachine.VirtualMachineVapp",
    jsii_struct_bases=[],
    name_mapping={"properties": "properties"},
)
class VirtualMachineVapp:
    def __init__(
        self,
        *,
        properties: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param properties: A map of customizable vApp properties and their values. Allows customization of VMs cloned from OVF templates which have customizable vApp properties. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#properties VirtualMachine#properties}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1848d1e6fc961d09d84a5403124aba4fe26261f18ed44fb93de7d99140cf3e33)
            check_type(argname="argument properties", value=properties, expected_type=type_hints["properties"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if properties is not None:
            self._values["properties"] = properties

    @builtins.property
    def properties(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''A map of customizable vApp properties and their values.

        Allows customization of VMs cloned from OVF templates which have customizable vApp properties.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#properties VirtualMachine#properties}
        '''
        result = self._values.get("properties")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VirtualMachineVapp(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class VirtualMachineVappOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.virtualMachine.VirtualMachineVappOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9750bab4dfce6cae7229f4624789604a20a695b48aded8ed793729b10c7a30a6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetProperties")
    def reset_properties(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProperties", []))

    @builtins.property
    @jsii.member(jsii_name="propertiesInput")
    def properties_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "propertiesInput"))

    @builtins.property
    @jsii.member(jsii_name="properties")
    def properties(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "properties"))

    @properties.setter
    def properties(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7a8c41e8727bb04e0ee86b734bc3c0278cf3d2c9891373e1ffc6f05414b899a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "properties", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[VirtualMachineVapp]:
        return typing.cast(typing.Optional[VirtualMachineVapp], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[VirtualMachineVapp]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c2498717d26319e781f284818a16903f1024f003bab0561373c4c72f56e6b29b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.virtualMachine.VirtualMachineVtpm",
    jsii_struct_bases=[],
    name_mapping={"version": "version"},
)
class VirtualMachineVtpm:
    def __init__(self, *, version: typing.Optional[builtins.str] = None) -> None:
        '''
        :param version: The version of the TPM device. Default is 2.0. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#version VirtualMachine#version}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4df26224215993767c252ffb54c143f0774a48dac272f15ce0a11e6e11284228)
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if version is not None:
            self._values["version"] = version

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''The version of the TPM device. Default is 2.0.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/virtual_machine#version VirtualMachine#version}
        '''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VirtualMachineVtpm(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class VirtualMachineVtpmOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.virtualMachine.VirtualMachineVtpmOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__564e3411d628d5e34c12a539e998cdd4d815f78650efe2ab208c950974914cbb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetVersion")
    def reset_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVersion", []))

    @builtins.property
    @jsii.member(jsii_name="versionInput")
    def version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "versionInput"))

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @version.setter
    def version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc6f086a241a9447b75dc1eb139a600d10870e5f164623b48a4ca8b25f81c61e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "version", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[VirtualMachineVtpm]:
        return typing.cast(typing.Optional[VirtualMachineVtpm], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[VirtualMachineVtpm]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3df2435ccc8a5c5c2aca633c26f535db9b55b7b16bbe5e36927e0b6eb49a144f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "VirtualMachine",
    "VirtualMachineCdrom",
    "VirtualMachineCdromList",
    "VirtualMachineCdromOutputReference",
    "VirtualMachineClone",
    "VirtualMachineCloneCustomizationSpec",
    "VirtualMachineCloneCustomizationSpecOutputReference",
    "VirtualMachineCloneCustomize",
    "VirtualMachineCloneCustomizeLinuxOptions",
    "VirtualMachineCloneCustomizeLinuxOptionsOutputReference",
    "VirtualMachineCloneCustomizeNetworkInterface",
    "VirtualMachineCloneCustomizeNetworkInterfaceList",
    "VirtualMachineCloneCustomizeNetworkInterfaceOutputReference",
    "VirtualMachineCloneCustomizeOutputReference",
    "VirtualMachineCloneCustomizeWindowsOptions",
    "VirtualMachineCloneCustomizeWindowsOptionsOutputReference",
    "VirtualMachineCloneOutputReference",
    "VirtualMachineConfig",
    "VirtualMachineDisk",
    "VirtualMachineDiskList",
    "VirtualMachineDiskOutputReference",
    "VirtualMachineNetworkInterface",
    "VirtualMachineNetworkInterfaceList",
    "VirtualMachineNetworkInterfaceOutputReference",
    "VirtualMachineOvfDeploy",
    "VirtualMachineOvfDeployOutputReference",
    "VirtualMachineVapp",
    "VirtualMachineVappOutputReference",
    "VirtualMachineVtpm",
    "VirtualMachineVtpmOutputReference",
]

publication.publish()

def _typecheckingstub__9d1beefa1ea634ee7a9f7d3716ff2c4e22d4abd84d0eba1f0ba9e3f7df6382c0(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    resource_pool_id: builtins.str,
    alternate_guest_name: typing.Optional[builtins.str] = None,
    annotation: typing.Optional[builtins.str] = None,
    boot_delay: typing.Optional[jsii.Number] = None,
    boot_retry_delay: typing.Optional[jsii.Number] = None,
    boot_retry_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    cdrom: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VirtualMachineCdrom, typing.Dict[builtins.str, typing.Any]]]]] = None,
    clone: typing.Optional[typing.Union[VirtualMachineClone, typing.Dict[builtins.str, typing.Any]]] = None,
    cpu_hot_add_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    cpu_hot_remove_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    cpu_limit: typing.Optional[jsii.Number] = None,
    cpu_performance_counters_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    cpu_reservation: typing.Optional[jsii.Number] = None,
    cpu_share_count: typing.Optional[jsii.Number] = None,
    cpu_share_level: typing.Optional[builtins.str] = None,
    custom_attributes: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    datacenter_id: typing.Optional[builtins.str] = None,
    datastore_cluster_id: typing.Optional[builtins.str] = None,
    datastore_id: typing.Optional[builtins.str] = None,
    disk: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VirtualMachineDisk, typing.Dict[builtins.str, typing.Any]]]]] = None,
    efi_secure_boot_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enable_disk_uuid: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enable_logging: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ept_rvi_mode: typing.Optional[builtins.str] = None,
    extra_config: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    extra_config_reboot_required: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    firmware: typing.Optional[builtins.str] = None,
    folder: typing.Optional[builtins.str] = None,
    force_power_off: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    guest_id: typing.Optional[builtins.str] = None,
    hardware_version: typing.Optional[jsii.Number] = None,
    host_system_id: typing.Optional[builtins.str] = None,
    hv_mode: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    ide_controller_count: typing.Optional[jsii.Number] = None,
    ignored_guest_ips: typing.Optional[typing.Sequence[builtins.str]] = None,
    latency_sensitivity: typing.Optional[builtins.str] = None,
    memory: typing.Optional[jsii.Number] = None,
    memory_hot_add_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    memory_limit: typing.Optional[jsii.Number] = None,
    memory_reservation: typing.Optional[jsii.Number] = None,
    memory_reservation_locked_to_max: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    memory_share_count: typing.Optional[jsii.Number] = None,
    memory_share_level: typing.Optional[builtins.str] = None,
    migrate_wait_timeout: typing.Optional[jsii.Number] = None,
    nested_hv_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    network_interface: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VirtualMachineNetworkInterface, typing.Dict[builtins.str, typing.Any]]]]] = None,
    num_cores_per_socket: typing.Optional[jsii.Number] = None,
    num_cpus: typing.Optional[jsii.Number] = None,
    nvme_controller_count: typing.Optional[jsii.Number] = None,
    ovf_deploy: typing.Optional[typing.Union[VirtualMachineOvfDeploy, typing.Dict[builtins.str, typing.Any]]] = None,
    pci_device_id: typing.Optional[typing.Sequence[builtins.str]] = None,
    poweron_timeout: typing.Optional[jsii.Number] = None,
    replace_trigger: typing.Optional[builtins.str] = None,
    run_tools_scripts_after_power_on: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    run_tools_scripts_after_resume: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    run_tools_scripts_before_guest_reboot: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    run_tools_scripts_before_guest_shutdown: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    run_tools_scripts_before_guest_standby: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    sata_controller_count: typing.Optional[jsii.Number] = None,
    scsi_bus_sharing: typing.Optional[builtins.str] = None,
    scsi_controller_count: typing.Optional[jsii.Number] = None,
    scsi_type: typing.Optional[builtins.str] = None,
    shutdown_wait_timeout: typing.Optional[jsii.Number] = None,
    storage_policy_id: typing.Optional[builtins.str] = None,
    swap_placement_policy: typing.Optional[builtins.str] = None,
    sync_time_with_host: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    sync_time_with_host_periodically: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    tools_upgrade_policy: typing.Optional[builtins.str] = None,
    vapp: typing.Optional[typing.Union[VirtualMachineVapp, typing.Dict[builtins.str, typing.Any]]] = None,
    vbs_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    vtpm: typing.Optional[typing.Union[VirtualMachineVtpm, typing.Dict[builtins.str, typing.Any]]] = None,
    vvtd_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    wait_for_guest_ip_timeout: typing.Optional[jsii.Number] = None,
    wait_for_guest_net_routable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    wait_for_guest_net_timeout: typing.Optional[jsii.Number] = None,
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

def _typecheckingstub__a4d4d6c1bb222ae6efdd4bad6633ef9b17d5f522ae4bc2ba6ef57539eeb38002(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1fcf134354c29061d7e4fb0169e7e7a20912c1a5b880bbdb2a4bb5ea01aada40(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VirtualMachineCdrom, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58fa4cc37d9bb816590e73256a903ca0d1eac1a1c25ba6b1e3602ac1de5d11b1(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VirtualMachineDisk, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ddfc29ea46f37ba23bc6d587142d3c2870f4795bc2ea5998d42291c8cd0db10a(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VirtualMachineNetworkInterface, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ba5330706b1bf9965a56bf13579f5d837be248be307e77c6e722597a6e7b7f7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a425e252ab02e685c4d67700ee811861319ed71e70adbf7183def42d28f87c0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b7e4dc7554f41f8c7e1483c8ef6742cf3d145ebed1167f7c6304ee136be408f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bfc28b95f319370cc2c9b97e530fd9813c44a3678abfe74ab012b68d0a857403(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f070fffa27a92511e0ce48fe3894cbc0a5500f631b3e4a25596c1409b122807f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a55d59ce35d1defed15c6308994aa202a6c026768ed0a06322c1c94f114d5315(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58c3cc3a5dd3056677931e9b57925eff86b759f6dbe4926b7e7ec4b093b2d21f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2867b6768f65aa7fa89499268307d8a7e5283ab2ec89d629ac8474e2fab4c09(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5db22cc3248cb2d8ae0eaeb8f16c6bc33de67cc8a933528e52d1c523e138402(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13afb1bed41b4bba1425acfabec583bc9bbe65d5d87a4812d0f57babaa274074(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aec048d2721e51416f7f9ddbea45b8a0342af9ea5c4e52d630c43ad2ee5e5531(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9277e65b9386aab8fc2c4fbe351a5fe6cdc61c0b6caccf9925fb6b10803a681e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da78df638e192682f8fa2155fc457957ad2886f26938892439be719a107c9479(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6260a7ca67a70b82d7217c115d27e51edd256ff22c91992665d7e5253e20328b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61ef44ac89d0f83f459f4591cefa392f4d24526ff6d9f4647de6643f8565c1bf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8985bd72fba6490f3496fe95b96309036d2af442ddf4c3f7642752403f88ad3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e696cc23cd23d5332b48dbcd23a23c7e80a5933752803021177c7d033cff53b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d646503fc240fc209be7c84b9b8d248ef6d78e8f83d32d9e8a20dabc2498f57(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__129838cac8713bebbb80ee8a05bebb726d26c113aad1c048c77d1becee692c94(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e04d68724056ae077046c133d22f7fcb40b0f0678b58549f9b78f3fb972a5e17(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db7f92fb8b53e5ec7cc29a32efcf58684c45c39632f9f42ccdf8ff4e1ad99903(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__827eb4d007aa4580496441537568311b0d50a24f974c31676a9bfd4eca76f4a7(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0354f581946a03f855a296e0e04332e97efa24527f993d7b553d49a6aade821d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41327995595bcd41649699b070e20b7987840b64da32b876d8803cb5d354f972(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3620ada25c8f6fe96462ea3d4866056ea5cb356a6637a543315942ac9f49f20f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a269783ceb28e05a70d58fb9a334e07557ad35e824c6d0de9b9dda6f216fbc3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05ffc72f401b81bc54167cecde0d59efce6e5378a142f3fc443904d1318335f0(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e454e386bc47a0784d25fa88a5c2059301cf7a107918937e0a4c7cbc3d933bb9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15f0b302e4ffd0ae9a8572de2afb5049ac7e8dc804fedbb346b1afdc41e91296(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eac110862722a9f858da985925cc26cccf7c84fab53026b73dfc14fa676a5b6e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5c00bd1c76ba4593b9af25ed5b6f7552d1b3c126c386387428ca468fde5a7eb(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d25fec1f5441117d24961df885f3c030027acfaf06815bc2e329fe63b360ccf3(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a9db60fad9259067f72a0b794ceb75b246794d6bde61ba8117bc264eaa2c5a7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f5daa3eb21983bb678d72dd777cf238cffc5d108d4194100f8a5a233e06d077(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e71691b3c7a290af103e2228d8048a23cb3d443369a30867ceda6f8fea6ffe22(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__720d90a5bb4db23b62315c9b6e6395aa8f341cd7c97e2487bb22bf09fc5a799d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07adffd6f2750f3daa8c3d011c00c65bf52472d7c2accd5a3473a573735055e0(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e69ca2b2fdfb904ad4bbf82bdfa98450307b052de6835b8e92ebeb8915e7494b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2803b3e6d763cb91ad7db58806318cb4f5c219b3ca2905572da8a5c23377601f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8a8daccba8c1143b215685c560c890936e8aeefc730a4874a5a4e7ff9ddec57(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1aed230e1a0ba99924292a0f6f56f89b03417d9f80c2cfe7d3f8298bbb0e424b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6ca57f2dfe7833c6b11e6beb69cbdd32ecc390a2780eed2fcb7693e35ef7b2f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e722deb0ded51bc305f34a4a6d762971a1c1d18ae93ff6fd8922bbe0fe72b43(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f60f8cd4e3b1fad5f0b427d7c8941d92fdb47d20f5923dfb24805bb6a808c88(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__793d0cff2c3d7cb8c7e08e825d7d9bd91064987c5a43abc1f6cdb82a022bbed5(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0da05056b45fb7f8dd0088c9ebb962cc9a0f1bdab9131405afb9a3ff0c0e81b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e6ed5237d069a9f34f8d01143f3048925ce3cbcb43810e80e7ea128d46951ad(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50a52787fb5a9ed86cf7df6e46b142b67287b023519785ac33f5cd15ff3d3b71(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__345a4f39fe904c3351766e38b06027bdb8ebbc4338d5e6a13d5f622c57878ae7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae7da94511492519e1e921c8e49f66e8a88a3439f2e3be2eff5635f38da8d494(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f37a48968cd3df7669956ad3b7697b790c0cba9776cc3ddab6650490da3039c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef023fc8dbb7c4b49d2e0ed4ba489a690f05ea5e203499da4e8b2a7d62784987(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69897ede9bc9831bedc9f4648be0447dc28eb70a4577beb7a723797b9e25bd4a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67e89a91b69dc10e7014912688cfb5102aad4449079d53897bf4cd15e0f6f2da(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a109095a3083c8cdf5fd6d36447e8d521f8d65e8d003e325ccd5c022df4170c8(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bbfbb2f31a1572191b3c0e07825c7f4563e2d53ee4efff1347f3c6bb45401d73(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72287081637ebd7d4c1c80b9d458f71c3b053cc61d6a2c5fbec5ca36a578e041(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16dbe14cde4ddbce43d93e76a7df105e22bb3a0cd0c30e0afc6c0147b8c11d7a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d00bf341c47c273df5376b299f9f67dc4c6ff2c0a36b4d5140ccc110652b086(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a4fd4c63ea830a7d8bd6ec3089f77bd77c87d2fb1d3d6076edd62e7fbecbb1d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__636617ed770a4a086968d6bd0c1bd2b6a4255e9c0cded5dcc0f2b023e6c4e7cc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de1d3b83cae9c88a95d4e4e7a489b1ada03c2671d3d045cfd749a621c648fa0a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5bf36f926d0426eef8510ad8be2cdc528b57e9b839d893f3c1ceb6473c2eaf4c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__705b9a2255149661521697571135163ab95dfd7ba275dd2e44a4f0973cbe398e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6d1f5eb89924e796e8640f75235a5f134b3be3066d9d2b99090a342cd402e80(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5fb55dd2605b80afbdd6f1dfeea1cfc37a75538bf1a3952d722e510fe3555a5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b7fece8c5dc5d778a776849995e38e7f30fc4e918d915c6a5dea0d27390994fa(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eabfe61f73841c75a9c95cf6b54df2307b4259e76893d0b18df08811fac2557f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d659b4207b24633382fd564a946924d6aa7052dd96ecf3371a18f0754aed6856(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__073ecab6b23708c92a289d888312aa17c27926ed0ae68c43b9e637727e9862f1(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a8413ab56184260d6d1d431ddf08a98493b146e1571ce108ca49c6c2ca22be6(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db6c206832ac558dd3570c60f20393b92900d2195b60691c29dedb8c08333591(
    *,
    client_device: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    datastore_id: typing.Optional[builtins.str] = None,
    path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da099c8719c5562b667440a30667628f072388bbdbe288e9c21a2226c22994cb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7a95734842c9148a4d1c948d643c535aab0cf67d607d74a5050823f9022af67(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55a393dddf3b40a315f0d7d3d32327e0031a36eb42fe2002a701d2d7c4c4f6ae(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__937d6be279adb9a1e5c1ec7d82bd108319a6f43b06404263a41657d8c8f254c2(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4f83413ef2cdc08322e49d33dc1014edd837a1138feb647c9b6d080d628edaa(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ab986fb66af572482aaec81fb552041770b9afb55d4c5e7299f56f8acd2a9e5(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VirtualMachineCdrom]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b341cf6c0e3df967c4469230fdc8fb5f7dd3b34c6e70f580f9acff90fc811dd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4fa64659643c9868ee0c5a85471e433bf07d8359455c3c8790e10219dfd953cd(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4118cba22f708b5344cd83e26ea1725166fbbde7fdd67e2c0f545412b5b1414(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ebd5ac9bc5fd966654f211e7c5ff35fd712c7a82398a1a477a5bdcfa63e28a5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__077ab4575066b341ad5cfc8e3cc596196c332d69e22489be6d7585ab67ef482f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VirtualMachineCdrom]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__293830fb9774d771f538120dcfa765be0b267765980eefe0dc73767ba0f8d9fc(
    *,
    template_uuid: builtins.str,
    customization_spec: typing.Optional[typing.Union[VirtualMachineCloneCustomizationSpec, typing.Dict[builtins.str, typing.Any]]] = None,
    customize: typing.Optional[typing.Union[VirtualMachineCloneCustomize, typing.Dict[builtins.str, typing.Any]]] = None,
    linked_clone: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ovf_network_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ovf_storage_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    timeout: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2114155cbd07283ebabb6160517744d3ca02bed7acce1ed8ff750110801694ba(
    *,
    id: builtins.str,
    timeout: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__677eddd7ffe1818393fb18badf2b0ae2fbb24bf8f212b0fc3c0a4731ed9e30a3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c2dbf13abb60268fe659973b3911e12bdb5feda266b41b01ea1700822e49193(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52b928a80f02abf621cf57c8aef5dbbb00a07f1123254dddc387057a530e026c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51ad427d15ce2ef0ecb05aac568c4d4a2685d44ba1940ddc59b82f359a7c0bc2(
    value: typing.Optional[VirtualMachineCloneCustomizationSpec],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d12c07cc841613da4f6fc2384f11a6e19de4bf27d3032cca2ed100c0b43f2b0(
    *,
    dns_server_list: typing.Optional[typing.Sequence[builtins.str]] = None,
    dns_suffix_list: typing.Optional[typing.Sequence[builtins.str]] = None,
    ipv4_gateway: typing.Optional[builtins.str] = None,
    ipv6_gateway: typing.Optional[builtins.str] = None,
    linux_options: typing.Optional[typing.Union[VirtualMachineCloneCustomizeLinuxOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    network_interface: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VirtualMachineCloneCustomizeNetworkInterface, typing.Dict[builtins.str, typing.Any]]]]] = None,
    timeout: typing.Optional[jsii.Number] = None,
    windows_options: typing.Optional[typing.Union[VirtualMachineCloneCustomizeWindowsOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    windows_sysprep_text: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1556122300d0463e6170c85145f524655221d1753b1ae06b0627cbf408520a50(
    *,
    domain: builtins.str,
    host_name: builtins.str,
    hw_clock_utc: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    script_text: typing.Optional[builtins.str] = None,
    time_zone: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__713fae389811e3c67e0da9820c9b9770bdc5dbaebb0c7d60d0e6b6c0b701590f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9716db47d936e76a2b4d8404355302d934a211dc26863474d15e2ec3908b8c0e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e6826c595a2a9e79747c5835281983f0d711faceb6d9cf712b45546d6958279(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b57dc9030109236260fc5fd3e9286cd9c6beecac80f9650014dacbe56439f78(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b252087ebe1e4eb7ff7c5bfe895738e28114418e31e2d8312eedefc10aa26e39(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__152ee819ddc4dd0546a70b2d88276025ba95051946d828b826532a62dac76694(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb02b73e19dd8dcb1991020d74c4dfa534e9b321d1b97b1eca5dfda9459f1621(
    value: typing.Optional[VirtualMachineCloneCustomizeLinuxOptions],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ff7104e6aeab39b8d3ec40b75330535bcacf136da04e3f12606a06d7720a6a5(
    *,
    dns_domain: typing.Optional[builtins.str] = None,
    dns_server_list: typing.Optional[typing.Sequence[builtins.str]] = None,
    ipv4_address: typing.Optional[builtins.str] = None,
    ipv4_netmask: typing.Optional[jsii.Number] = None,
    ipv6_address: typing.Optional[builtins.str] = None,
    ipv6_netmask: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__419d83219c0769a77112c0b0ef92b6f12c0331ac1c27fc52e4b86f41c0abfb92(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76629be8cc0545366e2b2cdad872712ef364c3e08ecedb02d2f99b4f4b9cc834(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a6ffbdd40086d07161f03187e615cb80180d22ca2ec4d15d0c628db38af290f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ede43286cf92c85dc9c3fc3f1ba711b8babe88d353e0d94098867de7e1dbb25c(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78faef14ff34646788b0c3def8fb13cf8381a3e85a15ae5dc688cae79ed764f0(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6e04c95b3fe8254998fc705a41fb352b12724c7962eea88d8c5446f86cf88fd(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VirtualMachineCloneCustomizeNetworkInterface]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce0f8e6f5bb0b03ebdc6b4300c42152ab2caf4c641037e92607cf067d258ec33(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53a6bffb68236b4fa14db6fb83a82e5c70e572949abc1dcb31acfba7c32e517c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__784602f584e8c41e594c33912147ed5af72a7e268961532ed4b7cd0b56c0c8ac(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d163140ef2f902d3d38224442e867475d9e50346a8ebc6abd3ddfda50df61103(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__654f5b18184b000490aa6a9206e9c1d9b0580bbeb8f70ea411ad372388dca9b6(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f7ece60636029850fd0026bffd0f03b3010b17583e006f687b3b9c43ce22551(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b063422561b09ae5b600f7610307d847ab111d9158ce56a0c8a7808d5c667f0(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9cf99001d5d036203796d4abd754e34eadf7746f4dfa18358ad7cbf4bd886ba2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VirtualMachineCloneCustomizeNetworkInterface]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__550b4de40fdf14c7952747bdadb84bb8918bbe7a50bf68fba8670724cecc1dae(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a97aebd933299c6d522c492d366a140928e3ba24cfaed809da6f8dad02fffee2(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VirtualMachineCloneCustomizeNetworkInterface, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f2d8f459c62a0206e87c311971a51e1b92ebc6fd8d833acadb1632619a38401(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db58206829516f1a7cb009bc9db17265ad956509bb1b13434e3b9f507ab2667c(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47a59106bc86d61b198c10021f02e025d5724993c79186eda6b9a16c483c51d5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b70d2895b12fe284f1e524387dd86d3c69f6c1e6c74ed0125100d270dd04967(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3247656088c58a5e08f290d700e1f9782a8e34413b4e1b42a668fdcd817cb03(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a1440619beeabd405172dad469fc9fa69760e50b26dab6a0aa351b3d9628624(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3aa25279ab32ed95b31423fdeb8b7556fa89893489451fa2d5d1f9ad78c07b5a(
    value: typing.Optional[VirtualMachineCloneCustomize],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0116db1b8b0ee4c2f9b0cc48bf9326f3b94a46fcbe940de46f0b06efb5248ed(
    *,
    computer_name: builtins.str,
    admin_password: typing.Optional[builtins.str] = None,
    auto_logon: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    auto_logon_count: typing.Optional[jsii.Number] = None,
    domain_admin_password: typing.Optional[builtins.str] = None,
    domain_admin_user: typing.Optional[builtins.str] = None,
    domain_ou: typing.Optional[builtins.str] = None,
    full_name: typing.Optional[builtins.str] = None,
    join_domain: typing.Optional[builtins.str] = None,
    organization_name: typing.Optional[builtins.str] = None,
    product_key: typing.Optional[builtins.str] = None,
    run_once_command_list: typing.Optional[typing.Sequence[builtins.str]] = None,
    time_zone: typing.Optional[jsii.Number] = None,
    workgroup: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0403c4cea7f349747a50360f4b07352e3fbf217f7ccfba7209a39c2528a3e1c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80dab348356470c231eddfacd268a463a821a12339ebb341ee8685e9047dbe21(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47f7463ebaa207ff911bd9e0a3d02972a153558c1502633bd91230b99f9b39d2(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__820d2a592b375270ef1d11d8b0f359a912e9d4a153d8e9bb9f3f2e5054024a81(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07686288e01e19393a29e9bcb71b5b8771e7493483caae78a2e6507a97fdc3b7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6f5a20f194da7993f787bde2a9a31b03837bde2bcbac51b52b536fdaccd68d5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4305a675f73e2444be3da59d88da0a47c045785c268386019951b27d338b6db7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebce476ec2b4b3eb00e2261a1262e3cff012e08e29aad1c150d1d6e627efecef(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__406f436a55ac6ed534f0eee3741772a0f8346ea84b7958f68a3b52254ce442e9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e903fa90cec789bec27ae55dad3e1c7040d517eca9c5d6dd932bd0bbab3c989(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9034fa1b2b110e029f53ce151a7c9891ecbb87dab1c32a04a5a2ecb12612bc44(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e01747404ea0013dfaf0b6091286ad98ed7742ff3549819ef254771bfc1fbad(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3b15f1b0384933ffa48d88c8009f7526059d1d0c8bb92fc1dc8a80fb7184830(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebf0c99b035559c01e66ad560ffecfef4faf04cb9044e09a60eb023668d81f78(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf0e26cafbcdf978a76eb4933d3cb156c144162a2fe2c1124ab50ee179f51348(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d4ae348e08133789c5279adc2ab586c3bc53390e76b7ee9c608cd95af2954cf(
    value: typing.Optional[VirtualMachineCloneCustomizeWindowsOptions],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22a23434afdd0bfa57c789686afac7c1e04394f88236c9c2c3602bbd38ae2aca(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c485edd657ef5fe7b5e3ce4eeb8e1343b72bc3605ffbaf3460f3ecde54ff6cd(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__edc06ce38e17e728527c1c3d71e1249e42412e1743d51e14d3bd8707186174d7(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5bec349910d07d3fde80822069fc2aeee6947a24d21197c0b173fa843fcc3f9(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8f7448e1f97d3870b1bb201c7a661eeea22f6d2c5ec301e08f8c8cfb431f21f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__228673e59a6569fc60cf65a2b5c7b31f5f52ee9eb06c5034e0e0711f202b498c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0774638501660981959ca52aaeacc6b1297d43c5e42de7b0bb64d36430107808(
    value: typing.Optional[VirtualMachineClone],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8cb994aacc5d8d8695d7507f4c95addbd577e3dfee85f804d3a5554ec9b5f9b1(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    resource_pool_id: builtins.str,
    alternate_guest_name: typing.Optional[builtins.str] = None,
    annotation: typing.Optional[builtins.str] = None,
    boot_delay: typing.Optional[jsii.Number] = None,
    boot_retry_delay: typing.Optional[jsii.Number] = None,
    boot_retry_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    cdrom: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VirtualMachineCdrom, typing.Dict[builtins.str, typing.Any]]]]] = None,
    clone: typing.Optional[typing.Union[VirtualMachineClone, typing.Dict[builtins.str, typing.Any]]] = None,
    cpu_hot_add_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    cpu_hot_remove_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    cpu_limit: typing.Optional[jsii.Number] = None,
    cpu_performance_counters_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    cpu_reservation: typing.Optional[jsii.Number] = None,
    cpu_share_count: typing.Optional[jsii.Number] = None,
    cpu_share_level: typing.Optional[builtins.str] = None,
    custom_attributes: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    datacenter_id: typing.Optional[builtins.str] = None,
    datastore_cluster_id: typing.Optional[builtins.str] = None,
    datastore_id: typing.Optional[builtins.str] = None,
    disk: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VirtualMachineDisk, typing.Dict[builtins.str, typing.Any]]]]] = None,
    efi_secure_boot_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enable_disk_uuid: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enable_logging: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ept_rvi_mode: typing.Optional[builtins.str] = None,
    extra_config: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    extra_config_reboot_required: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    firmware: typing.Optional[builtins.str] = None,
    folder: typing.Optional[builtins.str] = None,
    force_power_off: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    guest_id: typing.Optional[builtins.str] = None,
    hardware_version: typing.Optional[jsii.Number] = None,
    host_system_id: typing.Optional[builtins.str] = None,
    hv_mode: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    ide_controller_count: typing.Optional[jsii.Number] = None,
    ignored_guest_ips: typing.Optional[typing.Sequence[builtins.str]] = None,
    latency_sensitivity: typing.Optional[builtins.str] = None,
    memory: typing.Optional[jsii.Number] = None,
    memory_hot_add_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    memory_limit: typing.Optional[jsii.Number] = None,
    memory_reservation: typing.Optional[jsii.Number] = None,
    memory_reservation_locked_to_max: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    memory_share_count: typing.Optional[jsii.Number] = None,
    memory_share_level: typing.Optional[builtins.str] = None,
    migrate_wait_timeout: typing.Optional[jsii.Number] = None,
    nested_hv_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    network_interface: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VirtualMachineNetworkInterface, typing.Dict[builtins.str, typing.Any]]]]] = None,
    num_cores_per_socket: typing.Optional[jsii.Number] = None,
    num_cpus: typing.Optional[jsii.Number] = None,
    nvme_controller_count: typing.Optional[jsii.Number] = None,
    ovf_deploy: typing.Optional[typing.Union[VirtualMachineOvfDeploy, typing.Dict[builtins.str, typing.Any]]] = None,
    pci_device_id: typing.Optional[typing.Sequence[builtins.str]] = None,
    poweron_timeout: typing.Optional[jsii.Number] = None,
    replace_trigger: typing.Optional[builtins.str] = None,
    run_tools_scripts_after_power_on: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    run_tools_scripts_after_resume: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    run_tools_scripts_before_guest_reboot: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    run_tools_scripts_before_guest_shutdown: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    run_tools_scripts_before_guest_standby: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    sata_controller_count: typing.Optional[jsii.Number] = None,
    scsi_bus_sharing: typing.Optional[builtins.str] = None,
    scsi_controller_count: typing.Optional[jsii.Number] = None,
    scsi_type: typing.Optional[builtins.str] = None,
    shutdown_wait_timeout: typing.Optional[jsii.Number] = None,
    storage_policy_id: typing.Optional[builtins.str] = None,
    swap_placement_policy: typing.Optional[builtins.str] = None,
    sync_time_with_host: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    sync_time_with_host_periodically: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    tools_upgrade_policy: typing.Optional[builtins.str] = None,
    vapp: typing.Optional[typing.Union[VirtualMachineVapp, typing.Dict[builtins.str, typing.Any]]] = None,
    vbs_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    vtpm: typing.Optional[typing.Union[VirtualMachineVtpm, typing.Dict[builtins.str, typing.Any]]] = None,
    vvtd_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    wait_for_guest_ip_timeout: typing.Optional[jsii.Number] = None,
    wait_for_guest_net_routable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    wait_for_guest_net_timeout: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aab91385a396cb5112f20f1e520ccf43242269bf1d54b0652fb3445b6aac8f5a(
    *,
    label: builtins.str,
    attach: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    controller_type: typing.Optional[builtins.str] = None,
    datastore_id: typing.Optional[builtins.str] = None,
    disk_mode: typing.Optional[builtins.str] = None,
    disk_sharing: typing.Optional[builtins.str] = None,
    eagerly_scrub: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    io_limit: typing.Optional[jsii.Number] = None,
    io_reservation: typing.Optional[jsii.Number] = None,
    io_share_count: typing.Optional[jsii.Number] = None,
    io_share_level: typing.Optional[builtins.str] = None,
    keep_on_remove: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    path: typing.Optional[builtins.str] = None,
    size: typing.Optional[jsii.Number] = None,
    storage_policy_id: typing.Optional[builtins.str] = None,
    thin_provisioned: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    unit_number: typing.Optional[jsii.Number] = None,
    write_through: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ec46522bd19d3b0cfc98d651ba791e966992fde21f48bcef4dd434136073188(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__706490de336664979021a45f48535b98a42b940b6fa4cebaa6380dde13150028(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8847e7c4b0ad8b1f413dbd4cff963b91ecc732a7d92203adfef2bf6ebe47e08(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8a87cc61b2da5757cc23f0c0db555c29ed253846a57b8d846a14990fea02a2c(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__625831c40dd33c47afca70458ecbf103582d92e17b408102c189063eda696a14(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14c9c36a725b6cd4b504579ccb53340639358c9a5f6a332ca28dbc0e38618491(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VirtualMachineDisk]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4fa4f00f4801c110a9048fcd1a60c22a2d0756f06c670fa8d9237d74f3ba0fdd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c6e726a90c6fe0e61f81e4ce41334d9e9dcd1f889985d7b6bceb149ff51bd8b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a3519b33978c4dfe433ce0ceca8964c7a8b6e83002bad1fdf49ecf485d8d996(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__adb270334a184e5492364a527757f2834c10ad0c0a4421c7dcbb763656b3423e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9e4c9a71910f35ce0cf97b72c11f7e9d56844c2d9b01dbe2860f0d458cc47b3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__518baaf34051f451f6a2abaf0935a95e3546730bd0dd9dab28a229c2fe4b4a52(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5dc95b6cdfb2b74722337018873948d994ebcf41383f1dabcf93267bdd856811(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d49b9fef8343009871699ad470fa7fe5ee0bcfa587a8323c64615f2f96b806e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__258e5ba0e74db181d9cf2b26d19db13d466563830cf31783db81fb2bff92caea(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac522eaea7a607fce9d3184932d9bdf29a40cd238c4f57d9db59eb7fe9f3dcea(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d83e1ac723313882532fe92111923e472b3a45c864fc8a9732f70fd1fb280fd1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__705629d04d737f5db6f394fc6362bdd48aaae503ebcbb4081b69ede6c493a8b2(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7c8c8c6d970677f5fabe6c3c10db1169dc2a898efb43fdc6735de4fc1a78782(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3e3ddfce3dd83c51ade760fcdb82e702760974e13e4a325d20538f0dc814c76(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6437edb1f67aa1b093289fa52d2c959df29cde1a818515cc796beb4e3c59aa7(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a4f08f7db03e282de77ac2569b915b45ae785b58e503f682ea8ad6398cd680b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f11d5676f6d47fc98b65c3611b03c7bbd5fb85f11b49f1162b5c70e2eb8a1c94(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c355225b910fade253dd47433e76dca8cfbb2fddae10a491743d52b92ffc1c05(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c70aa33526b4a281f861455ec862161cc08a3451bcb37970d1f569a6a2c6fabc(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47afbcdbafa332ae97ca39fa7c984b32614f3fb114bab38350a6a0d945a00518(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VirtualMachineDisk]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__708827f70ceb09045c7032f0814f5fb082a31ce8dd932846e8f9b8e775214313(
    *,
    network_id: builtins.str,
    adapter_type: typing.Optional[builtins.str] = None,
    bandwidth_limit: typing.Optional[jsii.Number] = None,
    bandwidth_reservation: typing.Optional[jsii.Number] = None,
    bandwidth_share_count: typing.Optional[jsii.Number] = None,
    bandwidth_share_level: typing.Optional[builtins.str] = None,
    mac_address: typing.Optional[builtins.str] = None,
    ovf_mapping: typing.Optional[builtins.str] = None,
    physical_function: typing.Optional[builtins.str] = None,
    use_static_mac: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93bf52d0931e15652116851792a0d574a0385b6ef33ab4fc47073e9c500a0620(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce8141ee7f283564cd87d9898e638026927c5c7134e21605247891b903143c37(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4a689cc64a38da205b656835a2978762504159c9e38255d259652fcd031a5e5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92b00bbe88e295e71d3dc86f15fee437e70af29fe5182d3f8c41ae660cef0092(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__576f3b21ff7534a7e0b7c2958fde2915392135ca8407368a6641c3b15e42ae96(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9d17504496e6b9a6ac511be1d82cace9a26bf508b3afc77cce33c8bc34d9499(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VirtualMachineNetworkInterface]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2a7ea257c8585573e4a070f96ac8ea16794b9c33ff624c2e7d46047cd8fc7ae(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6ee69c722fa78cddb12c1da1be9638edd7a79b45cc6a9238f696cdda5fa25fc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a08753e4010b4fd96bba2bf085d04b7a600db7f515c0d812d6d21117d0779fdf(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da5c094e0866b11dd17636b4fd087eae687934a13e07949cc8acd3e0b446721f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dbe1197a94ad3d62675000cfe0c2ff00e24f58b180caaecc50f7460967fd5743(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78e35bbf20bcd27d84f977f6bb7f313432322f12cc4290d024179782956e6287(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c189bb0f05e182d9c30c70dff4c54b92f52da0694861df9e40d4e9d794059063(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53ba6813cdec3d066e9d2a8eb7984f7904a2bc4153b582ca2d6f38692cbd0cce(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98a47fcdd0a5d55d7aa2f90feee152e474c3d6249db79936719a123987ed8004(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7631102d58877e10ceec0691bb27391024ac1a38731eebe1b17ac651f5eb4a44(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee6157e8ea1176893e5bed8539baa801319421842ce1012ed9a0368f8e66f0a5(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8943d1b454a29f03379b36de6136a6e3d752b6300bc50327af4ba57c969e1099(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VirtualMachineNetworkInterface]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54248ad14ab80cbc48fcba75d1cf7cb7806eb218318c8969b2e4ba9fce1cd891(
    *,
    allow_unverified_ssl_cert: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    deployment_option: typing.Optional[builtins.str] = None,
    disk_provisioning: typing.Optional[builtins.str] = None,
    enable_hidden_properties: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ip_allocation_policy: typing.Optional[builtins.str] = None,
    ip_protocol: typing.Optional[builtins.str] = None,
    local_ovf_path: typing.Optional[builtins.str] = None,
    ovf_network_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    remote_ovf_url: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__100441516de3f7c50670de0876c984cdaf1bda7b8af9c15fed7b86d65245c91a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8995d8f47a71c7917ef04df93875df645d3de536271f95c8ff62dedc69e8c28(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20a6267ae9e70c4280dd2f5a18fbf939c8da0360fa296d4e201856525d5b520e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73e4bb0fba00e63fe62bff40293b0b5d5c65013375a9ce5865fd0b775cee0e46(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3069bf30a1de2f004551da3f6966e78a1b3f3ec9d3aea181092b5053fa918109(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6474c06f6d9a259a7744516c9fc13416fe9ebf843a1c1ba81ea0ba2dd95d0620(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1e60dadb1a107d61b67238dc16bda3ce88e61f09f6f03bd6d8c69ee788a42f7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d9f85e43210389468d6fe4f057b1992ba79dbd5b30ae79f37725b5f19577d3e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bcfd25c9ce5ba2e2200901e6bd9c91ad41385372409ab75cf7db38b45a0bd5ab(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec9d7dc3a2853c3909d1d1c018351ecbfd8dd8f8a71d37ab13d344cdf65eccc8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5380d49cffc84748d26f05ab906105129174c67bf6781931661d9b63f322c37d(
    value: typing.Optional[VirtualMachineOvfDeploy],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1848d1e6fc961d09d84a5403124aba4fe26261f18ed44fb93de7d99140cf3e33(
    *,
    properties: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9750bab4dfce6cae7229f4624789604a20a695b48aded8ed793729b10c7a30a6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7a8c41e8727bb04e0ee86b734bc3c0278cf3d2c9891373e1ffc6f05414b899a(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2498717d26319e781f284818a16903f1024f003bab0561373c4c72f56e6b29b(
    value: typing.Optional[VirtualMachineVapp],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4df26224215993767c252ffb54c143f0774a48dac272f15ce0a11e6e11284228(
    *,
    version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__564e3411d628d5e34c12a539e998cdd4d815f78650efe2ab208c950974914cbb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc6f086a241a9447b75dc1eb139a600d10870e5f164623b48a4ca8b25f81c61e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3df2435ccc8a5c5c2aca633c26f535db9b55b7b16bbe5e36927e0b6eb49a144f(
    value: typing.Optional[VirtualMachineVtpm],
) -> None:
    """Type checking stubs"""
    pass
