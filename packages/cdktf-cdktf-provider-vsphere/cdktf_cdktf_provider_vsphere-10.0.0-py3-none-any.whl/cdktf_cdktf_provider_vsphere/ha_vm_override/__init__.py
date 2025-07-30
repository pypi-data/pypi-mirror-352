r'''
# `vsphere_ha_vm_override`

Refer to the Terraform Registry for docs: [`vsphere_ha_vm_override`](https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override).
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


class HaVmOverride(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.haVmOverride.HaVmOverride",
):
    '''Represents a {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override vsphere_ha_vm_override}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        compute_cluster_id: builtins.str,
        virtual_machine_id: builtins.str,
        ha_datastore_apd_recovery_action: typing.Optional[builtins.str] = None,
        ha_datastore_apd_response: typing.Optional[builtins.str] = None,
        ha_datastore_apd_response_delay: typing.Optional[jsii.Number] = None,
        ha_datastore_pdl_response: typing.Optional[builtins.str] = None,
        ha_host_isolation_response: typing.Optional[builtins.str] = None,
        ha_vm_failure_interval: typing.Optional[jsii.Number] = None,
        ha_vm_maximum_failure_window: typing.Optional[jsii.Number] = None,
        ha_vm_maximum_resets: typing.Optional[jsii.Number] = None,
        ha_vm_minimum_uptime: typing.Optional[jsii.Number] = None,
        ha_vm_monitoring: typing.Optional[builtins.str] = None,
        ha_vm_monitoring_use_cluster_defaults: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ha_vm_restart_priority: typing.Optional[builtins.str] = None,
        ha_vm_restart_timeout: typing.Optional[jsii.Number] = None,
        id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override vsphere_ha_vm_override} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param compute_cluster_id: The managed object ID of the cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#compute_cluster_id HaVmOverride#compute_cluster_id}
        :param virtual_machine_id: The managed object ID of the virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#virtual_machine_id HaVmOverride#virtual_machine_id}
        :param ha_datastore_apd_recovery_action: Controls the action to take on this virtual machine if an APD status on an affected datastore clears in the middle of an APD event. Can be one of useClusterDefault, none or reset. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#ha_datastore_apd_recovery_action HaVmOverride#ha_datastore_apd_recovery_action}
        :param ha_datastore_apd_response: Controls the action to take on this virtual machine when the cluster has detected loss to all paths to a relevant datastore. Can be one of clusterDefault, disabled, warning, restartConservative, or restartAggressive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#ha_datastore_apd_response HaVmOverride#ha_datastore_apd_response}
        :param ha_datastore_apd_response_delay: Controls the delay in seconds to wait after an APD timeout event to execute the response action defined in ha_datastore_apd_response. Specify -1 to use the cluster setting. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#ha_datastore_apd_response_delay HaVmOverride#ha_datastore_apd_response_delay}
        :param ha_datastore_pdl_response: Controls the action to take on this virtual machine when the cluster has detected a permanent device loss to a relevant datastore. Can be one of clusterDefault, disabled, warning, or restartAggressive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#ha_datastore_pdl_response HaVmOverride#ha_datastore_pdl_response}
        :param ha_host_isolation_response: The action to take on this virtual machine when a host is isolated from the rest of the cluster. Can be one of clusterIsolationResponse, none, powerOff, or shutdown. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#ha_host_isolation_response HaVmOverride#ha_host_isolation_response}
        :param ha_vm_failure_interval: If a heartbeat from this virtual machine is not received within this configured interval, the virtual machine is marked as failed. The value is in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#ha_vm_failure_interval HaVmOverride#ha_vm_failure_interval}
        :param ha_vm_maximum_failure_window: The length of the reset window in which ha_vm_maximum_resets can operate. When this window expires, no more resets are attempted regardless of the setting configured in ha_vm_maximum_resets. -1 means no window, meaning an unlimited reset time is allotted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#ha_vm_maximum_failure_window HaVmOverride#ha_vm_maximum_failure_window}
        :param ha_vm_maximum_resets: The maximum number of resets that HA will perform to this virtual machine when responding to a failure event. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#ha_vm_maximum_resets HaVmOverride#ha_vm_maximum_resets}
        :param ha_vm_minimum_uptime: The time, in seconds, that HA waits after powering on this virtual machine before monitoring for heartbeats. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#ha_vm_minimum_uptime HaVmOverride#ha_vm_minimum_uptime}
        :param ha_vm_monitoring: The type of virtual machine monitoring to use for this virtual machine. Can be one of vmMonitoringDisabled, vmMonitoringOnly, or vmAndAppMonitoring. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#ha_vm_monitoring HaVmOverride#ha_vm_monitoring}
        :param ha_vm_monitoring_use_cluster_defaults: Determines whether or not the cluster's default settings or the VM override settings specified in this resource are used for virtual machine monitoring. The default is true (use cluster defaults) - set to false to have overrides take effect. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#ha_vm_monitoring_use_cluster_defaults HaVmOverride#ha_vm_monitoring_use_cluster_defaults}
        :param ha_vm_restart_priority: The restart priority for this virtual machine when vSphere detects a host failure. Can be one of clusterRestartPriority, lowest, low, medium, high, or highest. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#ha_vm_restart_priority HaVmOverride#ha_vm_restart_priority}
        :param ha_vm_restart_timeout: The maximum time, in seconds, that vSphere HA will wait for the virtual machine to be ready. Use -1 to use the cluster default. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#ha_vm_restart_timeout HaVmOverride#ha_vm_restart_timeout}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#id HaVmOverride#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a362f73d90dca8d6f75702e2c8edfa896016f62abcf695a0bb12dce218c9b52)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = HaVmOverrideConfig(
            compute_cluster_id=compute_cluster_id,
            virtual_machine_id=virtual_machine_id,
            ha_datastore_apd_recovery_action=ha_datastore_apd_recovery_action,
            ha_datastore_apd_response=ha_datastore_apd_response,
            ha_datastore_apd_response_delay=ha_datastore_apd_response_delay,
            ha_datastore_pdl_response=ha_datastore_pdl_response,
            ha_host_isolation_response=ha_host_isolation_response,
            ha_vm_failure_interval=ha_vm_failure_interval,
            ha_vm_maximum_failure_window=ha_vm_maximum_failure_window,
            ha_vm_maximum_resets=ha_vm_maximum_resets,
            ha_vm_minimum_uptime=ha_vm_minimum_uptime,
            ha_vm_monitoring=ha_vm_monitoring,
            ha_vm_monitoring_use_cluster_defaults=ha_vm_monitoring_use_cluster_defaults,
            ha_vm_restart_priority=ha_vm_restart_priority,
            ha_vm_restart_timeout=ha_vm_restart_timeout,
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
        '''Generates CDKTF code for importing a HaVmOverride resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the HaVmOverride to import.
        :param import_from_id: The id of the existing HaVmOverride that should be imported. Refer to the {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the HaVmOverride to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0bc88d1e41d4ddea6cf59b23d4a5178209fae0ac97f6f35da88169dac3122584)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetHaDatastoreApdRecoveryAction")
    def reset_ha_datastore_apd_recovery_action(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHaDatastoreApdRecoveryAction", []))

    @jsii.member(jsii_name="resetHaDatastoreApdResponse")
    def reset_ha_datastore_apd_response(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHaDatastoreApdResponse", []))

    @jsii.member(jsii_name="resetHaDatastoreApdResponseDelay")
    def reset_ha_datastore_apd_response_delay(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHaDatastoreApdResponseDelay", []))

    @jsii.member(jsii_name="resetHaDatastorePdlResponse")
    def reset_ha_datastore_pdl_response(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHaDatastorePdlResponse", []))

    @jsii.member(jsii_name="resetHaHostIsolationResponse")
    def reset_ha_host_isolation_response(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHaHostIsolationResponse", []))

    @jsii.member(jsii_name="resetHaVmFailureInterval")
    def reset_ha_vm_failure_interval(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHaVmFailureInterval", []))

    @jsii.member(jsii_name="resetHaVmMaximumFailureWindow")
    def reset_ha_vm_maximum_failure_window(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHaVmMaximumFailureWindow", []))

    @jsii.member(jsii_name="resetHaVmMaximumResets")
    def reset_ha_vm_maximum_resets(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHaVmMaximumResets", []))

    @jsii.member(jsii_name="resetHaVmMinimumUptime")
    def reset_ha_vm_minimum_uptime(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHaVmMinimumUptime", []))

    @jsii.member(jsii_name="resetHaVmMonitoring")
    def reset_ha_vm_monitoring(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHaVmMonitoring", []))

    @jsii.member(jsii_name="resetHaVmMonitoringUseClusterDefaults")
    def reset_ha_vm_monitoring_use_cluster_defaults(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHaVmMonitoringUseClusterDefaults", []))

    @jsii.member(jsii_name="resetHaVmRestartPriority")
    def reset_ha_vm_restart_priority(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHaVmRestartPriority", []))

    @jsii.member(jsii_name="resetHaVmRestartTimeout")
    def reset_ha_vm_restart_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHaVmRestartTimeout", []))

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
    @jsii.member(jsii_name="computeClusterIdInput")
    def compute_cluster_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "computeClusterIdInput"))

    @builtins.property
    @jsii.member(jsii_name="haDatastoreApdRecoveryActionInput")
    def ha_datastore_apd_recovery_action_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "haDatastoreApdRecoveryActionInput"))

    @builtins.property
    @jsii.member(jsii_name="haDatastoreApdResponseDelayInput")
    def ha_datastore_apd_response_delay_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "haDatastoreApdResponseDelayInput"))

    @builtins.property
    @jsii.member(jsii_name="haDatastoreApdResponseInput")
    def ha_datastore_apd_response_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "haDatastoreApdResponseInput"))

    @builtins.property
    @jsii.member(jsii_name="haDatastorePdlResponseInput")
    def ha_datastore_pdl_response_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "haDatastorePdlResponseInput"))

    @builtins.property
    @jsii.member(jsii_name="haHostIsolationResponseInput")
    def ha_host_isolation_response_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "haHostIsolationResponseInput"))

    @builtins.property
    @jsii.member(jsii_name="haVmFailureIntervalInput")
    def ha_vm_failure_interval_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "haVmFailureIntervalInput"))

    @builtins.property
    @jsii.member(jsii_name="haVmMaximumFailureWindowInput")
    def ha_vm_maximum_failure_window_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "haVmMaximumFailureWindowInput"))

    @builtins.property
    @jsii.member(jsii_name="haVmMaximumResetsInput")
    def ha_vm_maximum_resets_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "haVmMaximumResetsInput"))

    @builtins.property
    @jsii.member(jsii_name="haVmMinimumUptimeInput")
    def ha_vm_minimum_uptime_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "haVmMinimumUptimeInput"))

    @builtins.property
    @jsii.member(jsii_name="haVmMonitoringInput")
    def ha_vm_monitoring_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "haVmMonitoringInput"))

    @builtins.property
    @jsii.member(jsii_name="haVmMonitoringUseClusterDefaultsInput")
    def ha_vm_monitoring_use_cluster_defaults_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "haVmMonitoringUseClusterDefaultsInput"))

    @builtins.property
    @jsii.member(jsii_name="haVmRestartPriorityInput")
    def ha_vm_restart_priority_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "haVmRestartPriorityInput"))

    @builtins.property
    @jsii.member(jsii_name="haVmRestartTimeoutInput")
    def ha_vm_restart_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "haVmRestartTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="virtualMachineIdInput")
    def virtual_machine_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "virtualMachineIdInput"))

    @builtins.property
    @jsii.member(jsii_name="computeClusterId")
    def compute_cluster_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "computeClusterId"))

    @compute_cluster_id.setter
    def compute_cluster_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__557177dab0528ece41558a7ac7697cdc548705065084adfce0800056b354f542)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "computeClusterId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="haDatastoreApdRecoveryAction")
    def ha_datastore_apd_recovery_action(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "haDatastoreApdRecoveryAction"))

    @ha_datastore_apd_recovery_action.setter
    def ha_datastore_apd_recovery_action(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f256c9f5050cae30a5a4f8f84e0d110d8cb3e7154b5d7ce034f1ddd3a4755dde)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "haDatastoreApdRecoveryAction", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="haDatastoreApdResponse")
    def ha_datastore_apd_response(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "haDatastoreApdResponse"))

    @ha_datastore_apd_response.setter
    def ha_datastore_apd_response(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea523e6cfa809bc283af2f4d1418635e8b0452b4efe74792eee607e933770039)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "haDatastoreApdResponse", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="haDatastoreApdResponseDelay")
    def ha_datastore_apd_response_delay(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "haDatastoreApdResponseDelay"))

    @ha_datastore_apd_response_delay.setter
    def ha_datastore_apd_response_delay(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3bb6e4e2851b4c7f6f866494f79bd71ac773b9a38038c4e55301d6a52bc44af6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "haDatastoreApdResponseDelay", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="haDatastorePdlResponse")
    def ha_datastore_pdl_response(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "haDatastorePdlResponse"))

    @ha_datastore_pdl_response.setter
    def ha_datastore_pdl_response(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e22a9d6bb85c6efc7c2baafccc2b8071147dd5370530bee0151877299c60974e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "haDatastorePdlResponse", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="haHostIsolationResponse")
    def ha_host_isolation_response(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "haHostIsolationResponse"))

    @ha_host_isolation_response.setter
    def ha_host_isolation_response(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24eba372c4dc3ddc05440c19146b3817dd93055e36990f719a011fa8048bf5dd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "haHostIsolationResponse", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="haVmFailureInterval")
    def ha_vm_failure_interval(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "haVmFailureInterval"))

    @ha_vm_failure_interval.setter
    def ha_vm_failure_interval(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a59c2467408e14a5e776a9e38b168395004c9fd9f69bfe0b0748e87709d7f1c7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "haVmFailureInterval", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="haVmMaximumFailureWindow")
    def ha_vm_maximum_failure_window(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "haVmMaximumFailureWindow"))

    @ha_vm_maximum_failure_window.setter
    def ha_vm_maximum_failure_window(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eea261c1919e23959fbc771dc8fed0ba219ccaf427929a2aea52452d0257af20)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "haVmMaximumFailureWindow", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="haVmMaximumResets")
    def ha_vm_maximum_resets(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "haVmMaximumResets"))

    @ha_vm_maximum_resets.setter
    def ha_vm_maximum_resets(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ba13c4bac5f6d4f97d2d9cf98d2cc9050cce14ac68ccf13fb46528af4b3e189)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "haVmMaximumResets", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="haVmMinimumUptime")
    def ha_vm_minimum_uptime(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "haVmMinimumUptime"))

    @ha_vm_minimum_uptime.setter
    def ha_vm_minimum_uptime(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5819c3f82d8cd9a9505ec0a3e32598c1033cbf11867093eb9bd1557090a9a126)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "haVmMinimumUptime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="haVmMonitoring")
    def ha_vm_monitoring(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "haVmMonitoring"))

    @ha_vm_monitoring.setter
    def ha_vm_monitoring(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6565e93f8c94253a21c6a9d461bb5ae54dfdf0c875f59e6a6c268a04b54dfdd3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "haVmMonitoring", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="haVmMonitoringUseClusterDefaults")
    def ha_vm_monitoring_use_cluster_defaults(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "haVmMonitoringUseClusterDefaults"))

    @ha_vm_monitoring_use_cluster_defaults.setter
    def ha_vm_monitoring_use_cluster_defaults(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4345868e87693c387b7b01181a722805772338361c6ad67afdf1d2eef49c9d67)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "haVmMonitoringUseClusterDefaults", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="haVmRestartPriority")
    def ha_vm_restart_priority(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "haVmRestartPriority"))

    @ha_vm_restart_priority.setter
    def ha_vm_restart_priority(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ab3125195723f9f4b8d007e0cd7be6e953d4e31cd75b5f453a0e7e7764e6638)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "haVmRestartPriority", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="haVmRestartTimeout")
    def ha_vm_restart_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "haVmRestartTimeout"))

    @ha_vm_restart_timeout.setter
    def ha_vm_restart_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd4786a1c82dd41dcc593f0da050522c92f7195bb8a390e5d69cc31976fdb386)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "haVmRestartTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__502e30cf9cca42e53c488650d96eb7a63bc4d956fb3151070c6f901c2ef636ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="virtualMachineId")
    def virtual_machine_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "virtualMachineId"))

    @virtual_machine_id.setter
    def virtual_machine_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__915f3a1552773b6d97f4e79c4793bdba2607ceed57f0167a116aebed4b41dc2a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "virtualMachineId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.haVmOverride.HaVmOverrideConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "compute_cluster_id": "computeClusterId",
        "virtual_machine_id": "virtualMachineId",
        "ha_datastore_apd_recovery_action": "haDatastoreApdRecoveryAction",
        "ha_datastore_apd_response": "haDatastoreApdResponse",
        "ha_datastore_apd_response_delay": "haDatastoreApdResponseDelay",
        "ha_datastore_pdl_response": "haDatastorePdlResponse",
        "ha_host_isolation_response": "haHostIsolationResponse",
        "ha_vm_failure_interval": "haVmFailureInterval",
        "ha_vm_maximum_failure_window": "haVmMaximumFailureWindow",
        "ha_vm_maximum_resets": "haVmMaximumResets",
        "ha_vm_minimum_uptime": "haVmMinimumUptime",
        "ha_vm_monitoring": "haVmMonitoring",
        "ha_vm_monitoring_use_cluster_defaults": "haVmMonitoringUseClusterDefaults",
        "ha_vm_restart_priority": "haVmRestartPriority",
        "ha_vm_restart_timeout": "haVmRestartTimeout",
        "id": "id",
    },
)
class HaVmOverrideConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        compute_cluster_id: builtins.str,
        virtual_machine_id: builtins.str,
        ha_datastore_apd_recovery_action: typing.Optional[builtins.str] = None,
        ha_datastore_apd_response: typing.Optional[builtins.str] = None,
        ha_datastore_apd_response_delay: typing.Optional[jsii.Number] = None,
        ha_datastore_pdl_response: typing.Optional[builtins.str] = None,
        ha_host_isolation_response: typing.Optional[builtins.str] = None,
        ha_vm_failure_interval: typing.Optional[jsii.Number] = None,
        ha_vm_maximum_failure_window: typing.Optional[jsii.Number] = None,
        ha_vm_maximum_resets: typing.Optional[jsii.Number] = None,
        ha_vm_minimum_uptime: typing.Optional[jsii.Number] = None,
        ha_vm_monitoring: typing.Optional[builtins.str] = None,
        ha_vm_monitoring_use_cluster_defaults: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ha_vm_restart_priority: typing.Optional[builtins.str] = None,
        ha_vm_restart_timeout: typing.Optional[jsii.Number] = None,
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
        :param compute_cluster_id: The managed object ID of the cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#compute_cluster_id HaVmOverride#compute_cluster_id}
        :param virtual_machine_id: The managed object ID of the virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#virtual_machine_id HaVmOverride#virtual_machine_id}
        :param ha_datastore_apd_recovery_action: Controls the action to take on this virtual machine if an APD status on an affected datastore clears in the middle of an APD event. Can be one of useClusterDefault, none or reset. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#ha_datastore_apd_recovery_action HaVmOverride#ha_datastore_apd_recovery_action}
        :param ha_datastore_apd_response: Controls the action to take on this virtual machine when the cluster has detected loss to all paths to a relevant datastore. Can be one of clusterDefault, disabled, warning, restartConservative, or restartAggressive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#ha_datastore_apd_response HaVmOverride#ha_datastore_apd_response}
        :param ha_datastore_apd_response_delay: Controls the delay in seconds to wait after an APD timeout event to execute the response action defined in ha_datastore_apd_response. Specify -1 to use the cluster setting. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#ha_datastore_apd_response_delay HaVmOverride#ha_datastore_apd_response_delay}
        :param ha_datastore_pdl_response: Controls the action to take on this virtual machine when the cluster has detected a permanent device loss to a relevant datastore. Can be one of clusterDefault, disabled, warning, or restartAggressive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#ha_datastore_pdl_response HaVmOverride#ha_datastore_pdl_response}
        :param ha_host_isolation_response: The action to take on this virtual machine when a host is isolated from the rest of the cluster. Can be one of clusterIsolationResponse, none, powerOff, or shutdown. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#ha_host_isolation_response HaVmOverride#ha_host_isolation_response}
        :param ha_vm_failure_interval: If a heartbeat from this virtual machine is not received within this configured interval, the virtual machine is marked as failed. The value is in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#ha_vm_failure_interval HaVmOverride#ha_vm_failure_interval}
        :param ha_vm_maximum_failure_window: The length of the reset window in which ha_vm_maximum_resets can operate. When this window expires, no more resets are attempted regardless of the setting configured in ha_vm_maximum_resets. -1 means no window, meaning an unlimited reset time is allotted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#ha_vm_maximum_failure_window HaVmOverride#ha_vm_maximum_failure_window}
        :param ha_vm_maximum_resets: The maximum number of resets that HA will perform to this virtual machine when responding to a failure event. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#ha_vm_maximum_resets HaVmOverride#ha_vm_maximum_resets}
        :param ha_vm_minimum_uptime: The time, in seconds, that HA waits after powering on this virtual machine before monitoring for heartbeats. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#ha_vm_minimum_uptime HaVmOverride#ha_vm_minimum_uptime}
        :param ha_vm_monitoring: The type of virtual machine monitoring to use for this virtual machine. Can be one of vmMonitoringDisabled, vmMonitoringOnly, or vmAndAppMonitoring. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#ha_vm_monitoring HaVmOverride#ha_vm_monitoring}
        :param ha_vm_monitoring_use_cluster_defaults: Determines whether or not the cluster's default settings or the VM override settings specified in this resource are used for virtual machine monitoring. The default is true (use cluster defaults) - set to false to have overrides take effect. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#ha_vm_monitoring_use_cluster_defaults HaVmOverride#ha_vm_monitoring_use_cluster_defaults}
        :param ha_vm_restart_priority: The restart priority for this virtual machine when vSphere detects a host failure. Can be one of clusterRestartPriority, lowest, low, medium, high, or highest. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#ha_vm_restart_priority HaVmOverride#ha_vm_restart_priority}
        :param ha_vm_restart_timeout: The maximum time, in seconds, that vSphere HA will wait for the virtual machine to be ready. Use -1 to use the cluster default. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#ha_vm_restart_timeout HaVmOverride#ha_vm_restart_timeout}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#id HaVmOverride#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e901efdc3423ad9e40b41b2f1f51e91d15a27b4686337b35e9a82d02a3e9143)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument compute_cluster_id", value=compute_cluster_id, expected_type=type_hints["compute_cluster_id"])
            check_type(argname="argument virtual_machine_id", value=virtual_machine_id, expected_type=type_hints["virtual_machine_id"])
            check_type(argname="argument ha_datastore_apd_recovery_action", value=ha_datastore_apd_recovery_action, expected_type=type_hints["ha_datastore_apd_recovery_action"])
            check_type(argname="argument ha_datastore_apd_response", value=ha_datastore_apd_response, expected_type=type_hints["ha_datastore_apd_response"])
            check_type(argname="argument ha_datastore_apd_response_delay", value=ha_datastore_apd_response_delay, expected_type=type_hints["ha_datastore_apd_response_delay"])
            check_type(argname="argument ha_datastore_pdl_response", value=ha_datastore_pdl_response, expected_type=type_hints["ha_datastore_pdl_response"])
            check_type(argname="argument ha_host_isolation_response", value=ha_host_isolation_response, expected_type=type_hints["ha_host_isolation_response"])
            check_type(argname="argument ha_vm_failure_interval", value=ha_vm_failure_interval, expected_type=type_hints["ha_vm_failure_interval"])
            check_type(argname="argument ha_vm_maximum_failure_window", value=ha_vm_maximum_failure_window, expected_type=type_hints["ha_vm_maximum_failure_window"])
            check_type(argname="argument ha_vm_maximum_resets", value=ha_vm_maximum_resets, expected_type=type_hints["ha_vm_maximum_resets"])
            check_type(argname="argument ha_vm_minimum_uptime", value=ha_vm_minimum_uptime, expected_type=type_hints["ha_vm_minimum_uptime"])
            check_type(argname="argument ha_vm_monitoring", value=ha_vm_monitoring, expected_type=type_hints["ha_vm_monitoring"])
            check_type(argname="argument ha_vm_monitoring_use_cluster_defaults", value=ha_vm_monitoring_use_cluster_defaults, expected_type=type_hints["ha_vm_monitoring_use_cluster_defaults"])
            check_type(argname="argument ha_vm_restart_priority", value=ha_vm_restart_priority, expected_type=type_hints["ha_vm_restart_priority"])
            check_type(argname="argument ha_vm_restart_timeout", value=ha_vm_restart_timeout, expected_type=type_hints["ha_vm_restart_timeout"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "compute_cluster_id": compute_cluster_id,
            "virtual_machine_id": virtual_machine_id,
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
        if ha_datastore_apd_recovery_action is not None:
            self._values["ha_datastore_apd_recovery_action"] = ha_datastore_apd_recovery_action
        if ha_datastore_apd_response is not None:
            self._values["ha_datastore_apd_response"] = ha_datastore_apd_response
        if ha_datastore_apd_response_delay is not None:
            self._values["ha_datastore_apd_response_delay"] = ha_datastore_apd_response_delay
        if ha_datastore_pdl_response is not None:
            self._values["ha_datastore_pdl_response"] = ha_datastore_pdl_response
        if ha_host_isolation_response is not None:
            self._values["ha_host_isolation_response"] = ha_host_isolation_response
        if ha_vm_failure_interval is not None:
            self._values["ha_vm_failure_interval"] = ha_vm_failure_interval
        if ha_vm_maximum_failure_window is not None:
            self._values["ha_vm_maximum_failure_window"] = ha_vm_maximum_failure_window
        if ha_vm_maximum_resets is not None:
            self._values["ha_vm_maximum_resets"] = ha_vm_maximum_resets
        if ha_vm_minimum_uptime is not None:
            self._values["ha_vm_minimum_uptime"] = ha_vm_minimum_uptime
        if ha_vm_monitoring is not None:
            self._values["ha_vm_monitoring"] = ha_vm_monitoring
        if ha_vm_monitoring_use_cluster_defaults is not None:
            self._values["ha_vm_monitoring_use_cluster_defaults"] = ha_vm_monitoring_use_cluster_defaults
        if ha_vm_restart_priority is not None:
            self._values["ha_vm_restart_priority"] = ha_vm_restart_priority
        if ha_vm_restart_timeout is not None:
            self._values["ha_vm_restart_timeout"] = ha_vm_restart_timeout
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
    def compute_cluster_id(self) -> builtins.str:
        '''The managed object ID of the cluster.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#compute_cluster_id HaVmOverride#compute_cluster_id}
        '''
        result = self._values.get("compute_cluster_id")
        assert result is not None, "Required property 'compute_cluster_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def virtual_machine_id(self) -> builtins.str:
        '''The managed object ID of the virtual machine.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#virtual_machine_id HaVmOverride#virtual_machine_id}
        '''
        result = self._values.get("virtual_machine_id")
        assert result is not None, "Required property 'virtual_machine_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ha_datastore_apd_recovery_action(self) -> typing.Optional[builtins.str]:
        '''Controls the action to take on this virtual machine if an APD status on an affected datastore clears in the middle of an APD event.

        Can be one of useClusterDefault, none or reset.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#ha_datastore_apd_recovery_action HaVmOverride#ha_datastore_apd_recovery_action}
        '''
        result = self._values.get("ha_datastore_apd_recovery_action")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ha_datastore_apd_response(self) -> typing.Optional[builtins.str]:
        '''Controls the action to take on this virtual machine when the cluster has detected loss to all paths to a relevant datastore.

        Can be one of clusterDefault, disabled, warning, restartConservative, or restartAggressive.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#ha_datastore_apd_response HaVmOverride#ha_datastore_apd_response}
        '''
        result = self._values.get("ha_datastore_apd_response")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ha_datastore_apd_response_delay(self) -> typing.Optional[jsii.Number]:
        '''Controls the delay in seconds to wait after an APD timeout event to execute the response action defined in ha_datastore_apd_response.

        Specify -1 to use the cluster setting.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#ha_datastore_apd_response_delay HaVmOverride#ha_datastore_apd_response_delay}
        '''
        result = self._values.get("ha_datastore_apd_response_delay")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ha_datastore_pdl_response(self) -> typing.Optional[builtins.str]:
        '''Controls the action to take on this virtual machine when the cluster has detected a permanent device loss to a relevant datastore.

        Can be one of clusterDefault, disabled, warning, or restartAggressive.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#ha_datastore_pdl_response HaVmOverride#ha_datastore_pdl_response}
        '''
        result = self._values.get("ha_datastore_pdl_response")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ha_host_isolation_response(self) -> typing.Optional[builtins.str]:
        '''The action to take on this virtual machine when a host is isolated from the rest of the cluster.

        Can be one of clusterIsolationResponse, none, powerOff, or shutdown.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#ha_host_isolation_response HaVmOverride#ha_host_isolation_response}
        '''
        result = self._values.get("ha_host_isolation_response")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ha_vm_failure_interval(self) -> typing.Optional[jsii.Number]:
        '''If a heartbeat from this virtual machine is not received within this configured interval, the virtual machine is marked as failed.

        The value is in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#ha_vm_failure_interval HaVmOverride#ha_vm_failure_interval}
        '''
        result = self._values.get("ha_vm_failure_interval")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ha_vm_maximum_failure_window(self) -> typing.Optional[jsii.Number]:
        '''The length of the reset window in which ha_vm_maximum_resets can operate.

        When this window expires, no more resets are attempted regardless of the setting configured in ha_vm_maximum_resets. -1 means no window, meaning an unlimited reset time is allotted.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#ha_vm_maximum_failure_window HaVmOverride#ha_vm_maximum_failure_window}
        '''
        result = self._values.get("ha_vm_maximum_failure_window")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ha_vm_maximum_resets(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of resets that HA will perform to this virtual machine when responding to a failure event.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#ha_vm_maximum_resets HaVmOverride#ha_vm_maximum_resets}
        '''
        result = self._values.get("ha_vm_maximum_resets")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ha_vm_minimum_uptime(self) -> typing.Optional[jsii.Number]:
        '''The time, in seconds, that HA waits after powering on this virtual machine before monitoring for heartbeats.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#ha_vm_minimum_uptime HaVmOverride#ha_vm_minimum_uptime}
        '''
        result = self._values.get("ha_vm_minimum_uptime")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ha_vm_monitoring(self) -> typing.Optional[builtins.str]:
        '''The type of virtual machine monitoring to use for this virtual machine.

        Can be one of vmMonitoringDisabled, vmMonitoringOnly, or vmAndAppMonitoring.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#ha_vm_monitoring HaVmOverride#ha_vm_monitoring}
        '''
        result = self._values.get("ha_vm_monitoring")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ha_vm_monitoring_use_cluster_defaults(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Determines whether or not the cluster's default settings or the VM override settings specified in this resource are used for virtual machine monitoring.

        The default is true (use cluster defaults) - set to false to have overrides take effect.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#ha_vm_monitoring_use_cluster_defaults HaVmOverride#ha_vm_monitoring_use_cluster_defaults}
        '''
        result = self._values.get("ha_vm_monitoring_use_cluster_defaults")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def ha_vm_restart_priority(self) -> typing.Optional[builtins.str]:
        '''The restart priority for this virtual machine when vSphere detects a host failure.

        Can be one of clusterRestartPriority, lowest, low, medium, high, or highest.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#ha_vm_restart_priority HaVmOverride#ha_vm_restart_priority}
        '''
        result = self._values.get("ha_vm_restart_priority")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ha_vm_restart_timeout(self) -> typing.Optional[jsii.Number]:
        '''The maximum time, in seconds, that vSphere HA will wait for the virtual machine to be ready.

        Use -1 to use the cluster default.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#ha_vm_restart_timeout HaVmOverride#ha_vm_restart_timeout}
        '''
        result = self._values.get("ha_vm_restart_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/ha_vm_override#id HaVmOverride#id}.

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
        return "HaVmOverrideConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "HaVmOverride",
    "HaVmOverrideConfig",
]

publication.publish()

def _typecheckingstub__4a362f73d90dca8d6f75702e2c8edfa896016f62abcf695a0bb12dce218c9b52(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    compute_cluster_id: builtins.str,
    virtual_machine_id: builtins.str,
    ha_datastore_apd_recovery_action: typing.Optional[builtins.str] = None,
    ha_datastore_apd_response: typing.Optional[builtins.str] = None,
    ha_datastore_apd_response_delay: typing.Optional[jsii.Number] = None,
    ha_datastore_pdl_response: typing.Optional[builtins.str] = None,
    ha_host_isolation_response: typing.Optional[builtins.str] = None,
    ha_vm_failure_interval: typing.Optional[jsii.Number] = None,
    ha_vm_maximum_failure_window: typing.Optional[jsii.Number] = None,
    ha_vm_maximum_resets: typing.Optional[jsii.Number] = None,
    ha_vm_minimum_uptime: typing.Optional[jsii.Number] = None,
    ha_vm_monitoring: typing.Optional[builtins.str] = None,
    ha_vm_monitoring_use_cluster_defaults: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ha_vm_restart_priority: typing.Optional[builtins.str] = None,
    ha_vm_restart_timeout: typing.Optional[jsii.Number] = None,
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

def _typecheckingstub__0bc88d1e41d4ddea6cf59b23d4a5178209fae0ac97f6f35da88169dac3122584(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__557177dab0528ece41558a7ac7697cdc548705065084adfce0800056b354f542(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f256c9f5050cae30a5a4f8f84e0d110d8cb3e7154b5d7ce034f1ddd3a4755dde(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea523e6cfa809bc283af2f4d1418635e8b0452b4efe74792eee607e933770039(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3bb6e4e2851b4c7f6f866494f79bd71ac773b9a38038c4e55301d6a52bc44af6(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e22a9d6bb85c6efc7c2baafccc2b8071147dd5370530bee0151877299c60974e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24eba372c4dc3ddc05440c19146b3817dd93055e36990f719a011fa8048bf5dd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a59c2467408e14a5e776a9e38b168395004c9fd9f69bfe0b0748e87709d7f1c7(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eea261c1919e23959fbc771dc8fed0ba219ccaf427929a2aea52452d0257af20(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ba13c4bac5f6d4f97d2d9cf98d2cc9050cce14ac68ccf13fb46528af4b3e189(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5819c3f82d8cd9a9505ec0a3e32598c1033cbf11867093eb9bd1557090a9a126(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6565e93f8c94253a21c6a9d461bb5ae54dfdf0c875f59e6a6c268a04b54dfdd3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4345868e87693c387b7b01181a722805772338361c6ad67afdf1d2eef49c9d67(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ab3125195723f9f4b8d007e0cd7be6e953d4e31cd75b5f453a0e7e7764e6638(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd4786a1c82dd41dcc593f0da050522c92f7195bb8a390e5d69cc31976fdb386(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__502e30cf9cca42e53c488650d96eb7a63bc4d956fb3151070c6f901c2ef636ed(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__915f3a1552773b6d97f4e79c4793bdba2607ceed57f0167a116aebed4b41dc2a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e901efdc3423ad9e40b41b2f1f51e91d15a27b4686337b35e9a82d02a3e9143(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    compute_cluster_id: builtins.str,
    virtual_machine_id: builtins.str,
    ha_datastore_apd_recovery_action: typing.Optional[builtins.str] = None,
    ha_datastore_apd_response: typing.Optional[builtins.str] = None,
    ha_datastore_apd_response_delay: typing.Optional[jsii.Number] = None,
    ha_datastore_pdl_response: typing.Optional[builtins.str] = None,
    ha_host_isolation_response: typing.Optional[builtins.str] = None,
    ha_vm_failure_interval: typing.Optional[jsii.Number] = None,
    ha_vm_maximum_failure_window: typing.Optional[jsii.Number] = None,
    ha_vm_maximum_resets: typing.Optional[jsii.Number] = None,
    ha_vm_minimum_uptime: typing.Optional[jsii.Number] = None,
    ha_vm_monitoring: typing.Optional[builtins.str] = None,
    ha_vm_monitoring_use_cluster_defaults: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ha_vm_restart_priority: typing.Optional[builtins.str] = None,
    ha_vm_restart_timeout: typing.Optional[jsii.Number] = None,
    id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
