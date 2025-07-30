r'''
# `data_vsphere_virtual_machine`

Refer to the Terraform Registry for docs: [`data_vsphere_virtual_machine`](https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine).
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


class DataVsphereVirtualMachine(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.dataVsphereVirtualMachine.DataVsphereVirtualMachine",
):
    '''Represents a {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine vsphere_virtual_machine}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        alternate_guest_name: typing.Optional[builtins.str] = None,
        annotation: typing.Optional[builtins.str] = None,
        boot_delay: typing.Optional[jsii.Number] = None,
        boot_retry_delay: typing.Optional[jsii.Number] = None,
        boot_retry_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        cpu_hot_add_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        cpu_hot_remove_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        cpu_limit: typing.Optional[jsii.Number] = None,
        cpu_performance_counters_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        cpu_reservation: typing.Optional[jsii.Number] = None,
        cpu_share_count: typing.Optional[jsii.Number] = None,
        cpu_share_level: typing.Optional[builtins.str] = None,
        datacenter_id: typing.Optional[builtins.str] = None,
        efi_secure_boot_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enable_disk_uuid: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enable_logging: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ept_rvi_mode: typing.Optional[builtins.str] = None,
        extra_config: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        extra_config_reboot_required: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        firmware: typing.Optional[builtins.str] = None,
        folder: typing.Optional[builtins.str] = None,
        guest_id: typing.Optional[builtins.str] = None,
        hardware_version: typing.Optional[jsii.Number] = None,
        hv_mode: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        ide_controller_scan_count: typing.Optional[jsii.Number] = None,
        latency_sensitivity: typing.Optional[builtins.str] = None,
        memory: typing.Optional[jsii.Number] = None,
        memory_hot_add_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        memory_limit: typing.Optional[jsii.Number] = None,
        memory_reservation: typing.Optional[jsii.Number] = None,
        memory_reservation_locked_to_max: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        memory_share_count: typing.Optional[jsii.Number] = None,
        memory_share_level: typing.Optional[builtins.str] = None,
        moid: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        nested_hv_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        num_cores_per_socket: typing.Optional[jsii.Number] = None,
        num_cpus: typing.Optional[jsii.Number] = None,
        nvme_controller_scan_count: typing.Optional[jsii.Number] = None,
        replace_trigger: typing.Optional[builtins.str] = None,
        run_tools_scripts_after_power_on: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        run_tools_scripts_after_resume: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        run_tools_scripts_before_guest_reboot: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        run_tools_scripts_before_guest_shutdown: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        run_tools_scripts_before_guest_standby: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        sata_controller_scan_count: typing.Optional[jsii.Number] = None,
        scsi_controller_scan_count: typing.Optional[jsii.Number] = None,
        storage_policy_id: typing.Optional[builtins.str] = None,
        swap_placement_policy: typing.Optional[builtins.str] = None,
        sync_time_with_host: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        sync_time_with_host_periodically: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tools_upgrade_policy: typing.Optional[builtins.str] = None,
        uuid: typing.Optional[builtins.str] = None,
        vapp: typing.Optional[typing.Union["DataVsphereVirtualMachineVapp", typing.Dict[builtins.str, typing.Any]]] = None,
        vbs_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        vvtd_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine vsphere_virtual_machine} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param alternate_guest_name: The guest name for the operating system when guest_id is otherGuest or otherGuest64. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#alternate_guest_name DataVsphereVirtualMachine#alternate_guest_name}
        :param annotation: User-provided description of the virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#annotation DataVsphereVirtualMachine#annotation}
        :param boot_delay: The number of milliseconds to wait before starting the boot sequence. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#boot_delay DataVsphereVirtualMachine#boot_delay}
        :param boot_retry_delay: The number of milliseconds to wait before retrying the boot sequence. This only valid if boot_retry_enabled is true. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#boot_retry_delay DataVsphereVirtualMachine#boot_retry_delay}
        :param boot_retry_enabled: If set to true, a virtual machine that fails to boot will try again after the delay defined in boot_retry_delay. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#boot_retry_enabled DataVsphereVirtualMachine#boot_retry_enabled}
        :param cpu_hot_add_enabled: Allow CPUs to be added to this virtual machine while it is running. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#cpu_hot_add_enabled DataVsphereVirtualMachine#cpu_hot_add_enabled}
        :param cpu_hot_remove_enabled: Allow CPUs to be added to this virtual machine while it is running. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#cpu_hot_remove_enabled DataVsphereVirtualMachine#cpu_hot_remove_enabled}
        :param cpu_limit: The maximum amount of memory (in MB) or CPU (in MHz) that this virtual machine can consume, regardless of available resources. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#cpu_limit DataVsphereVirtualMachine#cpu_limit}
        :param cpu_performance_counters_enabled: Enable CPU performance counters on this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#cpu_performance_counters_enabled DataVsphereVirtualMachine#cpu_performance_counters_enabled}
        :param cpu_reservation: The amount of memory (in MB) or CPU (in MHz) that this virtual machine is guaranteed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#cpu_reservation DataVsphereVirtualMachine#cpu_reservation}
        :param cpu_share_count: The amount of shares to allocate to cpu for a custom share level. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#cpu_share_count DataVsphereVirtualMachine#cpu_share_count}
        :param cpu_share_level: The allocation level for cpu resources. Can be one of high, low, normal, or custom. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#cpu_share_level DataVsphereVirtualMachine#cpu_share_level}
        :param datacenter_id: The managed object ID of the datacenter the virtual machine is in. This is not required when using ESXi directly, or if there is only one datacenter in your infrastructure. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#datacenter_id DataVsphereVirtualMachine#datacenter_id}
        :param efi_secure_boot_enabled: When the boot type set in firmware is efi, this enables EFI secure boot. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#efi_secure_boot_enabled DataVsphereVirtualMachine#efi_secure_boot_enabled}
        :param enable_disk_uuid: Expose the UUIDs of attached virtual disks to the virtual machine, allowing access to them in the guest. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#enable_disk_uuid DataVsphereVirtualMachine#enable_disk_uuid}
        :param enable_logging: Enable logging on this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#enable_logging DataVsphereVirtualMachine#enable_logging}
        :param ept_rvi_mode: The EPT/RVI (hardware memory virtualization) setting for this virtual machine. Can be one of automatic, on, or off. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#ept_rvi_mode DataVsphereVirtualMachine#ept_rvi_mode}
        :param extra_config: Extra configuration data for this virtual machine. Can be used to supply advanced parameters not normally in configuration, such as instance metadata, or configuration data for OVF images. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#extra_config DataVsphereVirtualMachine#extra_config}
        :param extra_config_reboot_required: Allow the virtual machine to be rebooted when a change to ``extra_config`` occurs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#extra_config_reboot_required DataVsphereVirtualMachine#extra_config_reboot_required}
        :param firmware: The firmware interface to use on the virtual machine. Can be one of bios or efi. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#firmware DataVsphereVirtualMachine#firmware}
        :param folder: The name of the folder the virtual machine is in. Allows distinguishing virtual machines with the same name in different folder paths Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#folder DataVsphereVirtualMachine#folder}
        :param guest_id: The guest ID for the operating system. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#guest_id DataVsphereVirtualMachine#guest_id}
        :param hardware_version: The hardware version for the virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#hardware_version DataVsphereVirtualMachine#hardware_version}
        :param hv_mode: The (non-nested) hardware virtualization setting for this virtual machine. Can be one of hvAuto, hvOn, or hvOff. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#hv_mode DataVsphereVirtualMachine#hv_mode}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#id DataVsphereVirtualMachine#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param ide_controller_scan_count: The number of IDE controllers to scan for disk sizes and controller types on. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#ide_controller_scan_count DataVsphereVirtualMachine#ide_controller_scan_count}
        :param latency_sensitivity: Controls the scheduling delay of the virtual machine. Use a higher sensitivity for applications that require lower latency, such as VOIP, media player applications, or applications that require frequent access to mouse or keyboard devices. Can be one of low, normal, medium, or high. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#latency_sensitivity DataVsphereVirtualMachine#latency_sensitivity}
        :param memory: The size of the virtual machine's memory, in MB. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#memory DataVsphereVirtualMachine#memory}
        :param memory_hot_add_enabled: Allow memory to be added to this virtual machine while it is running. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#memory_hot_add_enabled DataVsphereVirtualMachine#memory_hot_add_enabled}
        :param memory_limit: The maximum amount of memory (in MB) or CPU (in MHz) that this virtual machine can consume, regardless of available resources. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#memory_limit DataVsphereVirtualMachine#memory_limit}
        :param memory_reservation: The amount of memory (in MB) or CPU (in MHz) that this virtual machine is guaranteed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#memory_reservation DataVsphereVirtualMachine#memory_reservation}
        :param memory_reservation_locked_to_max: If set true, memory resource reservation for this virtual machine will always be equal to the virtual machine's memory size;increases in memory size will be rejected when a corresponding reservation increase is not possible. This feature may only be enabled if it is currently possible to reserve all of the virtual machine's memory. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#memory_reservation_locked_to_max DataVsphereVirtualMachine#memory_reservation_locked_to_max}
        :param memory_share_count: The amount of shares to allocate to memory for a custom share level. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#memory_share_count DataVsphereVirtualMachine#memory_share_count}
        :param memory_share_level: The allocation level for memory resources. Can be one of high, low, normal, or custom. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#memory_share_level DataVsphereVirtualMachine#memory_share_level}
        :param moid: The machine object ID from VMware vSphere. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#moid DataVsphereVirtualMachine#moid}
        :param name: The name of this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#name DataVsphereVirtualMachine#name}
        :param nested_hv_enabled: Enable nested hardware virtualization on this virtual machine, facilitating nested virtualization in the guest. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#nested_hv_enabled DataVsphereVirtualMachine#nested_hv_enabled}
        :param num_cores_per_socket: The number of cores to distribute amongst the CPUs in this virtual machine. If specified, the value supplied to num_cpus must be evenly divisible by this value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#num_cores_per_socket DataVsphereVirtualMachine#num_cores_per_socket}
        :param num_cpus: The number of virtual processors to assign to this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#num_cpus DataVsphereVirtualMachine#num_cpus}
        :param nvme_controller_scan_count: The number of NVMe controllers to scan for disk sizes and controller types on. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#nvme_controller_scan_count DataVsphereVirtualMachine#nvme_controller_scan_count}
        :param replace_trigger: Triggers replacement of resource whenever it changes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#replace_trigger DataVsphereVirtualMachine#replace_trigger}
        :param run_tools_scripts_after_power_on: Enable the run of scripts after virtual machine power-on when VMware Tools is installed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#run_tools_scripts_after_power_on DataVsphereVirtualMachine#run_tools_scripts_after_power_on}
        :param run_tools_scripts_after_resume: Enable the run of scripts after virtual machine resume when when VMware Tools is installed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#run_tools_scripts_after_resume DataVsphereVirtualMachine#run_tools_scripts_after_resume}
        :param run_tools_scripts_before_guest_reboot: Enable the run of scripts before guest operating system reboot when VMware Tools is installed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#run_tools_scripts_before_guest_reboot DataVsphereVirtualMachine#run_tools_scripts_before_guest_reboot}
        :param run_tools_scripts_before_guest_shutdown: Enable the run of scripts before guest operating system shutdown when VMware Tools is installed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#run_tools_scripts_before_guest_shutdown DataVsphereVirtualMachine#run_tools_scripts_before_guest_shutdown}
        :param run_tools_scripts_before_guest_standby: Enable the run of scripts before guest operating system standby when VMware Tools is installed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#run_tools_scripts_before_guest_standby DataVsphereVirtualMachine#run_tools_scripts_before_guest_standby}
        :param sata_controller_scan_count: The number of SATA controllers to scan for disk sizes and controller types on. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#sata_controller_scan_count DataVsphereVirtualMachine#sata_controller_scan_count}
        :param scsi_controller_scan_count: The number of SCSI controllers to scan for disk sizes and controller types on. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#scsi_controller_scan_count DataVsphereVirtualMachine#scsi_controller_scan_count}
        :param storage_policy_id: The ID of the storage policy to assign to the virtual machine home directory. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#storage_policy_id DataVsphereVirtualMachine#storage_policy_id}
        :param swap_placement_policy: The swap file placement policy for this virtual machine. Can be one of inherit, hostLocal, or vmDirectory. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#swap_placement_policy DataVsphereVirtualMachine#swap_placement_policy}
        :param sync_time_with_host: Enable guest clock synchronization with the host. On vSphere 7.0 U1 and above, with only this setting the clock is synchronized on startup and resume. Requires VMware Tools to be installed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#sync_time_with_host DataVsphereVirtualMachine#sync_time_with_host}
        :param sync_time_with_host_periodically: Enable periodic clock synchronization with the host. Supported only on vSphere 7.0 U1 and above. On prior versions setting ``sync_time_with_host`` is enough for periodic synchronization. Requires VMware Tools to be installed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#sync_time_with_host_periodically DataVsphereVirtualMachine#sync_time_with_host_periodically}
        :param tools_upgrade_policy: Set the upgrade policy for VMware Tools. Can be one of ``manual`` or ``upgradeAtPowerCycle``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#tools_upgrade_policy DataVsphereVirtualMachine#tools_upgrade_policy}
        :param uuid: The UUID of the virtual machine. Also exposed as the ID of the resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#uuid DataVsphereVirtualMachine#uuid}
        :param vapp: vapp block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#vapp DataVsphereVirtualMachine#vapp}
        :param vbs_enabled: Flag to specify if Virtualization-based security is enabled for this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#vbs_enabled DataVsphereVirtualMachine#vbs_enabled}
        :param vvtd_enabled: Flag to specify if I/O MMU virtualization, also called Intel Virtualization Technology for Directed I/O (VT-d) and AMD I/O Virtualization (AMD-Vi or IOMMU), is enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#vvtd_enabled DataVsphereVirtualMachine#vvtd_enabled}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__978298f7fae272848b5f269f8795b8e50d5a329a8f95e14784b987259b26e0f0)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DataVsphereVirtualMachineConfig(
            alternate_guest_name=alternate_guest_name,
            annotation=annotation,
            boot_delay=boot_delay,
            boot_retry_delay=boot_retry_delay,
            boot_retry_enabled=boot_retry_enabled,
            cpu_hot_add_enabled=cpu_hot_add_enabled,
            cpu_hot_remove_enabled=cpu_hot_remove_enabled,
            cpu_limit=cpu_limit,
            cpu_performance_counters_enabled=cpu_performance_counters_enabled,
            cpu_reservation=cpu_reservation,
            cpu_share_count=cpu_share_count,
            cpu_share_level=cpu_share_level,
            datacenter_id=datacenter_id,
            efi_secure_boot_enabled=efi_secure_boot_enabled,
            enable_disk_uuid=enable_disk_uuid,
            enable_logging=enable_logging,
            ept_rvi_mode=ept_rvi_mode,
            extra_config=extra_config,
            extra_config_reboot_required=extra_config_reboot_required,
            firmware=firmware,
            folder=folder,
            guest_id=guest_id,
            hardware_version=hardware_version,
            hv_mode=hv_mode,
            id=id,
            ide_controller_scan_count=ide_controller_scan_count,
            latency_sensitivity=latency_sensitivity,
            memory=memory,
            memory_hot_add_enabled=memory_hot_add_enabled,
            memory_limit=memory_limit,
            memory_reservation=memory_reservation,
            memory_reservation_locked_to_max=memory_reservation_locked_to_max,
            memory_share_count=memory_share_count,
            memory_share_level=memory_share_level,
            moid=moid,
            name=name,
            nested_hv_enabled=nested_hv_enabled,
            num_cores_per_socket=num_cores_per_socket,
            num_cpus=num_cpus,
            nvme_controller_scan_count=nvme_controller_scan_count,
            replace_trigger=replace_trigger,
            run_tools_scripts_after_power_on=run_tools_scripts_after_power_on,
            run_tools_scripts_after_resume=run_tools_scripts_after_resume,
            run_tools_scripts_before_guest_reboot=run_tools_scripts_before_guest_reboot,
            run_tools_scripts_before_guest_shutdown=run_tools_scripts_before_guest_shutdown,
            run_tools_scripts_before_guest_standby=run_tools_scripts_before_guest_standby,
            sata_controller_scan_count=sata_controller_scan_count,
            scsi_controller_scan_count=scsi_controller_scan_count,
            storage_policy_id=storage_policy_id,
            swap_placement_policy=swap_placement_policy,
            sync_time_with_host=sync_time_with_host,
            sync_time_with_host_periodically=sync_time_with_host_periodically,
            tools_upgrade_policy=tools_upgrade_policy,
            uuid=uuid,
            vapp=vapp,
            vbs_enabled=vbs_enabled,
            vvtd_enabled=vvtd_enabled,
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
        '''Generates CDKTF code for importing a DataVsphereVirtualMachine resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataVsphereVirtualMachine to import.
        :param import_from_id: The id of the existing DataVsphereVirtualMachine that should be imported. Refer to the {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataVsphereVirtualMachine to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7fbc3b693f3e193744eeb2752b1b46b1c1924866be1f72ea4c6afae9adc206d3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putVapp")
    def put_vapp(
        self,
        *,
        properties: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param properties: A map of customizable vApp properties and their values. Allows customization of VMs cloned from OVF templates which have customizable vApp properties. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#properties DataVsphereVirtualMachine#properties}
        '''
        value = DataVsphereVirtualMachineVapp(properties=properties)

        return typing.cast(None, jsii.invoke(self, "putVapp", [value]))

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

    @jsii.member(jsii_name="resetDatacenterId")
    def reset_datacenter_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatacenterId", []))

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

    @jsii.member(jsii_name="resetGuestId")
    def reset_guest_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGuestId", []))

    @jsii.member(jsii_name="resetHardwareVersion")
    def reset_hardware_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHardwareVersion", []))

    @jsii.member(jsii_name="resetHvMode")
    def reset_hv_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHvMode", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIdeControllerScanCount")
    def reset_ide_controller_scan_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdeControllerScanCount", []))

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

    @jsii.member(jsii_name="resetMoid")
    def reset_moid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMoid", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetNestedHvEnabled")
    def reset_nested_hv_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNestedHvEnabled", []))

    @jsii.member(jsii_name="resetNumCoresPerSocket")
    def reset_num_cores_per_socket(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNumCoresPerSocket", []))

    @jsii.member(jsii_name="resetNumCpus")
    def reset_num_cpus(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNumCpus", []))

    @jsii.member(jsii_name="resetNvmeControllerScanCount")
    def reset_nvme_controller_scan_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNvmeControllerScanCount", []))

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

    @jsii.member(jsii_name="resetSataControllerScanCount")
    def reset_sata_controller_scan_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSataControllerScanCount", []))

    @jsii.member(jsii_name="resetScsiControllerScanCount")
    def reset_scsi_controller_scan_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScsiControllerScanCount", []))

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

    @jsii.member(jsii_name="resetToolsUpgradePolicy")
    def reset_tools_upgrade_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetToolsUpgradePolicy", []))

    @jsii.member(jsii_name="resetUuid")
    def reset_uuid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUuid", []))

    @jsii.member(jsii_name="resetVapp")
    def reset_vapp(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVapp", []))

    @jsii.member(jsii_name="resetVbsEnabled")
    def reset_vbs_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVbsEnabled", []))

    @jsii.member(jsii_name="resetVvtdEnabled")
    def reset_vvtd_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVvtdEnabled", []))

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
    @jsii.member(jsii_name="changeVersion")
    def change_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "changeVersion"))

    @builtins.property
    @jsii.member(jsii_name="defaultIpAddress")
    def default_ip_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultIpAddress"))

    @builtins.property
    @jsii.member(jsii_name="disks")
    def disks(self) -> "DataVsphereVirtualMachineDisksList":
        return typing.cast("DataVsphereVirtualMachineDisksList", jsii.get(self, "disks"))

    @builtins.property
    @jsii.member(jsii_name="guestIpAddresses")
    def guest_ip_addresses(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "guestIpAddresses"))

    @builtins.property
    @jsii.member(jsii_name="instanceUuid")
    def instance_uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceUuid"))

    @builtins.property
    @jsii.member(jsii_name="networkInterfaces")
    def network_interfaces(self) -> "DataVsphereVirtualMachineNetworkInterfacesList":
        return typing.cast("DataVsphereVirtualMachineNetworkInterfacesList", jsii.get(self, "networkInterfaces"))

    @builtins.property
    @jsii.member(jsii_name="networkInterfaceTypes")
    def network_interface_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "networkInterfaceTypes"))

    @builtins.property
    @jsii.member(jsii_name="scsiBusSharing")
    def scsi_bus_sharing(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scsiBusSharing"))

    @builtins.property
    @jsii.member(jsii_name="scsiType")
    def scsi_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scsiType"))

    @builtins.property
    @jsii.member(jsii_name="vapp")
    def vapp(self) -> "DataVsphereVirtualMachineVappOutputReference":
        return typing.cast("DataVsphereVirtualMachineVappOutputReference", jsii.get(self, "vapp"))

    @builtins.property
    @jsii.member(jsii_name="vappTransport")
    def vapp_transport(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "vappTransport"))

    @builtins.property
    @jsii.member(jsii_name="vtpm")
    def vtpm(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "vtpm"))

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
    @jsii.member(jsii_name="datacenterIdInput")
    def datacenter_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "datacenterIdInput"))

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
    @jsii.member(jsii_name="guestIdInput")
    def guest_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "guestIdInput"))

    @builtins.property
    @jsii.member(jsii_name="hardwareVersionInput")
    def hardware_version_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "hardwareVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="hvModeInput")
    def hv_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hvModeInput"))

    @builtins.property
    @jsii.member(jsii_name="ideControllerScanCountInput")
    def ide_controller_scan_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ideControllerScanCountInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

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
    @jsii.member(jsii_name="moidInput")
    def moid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "moidInput"))

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
    @jsii.member(jsii_name="numCoresPerSocketInput")
    def num_cores_per_socket_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "numCoresPerSocketInput"))

    @builtins.property
    @jsii.member(jsii_name="numCpusInput")
    def num_cpus_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "numCpusInput"))

    @builtins.property
    @jsii.member(jsii_name="nvmeControllerScanCountInput")
    def nvme_controller_scan_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "nvmeControllerScanCountInput"))

    @builtins.property
    @jsii.member(jsii_name="replaceTriggerInput")
    def replace_trigger_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "replaceTriggerInput"))

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
    @jsii.member(jsii_name="sataControllerScanCountInput")
    def sata_controller_scan_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "sataControllerScanCountInput"))

    @builtins.property
    @jsii.member(jsii_name="scsiControllerScanCountInput")
    def scsi_controller_scan_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "scsiControllerScanCountInput"))

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
    @jsii.member(jsii_name="toolsUpgradePolicyInput")
    def tools_upgrade_policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "toolsUpgradePolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="uuidInput")
    def uuid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "uuidInput"))

    @builtins.property
    @jsii.member(jsii_name="vappInput")
    def vapp_input(self) -> typing.Optional["DataVsphereVirtualMachineVapp"]:
        return typing.cast(typing.Optional["DataVsphereVirtualMachineVapp"], jsii.get(self, "vappInput"))

    @builtins.property
    @jsii.member(jsii_name="vbsEnabledInput")
    def vbs_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "vbsEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="vvtdEnabledInput")
    def vvtd_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "vvtdEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="alternateGuestName")
    def alternate_guest_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "alternateGuestName"))

    @alternate_guest_name.setter
    def alternate_guest_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf2f4fa4dc2f8a6ebdc38033481c377c4d49c7b738e3bd350715af95c005de37)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alternateGuestName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="annotation")
    def annotation(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "annotation"))

    @annotation.setter
    def annotation(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3587957eb912202924ef765b2af3220fb6c7658c9f304082b10bdb1cfc2557dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "annotation", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bootDelay")
    def boot_delay(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "bootDelay"))

    @boot_delay.setter
    def boot_delay(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf72a91d0ac08dffe362782eb805c3d5f78905040276370cdb99c1dfdfee6510)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bootDelay", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bootRetryDelay")
    def boot_retry_delay(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "bootRetryDelay"))

    @boot_retry_delay.setter
    def boot_retry_delay(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__537aeb9bd18a7723f7399f576c85d1074d5b4a9ec9f00c2562372c0cf6c71386)
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
            type_hints = typing.get_type_hints(_typecheckingstub__61304d30488e473466fc45d9a383f290c1526abc6470dd0564f534be964165f6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__bc565ed7548974f3ffd2839046b0b0061df681a6ab17ffe4e27e9c3a743dabbb)
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
            type_hints = typing.get_type_hints(_typecheckingstub__415fc03b410a979a7b0780b109792c89633c8f27ffb9eef6db64f7fb0b751b98)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cpuHotRemoveEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cpuLimit")
    def cpu_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cpuLimit"))

    @cpu_limit.setter
    def cpu_limit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e01cb8fc390679c31be9b7f516028923215eb4e06c9b2fdac91fe75fff932f6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__785c82bc9ab2fa6e7f09395661c35220e1f8e563369f07221a4699f878012257)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cpuPerformanceCountersEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cpuReservation")
    def cpu_reservation(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cpuReservation"))

    @cpu_reservation.setter
    def cpu_reservation(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d62bf9df144e6e2585b81d3d057e329899d33f7f0189a256f01aa9e4f375f899)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cpuReservation", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cpuShareCount")
    def cpu_share_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cpuShareCount"))

    @cpu_share_count.setter
    def cpu_share_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fecbbf59f9c959c9fc463498c2a486354787af9a268d280cf19a7be3bfae703a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cpuShareCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cpuShareLevel")
    def cpu_share_level(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cpuShareLevel"))

    @cpu_share_level.setter
    def cpu_share_level(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__69a912bdbf5f93f291ba3555a82b301093197043ed6ba0b6ee9a4ffde8cbfc27)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cpuShareLevel", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="datacenterId")
    def datacenter_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "datacenterId"))

    @datacenter_id.setter
    def datacenter_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1444e3fb2f6c126a2efe41f081cbe7255174148010ea3e97620f008482cadee7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "datacenterId", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__463f6b52c7d3845511e4c59c938e0fa005516aff0bebebdef83d174f0fab2a9e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__48a3ab61fc12862cf093537fe5344f0a0eb241caafe9b563ac5bdf31593bde71)
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
            type_hints = typing.get_type_hints(_typecheckingstub__80b12c9a443f0e0caef3fa32fc6379511c4691363b26fbd3bc8c553f8d72661c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableLogging", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="eptRviMode")
    def ept_rvi_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "eptRviMode"))

    @ept_rvi_mode.setter
    def ept_rvi_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dde764e33924692ea2aa4c039d9817770651c978e8f4f3d66772eec700c5f0f3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "eptRviMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="extraConfig")
    def extra_config(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "extraConfig"))

    @extra_config.setter
    def extra_config(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60c1f8b11fed5b235308e313a1265908ee85313af3471d1973d82995ec0fdd41)
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
            type_hints = typing.get_type_hints(_typecheckingstub__626286b21383205f6da12bed6ab55027b965f33d456ca8e659d1ebe024cc3c04)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "extraConfigRebootRequired", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="firmware")
    def firmware(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "firmware"))

    @firmware.setter
    def firmware(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83b0ab45cca74ccbc6b14856fdb26591ea1780c6319bbbe3c2dabab7b00c9f1d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "firmware", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="folder")
    def folder(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "folder"))

    @folder.setter
    def folder(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__affe2f34a7ab1364fab11cdadb0a693a0521a409b15ade69ed4e5ab3935fb656)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "folder", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="guestId")
    def guest_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "guestId"))

    @guest_id.setter
    def guest_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__013dd63dce824c2642ae443028bb309152eba7faec5217b690dec671d63ec9bd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "guestId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="hardwareVersion")
    def hardware_version(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "hardwareVersion"))

    @hardware_version.setter
    def hardware_version(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b803466a13111ebb454d3478bd1110abdbf27a4abd8f9e2b6d8c9234a59c8897)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hardwareVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="hvMode")
    def hv_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hvMode"))

    @hv_mode.setter
    def hv_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e4970964f67002160eab44a8370f88ed35d92f7d353e6bfb902d7392b2f8943)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hvMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26ecba812036e4448c8cd590c5f7f54098d5cac3644865e7f4d420a3b2a631c5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ideControllerScanCount")
    def ide_controller_scan_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ideControllerScanCount"))

    @ide_controller_scan_count.setter
    def ide_controller_scan_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64477ac96403faa22578af3707663f54d6f3398e97286ed40a415a199e4a396b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ideControllerScanCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="latencySensitivity")
    def latency_sensitivity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "latencySensitivity"))

    @latency_sensitivity.setter
    def latency_sensitivity(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5913855c1d8ff85fc0c8f4cb4fb5e1707f798a2dd983b714e2337b48bea892d7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "latencySensitivity", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="memory")
    def memory(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "memory"))

    @memory.setter
    def memory(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c4efa7e3539f976965a5d01f743c784ad3089985043d37ef22b0d8ecd807a933)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a03c8e3e730949f7240cb4e5c2c4d9501ab72794631ffe98cb1da185bf172317)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "memoryHotAddEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="memoryLimit")
    def memory_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "memoryLimit"))

    @memory_limit.setter
    def memory_limit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__69eeececbb891a5932133739246ce1b570d637148019d2bfcb36563e6cd5862c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "memoryLimit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="memoryReservation")
    def memory_reservation(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "memoryReservation"))

    @memory_reservation.setter
    def memory_reservation(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6fa2212f7ba970ed5a23471cdccf5b1e6833bdb886ae540fef066ec099bc6c55)
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
            type_hints = typing.get_type_hints(_typecheckingstub__44acd152678104726506109772adff3c1dd31c595932578b8121cdf9259beb71)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "memoryReservationLockedToMax", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="memoryShareCount")
    def memory_share_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "memoryShareCount"))

    @memory_share_count.setter
    def memory_share_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81c7e99ff05a38d6396c60fe08280fa94f90b53832d697ab5414c6f96b3808a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "memoryShareCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="memoryShareLevel")
    def memory_share_level(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "memoryShareLevel"))

    @memory_share_level.setter
    def memory_share_level(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__954a078b5608bbf58c534c6d4f82dc7fdb3398117435c07f319d51d27016e3e4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "memoryShareLevel", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="moid")
    def moid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "moid"))

    @moid.setter
    def moid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__296e1344e5754f846203d862c287e40afba7ac871dce10ff9dd0942c2816623d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "moid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__78cf48270f6ba82a52c672775e6a9291b3c8f1bc1899e219bb9a1f7ca13d5bca)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e34a9b953fcc66a38a29631a84684f6d78a17e21fd88961dbdfc1b0354c18d8e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nestedHvEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="numCoresPerSocket")
    def num_cores_per_socket(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numCoresPerSocket"))

    @num_cores_per_socket.setter
    def num_cores_per_socket(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2f5aa34ca61d73fae0bbd5a9911ce50b0ab8bb56afccab110a11db0ef826670)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "numCoresPerSocket", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="numCpus")
    def num_cpus(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numCpus"))

    @num_cpus.setter
    def num_cpus(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__685d570c1c6a316403020d5c649f68fd0b040b85f0f24f9cd34e4bb8761c81c8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "numCpus", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="nvmeControllerScanCount")
    def nvme_controller_scan_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "nvmeControllerScanCount"))

    @nvme_controller_scan_count.setter
    def nvme_controller_scan_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__864525f6073687b015fa45959d0dd835618150f655a665bfc3ec14a1eefd4a63)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nvmeControllerScanCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="replaceTrigger")
    def replace_trigger(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "replaceTrigger"))

    @replace_trigger.setter
    def replace_trigger(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e243f005e9d734dee6eb99862ddfad863789db59531c171f4f1c4a74a84df04)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "replaceTrigger", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__a55eba0e39e799fecf79bb8d782aeff791f2e53b9337b8806da0469e3e830a61)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5699470252834a4c9a26fd663a49d0332a77a0190c48d0237a2386d5e763bfc5)
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
            type_hints = typing.get_type_hints(_typecheckingstub__05662863332c200d8312860ca82f5c1880a96114465f8cfdb9db395305d6dd25)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7d9ab7b3458843430f5f6d1cc32d2726c6290774a6a5ab396dccf8029c9cdeff)
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
            type_hints = typing.get_type_hints(_typecheckingstub__57de10a5c2a3eef0f89e332db158c5f6e4e24eb84c32f881c6e5bb82ec09bd2a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "runToolsScriptsBeforeGuestStandby", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sataControllerScanCount")
    def sata_controller_scan_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "sataControllerScanCount"))

    @sata_controller_scan_count.setter
    def sata_controller_scan_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76b44e736be9e11525b67f21196d0748af67b312d84b7ad2a3c48bad781714da)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sataControllerScanCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scsiControllerScanCount")
    def scsi_controller_scan_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "scsiControllerScanCount"))

    @scsi_controller_scan_count.setter
    def scsi_controller_scan_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__629dd2ede7de48a0b5327ecea008ba32e076f13754523ca4aaf5475d53d149c2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scsiControllerScanCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="storagePolicyId")
    def storage_policy_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storagePolicyId"))

    @storage_policy_id.setter
    def storage_policy_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e1783567549077e972e5da41ef16a3734da0f2ca9c85ebcf3ceff19e38ebd022)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "storagePolicyId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="swapPlacementPolicy")
    def swap_placement_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "swapPlacementPolicy"))

    @swap_placement_policy.setter
    def swap_placement_policy(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e89952ddfa62290296776425879cce4cfd08957d00334c6f8a9a03c79fb0a33)
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
            type_hints = typing.get_type_hints(_typecheckingstub__efb41f65dc5022f2b958b1ae49953ba0a68d0c32459b28b4aade1761c69e497b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d76cbe2a67b0b987ff54f118dc79ac908445eec61f2530869d8403ed95a724ba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "syncTimeWithHostPeriodically", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="toolsUpgradePolicy")
    def tools_upgrade_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "toolsUpgradePolicy"))

    @tools_upgrade_policy.setter
    def tools_upgrade_policy(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ee58baaff8d23216dd20c7f0ea3ec09383f98c7134b79d0ff861ec032d606c9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "toolsUpgradePolicy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @uuid.setter
    def uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c61693c4c000e0e2ba4c45e71ae93f1bbc838dbac9752a5a45e10da7b50bb9f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uuid", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__c7243fb9b60b1f3755fd67668d8a81d1c288290ef05a1e57c2e87e9c32358abb)
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
            type_hints = typing.get_type_hints(_typecheckingstub__615e8fc45be9ddcdd1f317b7dd0576f819f2cf0f387bfec4fc846d8d6b25083f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vvtdEnabled", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.dataVsphereVirtualMachine.DataVsphereVirtualMachineConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "alternate_guest_name": "alternateGuestName",
        "annotation": "annotation",
        "boot_delay": "bootDelay",
        "boot_retry_delay": "bootRetryDelay",
        "boot_retry_enabled": "bootRetryEnabled",
        "cpu_hot_add_enabled": "cpuHotAddEnabled",
        "cpu_hot_remove_enabled": "cpuHotRemoveEnabled",
        "cpu_limit": "cpuLimit",
        "cpu_performance_counters_enabled": "cpuPerformanceCountersEnabled",
        "cpu_reservation": "cpuReservation",
        "cpu_share_count": "cpuShareCount",
        "cpu_share_level": "cpuShareLevel",
        "datacenter_id": "datacenterId",
        "efi_secure_boot_enabled": "efiSecureBootEnabled",
        "enable_disk_uuid": "enableDiskUuid",
        "enable_logging": "enableLogging",
        "ept_rvi_mode": "eptRviMode",
        "extra_config": "extraConfig",
        "extra_config_reboot_required": "extraConfigRebootRequired",
        "firmware": "firmware",
        "folder": "folder",
        "guest_id": "guestId",
        "hardware_version": "hardwareVersion",
        "hv_mode": "hvMode",
        "id": "id",
        "ide_controller_scan_count": "ideControllerScanCount",
        "latency_sensitivity": "latencySensitivity",
        "memory": "memory",
        "memory_hot_add_enabled": "memoryHotAddEnabled",
        "memory_limit": "memoryLimit",
        "memory_reservation": "memoryReservation",
        "memory_reservation_locked_to_max": "memoryReservationLockedToMax",
        "memory_share_count": "memoryShareCount",
        "memory_share_level": "memoryShareLevel",
        "moid": "moid",
        "name": "name",
        "nested_hv_enabled": "nestedHvEnabled",
        "num_cores_per_socket": "numCoresPerSocket",
        "num_cpus": "numCpus",
        "nvme_controller_scan_count": "nvmeControllerScanCount",
        "replace_trigger": "replaceTrigger",
        "run_tools_scripts_after_power_on": "runToolsScriptsAfterPowerOn",
        "run_tools_scripts_after_resume": "runToolsScriptsAfterResume",
        "run_tools_scripts_before_guest_reboot": "runToolsScriptsBeforeGuestReboot",
        "run_tools_scripts_before_guest_shutdown": "runToolsScriptsBeforeGuestShutdown",
        "run_tools_scripts_before_guest_standby": "runToolsScriptsBeforeGuestStandby",
        "sata_controller_scan_count": "sataControllerScanCount",
        "scsi_controller_scan_count": "scsiControllerScanCount",
        "storage_policy_id": "storagePolicyId",
        "swap_placement_policy": "swapPlacementPolicy",
        "sync_time_with_host": "syncTimeWithHost",
        "sync_time_with_host_periodically": "syncTimeWithHostPeriodically",
        "tools_upgrade_policy": "toolsUpgradePolicy",
        "uuid": "uuid",
        "vapp": "vapp",
        "vbs_enabled": "vbsEnabled",
        "vvtd_enabled": "vvtdEnabled",
    },
)
class DataVsphereVirtualMachineConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        alternate_guest_name: typing.Optional[builtins.str] = None,
        annotation: typing.Optional[builtins.str] = None,
        boot_delay: typing.Optional[jsii.Number] = None,
        boot_retry_delay: typing.Optional[jsii.Number] = None,
        boot_retry_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        cpu_hot_add_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        cpu_hot_remove_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        cpu_limit: typing.Optional[jsii.Number] = None,
        cpu_performance_counters_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        cpu_reservation: typing.Optional[jsii.Number] = None,
        cpu_share_count: typing.Optional[jsii.Number] = None,
        cpu_share_level: typing.Optional[builtins.str] = None,
        datacenter_id: typing.Optional[builtins.str] = None,
        efi_secure_boot_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enable_disk_uuid: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enable_logging: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ept_rvi_mode: typing.Optional[builtins.str] = None,
        extra_config: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        extra_config_reboot_required: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        firmware: typing.Optional[builtins.str] = None,
        folder: typing.Optional[builtins.str] = None,
        guest_id: typing.Optional[builtins.str] = None,
        hardware_version: typing.Optional[jsii.Number] = None,
        hv_mode: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        ide_controller_scan_count: typing.Optional[jsii.Number] = None,
        latency_sensitivity: typing.Optional[builtins.str] = None,
        memory: typing.Optional[jsii.Number] = None,
        memory_hot_add_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        memory_limit: typing.Optional[jsii.Number] = None,
        memory_reservation: typing.Optional[jsii.Number] = None,
        memory_reservation_locked_to_max: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        memory_share_count: typing.Optional[jsii.Number] = None,
        memory_share_level: typing.Optional[builtins.str] = None,
        moid: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        nested_hv_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        num_cores_per_socket: typing.Optional[jsii.Number] = None,
        num_cpus: typing.Optional[jsii.Number] = None,
        nvme_controller_scan_count: typing.Optional[jsii.Number] = None,
        replace_trigger: typing.Optional[builtins.str] = None,
        run_tools_scripts_after_power_on: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        run_tools_scripts_after_resume: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        run_tools_scripts_before_guest_reboot: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        run_tools_scripts_before_guest_shutdown: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        run_tools_scripts_before_guest_standby: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        sata_controller_scan_count: typing.Optional[jsii.Number] = None,
        scsi_controller_scan_count: typing.Optional[jsii.Number] = None,
        storage_policy_id: typing.Optional[builtins.str] = None,
        swap_placement_policy: typing.Optional[builtins.str] = None,
        sync_time_with_host: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        sync_time_with_host_periodically: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tools_upgrade_policy: typing.Optional[builtins.str] = None,
        uuid: typing.Optional[builtins.str] = None,
        vapp: typing.Optional[typing.Union["DataVsphereVirtualMachineVapp", typing.Dict[builtins.str, typing.Any]]] = None,
        vbs_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        vvtd_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param alternate_guest_name: The guest name for the operating system when guest_id is otherGuest or otherGuest64. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#alternate_guest_name DataVsphereVirtualMachine#alternate_guest_name}
        :param annotation: User-provided description of the virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#annotation DataVsphereVirtualMachine#annotation}
        :param boot_delay: The number of milliseconds to wait before starting the boot sequence. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#boot_delay DataVsphereVirtualMachine#boot_delay}
        :param boot_retry_delay: The number of milliseconds to wait before retrying the boot sequence. This only valid if boot_retry_enabled is true. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#boot_retry_delay DataVsphereVirtualMachine#boot_retry_delay}
        :param boot_retry_enabled: If set to true, a virtual machine that fails to boot will try again after the delay defined in boot_retry_delay. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#boot_retry_enabled DataVsphereVirtualMachine#boot_retry_enabled}
        :param cpu_hot_add_enabled: Allow CPUs to be added to this virtual machine while it is running. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#cpu_hot_add_enabled DataVsphereVirtualMachine#cpu_hot_add_enabled}
        :param cpu_hot_remove_enabled: Allow CPUs to be added to this virtual machine while it is running. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#cpu_hot_remove_enabled DataVsphereVirtualMachine#cpu_hot_remove_enabled}
        :param cpu_limit: The maximum amount of memory (in MB) or CPU (in MHz) that this virtual machine can consume, regardless of available resources. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#cpu_limit DataVsphereVirtualMachine#cpu_limit}
        :param cpu_performance_counters_enabled: Enable CPU performance counters on this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#cpu_performance_counters_enabled DataVsphereVirtualMachine#cpu_performance_counters_enabled}
        :param cpu_reservation: The amount of memory (in MB) or CPU (in MHz) that this virtual machine is guaranteed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#cpu_reservation DataVsphereVirtualMachine#cpu_reservation}
        :param cpu_share_count: The amount of shares to allocate to cpu for a custom share level. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#cpu_share_count DataVsphereVirtualMachine#cpu_share_count}
        :param cpu_share_level: The allocation level for cpu resources. Can be one of high, low, normal, or custom. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#cpu_share_level DataVsphereVirtualMachine#cpu_share_level}
        :param datacenter_id: The managed object ID of the datacenter the virtual machine is in. This is not required when using ESXi directly, or if there is only one datacenter in your infrastructure. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#datacenter_id DataVsphereVirtualMachine#datacenter_id}
        :param efi_secure_boot_enabled: When the boot type set in firmware is efi, this enables EFI secure boot. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#efi_secure_boot_enabled DataVsphereVirtualMachine#efi_secure_boot_enabled}
        :param enable_disk_uuid: Expose the UUIDs of attached virtual disks to the virtual machine, allowing access to them in the guest. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#enable_disk_uuid DataVsphereVirtualMachine#enable_disk_uuid}
        :param enable_logging: Enable logging on this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#enable_logging DataVsphereVirtualMachine#enable_logging}
        :param ept_rvi_mode: The EPT/RVI (hardware memory virtualization) setting for this virtual machine. Can be one of automatic, on, or off. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#ept_rvi_mode DataVsphereVirtualMachine#ept_rvi_mode}
        :param extra_config: Extra configuration data for this virtual machine. Can be used to supply advanced parameters not normally in configuration, such as instance metadata, or configuration data for OVF images. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#extra_config DataVsphereVirtualMachine#extra_config}
        :param extra_config_reboot_required: Allow the virtual machine to be rebooted when a change to ``extra_config`` occurs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#extra_config_reboot_required DataVsphereVirtualMachine#extra_config_reboot_required}
        :param firmware: The firmware interface to use on the virtual machine. Can be one of bios or efi. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#firmware DataVsphereVirtualMachine#firmware}
        :param folder: The name of the folder the virtual machine is in. Allows distinguishing virtual machines with the same name in different folder paths Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#folder DataVsphereVirtualMachine#folder}
        :param guest_id: The guest ID for the operating system. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#guest_id DataVsphereVirtualMachine#guest_id}
        :param hardware_version: The hardware version for the virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#hardware_version DataVsphereVirtualMachine#hardware_version}
        :param hv_mode: The (non-nested) hardware virtualization setting for this virtual machine. Can be one of hvAuto, hvOn, or hvOff. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#hv_mode DataVsphereVirtualMachine#hv_mode}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#id DataVsphereVirtualMachine#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param ide_controller_scan_count: The number of IDE controllers to scan for disk sizes and controller types on. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#ide_controller_scan_count DataVsphereVirtualMachine#ide_controller_scan_count}
        :param latency_sensitivity: Controls the scheduling delay of the virtual machine. Use a higher sensitivity for applications that require lower latency, such as VOIP, media player applications, or applications that require frequent access to mouse or keyboard devices. Can be one of low, normal, medium, or high. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#latency_sensitivity DataVsphereVirtualMachine#latency_sensitivity}
        :param memory: The size of the virtual machine's memory, in MB. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#memory DataVsphereVirtualMachine#memory}
        :param memory_hot_add_enabled: Allow memory to be added to this virtual machine while it is running. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#memory_hot_add_enabled DataVsphereVirtualMachine#memory_hot_add_enabled}
        :param memory_limit: The maximum amount of memory (in MB) or CPU (in MHz) that this virtual machine can consume, regardless of available resources. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#memory_limit DataVsphereVirtualMachine#memory_limit}
        :param memory_reservation: The amount of memory (in MB) or CPU (in MHz) that this virtual machine is guaranteed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#memory_reservation DataVsphereVirtualMachine#memory_reservation}
        :param memory_reservation_locked_to_max: If set true, memory resource reservation for this virtual machine will always be equal to the virtual machine's memory size;increases in memory size will be rejected when a corresponding reservation increase is not possible. This feature may only be enabled if it is currently possible to reserve all of the virtual machine's memory. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#memory_reservation_locked_to_max DataVsphereVirtualMachine#memory_reservation_locked_to_max}
        :param memory_share_count: The amount of shares to allocate to memory for a custom share level. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#memory_share_count DataVsphereVirtualMachine#memory_share_count}
        :param memory_share_level: The allocation level for memory resources. Can be one of high, low, normal, or custom. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#memory_share_level DataVsphereVirtualMachine#memory_share_level}
        :param moid: The machine object ID from VMware vSphere. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#moid DataVsphereVirtualMachine#moid}
        :param name: The name of this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#name DataVsphereVirtualMachine#name}
        :param nested_hv_enabled: Enable nested hardware virtualization on this virtual machine, facilitating nested virtualization in the guest. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#nested_hv_enabled DataVsphereVirtualMachine#nested_hv_enabled}
        :param num_cores_per_socket: The number of cores to distribute amongst the CPUs in this virtual machine. If specified, the value supplied to num_cpus must be evenly divisible by this value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#num_cores_per_socket DataVsphereVirtualMachine#num_cores_per_socket}
        :param num_cpus: The number of virtual processors to assign to this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#num_cpus DataVsphereVirtualMachine#num_cpus}
        :param nvme_controller_scan_count: The number of NVMe controllers to scan for disk sizes and controller types on. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#nvme_controller_scan_count DataVsphereVirtualMachine#nvme_controller_scan_count}
        :param replace_trigger: Triggers replacement of resource whenever it changes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#replace_trigger DataVsphereVirtualMachine#replace_trigger}
        :param run_tools_scripts_after_power_on: Enable the run of scripts after virtual machine power-on when VMware Tools is installed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#run_tools_scripts_after_power_on DataVsphereVirtualMachine#run_tools_scripts_after_power_on}
        :param run_tools_scripts_after_resume: Enable the run of scripts after virtual machine resume when when VMware Tools is installed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#run_tools_scripts_after_resume DataVsphereVirtualMachine#run_tools_scripts_after_resume}
        :param run_tools_scripts_before_guest_reboot: Enable the run of scripts before guest operating system reboot when VMware Tools is installed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#run_tools_scripts_before_guest_reboot DataVsphereVirtualMachine#run_tools_scripts_before_guest_reboot}
        :param run_tools_scripts_before_guest_shutdown: Enable the run of scripts before guest operating system shutdown when VMware Tools is installed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#run_tools_scripts_before_guest_shutdown DataVsphereVirtualMachine#run_tools_scripts_before_guest_shutdown}
        :param run_tools_scripts_before_guest_standby: Enable the run of scripts before guest operating system standby when VMware Tools is installed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#run_tools_scripts_before_guest_standby DataVsphereVirtualMachine#run_tools_scripts_before_guest_standby}
        :param sata_controller_scan_count: The number of SATA controllers to scan for disk sizes and controller types on. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#sata_controller_scan_count DataVsphereVirtualMachine#sata_controller_scan_count}
        :param scsi_controller_scan_count: The number of SCSI controllers to scan for disk sizes and controller types on. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#scsi_controller_scan_count DataVsphereVirtualMachine#scsi_controller_scan_count}
        :param storage_policy_id: The ID of the storage policy to assign to the virtual machine home directory. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#storage_policy_id DataVsphereVirtualMachine#storage_policy_id}
        :param swap_placement_policy: The swap file placement policy for this virtual machine. Can be one of inherit, hostLocal, or vmDirectory. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#swap_placement_policy DataVsphereVirtualMachine#swap_placement_policy}
        :param sync_time_with_host: Enable guest clock synchronization with the host. On vSphere 7.0 U1 and above, with only this setting the clock is synchronized on startup and resume. Requires VMware Tools to be installed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#sync_time_with_host DataVsphereVirtualMachine#sync_time_with_host}
        :param sync_time_with_host_periodically: Enable periodic clock synchronization with the host. Supported only on vSphere 7.0 U1 and above. On prior versions setting ``sync_time_with_host`` is enough for periodic synchronization. Requires VMware Tools to be installed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#sync_time_with_host_periodically DataVsphereVirtualMachine#sync_time_with_host_periodically}
        :param tools_upgrade_policy: Set the upgrade policy for VMware Tools. Can be one of ``manual`` or ``upgradeAtPowerCycle``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#tools_upgrade_policy DataVsphereVirtualMachine#tools_upgrade_policy}
        :param uuid: The UUID of the virtual machine. Also exposed as the ID of the resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#uuid DataVsphereVirtualMachine#uuid}
        :param vapp: vapp block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#vapp DataVsphereVirtualMachine#vapp}
        :param vbs_enabled: Flag to specify if Virtualization-based security is enabled for this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#vbs_enabled DataVsphereVirtualMachine#vbs_enabled}
        :param vvtd_enabled: Flag to specify if I/O MMU virtualization, also called Intel Virtualization Technology for Directed I/O (VT-d) and AMD I/O Virtualization (AMD-Vi or IOMMU), is enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#vvtd_enabled DataVsphereVirtualMachine#vvtd_enabled}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(vapp, dict):
            vapp = DataVsphereVirtualMachineVapp(**vapp)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00ea257fbad5c9c6813a6d4203d5b0417512fca66567ded2e275fdb8ac569659)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument alternate_guest_name", value=alternate_guest_name, expected_type=type_hints["alternate_guest_name"])
            check_type(argname="argument annotation", value=annotation, expected_type=type_hints["annotation"])
            check_type(argname="argument boot_delay", value=boot_delay, expected_type=type_hints["boot_delay"])
            check_type(argname="argument boot_retry_delay", value=boot_retry_delay, expected_type=type_hints["boot_retry_delay"])
            check_type(argname="argument boot_retry_enabled", value=boot_retry_enabled, expected_type=type_hints["boot_retry_enabled"])
            check_type(argname="argument cpu_hot_add_enabled", value=cpu_hot_add_enabled, expected_type=type_hints["cpu_hot_add_enabled"])
            check_type(argname="argument cpu_hot_remove_enabled", value=cpu_hot_remove_enabled, expected_type=type_hints["cpu_hot_remove_enabled"])
            check_type(argname="argument cpu_limit", value=cpu_limit, expected_type=type_hints["cpu_limit"])
            check_type(argname="argument cpu_performance_counters_enabled", value=cpu_performance_counters_enabled, expected_type=type_hints["cpu_performance_counters_enabled"])
            check_type(argname="argument cpu_reservation", value=cpu_reservation, expected_type=type_hints["cpu_reservation"])
            check_type(argname="argument cpu_share_count", value=cpu_share_count, expected_type=type_hints["cpu_share_count"])
            check_type(argname="argument cpu_share_level", value=cpu_share_level, expected_type=type_hints["cpu_share_level"])
            check_type(argname="argument datacenter_id", value=datacenter_id, expected_type=type_hints["datacenter_id"])
            check_type(argname="argument efi_secure_boot_enabled", value=efi_secure_boot_enabled, expected_type=type_hints["efi_secure_boot_enabled"])
            check_type(argname="argument enable_disk_uuid", value=enable_disk_uuid, expected_type=type_hints["enable_disk_uuid"])
            check_type(argname="argument enable_logging", value=enable_logging, expected_type=type_hints["enable_logging"])
            check_type(argname="argument ept_rvi_mode", value=ept_rvi_mode, expected_type=type_hints["ept_rvi_mode"])
            check_type(argname="argument extra_config", value=extra_config, expected_type=type_hints["extra_config"])
            check_type(argname="argument extra_config_reboot_required", value=extra_config_reboot_required, expected_type=type_hints["extra_config_reboot_required"])
            check_type(argname="argument firmware", value=firmware, expected_type=type_hints["firmware"])
            check_type(argname="argument folder", value=folder, expected_type=type_hints["folder"])
            check_type(argname="argument guest_id", value=guest_id, expected_type=type_hints["guest_id"])
            check_type(argname="argument hardware_version", value=hardware_version, expected_type=type_hints["hardware_version"])
            check_type(argname="argument hv_mode", value=hv_mode, expected_type=type_hints["hv_mode"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument ide_controller_scan_count", value=ide_controller_scan_count, expected_type=type_hints["ide_controller_scan_count"])
            check_type(argname="argument latency_sensitivity", value=latency_sensitivity, expected_type=type_hints["latency_sensitivity"])
            check_type(argname="argument memory", value=memory, expected_type=type_hints["memory"])
            check_type(argname="argument memory_hot_add_enabled", value=memory_hot_add_enabled, expected_type=type_hints["memory_hot_add_enabled"])
            check_type(argname="argument memory_limit", value=memory_limit, expected_type=type_hints["memory_limit"])
            check_type(argname="argument memory_reservation", value=memory_reservation, expected_type=type_hints["memory_reservation"])
            check_type(argname="argument memory_reservation_locked_to_max", value=memory_reservation_locked_to_max, expected_type=type_hints["memory_reservation_locked_to_max"])
            check_type(argname="argument memory_share_count", value=memory_share_count, expected_type=type_hints["memory_share_count"])
            check_type(argname="argument memory_share_level", value=memory_share_level, expected_type=type_hints["memory_share_level"])
            check_type(argname="argument moid", value=moid, expected_type=type_hints["moid"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument nested_hv_enabled", value=nested_hv_enabled, expected_type=type_hints["nested_hv_enabled"])
            check_type(argname="argument num_cores_per_socket", value=num_cores_per_socket, expected_type=type_hints["num_cores_per_socket"])
            check_type(argname="argument num_cpus", value=num_cpus, expected_type=type_hints["num_cpus"])
            check_type(argname="argument nvme_controller_scan_count", value=nvme_controller_scan_count, expected_type=type_hints["nvme_controller_scan_count"])
            check_type(argname="argument replace_trigger", value=replace_trigger, expected_type=type_hints["replace_trigger"])
            check_type(argname="argument run_tools_scripts_after_power_on", value=run_tools_scripts_after_power_on, expected_type=type_hints["run_tools_scripts_after_power_on"])
            check_type(argname="argument run_tools_scripts_after_resume", value=run_tools_scripts_after_resume, expected_type=type_hints["run_tools_scripts_after_resume"])
            check_type(argname="argument run_tools_scripts_before_guest_reboot", value=run_tools_scripts_before_guest_reboot, expected_type=type_hints["run_tools_scripts_before_guest_reboot"])
            check_type(argname="argument run_tools_scripts_before_guest_shutdown", value=run_tools_scripts_before_guest_shutdown, expected_type=type_hints["run_tools_scripts_before_guest_shutdown"])
            check_type(argname="argument run_tools_scripts_before_guest_standby", value=run_tools_scripts_before_guest_standby, expected_type=type_hints["run_tools_scripts_before_guest_standby"])
            check_type(argname="argument sata_controller_scan_count", value=sata_controller_scan_count, expected_type=type_hints["sata_controller_scan_count"])
            check_type(argname="argument scsi_controller_scan_count", value=scsi_controller_scan_count, expected_type=type_hints["scsi_controller_scan_count"])
            check_type(argname="argument storage_policy_id", value=storage_policy_id, expected_type=type_hints["storage_policy_id"])
            check_type(argname="argument swap_placement_policy", value=swap_placement_policy, expected_type=type_hints["swap_placement_policy"])
            check_type(argname="argument sync_time_with_host", value=sync_time_with_host, expected_type=type_hints["sync_time_with_host"])
            check_type(argname="argument sync_time_with_host_periodically", value=sync_time_with_host_periodically, expected_type=type_hints["sync_time_with_host_periodically"])
            check_type(argname="argument tools_upgrade_policy", value=tools_upgrade_policy, expected_type=type_hints["tools_upgrade_policy"])
            check_type(argname="argument uuid", value=uuid, expected_type=type_hints["uuid"])
            check_type(argname="argument vapp", value=vapp, expected_type=type_hints["vapp"])
            check_type(argname="argument vbs_enabled", value=vbs_enabled, expected_type=type_hints["vbs_enabled"])
            check_type(argname="argument vvtd_enabled", value=vvtd_enabled, expected_type=type_hints["vvtd_enabled"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
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
        if datacenter_id is not None:
            self._values["datacenter_id"] = datacenter_id
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
        if guest_id is not None:
            self._values["guest_id"] = guest_id
        if hardware_version is not None:
            self._values["hardware_version"] = hardware_version
        if hv_mode is not None:
            self._values["hv_mode"] = hv_mode
        if id is not None:
            self._values["id"] = id
        if ide_controller_scan_count is not None:
            self._values["ide_controller_scan_count"] = ide_controller_scan_count
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
        if moid is not None:
            self._values["moid"] = moid
        if name is not None:
            self._values["name"] = name
        if nested_hv_enabled is not None:
            self._values["nested_hv_enabled"] = nested_hv_enabled
        if num_cores_per_socket is not None:
            self._values["num_cores_per_socket"] = num_cores_per_socket
        if num_cpus is not None:
            self._values["num_cpus"] = num_cpus
        if nvme_controller_scan_count is not None:
            self._values["nvme_controller_scan_count"] = nvme_controller_scan_count
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
        if sata_controller_scan_count is not None:
            self._values["sata_controller_scan_count"] = sata_controller_scan_count
        if scsi_controller_scan_count is not None:
            self._values["scsi_controller_scan_count"] = scsi_controller_scan_count
        if storage_policy_id is not None:
            self._values["storage_policy_id"] = storage_policy_id
        if swap_placement_policy is not None:
            self._values["swap_placement_policy"] = swap_placement_policy
        if sync_time_with_host is not None:
            self._values["sync_time_with_host"] = sync_time_with_host
        if sync_time_with_host_periodically is not None:
            self._values["sync_time_with_host_periodically"] = sync_time_with_host_periodically
        if tools_upgrade_policy is not None:
            self._values["tools_upgrade_policy"] = tools_upgrade_policy
        if uuid is not None:
            self._values["uuid"] = uuid
        if vapp is not None:
            self._values["vapp"] = vapp
        if vbs_enabled is not None:
            self._values["vbs_enabled"] = vbs_enabled
        if vvtd_enabled is not None:
            self._values["vvtd_enabled"] = vvtd_enabled

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
    def alternate_guest_name(self) -> typing.Optional[builtins.str]:
        '''The guest name for the operating system when guest_id is otherGuest or otherGuest64.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#alternate_guest_name DataVsphereVirtualMachine#alternate_guest_name}
        '''
        result = self._values.get("alternate_guest_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def annotation(self) -> typing.Optional[builtins.str]:
        '''User-provided description of the virtual machine.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#annotation DataVsphereVirtualMachine#annotation}
        '''
        result = self._values.get("annotation")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def boot_delay(self) -> typing.Optional[jsii.Number]:
        '''The number of milliseconds to wait before starting the boot sequence.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#boot_delay DataVsphereVirtualMachine#boot_delay}
        '''
        result = self._values.get("boot_delay")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def boot_retry_delay(self) -> typing.Optional[jsii.Number]:
        '''The number of milliseconds to wait before retrying the boot sequence. This only valid if boot_retry_enabled is true.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#boot_retry_delay DataVsphereVirtualMachine#boot_retry_delay}
        '''
        result = self._values.get("boot_retry_delay")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def boot_retry_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If set to true, a virtual machine that fails to boot will try again after the delay defined in boot_retry_delay.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#boot_retry_enabled DataVsphereVirtualMachine#boot_retry_enabled}
        '''
        result = self._values.get("boot_retry_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def cpu_hot_add_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Allow CPUs to be added to this virtual machine while it is running.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#cpu_hot_add_enabled DataVsphereVirtualMachine#cpu_hot_add_enabled}
        '''
        result = self._values.get("cpu_hot_add_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def cpu_hot_remove_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Allow CPUs to be added to this virtual machine while it is running.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#cpu_hot_remove_enabled DataVsphereVirtualMachine#cpu_hot_remove_enabled}
        '''
        result = self._values.get("cpu_hot_remove_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def cpu_limit(self) -> typing.Optional[jsii.Number]:
        '''The maximum amount of memory (in MB) or CPU (in MHz) that this virtual machine can consume, regardless of available resources.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#cpu_limit DataVsphereVirtualMachine#cpu_limit}
        '''
        result = self._values.get("cpu_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def cpu_performance_counters_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable CPU performance counters on this virtual machine.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#cpu_performance_counters_enabled DataVsphereVirtualMachine#cpu_performance_counters_enabled}
        '''
        result = self._values.get("cpu_performance_counters_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def cpu_reservation(self) -> typing.Optional[jsii.Number]:
        '''The amount of memory (in MB) or CPU (in MHz) that this virtual machine is guaranteed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#cpu_reservation DataVsphereVirtualMachine#cpu_reservation}
        '''
        result = self._values.get("cpu_reservation")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def cpu_share_count(self) -> typing.Optional[jsii.Number]:
        '''The amount of shares to allocate to cpu for a custom share level.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#cpu_share_count DataVsphereVirtualMachine#cpu_share_count}
        '''
        result = self._values.get("cpu_share_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def cpu_share_level(self) -> typing.Optional[builtins.str]:
        '''The allocation level for cpu resources. Can be one of high, low, normal, or custom.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#cpu_share_level DataVsphereVirtualMachine#cpu_share_level}
        '''
        result = self._values.get("cpu_share_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def datacenter_id(self) -> typing.Optional[builtins.str]:
        '''The managed object ID of the datacenter the virtual machine is in.

        This is not required when using ESXi directly, or if there is only one datacenter in your infrastructure.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#datacenter_id DataVsphereVirtualMachine#datacenter_id}
        '''
        result = self._values.get("datacenter_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def efi_secure_boot_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''When the boot type set in firmware is efi, this enables EFI secure boot.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#efi_secure_boot_enabled DataVsphereVirtualMachine#efi_secure_boot_enabled}
        '''
        result = self._values.get("efi_secure_boot_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def enable_disk_uuid(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Expose the UUIDs of attached virtual disks to the virtual machine, allowing access to them in the guest.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#enable_disk_uuid DataVsphereVirtualMachine#enable_disk_uuid}
        '''
        result = self._values.get("enable_disk_uuid")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def enable_logging(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable logging on this virtual machine.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#enable_logging DataVsphereVirtualMachine#enable_logging}
        '''
        result = self._values.get("enable_logging")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def ept_rvi_mode(self) -> typing.Optional[builtins.str]:
        '''The EPT/RVI (hardware memory virtualization) setting for this virtual machine. Can be one of automatic, on, or off.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#ept_rvi_mode DataVsphereVirtualMachine#ept_rvi_mode}
        '''
        result = self._values.get("ept_rvi_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def extra_config(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Extra configuration data for this virtual machine.

        Can be used to supply advanced parameters not normally in configuration, such as instance metadata, or configuration data for OVF images.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#extra_config DataVsphereVirtualMachine#extra_config}
        '''
        result = self._values.get("extra_config")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def extra_config_reboot_required(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Allow the virtual machine to be rebooted when a change to ``extra_config`` occurs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#extra_config_reboot_required DataVsphereVirtualMachine#extra_config_reboot_required}
        '''
        result = self._values.get("extra_config_reboot_required")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def firmware(self) -> typing.Optional[builtins.str]:
        '''The firmware interface to use on the virtual machine. Can be one of bios or efi.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#firmware DataVsphereVirtualMachine#firmware}
        '''
        result = self._values.get("firmware")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def folder(self) -> typing.Optional[builtins.str]:
        '''The name of the folder the virtual machine is in.

        Allows distinguishing virtual machines with the same name in different folder paths

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#folder DataVsphereVirtualMachine#folder}
        '''
        result = self._values.get("folder")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def guest_id(self) -> typing.Optional[builtins.str]:
        '''The guest ID for the operating system.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#guest_id DataVsphereVirtualMachine#guest_id}
        '''
        result = self._values.get("guest_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def hardware_version(self) -> typing.Optional[jsii.Number]:
        '''The hardware version for the virtual machine.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#hardware_version DataVsphereVirtualMachine#hardware_version}
        '''
        result = self._values.get("hardware_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def hv_mode(self) -> typing.Optional[builtins.str]:
        '''The (non-nested) hardware virtualization setting for this virtual machine. Can be one of hvAuto, hvOn, or hvOff.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#hv_mode DataVsphereVirtualMachine#hv_mode}
        '''
        result = self._values.get("hv_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#id DataVsphereVirtualMachine#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ide_controller_scan_count(self) -> typing.Optional[jsii.Number]:
        '''The number of IDE controllers to scan for disk sizes and controller types on.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#ide_controller_scan_count DataVsphereVirtualMachine#ide_controller_scan_count}
        '''
        result = self._values.get("ide_controller_scan_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def latency_sensitivity(self) -> typing.Optional[builtins.str]:
        '''Controls the scheduling delay of the virtual machine.

        Use a higher sensitivity for applications that require lower latency, such as VOIP, media player applications, or applications that require frequent access to mouse or keyboard devices. Can be one of low, normal, medium, or high.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#latency_sensitivity DataVsphereVirtualMachine#latency_sensitivity}
        '''
        result = self._values.get("latency_sensitivity")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def memory(self) -> typing.Optional[jsii.Number]:
        '''The size of the virtual machine's memory, in MB.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#memory DataVsphereVirtualMachine#memory}
        '''
        result = self._values.get("memory")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def memory_hot_add_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Allow memory to be added to this virtual machine while it is running.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#memory_hot_add_enabled DataVsphereVirtualMachine#memory_hot_add_enabled}
        '''
        result = self._values.get("memory_hot_add_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def memory_limit(self) -> typing.Optional[jsii.Number]:
        '''The maximum amount of memory (in MB) or CPU (in MHz) that this virtual machine can consume, regardless of available resources.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#memory_limit DataVsphereVirtualMachine#memory_limit}
        '''
        result = self._values.get("memory_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def memory_reservation(self) -> typing.Optional[jsii.Number]:
        '''The amount of memory (in MB) or CPU (in MHz) that this virtual machine is guaranteed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#memory_reservation DataVsphereVirtualMachine#memory_reservation}
        '''
        result = self._values.get("memory_reservation")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def memory_reservation_locked_to_max(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If set true, memory resource reservation for this virtual machine will always be equal to the virtual machine's memory size;increases in memory size will be rejected when a corresponding reservation increase is not possible. This feature may only be enabled if it is currently possible to reserve all of the virtual machine's memory.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#memory_reservation_locked_to_max DataVsphereVirtualMachine#memory_reservation_locked_to_max}
        '''
        result = self._values.get("memory_reservation_locked_to_max")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def memory_share_count(self) -> typing.Optional[jsii.Number]:
        '''The amount of shares to allocate to memory for a custom share level.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#memory_share_count DataVsphereVirtualMachine#memory_share_count}
        '''
        result = self._values.get("memory_share_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def memory_share_level(self) -> typing.Optional[builtins.str]:
        '''The allocation level for memory resources. Can be one of high, low, normal, or custom.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#memory_share_level DataVsphereVirtualMachine#memory_share_level}
        '''
        result = self._values.get("memory_share_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def moid(self) -> typing.Optional[builtins.str]:
        '''The machine object ID from VMware vSphere.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#moid DataVsphereVirtualMachine#moid}
        '''
        result = self._values.get("moid")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of this virtual machine.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#name DataVsphereVirtualMachine#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def nested_hv_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable nested hardware virtualization on this virtual machine, facilitating nested virtualization in the guest.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#nested_hv_enabled DataVsphereVirtualMachine#nested_hv_enabled}
        '''
        result = self._values.get("nested_hv_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def num_cores_per_socket(self) -> typing.Optional[jsii.Number]:
        '''The number of cores to distribute amongst the CPUs in this virtual machine.

        If specified, the value supplied to num_cpus must be evenly divisible by this value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#num_cores_per_socket DataVsphereVirtualMachine#num_cores_per_socket}
        '''
        result = self._values.get("num_cores_per_socket")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def num_cpus(self) -> typing.Optional[jsii.Number]:
        '''The number of virtual processors to assign to this virtual machine.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#num_cpus DataVsphereVirtualMachine#num_cpus}
        '''
        result = self._values.get("num_cpus")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def nvme_controller_scan_count(self) -> typing.Optional[jsii.Number]:
        '''The number of NVMe controllers to scan for disk sizes and controller types on.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#nvme_controller_scan_count DataVsphereVirtualMachine#nvme_controller_scan_count}
        '''
        result = self._values.get("nvme_controller_scan_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def replace_trigger(self) -> typing.Optional[builtins.str]:
        '''Triggers replacement of resource whenever it changes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#replace_trigger DataVsphereVirtualMachine#replace_trigger}
        '''
        result = self._values.get("replace_trigger")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def run_tools_scripts_after_power_on(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable the run of scripts after virtual machine power-on when VMware Tools is installed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#run_tools_scripts_after_power_on DataVsphereVirtualMachine#run_tools_scripts_after_power_on}
        '''
        result = self._values.get("run_tools_scripts_after_power_on")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def run_tools_scripts_after_resume(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable the run of scripts after virtual machine resume when when VMware Tools is installed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#run_tools_scripts_after_resume DataVsphereVirtualMachine#run_tools_scripts_after_resume}
        '''
        result = self._values.get("run_tools_scripts_after_resume")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def run_tools_scripts_before_guest_reboot(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable the run of scripts before guest operating system reboot when VMware Tools is installed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#run_tools_scripts_before_guest_reboot DataVsphereVirtualMachine#run_tools_scripts_before_guest_reboot}
        '''
        result = self._values.get("run_tools_scripts_before_guest_reboot")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def run_tools_scripts_before_guest_shutdown(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable the run of scripts before guest operating system shutdown when VMware Tools is installed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#run_tools_scripts_before_guest_shutdown DataVsphereVirtualMachine#run_tools_scripts_before_guest_shutdown}
        '''
        result = self._values.get("run_tools_scripts_before_guest_shutdown")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def run_tools_scripts_before_guest_standby(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable the run of scripts before guest operating system standby when VMware Tools is installed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#run_tools_scripts_before_guest_standby DataVsphereVirtualMachine#run_tools_scripts_before_guest_standby}
        '''
        result = self._values.get("run_tools_scripts_before_guest_standby")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def sata_controller_scan_count(self) -> typing.Optional[jsii.Number]:
        '''The number of SATA controllers to scan for disk sizes and controller types on.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#sata_controller_scan_count DataVsphereVirtualMachine#sata_controller_scan_count}
        '''
        result = self._values.get("sata_controller_scan_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def scsi_controller_scan_count(self) -> typing.Optional[jsii.Number]:
        '''The number of SCSI controllers to scan for disk sizes and controller types on.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#scsi_controller_scan_count DataVsphereVirtualMachine#scsi_controller_scan_count}
        '''
        result = self._values.get("scsi_controller_scan_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def storage_policy_id(self) -> typing.Optional[builtins.str]:
        '''The ID of the storage policy to assign to the virtual machine home directory.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#storage_policy_id DataVsphereVirtualMachine#storage_policy_id}
        '''
        result = self._values.get("storage_policy_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def swap_placement_policy(self) -> typing.Optional[builtins.str]:
        '''The swap file placement policy for this virtual machine. Can be one of inherit, hostLocal, or vmDirectory.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#swap_placement_policy DataVsphereVirtualMachine#swap_placement_policy}
        '''
        result = self._values.get("swap_placement_policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sync_time_with_host(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable guest clock synchronization with the host.

        On vSphere 7.0 U1 and above, with only this setting the clock is synchronized on startup and resume. Requires VMware Tools to be installed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#sync_time_with_host DataVsphereVirtualMachine#sync_time_with_host}
        '''
        result = self._values.get("sync_time_with_host")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def sync_time_with_host_periodically(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable periodic clock synchronization with the host.

        Supported only on vSphere 7.0 U1 and above. On prior versions setting ``sync_time_with_host`` is enough for periodic synchronization. Requires VMware Tools to be installed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#sync_time_with_host_periodically DataVsphereVirtualMachine#sync_time_with_host_periodically}
        '''
        result = self._values.get("sync_time_with_host_periodically")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tools_upgrade_policy(self) -> typing.Optional[builtins.str]:
        '''Set the upgrade policy for VMware Tools. Can be one of ``manual`` or ``upgradeAtPowerCycle``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#tools_upgrade_policy DataVsphereVirtualMachine#tools_upgrade_policy}
        '''
        result = self._values.get("tools_upgrade_policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def uuid(self) -> typing.Optional[builtins.str]:
        '''The UUID of the virtual machine. Also exposed as the ID of the resource.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#uuid DataVsphereVirtualMachine#uuid}
        '''
        result = self._values.get("uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vapp(self) -> typing.Optional["DataVsphereVirtualMachineVapp"]:
        '''vapp block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#vapp DataVsphereVirtualMachine#vapp}
        '''
        result = self._values.get("vapp")
        return typing.cast(typing.Optional["DataVsphereVirtualMachineVapp"], result)

    @builtins.property
    def vbs_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Flag to specify if Virtualization-based security is enabled for this virtual machine.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#vbs_enabled DataVsphereVirtualMachine#vbs_enabled}
        '''
        result = self._values.get("vbs_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def vvtd_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Flag to specify if I/O MMU virtualization, also called Intel Virtualization Technology for Directed I/O (VT-d) and AMD I/O Virtualization (AMD-Vi or IOMMU), is enabled.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#vvtd_enabled DataVsphereVirtualMachine#vvtd_enabled}
        '''
        result = self._values.get("vvtd_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataVsphereVirtualMachineConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.dataVsphereVirtualMachine.DataVsphereVirtualMachineDisks",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataVsphereVirtualMachineDisks:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataVsphereVirtualMachineDisks(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataVsphereVirtualMachineDisksList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.dataVsphereVirtualMachine.DataVsphereVirtualMachineDisksList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e60f8e6b86730f08e3f94072abc0092d6d36ae52217089c32aa59e3781e23684)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataVsphereVirtualMachineDisksOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3bd2030195e686027d1ed6830fca7a16c2bb21890d43e65ad0d198a35ab3e3a6)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataVsphereVirtualMachineDisksOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77aab0ed759f0636ee3bb9393796eae4ef4d9136c992d6aa9a9d89095b58bef5)
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
            type_hints = typing.get_type_hints(_typecheckingstub__226e8f7b4c572cb856432c0ff1079e5b20d81825f73a234c2fb85302b9458634)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8cc56f678d0f2037da14d763004999833cfabfa22bb1227904fa29a3c41d20da)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataVsphereVirtualMachineDisksOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.dataVsphereVirtualMachine.DataVsphereVirtualMachineDisksOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7d36c399f9842bf2e4ae05a591357c5e0948c2cdaf48d4d5ca789baaa4436469)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="eagerlyScrub")
    def eagerly_scrub(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "eagerlyScrub"))

    @builtins.property
    @jsii.member(jsii_name="label")
    def label(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "label"))

    @builtins.property
    @jsii.member(jsii_name="size")
    def size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "size"))

    @builtins.property
    @jsii.member(jsii_name="thinProvisioned")
    def thin_provisioned(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "thinProvisioned"))

    @builtins.property
    @jsii.member(jsii_name="unitNumber")
    def unit_number(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "unitNumber"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataVsphereVirtualMachineDisks]:
        return typing.cast(typing.Optional[DataVsphereVirtualMachineDisks], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataVsphereVirtualMachineDisks],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e2599b70555ea0ada3fcfd83f142931c63531eacb14c54f6bbbf3fa2cf075ca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.dataVsphereVirtualMachine.DataVsphereVirtualMachineNetworkInterfaces",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataVsphereVirtualMachineNetworkInterfaces:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataVsphereVirtualMachineNetworkInterfaces(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataVsphereVirtualMachineNetworkInterfacesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.dataVsphereVirtualMachine.DataVsphereVirtualMachineNetworkInterfacesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b4bd8e7ecb83dc8b4b4a13bc7dcffdf13a577501978b2ce72c0a9921ceeffb22)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataVsphereVirtualMachineNetworkInterfacesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88f7b81d899eac96469efca68cd925c2ce32a7c17ded9aa8d8ac253fcbb34816)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataVsphereVirtualMachineNetworkInterfacesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce828cbaa732fdff9487f353f495e3c535a499554764b199679315cabd40e314)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f14c6f03a82335e5cdd4415ac1576aeebff370b5b07b5354077907a06d80d3c1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__98e5c414be38eee9a13fbdf7e4cab27522739d486165e1e3cb851d696d2097bb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataVsphereVirtualMachineNetworkInterfacesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.dataVsphereVirtualMachine.DataVsphereVirtualMachineNetworkInterfacesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__20591ccdbef168727f1a1442466a42898e7b9b3b32691834baeae30f66fe3b0f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="adapterType")
    def adapter_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "adapterType"))

    @builtins.property
    @jsii.member(jsii_name="bandwidthLimit")
    def bandwidth_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "bandwidthLimit"))

    @builtins.property
    @jsii.member(jsii_name="bandwidthReservation")
    def bandwidth_reservation(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "bandwidthReservation"))

    @builtins.property
    @jsii.member(jsii_name="bandwidthShareCount")
    def bandwidth_share_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "bandwidthShareCount"))

    @builtins.property
    @jsii.member(jsii_name="bandwidthShareLevel")
    def bandwidth_share_level(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bandwidthShareLevel"))

    @builtins.property
    @jsii.member(jsii_name="macAddress")
    def mac_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "macAddress"))

    @builtins.property
    @jsii.member(jsii_name="networkId")
    def network_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "networkId"))

    @builtins.property
    @jsii.member(jsii_name="physicalFunction")
    def physical_function(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "physicalFunction"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataVsphereVirtualMachineNetworkInterfaces]:
        return typing.cast(typing.Optional[DataVsphereVirtualMachineNetworkInterfaces], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataVsphereVirtualMachineNetworkInterfaces],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc7316154ba3151ae273e62a6c7849e1b4c91fc83657ec801d3dc603fd31cd24)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.dataVsphereVirtualMachine.DataVsphereVirtualMachineVapp",
    jsii_struct_bases=[],
    name_mapping={"properties": "properties"},
)
class DataVsphereVirtualMachineVapp:
    def __init__(
        self,
        *,
        properties: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param properties: A map of customizable vApp properties and their values. Allows customization of VMs cloned from OVF templates which have customizable vApp properties. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#properties DataVsphereVirtualMachine#properties}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c204cea8267005496fb48c644fa64689b984cb27ec09a0387a22847345e0f969)
            check_type(argname="argument properties", value=properties, expected_type=type_hints["properties"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if properties is not None:
            self._values["properties"] = properties

    @builtins.property
    def properties(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''A map of customizable vApp properties and their values.

        Allows customization of VMs cloned from OVF templates which have customizable vApp properties.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/virtual_machine#properties DataVsphereVirtualMachine#properties}
        '''
        result = self._values.get("properties")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataVsphereVirtualMachineVapp(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataVsphereVirtualMachineVappOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.dataVsphereVirtualMachine.DataVsphereVirtualMachineVappOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__588cdd4004a07ca43caf4d8fbb15b617a89f364831283fbc290930afdd32b44a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9de43249edcf71dbc85589fee3e00eb947c107e51453e383d7ed086f78c6a03c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "properties", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataVsphereVirtualMachineVapp]:
        return typing.cast(typing.Optional[DataVsphereVirtualMachineVapp], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataVsphereVirtualMachineVapp],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d55f22666201a1f49f35a774991f3abf8fc045fd2c178c8071037547dd613d95)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataVsphereVirtualMachine",
    "DataVsphereVirtualMachineConfig",
    "DataVsphereVirtualMachineDisks",
    "DataVsphereVirtualMachineDisksList",
    "DataVsphereVirtualMachineDisksOutputReference",
    "DataVsphereVirtualMachineNetworkInterfaces",
    "DataVsphereVirtualMachineNetworkInterfacesList",
    "DataVsphereVirtualMachineNetworkInterfacesOutputReference",
    "DataVsphereVirtualMachineVapp",
    "DataVsphereVirtualMachineVappOutputReference",
]

publication.publish()

def _typecheckingstub__978298f7fae272848b5f269f8795b8e50d5a329a8f95e14784b987259b26e0f0(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    alternate_guest_name: typing.Optional[builtins.str] = None,
    annotation: typing.Optional[builtins.str] = None,
    boot_delay: typing.Optional[jsii.Number] = None,
    boot_retry_delay: typing.Optional[jsii.Number] = None,
    boot_retry_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    cpu_hot_add_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    cpu_hot_remove_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    cpu_limit: typing.Optional[jsii.Number] = None,
    cpu_performance_counters_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    cpu_reservation: typing.Optional[jsii.Number] = None,
    cpu_share_count: typing.Optional[jsii.Number] = None,
    cpu_share_level: typing.Optional[builtins.str] = None,
    datacenter_id: typing.Optional[builtins.str] = None,
    efi_secure_boot_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enable_disk_uuid: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enable_logging: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ept_rvi_mode: typing.Optional[builtins.str] = None,
    extra_config: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    extra_config_reboot_required: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    firmware: typing.Optional[builtins.str] = None,
    folder: typing.Optional[builtins.str] = None,
    guest_id: typing.Optional[builtins.str] = None,
    hardware_version: typing.Optional[jsii.Number] = None,
    hv_mode: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    ide_controller_scan_count: typing.Optional[jsii.Number] = None,
    latency_sensitivity: typing.Optional[builtins.str] = None,
    memory: typing.Optional[jsii.Number] = None,
    memory_hot_add_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    memory_limit: typing.Optional[jsii.Number] = None,
    memory_reservation: typing.Optional[jsii.Number] = None,
    memory_reservation_locked_to_max: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    memory_share_count: typing.Optional[jsii.Number] = None,
    memory_share_level: typing.Optional[builtins.str] = None,
    moid: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    nested_hv_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    num_cores_per_socket: typing.Optional[jsii.Number] = None,
    num_cpus: typing.Optional[jsii.Number] = None,
    nvme_controller_scan_count: typing.Optional[jsii.Number] = None,
    replace_trigger: typing.Optional[builtins.str] = None,
    run_tools_scripts_after_power_on: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    run_tools_scripts_after_resume: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    run_tools_scripts_before_guest_reboot: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    run_tools_scripts_before_guest_shutdown: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    run_tools_scripts_before_guest_standby: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    sata_controller_scan_count: typing.Optional[jsii.Number] = None,
    scsi_controller_scan_count: typing.Optional[jsii.Number] = None,
    storage_policy_id: typing.Optional[builtins.str] = None,
    swap_placement_policy: typing.Optional[builtins.str] = None,
    sync_time_with_host: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    sync_time_with_host_periodically: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tools_upgrade_policy: typing.Optional[builtins.str] = None,
    uuid: typing.Optional[builtins.str] = None,
    vapp: typing.Optional[typing.Union[DataVsphereVirtualMachineVapp, typing.Dict[builtins.str, typing.Any]]] = None,
    vbs_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    vvtd_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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

def _typecheckingstub__7fbc3b693f3e193744eeb2752b1b46b1c1924866be1f72ea4c6afae9adc206d3(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf2f4fa4dc2f8a6ebdc38033481c377c4d49c7b738e3bd350715af95c005de37(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3587957eb912202924ef765b2af3220fb6c7658c9f304082b10bdb1cfc2557dc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf72a91d0ac08dffe362782eb805c3d5f78905040276370cdb99c1dfdfee6510(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__537aeb9bd18a7723f7399f576c85d1074d5b4a9ec9f00c2562372c0cf6c71386(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61304d30488e473466fc45d9a383f290c1526abc6470dd0564f534be964165f6(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc565ed7548974f3ffd2839046b0b0061df681a6ab17ffe4e27e9c3a743dabbb(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__415fc03b410a979a7b0780b109792c89633c8f27ffb9eef6db64f7fb0b751b98(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e01cb8fc390679c31be9b7f516028923215eb4e06c9b2fdac91fe75fff932f6(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__785c82bc9ab2fa6e7f09395661c35220e1f8e563369f07221a4699f878012257(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d62bf9df144e6e2585b81d3d057e329899d33f7f0189a256f01aa9e4f375f899(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fecbbf59f9c959c9fc463498c2a486354787af9a268d280cf19a7be3bfae703a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69a912bdbf5f93f291ba3555a82b301093197043ed6ba0b6ee9a4ffde8cbfc27(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1444e3fb2f6c126a2efe41f081cbe7255174148010ea3e97620f008482cadee7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__463f6b52c7d3845511e4c59c938e0fa005516aff0bebebdef83d174f0fab2a9e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48a3ab61fc12862cf093537fe5344f0a0eb241caafe9b563ac5bdf31593bde71(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80b12c9a443f0e0caef3fa32fc6379511c4691363b26fbd3bc8c553f8d72661c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dde764e33924692ea2aa4c039d9817770651c978e8f4f3d66772eec700c5f0f3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60c1f8b11fed5b235308e313a1265908ee85313af3471d1973d82995ec0fdd41(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__626286b21383205f6da12bed6ab55027b965f33d456ca8e659d1ebe024cc3c04(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83b0ab45cca74ccbc6b14856fdb26591ea1780c6319bbbe3c2dabab7b00c9f1d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__affe2f34a7ab1364fab11cdadb0a693a0521a409b15ade69ed4e5ab3935fb656(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__013dd63dce824c2642ae443028bb309152eba7faec5217b690dec671d63ec9bd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b803466a13111ebb454d3478bd1110abdbf27a4abd8f9e2b6d8c9234a59c8897(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e4970964f67002160eab44a8370f88ed35d92f7d353e6bfb902d7392b2f8943(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26ecba812036e4448c8cd590c5f7f54098d5cac3644865e7f4d420a3b2a631c5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64477ac96403faa22578af3707663f54d6f3398e97286ed40a415a199e4a396b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5913855c1d8ff85fc0c8f4cb4fb5e1707f798a2dd983b714e2337b48bea892d7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4efa7e3539f976965a5d01f743c784ad3089985043d37ef22b0d8ecd807a933(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a03c8e3e730949f7240cb4e5c2c4d9501ab72794631ffe98cb1da185bf172317(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69eeececbb891a5932133739246ce1b570d637148019d2bfcb36563e6cd5862c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6fa2212f7ba970ed5a23471cdccf5b1e6833bdb886ae540fef066ec099bc6c55(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44acd152678104726506109772adff3c1dd31c595932578b8121cdf9259beb71(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81c7e99ff05a38d6396c60fe08280fa94f90b53832d697ab5414c6f96b3808a3(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__954a078b5608bbf58c534c6d4f82dc7fdb3398117435c07f319d51d27016e3e4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__296e1344e5754f846203d862c287e40afba7ac871dce10ff9dd0942c2816623d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78cf48270f6ba82a52c672775e6a9291b3c8f1bc1899e219bb9a1f7ca13d5bca(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e34a9b953fcc66a38a29631a84684f6d78a17e21fd88961dbdfc1b0354c18d8e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2f5aa34ca61d73fae0bbd5a9911ce50b0ab8bb56afccab110a11db0ef826670(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__685d570c1c6a316403020d5c649f68fd0b040b85f0f24f9cd34e4bb8761c81c8(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__864525f6073687b015fa45959d0dd835618150f655a665bfc3ec14a1eefd4a63(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e243f005e9d734dee6eb99862ddfad863789db59531c171f4f1c4a74a84df04(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a55eba0e39e799fecf79bb8d782aeff791f2e53b9337b8806da0469e3e830a61(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5699470252834a4c9a26fd663a49d0332a77a0190c48d0237a2386d5e763bfc5(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05662863332c200d8312860ca82f5c1880a96114465f8cfdb9db395305d6dd25(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d9ab7b3458843430f5f6d1cc32d2726c6290774a6a5ab396dccf8029c9cdeff(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57de10a5c2a3eef0f89e332db158c5f6e4e24eb84c32f881c6e5bb82ec09bd2a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76b44e736be9e11525b67f21196d0748af67b312d84b7ad2a3c48bad781714da(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__629dd2ede7de48a0b5327ecea008ba32e076f13754523ca4aaf5475d53d149c2(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1783567549077e972e5da41ef16a3734da0f2ca9c85ebcf3ceff19e38ebd022(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e89952ddfa62290296776425879cce4cfd08957d00334c6f8a9a03c79fb0a33(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efb41f65dc5022f2b958b1ae49953ba0a68d0c32459b28b4aade1761c69e497b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d76cbe2a67b0b987ff54f118dc79ac908445eec61f2530869d8403ed95a724ba(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ee58baaff8d23216dd20c7f0ea3ec09383f98c7134b79d0ff861ec032d606c9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c61693c4c000e0e2ba4c45e71ae93f1bbc838dbac9752a5a45e10da7b50bb9f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7243fb9b60b1f3755fd67668d8a81d1c288290ef05a1e57c2e87e9c32358abb(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__615e8fc45be9ddcdd1f317b7dd0576f819f2cf0f387bfec4fc846d8d6b25083f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00ea257fbad5c9c6813a6d4203d5b0417512fca66567ded2e275fdb8ac569659(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    alternate_guest_name: typing.Optional[builtins.str] = None,
    annotation: typing.Optional[builtins.str] = None,
    boot_delay: typing.Optional[jsii.Number] = None,
    boot_retry_delay: typing.Optional[jsii.Number] = None,
    boot_retry_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    cpu_hot_add_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    cpu_hot_remove_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    cpu_limit: typing.Optional[jsii.Number] = None,
    cpu_performance_counters_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    cpu_reservation: typing.Optional[jsii.Number] = None,
    cpu_share_count: typing.Optional[jsii.Number] = None,
    cpu_share_level: typing.Optional[builtins.str] = None,
    datacenter_id: typing.Optional[builtins.str] = None,
    efi_secure_boot_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enable_disk_uuid: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enable_logging: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ept_rvi_mode: typing.Optional[builtins.str] = None,
    extra_config: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    extra_config_reboot_required: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    firmware: typing.Optional[builtins.str] = None,
    folder: typing.Optional[builtins.str] = None,
    guest_id: typing.Optional[builtins.str] = None,
    hardware_version: typing.Optional[jsii.Number] = None,
    hv_mode: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    ide_controller_scan_count: typing.Optional[jsii.Number] = None,
    latency_sensitivity: typing.Optional[builtins.str] = None,
    memory: typing.Optional[jsii.Number] = None,
    memory_hot_add_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    memory_limit: typing.Optional[jsii.Number] = None,
    memory_reservation: typing.Optional[jsii.Number] = None,
    memory_reservation_locked_to_max: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    memory_share_count: typing.Optional[jsii.Number] = None,
    memory_share_level: typing.Optional[builtins.str] = None,
    moid: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    nested_hv_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    num_cores_per_socket: typing.Optional[jsii.Number] = None,
    num_cpus: typing.Optional[jsii.Number] = None,
    nvme_controller_scan_count: typing.Optional[jsii.Number] = None,
    replace_trigger: typing.Optional[builtins.str] = None,
    run_tools_scripts_after_power_on: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    run_tools_scripts_after_resume: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    run_tools_scripts_before_guest_reboot: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    run_tools_scripts_before_guest_shutdown: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    run_tools_scripts_before_guest_standby: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    sata_controller_scan_count: typing.Optional[jsii.Number] = None,
    scsi_controller_scan_count: typing.Optional[jsii.Number] = None,
    storage_policy_id: typing.Optional[builtins.str] = None,
    swap_placement_policy: typing.Optional[builtins.str] = None,
    sync_time_with_host: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    sync_time_with_host_periodically: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tools_upgrade_policy: typing.Optional[builtins.str] = None,
    uuid: typing.Optional[builtins.str] = None,
    vapp: typing.Optional[typing.Union[DataVsphereVirtualMachineVapp, typing.Dict[builtins.str, typing.Any]]] = None,
    vbs_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    vvtd_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e60f8e6b86730f08e3f94072abc0092d6d36ae52217089c32aa59e3781e23684(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3bd2030195e686027d1ed6830fca7a16c2bb21890d43e65ad0d198a35ab3e3a6(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77aab0ed759f0636ee3bb9393796eae4ef4d9136c992d6aa9a9d89095b58bef5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__226e8f7b4c572cb856432c0ff1079e5b20d81825f73a234c2fb85302b9458634(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8cc56f678d0f2037da14d763004999833cfabfa22bb1227904fa29a3c41d20da(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d36c399f9842bf2e4ae05a591357c5e0948c2cdaf48d4d5ca789baaa4436469(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e2599b70555ea0ada3fcfd83f142931c63531eacb14c54f6bbbf3fa2cf075ca(
    value: typing.Optional[DataVsphereVirtualMachineDisks],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4bd8e7ecb83dc8b4b4a13bc7dcffdf13a577501978b2ce72c0a9921ceeffb22(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88f7b81d899eac96469efca68cd925c2ce32a7c17ded9aa8d8ac253fcbb34816(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce828cbaa732fdff9487f353f495e3c535a499554764b199679315cabd40e314(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f14c6f03a82335e5cdd4415ac1576aeebff370b5b07b5354077907a06d80d3c1(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98e5c414be38eee9a13fbdf7e4cab27522739d486165e1e3cb851d696d2097bb(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20591ccdbef168727f1a1442466a42898e7b9b3b32691834baeae30f66fe3b0f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc7316154ba3151ae273e62a6c7849e1b4c91fc83657ec801d3dc603fd31cd24(
    value: typing.Optional[DataVsphereVirtualMachineNetworkInterfaces],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c204cea8267005496fb48c644fa64689b984cb27ec09a0387a22847345e0f969(
    *,
    properties: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__588cdd4004a07ca43caf4d8fbb15b617a89f364831283fbc290930afdd32b44a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9de43249edcf71dbc85589fee3e00eb947c107e51453e383d7ed086f78c6a03c(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d55f22666201a1f49f35a774991f3abf8fc045fd2c178c8071037547dd613d95(
    value: typing.Optional[DataVsphereVirtualMachineVapp],
) -> None:
    """Type checking stubs"""
    pass
