r'''
# `vsphere_vnic`

Refer to the Terraform Registry for docs: [`vsphere_vnic`](https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic).
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


class Vnic(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.vnic.Vnic",
):
    '''Represents a {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic vsphere_vnic}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        host: builtins.str,
        distributed_port_group: typing.Optional[builtins.str] = None,
        distributed_switch_port: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        ipv4: typing.Optional[typing.Union["VnicIpv4", typing.Dict[builtins.str, typing.Any]]] = None,
        ipv6: typing.Optional[typing.Union["VnicIpv6", typing.Dict[builtins.str, typing.Any]]] = None,
        mac: typing.Optional[builtins.str] = None,
        mtu: typing.Optional[jsii.Number] = None,
        netstack: typing.Optional[builtins.str] = None,
        portgroup: typing.Optional[builtins.str] = None,
        services: typing.Optional[typing.Sequence[builtins.str]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic vsphere_vnic} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param host: ESX host the interface belongs to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#host Vnic#host}
        :param distributed_port_group: Key of the distributed portgroup the nic will connect to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#distributed_port_group Vnic#distributed_port_group}
        :param distributed_switch_port: UUID of the DVSwitch the nic will be attached to. Do not set if you set portgroup. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#distributed_switch_port Vnic#distributed_switch_port}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#id Vnic#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param ipv4: ipv4 block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#ipv4 Vnic#ipv4}
        :param ipv6: ipv6 block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#ipv6 Vnic#ipv6}
        :param mac: MAC address of the interface. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#mac Vnic#mac}
        :param mtu: MTU of the interface. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#mtu Vnic#mtu}
        :param netstack: TCP/IP stack setting for this interface. Possible values are 'defaultTcpipStack', 'vmotion', 'provisioning'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#netstack Vnic#netstack}
        :param portgroup: portgroup to attach the nic to. Do not set if you set distributed_switch_port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#portgroup Vnic#portgroup}
        :param services: Enabled services setting for this interface. Current possible values are 'vmotion', 'management' and 'vsan'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#services Vnic#services}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc55ec4560b3c2924d86861886726d360d68939a52c02ef84d6ed7544ec911df)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = VnicConfig(
            host=host,
            distributed_port_group=distributed_port_group,
            distributed_switch_port=distributed_switch_port,
            id=id,
            ipv4=ipv4,
            ipv6=ipv6,
            mac=mac,
            mtu=mtu,
            netstack=netstack,
            portgroup=portgroup,
            services=services,
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
        '''Generates CDKTF code for importing a Vnic resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the Vnic to import.
        :param import_from_id: The id of the existing Vnic that should be imported. Refer to the {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the Vnic to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47bd4a708ce5cd7b2ed9752fc1eb6e65c913c715731ba0c71ce5dda5585328bf)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putIpv4")
    def put_ipv4(
        self,
        *,
        dhcp: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        gw: typing.Optional[builtins.str] = None,
        ip: typing.Optional[builtins.str] = None,
        netmask: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param dhcp: Use DHCP to configure the interface's IPv4 stack. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#dhcp Vnic#dhcp}
        :param gw: IP address of the default gateway, if DHCP is not set. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#gw Vnic#gw}
        :param ip: address of the interface, if DHCP is not set. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#ip Vnic#ip}
        :param netmask: netmask of the interface, if DHCP is not set. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#netmask Vnic#netmask}
        '''
        value = VnicIpv4(dhcp=dhcp, gw=gw, ip=ip, netmask=netmask)

        return typing.cast(None, jsii.invoke(self, "putIpv4", [value]))

    @jsii.member(jsii_name="putIpv6")
    def put_ipv6(
        self,
        *,
        addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
        autoconfig: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        dhcp: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        gw: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param addresses: List of IPv6 addresses. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#addresses Vnic#addresses}
        :param autoconfig: Use IPv6 Autoconfiguration (RFC2462). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#autoconfig Vnic#autoconfig}
        :param dhcp: Use DHCP to configure the interface's IPv4 stack. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#dhcp Vnic#dhcp}
        :param gw: IP address of the default gateway, if DHCP or autoconfig is not set. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#gw Vnic#gw}
        '''
        value = VnicIpv6(addresses=addresses, autoconfig=autoconfig, dhcp=dhcp, gw=gw)

        return typing.cast(None, jsii.invoke(self, "putIpv6", [value]))

    @jsii.member(jsii_name="resetDistributedPortGroup")
    def reset_distributed_port_group(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDistributedPortGroup", []))

    @jsii.member(jsii_name="resetDistributedSwitchPort")
    def reset_distributed_switch_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDistributedSwitchPort", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIpv4")
    def reset_ipv4(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpv4", []))

    @jsii.member(jsii_name="resetIpv6")
    def reset_ipv6(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpv6", []))

    @jsii.member(jsii_name="resetMac")
    def reset_mac(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMac", []))

    @jsii.member(jsii_name="resetMtu")
    def reset_mtu(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMtu", []))

    @jsii.member(jsii_name="resetNetstack")
    def reset_netstack(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetstack", []))

    @jsii.member(jsii_name="resetPortgroup")
    def reset_portgroup(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPortgroup", []))

    @jsii.member(jsii_name="resetServices")
    def reset_services(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServices", []))

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
    @jsii.member(jsii_name="ipv4")
    def ipv4(self) -> "VnicIpv4OutputReference":
        return typing.cast("VnicIpv4OutputReference", jsii.get(self, "ipv4"))

    @builtins.property
    @jsii.member(jsii_name="ipv6")
    def ipv6(self) -> "VnicIpv6OutputReference":
        return typing.cast("VnicIpv6OutputReference", jsii.get(self, "ipv6"))

    @builtins.property
    @jsii.member(jsii_name="distributedPortGroupInput")
    def distributed_port_group_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "distributedPortGroupInput"))

    @builtins.property
    @jsii.member(jsii_name="distributedSwitchPortInput")
    def distributed_switch_port_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "distributedSwitchPortInput"))

    @builtins.property
    @jsii.member(jsii_name="hostInput")
    def host_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="ipv4Input")
    def ipv4_input(self) -> typing.Optional["VnicIpv4"]:
        return typing.cast(typing.Optional["VnicIpv4"], jsii.get(self, "ipv4Input"))

    @builtins.property
    @jsii.member(jsii_name="ipv6Input")
    def ipv6_input(self) -> typing.Optional["VnicIpv6"]:
        return typing.cast(typing.Optional["VnicIpv6"], jsii.get(self, "ipv6Input"))

    @builtins.property
    @jsii.member(jsii_name="macInput")
    def mac_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "macInput"))

    @builtins.property
    @jsii.member(jsii_name="mtuInput")
    def mtu_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "mtuInput"))

    @builtins.property
    @jsii.member(jsii_name="netstackInput")
    def netstack_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "netstackInput"))

    @builtins.property
    @jsii.member(jsii_name="portgroupInput")
    def portgroup_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "portgroupInput"))

    @builtins.property
    @jsii.member(jsii_name="servicesInput")
    def services_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "servicesInput"))

    @builtins.property
    @jsii.member(jsii_name="distributedPortGroup")
    def distributed_port_group(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "distributedPortGroup"))

    @distributed_port_group.setter
    def distributed_port_group(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dff968615d10d37b5c81eb031fa0db3a3615be34cf5135737557bd9e738a646a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "distributedPortGroup", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="distributedSwitchPort")
    def distributed_switch_port(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "distributedSwitchPort"))

    @distributed_switch_port.setter
    def distributed_switch_port(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__045236e20bbe70cf4ac9a97a8040fc0d0db5a8af01ce5083aa666c262aabedec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "distributedSwitchPort", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="host")
    def host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "host"))

    @host.setter
    def host(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d31cc9df9a09b1a79091d1e8e5a9451e8651ece2dc2ceabd5ab0431b336b51c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "host", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08b3b72ebedb095960313d06bee9ef86ab87dd6320effefc455d12793dbb6e6b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="mac")
    def mac(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mac"))

    @mac.setter
    def mac(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cbefdfb6c323570ca0f90f55655710bda687fc02790e6f007afc2b7e55663273)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mac", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="mtu")
    def mtu(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "mtu"))

    @mtu.setter
    def mtu(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3893684cd3f339dfdfeb76905fdfacc691b56ddcdee499a7eef00a25c1bd602d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mtu", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="netstack")
    def netstack(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "netstack"))

    @netstack.setter
    def netstack(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__293d910b7325dc27bd69028a7e65dac9282de9b527f43b320443558facc60666)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "netstack", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="portgroup")
    def portgroup(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "portgroup"))

    @portgroup.setter
    def portgroup(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2bc0d1479cc1e161ee0ace386202b6178125cab3b270190c3dd71c84a4e03404)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "portgroup", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="services")
    def services(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "services"))

    @services.setter
    def services(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__774adc7a51516f699169cb7e38eaf3afcaab08cde33f45e1993f1391e05d1d10)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "services", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.vnic.VnicConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "host": "host",
        "distributed_port_group": "distributedPortGroup",
        "distributed_switch_port": "distributedSwitchPort",
        "id": "id",
        "ipv4": "ipv4",
        "ipv6": "ipv6",
        "mac": "mac",
        "mtu": "mtu",
        "netstack": "netstack",
        "portgroup": "portgroup",
        "services": "services",
    },
)
class VnicConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        host: builtins.str,
        distributed_port_group: typing.Optional[builtins.str] = None,
        distributed_switch_port: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        ipv4: typing.Optional[typing.Union["VnicIpv4", typing.Dict[builtins.str, typing.Any]]] = None,
        ipv6: typing.Optional[typing.Union["VnicIpv6", typing.Dict[builtins.str, typing.Any]]] = None,
        mac: typing.Optional[builtins.str] = None,
        mtu: typing.Optional[jsii.Number] = None,
        netstack: typing.Optional[builtins.str] = None,
        portgroup: typing.Optional[builtins.str] = None,
        services: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param host: ESX host the interface belongs to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#host Vnic#host}
        :param distributed_port_group: Key of the distributed portgroup the nic will connect to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#distributed_port_group Vnic#distributed_port_group}
        :param distributed_switch_port: UUID of the DVSwitch the nic will be attached to. Do not set if you set portgroup. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#distributed_switch_port Vnic#distributed_switch_port}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#id Vnic#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param ipv4: ipv4 block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#ipv4 Vnic#ipv4}
        :param ipv6: ipv6 block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#ipv6 Vnic#ipv6}
        :param mac: MAC address of the interface. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#mac Vnic#mac}
        :param mtu: MTU of the interface. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#mtu Vnic#mtu}
        :param netstack: TCP/IP stack setting for this interface. Possible values are 'defaultTcpipStack', 'vmotion', 'provisioning'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#netstack Vnic#netstack}
        :param portgroup: portgroup to attach the nic to. Do not set if you set distributed_switch_port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#portgroup Vnic#portgroup}
        :param services: Enabled services setting for this interface. Current possible values are 'vmotion', 'management' and 'vsan'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#services Vnic#services}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(ipv4, dict):
            ipv4 = VnicIpv4(**ipv4)
        if isinstance(ipv6, dict):
            ipv6 = VnicIpv6(**ipv6)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__398fbb5e2b3ed8a654a13d2b8ed247cac901f6f9dd24bf4ee1328421590a92f2)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument host", value=host, expected_type=type_hints["host"])
            check_type(argname="argument distributed_port_group", value=distributed_port_group, expected_type=type_hints["distributed_port_group"])
            check_type(argname="argument distributed_switch_port", value=distributed_switch_port, expected_type=type_hints["distributed_switch_port"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument ipv4", value=ipv4, expected_type=type_hints["ipv4"])
            check_type(argname="argument ipv6", value=ipv6, expected_type=type_hints["ipv6"])
            check_type(argname="argument mac", value=mac, expected_type=type_hints["mac"])
            check_type(argname="argument mtu", value=mtu, expected_type=type_hints["mtu"])
            check_type(argname="argument netstack", value=netstack, expected_type=type_hints["netstack"])
            check_type(argname="argument portgroup", value=portgroup, expected_type=type_hints["portgroup"])
            check_type(argname="argument services", value=services, expected_type=type_hints["services"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "host": host,
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
        if distributed_port_group is not None:
            self._values["distributed_port_group"] = distributed_port_group
        if distributed_switch_port is not None:
            self._values["distributed_switch_port"] = distributed_switch_port
        if id is not None:
            self._values["id"] = id
        if ipv4 is not None:
            self._values["ipv4"] = ipv4
        if ipv6 is not None:
            self._values["ipv6"] = ipv6
        if mac is not None:
            self._values["mac"] = mac
        if mtu is not None:
            self._values["mtu"] = mtu
        if netstack is not None:
            self._values["netstack"] = netstack
        if portgroup is not None:
            self._values["portgroup"] = portgroup
        if services is not None:
            self._values["services"] = services

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
    def host(self) -> builtins.str:
        '''ESX host the interface belongs to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#host Vnic#host}
        '''
        result = self._values.get("host")
        assert result is not None, "Required property 'host' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def distributed_port_group(self) -> typing.Optional[builtins.str]:
        '''Key of the distributed portgroup the nic will connect to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#distributed_port_group Vnic#distributed_port_group}
        '''
        result = self._values.get("distributed_port_group")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def distributed_switch_port(self) -> typing.Optional[builtins.str]:
        '''UUID of the DVSwitch the nic will be attached to. Do not set if you set portgroup.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#distributed_switch_port Vnic#distributed_switch_port}
        '''
        result = self._values.get("distributed_switch_port")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#id Vnic#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ipv4(self) -> typing.Optional["VnicIpv4"]:
        '''ipv4 block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#ipv4 Vnic#ipv4}
        '''
        result = self._values.get("ipv4")
        return typing.cast(typing.Optional["VnicIpv4"], result)

    @builtins.property
    def ipv6(self) -> typing.Optional["VnicIpv6"]:
        '''ipv6 block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#ipv6 Vnic#ipv6}
        '''
        result = self._values.get("ipv6")
        return typing.cast(typing.Optional["VnicIpv6"], result)

    @builtins.property
    def mac(self) -> typing.Optional[builtins.str]:
        '''MAC address of the interface.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#mac Vnic#mac}
        '''
        result = self._values.get("mac")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mtu(self) -> typing.Optional[jsii.Number]:
        '''MTU of the interface.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#mtu Vnic#mtu}
        '''
        result = self._values.get("mtu")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def netstack(self) -> typing.Optional[builtins.str]:
        '''TCP/IP stack setting for this interface. Possible values are 'defaultTcpipStack', 'vmotion', 'provisioning'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#netstack Vnic#netstack}
        '''
        result = self._values.get("netstack")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def portgroup(self) -> typing.Optional[builtins.str]:
        '''portgroup to attach the nic to. Do not set if you set distributed_switch_port.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#portgroup Vnic#portgroup}
        '''
        result = self._values.get("portgroup")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def services(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Enabled services setting for this interface. Current possible values are 'vmotion', 'management' and 'vsan'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#services Vnic#services}
        '''
        result = self._values.get("services")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VnicConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.vnic.VnicIpv4",
    jsii_struct_bases=[],
    name_mapping={"dhcp": "dhcp", "gw": "gw", "ip": "ip", "netmask": "netmask"},
)
class VnicIpv4:
    def __init__(
        self,
        *,
        dhcp: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        gw: typing.Optional[builtins.str] = None,
        ip: typing.Optional[builtins.str] = None,
        netmask: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param dhcp: Use DHCP to configure the interface's IPv4 stack. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#dhcp Vnic#dhcp}
        :param gw: IP address of the default gateway, if DHCP is not set. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#gw Vnic#gw}
        :param ip: address of the interface, if DHCP is not set. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#ip Vnic#ip}
        :param netmask: netmask of the interface, if DHCP is not set. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#netmask Vnic#netmask}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a4fa94b5124279e0c900f135a3fb5f8a49bfd00cc80eee7a17952c47efae67a)
            check_type(argname="argument dhcp", value=dhcp, expected_type=type_hints["dhcp"])
            check_type(argname="argument gw", value=gw, expected_type=type_hints["gw"])
            check_type(argname="argument ip", value=ip, expected_type=type_hints["ip"])
            check_type(argname="argument netmask", value=netmask, expected_type=type_hints["netmask"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if dhcp is not None:
            self._values["dhcp"] = dhcp
        if gw is not None:
            self._values["gw"] = gw
        if ip is not None:
            self._values["ip"] = ip
        if netmask is not None:
            self._values["netmask"] = netmask

    @builtins.property
    def dhcp(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Use DHCP to configure the interface's IPv4 stack.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#dhcp Vnic#dhcp}
        '''
        result = self._values.get("dhcp")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def gw(self) -> typing.Optional[builtins.str]:
        '''IP address of the default gateway, if DHCP is not set.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#gw Vnic#gw}
        '''
        result = self._values.get("gw")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ip(self) -> typing.Optional[builtins.str]:
        '''address of the interface, if DHCP is not set.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#ip Vnic#ip}
        '''
        result = self._values.get("ip")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def netmask(self) -> typing.Optional[builtins.str]:
        '''netmask of the interface, if DHCP is not set.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#netmask Vnic#netmask}
        '''
        result = self._values.get("netmask")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VnicIpv4(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class VnicIpv4OutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.vnic.VnicIpv4OutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f3bc772bb62f352d3f9fe7177fcef5e0a1752d23cf57c9fa478a40f35034f133)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDhcp")
    def reset_dhcp(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDhcp", []))

    @jsii.member(jsii_name="resetGw")
    def reset_gw(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGw", []))

    @jsii.member(jsii_name="resetIp")
    def reset_ip(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIp", []))

    @jsii.member(jsii_name="resetNetmask")
    def reset_netmask(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetmask", []))

    @builtins.property
    @jsii.member(jsii_name="dhcpInput")
    def dhcp_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "dhcpInput"))

    @builtins.property
    @jsii.member(jsii_name="gwInput")
    def gw_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gwInput"))

    @builtins.property
    @jsii.member(jsii_name="ipInput")
    def ip_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ipInput"))

    @builtins.property
    @jsii.member(jsii_name="netmaskInput")
    def netmask_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "netmaskInput"))

    @builtins.property
    @jsii.member(jsii_name="dhcp")
    def dhcp(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "dhcp"))

    @dhcp.setter
    def dhcp(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__802dbbfe2847a9f14b621c42dafcfb430277ebf1fee1eac15db98982a5cee4c5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dhcp", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="gw")
    def gw(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gw"))

    @gw.setter
    def gw(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e256e59fd72006c09b00119472f82d4e21fe4cc17e7a9cecb0716216c80a5b8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gw", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ip")
    def ip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ip"))

    @ip.setter
    def ip(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__deea09411059bcfd75731c98f435e831a55781b5f675b5dfe506679fa51bb59e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ip", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="netmask")
    def netmask(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "netmask"))

    @netmask.setter
    def netmask(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ebfdf110fd08377e0bde0b5c2897cc8b057f343cb5a2e282e9e5879fd57b6e04)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "netmask", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[VnicIpv4]:
        return typing.cast(typing.Optional[VnicIpv4], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[VnicIpv4]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22afec6f86c82326cf1fc6fcc7b0b1de43e075751a3315382a8fb7455ce15ba6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.vnic.VnicIpv6",
    jsii_struct_bases=[],
    name_mapping={
        "addresses": "addresses",
        "autoconfig": "autoconfig",
        "dhcp": "dhcp",
        "gw": "gw",
    },
)
class VnicIpv6:
    def __init__(
        self,
        *,
        addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
        autoconfig: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        dhcp: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        gw: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param addresses: List of IPv6 addresses. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#addresses Vnic#addresses}
        :param autoconfig: Use IPv6 Autoconfiguration (RFC2462). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#autoconfig Vnic#autoconfig}
        :param dhcp: Use DHCP to configure the interface's IPv4 stack. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#dhcp Vnic#dhcp}
        :param gw: IP address of the default gateway, if DHCP or autoconfig is not set. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#gw Vnic#gw}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a18bfd2ed366a9267149629148243a91d61821cd0a2e8f2490cac459f6385a8)
            check_type(argname="argument addresses", value=addresses, expected_type=type_hints["addresses"])
            check_type(argname="argument autoconfig", value=autoconfig, expected_type=type_hints["autoconfig"])
            check_type(argname="argument dhcp", value=dhcp, expected_type=type_hints["dhcp"])
            check_type(argname="argument gw", value=gw, expected_type=type_hints["gw"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if addresses is not None:
            self._values["addresses"] = addresses
        if autoconfig is not None:
            self._values["autoconfig"] = autoconfig
        if dhcp is not None:
            self._values["dhcp"] = dhcp
        if gw is not None:
            self._values["gw"] = gw

    @builtins.property
    def addresses(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of IPv6 addresses.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#addresses Vnic#addresses}
        '''
        result = self._values.get("addresses")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def autoconfig(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Use IPv6 Autoconfiguration (RFC2462).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#autoconfig Vnic#autoconfig}
        '''
        result = self._values.get("autoconfig")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def dhcp(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Use DHCP to configure the interface's IPv4 stack.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#dhcp Vnic#dhcp}
        '''
        result = self._values.get("dhcp")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def gw(self) -> typing.Optional[builtins.str]:
        '''IP address of the default gateway, if DHCP or autoconfig is not set.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/vnic#gw Vnic#gw}
        '''
        result = self._values.get("gw")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VnicIpv6(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class VnicIpv6OutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.vnic.VnicIpv6OutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9f6024fc04245b96defdb175a82fda0b68ef8c24caaeec1f7e1e0d7fe56ca20c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAddresses")
    def reset_addresses(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAddresses", []))

    @jsii.member(jsii_name="resetAutoconfig")
    def reset_autoconfig(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoconfig", []))

    @jsii.member(jsii_name="resetDhcp")
    def reset_dhcp(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDhcp", []))

    @jsii.member(jsii_name="resetGw")
    def reset_gw(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGw", []))

    @builtins.property
    @jsii.member(jsii_name="addressesInput")
    def addresses_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "addressesInput"))

    @builtins.property
    @jsii.member(jsii_name="autoconfigInput")
    def autoconfig_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "autoconfigInput"))

    @builtins.property
    @jsii.member(jsii_name="dhcpInput")
    def dhcp_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "dhcpInput"))

    @builtins.property
    @jsii.member(jsii_name="gwInput")
    def gw_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gwInput"))

    @builtins.property
    @jsii.member(jsii_name="addresses")
    def addresses(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "addresses"))

    @addresses.setter
    def addresses(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__37ce00cb38b9eaf3b403fefcc640b1eacf92914eee3beb05ebbfe8edcdee0497)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "addresses", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="autoconfig")
    def autoconfig(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "autoconfig"))

    @autoconfig.setter
    def autoconfig(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0422d0ba8b523422d82848bf0b53d9c3f7f7c6093ef037296383d5e909150f0d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoconfig", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dhcp")
    def dhcp(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "dhcp"))

    @dhcp.setter
    def dhcp(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__122869659500fd144908c55318213d38ef37c221aca74fce1191f86c4aa7cb66)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dhcp", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="gw")
    def gw(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gw"))

    @gw.setter
    def gw(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de253483dc7b6cc5866ac04c87b868e0df8c3784dad4d69d6e3608e46e222a26)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gw", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[VnicIpv6]:
        return typing.cast(typing.Optional[VnicIpv6], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[VnicIpv6]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__469f9e327ac5e0c4e36dca803a78f3bdddd0c0d66e08c05d589ce10a82eaad2c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "Vnic",
    "VnicConfig",
    "VnicIpv4",
    "VnicIpv4OutputReference",
    "VnicIpv6",
    "VnicIpv6OutputReference",
]

publication.publish()

def _typecheckingstub__fc55ec4560b3c2924d86861886726d360d68939a52c02ef84d6ed7544ec911df(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    host: builtins.str,
    distributed_port_group: typing.Optional[builtins.str] = None,
    distributed_switch_port: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    ipv4: typing.Optional[typing.Union[VnicIpv4, typing.Dict[builtins.str, typing.Any]]] = None,
    ipv6: typing.Optional[typing.Union[VnicIpv6, typing.Dict[builtins.str, typing.Any]]] = None,
    mac: typing.Optional[builtins.str] = None,
    mtu: typing.Optional[jsii.Number] = None,
    netstack: typing.Optional[builtins.str] = None,
    portgroup: typing.Optional[builtins.str] = None,
    services: typing.Optional[typing.Sequence[builtins.str]] = None,
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

def _typecheckingstub__47bd4a708ce5cd7b2ed9752fc1eb6e65c913c715731ba0c71ce5dda5585328bf(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dff968615d10d37b5c81eb031fa0db3a3615be34cf5135737557bd9e738a646a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__045236e20bbe70cf4ac9a97a8040fc0d0db5a8af01ce5083aa666c262aabedec(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d31cc9df9a09b1a79091d1e8e5a9451e8651ece2dc2ceabd5ab0431b336b51c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08b3b72ebedb095960313d06bee9ef86ab87dd6320effefc455d12793dbb6e6b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cbefdfb6c323570ca0f90f55655710bda687fc02790e6f007afc2b7e55663273(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3893684cd3f339dfdfeb76905fdfacc691b56ddcdee499a7eef00a25c1bd602d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__293d910b7325dc27bd69028a7e65dac9282de9b527f43b320443558facc60666(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2bc0d1479cc1e161ee0ace386202b6178125cab3b270190c3dd71c84a4e03404(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__774adc7a51516f699169cb7e38eaf3afcaab08cde33f45e1993f1391e05d1d10(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__398fbb5e2b3ed8a654a13d2b8ed247cac901f6f9dd24bf4ee1328421590a92f2(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    host: builtins.str,
    distributed_port_group: typing.Optional[builtins.str] = None,
    distributed_switch_port: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    ipv4: typing.Optional[typing.Union[VnicIpv4, typing.Dict[builtins.str, typing.Any]]] = None,
    ipv6: typing.Optional[typing.Union[VnicIpv6, typing.Dict[builtins.str, typing.Any]]] = None,
    mac: typing.Optional[builtins.str] = None,
    mtu: typing.Optional[jsii.Number] = None,
    netstack: typing.Optional[builtins.str] = None,
    portgroup: typing.Optional[builtins.str] = None,
    services: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a4fa94b5124279e0c900f135a3fb5f8a49bfd00cc80eee7a17952c47efae67a(
    *,
    dhcp: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    gw: typing.Optional[builtins.str] = None,
    ip: typing.Optional[builtins.str] = None,
    netmask: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3bc772bb62f352d3f9fe7177fcef5e0a1752d23cf57c9fa478a40f35034f133(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__802dbbfe2847a9f14b621c42dafcfb430277ebf1fee1eac15db98982a5cee4c5(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e256e59fd72006c09b00119472f82d4e21fe4cc17e7a9cecb0716216c80a5b8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__deea09411059bcfd75731c98f435e831a55781b5f675b5dfe506679fa51bb59e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebfdf110fd08377e0bde0b5c2897cc8b057f343cb5a2e282e9e5879fd57b6e04(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22afec6f86c82326cf1fc6fcc7b0b1de43e075751a3315382a8fb7455ce15ba6(
    value: typing.Optional[VnicIpv4],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a18bfd2ed366a9267149629148243a91d61821cd0a2e8f2490cac459f6385a8(
    *,
    addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
    autoconfig: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    dhcp: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    gw: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f6024fc04245b96defdb175a82fda0b68ef8c24caaeec1f7e1e0d7fe56ca20c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37ce00cb38b9eaf3b403fefcc640b1eacf92914eee3beb05ebbfe8edcdee0497(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0422d0ba8b523422d82848bf0b53d9c3f7f7c6093ef037296383d5e909150f0d(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__122869659500fd144908c55318213d38ef37c221aca74fce1191f86c4aa7cb66(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de253483dc7b6cc5866ac04c87b868e0df8c3784dad4d69d6e3608e46e222a26(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__469f9e327ac5e0c4e36dca803a78f3bdddd0c0d66e08c05d589ce10a82eaad2c(
    value: typing.Optional[VnicIpv6],
) -> None:
    """Type checking stubs"""
    pass
