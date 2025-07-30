r'''
# `data_vsphere_ovf_vm_template`

Refer to the Terraform Registry for docs: [`data_vsphere_ovf_vm_template`](https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template).
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


class DataVsphereOvfVmTemplate(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.dataVsphereOvfVmTemplate.DataVsphereOvfVmTemplate",
):
    '''Represents a {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template vsphere_ovf_vm_template}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        host_system_id: builtins.str,
        name: builtins.str,
        resource_pool_id: builtins.str,
        allow_unverified_ssl_cert: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        datastore_id: typing.Optional[builtins.str] = None,
        deployment_option: typing.Optional[builtins.str] = None,
        disk_provisioning: typing.Optional[builtins.str] = None,
        enable_hidden_properties: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        folder: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        ip_allocation_policy: typing.Optional[builtins.str] = None,
        ip_protocol: typing.Optional[builtins.str] = None,
        local_ovf_path: typing.Optional[builtins.str] = None,
        ovf_network_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        remote_ovf_url: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template vsphere_ovf_vm_template} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param host_system_id: The ID of an optional host system to pin the virtual machine to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template#host_system_id DataVsphereOvfVmTemplate#host_system_id}
        :param name: Name of the virtual machine to create. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template#name DataVsphereOvfVmTemplate#name}
        :param resource_pool_id: The ID of a resource pool to put the virtual machine in. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template#resource_pool_id DataVsphereOvfVmTemplate#resource_pool_id}
        :param allow_unverified_ssl_cert: Allow unverified ssl certificates while deploying ovf/ova from url. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template#allow_unverified_ssl_cert DataVsphereOvfVmTemplate#allow_unverified_ssl_cert}
        :param datastore_id: The ID of the virtual machine's datastore. The virtual machine configuration is placed here, along with any virtual disks that are created without datastores. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template#datastore_id DataVsphereOvfVmTemplate#datastore_id}
        :param deployment_option: The Deployment option to be chosen. If empty, the default option is used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template#deployment_option DataVsphereOvfVmTemplate#deployment_option}
        :param disk_provisioning: An optional disk provisioning. If set, all the disks in the deployed ovf will have the same specified disk type (e.g., thin provisioned). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template#disk_provisioning DataVsphereOvfVmTemplate#disk_provisioning}
        :param enable_hidden_properties: Allow properties with ovf:userConfigurable=false to be set. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template#enable_hidden_properties DataVsphereOvfVmTemplate#enable_hidden_properties}
        :param folder: The name of the folder to locate the virtual machine in. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template#folder DataVsphereOvfVmTemplate#folder}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template#id DataVsphereOvfVmTemplate#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param ip_allocation_policy: The IP allocation policy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template#ip_allocation_policy DataVsphereOvfVmTemplate#ip_allocation_policy}
        :param ip_protocol: The IP protocol. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template#ip_protocol DataVsphereOvfVmTemplate#ip_protocol}
        :param local_ovf_path: The absolute path to the ovf/ova file in the local system. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template#local_ovf_path DataVsphereOvfVmTemplate#local_ovf_path}
        :param ovf_network_map: The mapping of name of network identifiers from the ovf descriptor to network UUID in the VI infrastructure. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template#ovf_network_map DataVsphereOvfVmTemplate#ovf_network_map}
        :param remote_ovf_url: URL to the remote ovf/ova file to be deployed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template#remote_ovf_url DataVsphereOvfVmTemplate#remote_ovf_url}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9dea0874729c6d866f94eca6240ad786c9c24bf3aa91dff0cd425f56788defcf)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DataVsphereOvfVmTemplateConfig(
            host_system_id=host_system_id,
            name=name,
            resource_pool_id=resource_pool_id,
            allow_unverified_ssl_cert=allow_unverified_ssl_cert,
            datastore_id=datastore_id,
            deployment_option=deployment_option,
            disk_provisioning=disk_provisioning,
            enable_hidden_properties=enable_hidden_properties,
            folder=folder,
            id=id,
            ip_allocation_policy=ip_allocation_policy,
            ip_protocol=ip_protocol,
            local_ovf_path=local_ovf_path,
            ovf_network_map=ovf_network_map,
            remote_ovf_url=remote_ovf_url,
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
        '''Generates CDKTF code for importing a DataVsphereOvfVmTemplate resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataVsphereOvfVmTemplate to import.
        :param import_from_id: The id of the existing DataVsphereOvfVmTemplate that should be imported. Refer to the {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataVsphereOvfVmTemplate to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6de98009ec72a84421bfdeb3e6abf32fa243def2164001fac27f11efbafd7d40)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAllowUnverifiedSslCert")
    def reset_allow_unverified_ssl_cert(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowUnverifiedSslCert", []))

    @jsii.member(jsii_name="resetDatastoreId")
    def reset_datastore_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatastoreId", []))

    @jsii.member(jsii_name="resetDeploymentOption")
    def reset_deployment_option(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeploymentOption", []))

    @jsii.member(jsii_name="resetDiskProvisioning")
    def reset_disk_provisioning(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDiskProvisioning", []))

    @jsii.member(jsii_name="resetEnableHiddenProperties")
    def reset_enable_hidden_properties(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableHiddenProperties", []))

    @jsii.member(jsii_name="resetFolder")
    def reset_folder(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFolder", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

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
    @jsii.member(jsii_name="alternateGuestName")
    def alternate_guest_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "alternateGuestName"))

    @builtins.property
    @jsii.member(jsii_name="annotation")
    def annotation(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "annotation"))

    @builtins.property
    @jsii.member(jsii_name="cpuHotAddEnabled")
    def cpu_hot_add_enabled(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "cpuHotAddEnabled"))

    @builtins.property
    @jsii.member(jsii_name="cpuHotRemoveEnabled")
    def cpu_hot_remove_enabled(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "cpuHotRemoveEnabled"))

    @builtins.property
    @jsii.member(jsii_name="cpuPerformanceCountersEnabled")
    def cpu_performance_counters_enabled(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "cpuPerformanceCountersEnabled"))

    @builtins.property
    @jsii.member(jsii_name="firmware")
    def firmware(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "firmware"))

    @builtins.property
    @jsii.member(jsii_name="guestId")
    def guest_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "guestId"))

    @builtins.property
    @jsii.member(jsii_name="ideControllerCount")
    def ide_controller_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ideControllerCount"))

    @builtins.property
    @jsii.member(jsii_name="memory")
    def memory(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "memory"))

    @builtins.property
    @jsii.member(jsii_name="memoryHotAddEnabled")
    def memory_hot_add_enabled(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "memoryHotAddEnabled"))

    @builtins.property
    @jsii.member(jsii_name="nestedHvEnabled")
    def nested_hv_enabled(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "nestedHvEnabled"))

    @builtins.property
    @jsii.member(jsii_name="numCoresPerSocket")
    def num_cores_per_socket(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numCoresPerSocket"))

    @builtins.property
    @jsii.member(jsii_name="numCpus")
    def num_cpus(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numCpus"))

    @builtins.property
    @jsii.member(jsii_name="sataControllerCount")
    def sata_controller_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "sataControllerCount"))

    @builtins.property
    @jsii.member(jsii_name="scsiControllerCount")
    def scsi_controller_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "scsiControllerCount"))

    @builtins.property
    @jsii.member(jsii_name="scsiType")
    def scsi_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scsiType"))

    @builtins.property
    @jsii.member(jsii_name="swapPlacementPolicy")
    def swap_placement_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "swapPlacementPolicy"))

    @builtins.property
    @jsii.member(jsii_name="allowUnverifiedSslCertInput")
    def allow_unverified_ssl_cert_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "allowUnverifiedSslCertInput"))

    @builtins.property
    @jsii.member(jsii_name="datastoreIdInput")
    def datastore_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "datastoreIdInput"))

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
    @jsii.member(jsii_name="folderInput")
    def folder_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "folderInput"))

    @builtins.property
    @jsii.member(jsii_name="hostSystemIdInput")
    def host_system_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostSystemIdInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

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
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

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
    @jsii.member(jsii_name="resourcePoolIdInput")
    def resource_pool_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourcePoolIdInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__57bee6a973031eb16cd72ba535d8f4cbe1c7591873ae11be4b89ba16e4a9524b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowUnverifiedSslCert", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="datastoreId")
    def datastore_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "datastoreId"))

    @datastore_id.setter
    def datastore_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ebc908ada524716f33b697465978947b671b7fe718d2de11bfd95f8d48f4dc4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "datastoreId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="deploymentOption")
    def deployment_option(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deploymentOption"))

    @deployment_option.setter
    def deployment_option(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2f885f782756428af452e3ced3a22554106321da2fcb05be875cdb40437b212)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deploymentOption", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="diskProvisioning")
    def disk_provisioning(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "diskProvisioning"))

    @disk_provisioning.setter
    def disk_provisioning(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7bdd8e340da6d4cb1a1d6301d894913081226b116730dd1ba1ed0090ecc3ddf6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b0a635f5b2838a3a84567528f9d71f888bf24470a810f062d809a43c78aabe06)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableHiddenProperties", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="folder")
    def folder(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "folder"))

    @folder.setter
    def folder(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00652cf8a999cf48a6b1d5cb0ce02d222eac9517a13872da3ce2f600ad5bf9ee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "folder", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="hostSystemId")
    def host_system_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostSystemId"))

    @host_system_id.setter
    def host_system_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52eebf3593ee4efddd7e11f286988928dd1e5bf81252f374a04c600e1ab12896)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hostSystemId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__591ca7fb4d20d621769a216a7769c05c173a092e0b65fb619a93fcf3803ea259)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipAllocationPolicy")
    def ip_allocation_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipAllocationPolicy"))

    @ip_allocation_policy.setter
    def ip_allocation_policy(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__458873d4169a317c39f3b629fcc3b4e3cc1f24c5e07fa6de2e092fb58ebdf03f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipAllocationPolicy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipProtocol")
    def ip_protocol(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipProtocol"))

    @ip_protocol.setter
    def ip_protocol(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8dccf409aa18c035609e04499b94503b081b01d36e62784c1bbeaf672a4070a5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipProtocol", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="localOvfPath")
    def local_ovf_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "localOvfPath"))

    @local_ovf_path.setter
    def local_ovf_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74038db3191cc919ba81c4a0cace09d3a1370a1541866abaee70d1bd380269f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "localOvfPath", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc8485258e06ca0cdfe9af75f3505e34fe2eef0eb5baad3534163bc616deb23d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__983ef20fe200d9bcdd62dc66ca51c3a2843bed4384a56809efefba8f7784ba2a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ovfNetworkMap", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="remoteOvfUrl")
    def remote_ovf_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "remoteOvfUrl"))

    @remote_ovf_url.setter
    def remote_ovf_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eab5dd6b1a4080b4f75e9b0cd7b77cbd97596b6ebf8f4e46d248f44a01ee538b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "remoteOvfUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="resourcePoolId")
    def resource_pool_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourcePoolId"))

    @resource_pool_id.setter
    def resource_pool_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e1aac61c40114ece294418c8497dbe4104b7e2090bab979a70f6b39ddaaec080)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resourcePoolId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.dataVsphereOvfVmTemplate.DataVsphereOvfVmTemplateConfig",
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
        "resource_pool_id": "resourcePoolId",
        "allow_unverified_ssl_cert": "allowUnverifiedSslCert",
        "datastore_id": "datastoreId",
        "deployment_option": "deploymentOption",
        "disk_provisioning": "diskProvisioning",
        "enable_hidden_properties": "enableHiddenProperties",
        "folder": "folder",
        "id": "id",
        "ip_allocation_policy": "ipAllocationPolicy",
        "ip_protocol": "ipProtocol",
        "local_ovf_path": "localOvfPath",
        "ovf_network_map": "ovfNetworkMap",
        "remote_ovf_url": "remoteOvfUrl",
    },
)
class DataVsphereOvfVmTemplateConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        resource_pool_id: builtins.str,
        allow_unverified_ssl_cert: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        datastore_id: typing.Optional[builtins.str] = None,
        deployment_option: typing.Optional[builtins.str] = None,
        disk_provisioning: typing.Optional[builtins.str] = None,
        enable_hidden_properties: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        folder: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        ip_allocation_policy: typing.Optional[builtins.str] = None,
        ip_protocol: typing.Optional[builtins.str] = None,
        local_ovf_path: typing.Optional[builtins.str] = None,
        ovf_network_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        remote_ovf_url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param host_system_id: The ID of an optional host system to pin the virtual machine to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template#host_system_id DataVsphereOvfVmTemplate#host_system_id}
        :param name: Name of the virtual machine to create. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template#name DataVsphereOvfVmTemplate#name}
        :param resource_pool_id: The ID of a resource pool to put the virtual machine in. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template#resource_pool_id DataVsphereOvfVmTemplate#resource_pool_id}
        :param allow_unverified_ssl_cert: Allow unverified ssl certificates while deploying ovf/ova from url. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template#allow_unverified_ssl_cert DataVsphereOvfVmTemplate#allow_unverified_ssl_cert}
        :param datastore_id: The ID of the virtual machine's datastore. The virtual machine configuration is placed here, along with any virtual disks that are created without datastores. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template#datastore_id DataVsphereOvfVmTemplate#datastore_id}
        :param deployment_option: The Deployment option to be chosen. If empty, the default option is used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template#deployment_option DataVsphereOvfVmTemplate#deployment_option}
        :param disk_provisioning: An optional disk provisioning. If set, all the disks in the deployed ovf will have the same specified disk type (e.g., thin provisioned). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template#disk_provisioning DataVsphereOvfVmTemplate#disk_provisioning}
        :param enable_hidden_properties: Allow properties with ovf:userConfigurable=false to be set. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template#enable_hidden_properties DataVsphereOvfVmTemplate#enable_hidden_properties}
        :param folder: The name of the folder to locate the virtual machine in. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template#folder DataVsphereOvfVmTemplate#folder}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template#id DataVsphereOvfVmTemplate#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param ip_allocation_policy: The IP allocation policy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template#ip_allocation_policy DataVsphereOvfVmTemplate#ip_allocation_policy}
        :param ip_protocol: The IP protocol. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template#ip_protocol DataVsphereOvfVmTemplate#ip_protocol}
        :param local_ovf_path: The absolute path to the ovf/ova file in the local system. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template#local_ovf_path DataVsphereOvfVmTemplate#local_ovf_path}
        :param ovf_network_map: The mapping of name of network identifiers from the ovf descriptor to network UUID in the VI infrastructure. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template#ovf_network_map DataVsphereOvfVmTemplate#ovf_network_map}
        :param remote_ovf_url: URL to the remote ovf/ova file to be deployed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template#remote_ovf_url DataVsphereOvfVmTemplate#remote_ovf_url}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5544f7fdaa46124448595a68ebfdfd2a2be6d133b0eaf87ba780b43724be391c)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument host_system_id", value=host_system_id, expected_type=type_hints["host_system_id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument resource_pool_id", value=resource_pool_id, expected_type=type_hints["resource_pool_id"])
            check_type(argname="argument allow_unverified_ssl_cert", value=allow_unverified_ssl_cert, expected_type=type_hints["allow_unverified_ssl_cert"])
            check_type(argname="argument datastore_id", value=datastore_id, expected_type=type_hints["datastore_id"])
            check_type(argname="argument deployment_option", value=deployment_option, expected_type=type_hints["deployment_option"])
            check_type(argname="argument disk_provisioning", value=disk_provisioning, expected_type=type_hints["disk_provisioning"])
            check_type(argname="argument enable_hidden_properties", value=enable_hidden_properties, expected_type=type_hints["enable_hidden_properties"])
            check_type(argname="argument folder", value=folder, expected_type=type_hints["folder"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument ip_allocation_policy", value=ip_allocation_policy, expected_type=type_hints["ip_allocation_policy"])
            check_type(argname="argument ip_protocol", value=ip_protocol, expected_type=type_hints["ip_protocol"])
            check_type(argname="argument local_ovf_path", value=local_ovf_path, expected_type=type_hints["local_ovf_path"])
            check_type(argname="argument ovf_network_map", value=ovf_network_map, expected_type=type_hints["ovf_network_map"])
            check_type(argname="argument remote_ovf_url", value=remote_ovf_url, expected_type=type_hints["remote_ovf_url"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "host_system_id": host_system_id,
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
        if allow_unverified_ssl_cert is not None:
            self._values["allow_unverified_ssl_cert"] = allow_unverified_ssl_cert
        if datastore_id is not None:
            self._values["datastore_id"] = datastore_id
        if deployment_option is not None:
            self._values["deployment_option"] = deployment_option
        if disk_provisioning is not None:
            self._values["disk_provisioning"] = disk_provisioning
        if enable_hidden_properties is not None:
            self._values["enable_hidden_properties"] = enable_hidden_properties
        if folder is not None:
            self._values["folder"] = folder
        if id is not None:
            self._values["id"] = id
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
        '''The ID of an optional host system to pin the virtual machine to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template#host_system_id DataVsphereOvfVmTemplate#host_system_id}
        '''
        result = self._values.get("host_system_id")
        assert result is not None, "Required property 'host_system_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Name of the virtual machine to create.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template#name DataVsphereOvfVmTemplate#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def resource_pool_id(self) -> builtins.str:
        '''The ID of a resource pool to put the virtual machine in.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template#resource_pool_id DataVsphereOvfVmTemplate#resource_pool_id}
        '''
        result = self._values.get("resource_pool_id")
        assert result is not None, "Required property 'resource_pool_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allow_unverified_ssl_cert(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Allow unverified ssl certificates while deploying ovf/ova from url.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template#allow_unverified_ssl_cert DataVsphereOvfVmTemplate#allow_unverified_ssl_cert}
        '''
        result = self._values.get("allow_unverified_ssl_cert")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def datastore_id(self) -> typing.Optional[builtins.str]:
        '''The ID of the virtual machine's datastore.

        The virtual machine configuration is placed here, along with any virtual disks that are created without datastores.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template#datastore_id DataVsphereOvfVmTemplate#datastore_id}
        '''
        result = self._values.get("datastore_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def deployment_option(self) -> typing.Optional[builtins.str]:
        '''The Deployment option to be chosen. If empty, the default option is used.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template#deployment_option DataVsphereOvfVmTemplate#deployment_option}
        '''
        result = self._values.get("deployment_option")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disk_provisioning(self) -> typing.Optional[builtins.str]:
        '''An optional disk provisioning.

        If set, all the disks in the deployed ovf will have the same specified disk type (e.g., thin provisioned).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template#disk_provisioning DataVsphereOvfVmTemplate#disk_provisioning}
        '''
        result = self._values.get("disk_provisioning")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_hidden_properties(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Allow properties with ovf:userConfigurable=false to be set.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template#enable_hidden_properties DataVsphereOvfVmTemplate#enable_hidden_properties}
        '''
        result = self._values.get("enable_hidden_properties")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def folder(self) -> typing.Optional[builtins.str]:
        '''The name of the folder to locate the virtual machine in.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template#folder DataVsphereOvfVmTemplate#folder}
        '''
        result = self._values.get("folder")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template#id DataVsphereOvfVmTemplate#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ip_allocation_policy(self) -> typing.Optional[builtins.str]:
        '''The IP allocation policy.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template#ip_allocation_policy DataVsphereOvfVmTemplate#ip_allocation_policy}
        '''
        result = self._values.get("ip_allocation_policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ip_protocol(self) -> typing.Optional[builtins.str]:
        '''The IP protocol.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template#ip_protocol DataVsphereOvfVmTemplate#ip_protocol}
        '''
        result = self._values.get("ip_protocol")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def local_ovf_path(self) -> typing.Optional[builtins.str]:
        '''The absolute path to the ovf/ova file in the local system.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template#local_ovf_path DataVsphereOvfVmTemplate#local_ovf_path}
        '''
        result = self._values.get("local_ovf_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ovf_network_map(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''The mapping of name of network identifiers from the ovf descriptor to network UUID in the VI infrastructure.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template#ovf_network_map DataVsphereOvfVmTemplate#ovf_network_map}
        '''
        result = self._values.get("ovf_network_map")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def remote_ovf_url(self) -> typing.Optional[builtins.str]:
        '''URL to the remote ovf/ova file to be deployed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/data-sources/ovf_vm_template#remote_ovf_url DataVsphereOvfVmTemplate#remote_ovf_url}
        '''
        result = self._values.get("remote_ovf_url")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataVsphereOvfVmTemplateConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DataVsphereOvfVmTemplate",
    "DataVsphereOvfVmTemplateConfig",
]

publication.publish()

def _typecheckingstub__9dea0874729c6d866f94eca6240ad786c9c24bf3aa91dff0cd425f56788defcf(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    host_system_id: builtins.str,
    name: builtins.str,
    resource_pool_id: builtins.str,
    allow_unverified_ssl_cert: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    datastore_id: typing.Optional[builtins.str] = None,
    deployment_option: typing.Optional[builtins.str] = None,
    disk_provisioning: typing.Optional[builtins.str] = None,
    enable_hidden_properties: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    folder: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    ip_allocation_policy: typing.Optional[builtins.str] = None,
    ip_protocol: typing.Optional[builtins.str] = None,
    local_ovf_path: typing.Optional[builtins.str] = None,
    ovf_network_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    remote_ovf_url: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__6de98009ec72a84421bfdeb3e6abf32fa243def2164001fac27f11efbafd7d40(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57bee6a973031eb16cd72ba535d8f4cbe1c7591873ae11be4b89ba16e4a9524b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ebc908ada524716f33b697465978947b671b7fe718d2de11bfd95f8d48f4dc4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2f885f782756428af452e3ced3a22554106321da2fcb05be875cdb40437b212(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7bdd8e340da6d4cb1a1d6301d894913081226b116730dd1ba1ed0090ecc3ddf6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0a635f5b2838a3a84567528f9d71f888bf24470a810f062d809a43c78aabe06(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00652cf8a999cf48a6b1d5cb0ce02d222eac9517a13872da3ce2f600ad5bf9ee(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52eebf3593ee4efddd7e11f286988928dd1e5bf81252f374a04c600e1ab12896(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__591ca7fb4d20d621769a216a7769c05c173a092e0b65fb619a93fcf3803ea259(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__458873d4169a317c39f3b629fcc3b4e3cc1f24c5e07fa6de2e092fb58ebdf03f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8dccf409aa18c035609e04499b94503b081b01d36e62784c1bbeaf672a4070a5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74038db3191cc919ba81c4a0cace09d3a1370a1541866abaee70d1bd380269f8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc8485258e06ca0cdfe9af75f3505e34fe2eef0eb5baad3534163bc616deb23d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__983ef20fe200d9bcdd62dc66ca51c3a2843bed4384a56809efefba8f7784ba2a(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eab5dd6b1a4080b4f75e9b0cd7b77cbd97596b6ebf8f4e46d248f44a01ee538b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1aac61c40114ece294418c8497dbe4104b7e2090bab979a70f6b39ddaaec080(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5544f7fdaa46124448595a68ebfdfd2a2be6d133b0eaf87ba780b43724be391c(
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
    resource_pool_id: builtins.str,
    allow_unverified_ssl_cert: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    datastore_id: typing.Optional[builtins.str] = None,
    deployment_option: typing.Optional[builtins.str] = None,
    disk_provisioning: typing.Optional[builtins.str] = None,
    enable_hidden_properties: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    folder: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    ip_allocation_policy: typing.Optional[builtins.str] = None,
    ip_protocol: typing.Optional[builtins.str] = None,
    local_ovf_path: typing.Optional[builtins.str] = None,
    ovf_network_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    remote_ovf_url: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
