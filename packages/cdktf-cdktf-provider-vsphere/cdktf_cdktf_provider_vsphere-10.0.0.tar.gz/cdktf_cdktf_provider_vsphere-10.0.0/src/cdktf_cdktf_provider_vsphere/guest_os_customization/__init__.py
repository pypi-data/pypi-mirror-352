r'''
# `vsphere_guest_os_customization`

Refer to the Terraform Registry for docs: [`vsphere_guest_os_customization`](https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization).
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


class GuestOsCustomization(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.guestOsCustomization.GuestOsCustomization",
):
    '''Represents a {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization vsphere_guest_os_customization}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        spec: typing.Union["GuestOsCustomizationSpec", typing.Dict[builtins.str, typing.Any]],
        type: builtins.str,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization vsphere_guest_os_customization} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: The name of the customization specification is the unique identifier per vCenter Server instance. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#name GuestOsCustomization#name}
        :param spec: spec block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#spec GuestOsCustomization#spec}
        :param type: The type of customization specification: One among: Windows, Linux. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#type GuestOsCustomization#type}
        :param description: The description for the customization specification. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#description GuestOsCustomization#description}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#id GuestOsCustomization#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f7f4d26a0c2a85584648ff341ccf75385e7c9482ffd9428e3bc8f4fbc8d14a05)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = GuestOsCustomizationConfig(
            name=name,
            spec=spec,
            type=type,
            description=description,
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
        '''Generates CDKTF code for importing a GuestOsCustomization resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the GuestOsCustomization to import.
        :param import_from_id: The id of the existing GuestOsCustomization that should be imported. Refer to the {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the GuestOsCustomization to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e72c000958b374d71e1e7f3c9386da36d68a257a8054df388c6db8e94b064b10)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putSpec")
    def put_spec(
        self,
        *,
        dns_server_list: typing.Optional[typing.Sequence[builtins.str]] = None,
        dns_suffix_list: typing.Optional[typing.Sequence[builtins.str]] = None,
        ipv4_gateway: typing.Optional[builtins.str] = None,
        ipv6_gateway: typing.Optional[builtins.str] = None,
        linux_options: typing.Optional[typing.Union["GuestOsCustomizationSpecLinuxOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        network_interface: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GuestOsCustomizationSpecNetworkInterface", typing.Dict[builtins.str, typing.Any]]]]] = None,
        windows_options: typing.Optional[typing.Union["GuestOsCustomizationSpecWindowsOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        windows_sysprep_text: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param dns_server_list: The list of DNS servers for a virtual network adapter with a static IP address. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#dns_server_list GuestOsCustomization#dns_server_list}
        :param dns_suffix_list: A list of DNS search domains to add to the DNS configuration on the virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#dns_suffix_list GuestOsCustomization#dns_suffix_list}
        :param ipv4_gateway: The IPv4 default gateway when using network_interface customization on the virtual machine. This address must be local to a static IPv4 address configured in an interface sub-resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#ipv4_gateway GuestOsCustomization#ipv4_gateway}
        :param ipv6_gateway: The IPv6 default gateway when using network_interface customization on the virtual machine. This address must be local to a static IPv4 address configured in an interface sub-resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#ipv6_gateway GuestOsCustomization#ipv6_gateway}
        :param linux_options: linux_options block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#linux_options GuestOsCustomization#linux_options}
        :param network_interface: network_interface block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#network_interface GuestOsCustomization#network_interface}
        :param windows_options: windows_options block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#windows_options GuestOsCustomization#windows_options}
        :param windows_sysprep_text: Use this option to specify a windows sysprep file directly. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#windows_sysprep_text GuestOsCustomization#windows_sysprep_text}
        '''
        value = GuestOsCustomizationSpec(
            dns_server_list=dns_server_list,
            dns_suffix_list=dns_suffix_list,
            ipv4_gateway=ipv4_gateway,
            ipv6_gateway=ipv6_gateway,
            linux_options=linux_options,
            network_interface=network_interface,
            windows_options=windows_options,
            windows_sysprep_text=windows_sysprep_text,
        )

        return typing.cast(None, jsii.invoke(self, "putSpec", [value]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

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
    @jsii.member(jsii_name="changeVersion")
    def change_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "changeVersion"))

    @builtins.property
    @jsii.member(jsii_name="lastUpdateTime")
    def last_update_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastUpdateTime"))

    @builtins.property
    @jsii.member(jsii_name="spec")
    def spec(self) -> "GuestOsCustomizationSpecOutputReference":
        return typing.cast("GuestOsCustomizationSpecOutputReference", jsii.get(self, "spec"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="specInput")
    def spec_input(self) -> typing.Optional["GuestOsCustomizationSpec"]:
        return typing.cast(typing.Optional["GuestOsCustomizationSpec"], jsii.get(self, "specInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2878744098b51ea1c484b86e3f3803f5d4a60cfcd9133464461e2c32db859ec3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__234cdc1e12976d1638f0c84b00f6d7ea9d0c0d141f0dc0efa171289558d5f4f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__343c50c7b6ac40f364da0dcc3c7f520fbc09b337d0163a4eb49ca0f27b9ea9d3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__767ba5a50877a479f1d79a17e8228f05b524f25e634b5818797fa58cc031d634)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.guestOsCustomization.GuestOsCustomizationConfig",
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
        "spec": "spec",
        "type": "type",
        "description": "description",
        "id": "id",
    },
)
class GuestOsCustomizationConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        spec: typing.Union["GuestOsCustomizationSpec", typing.Dict[builtins.str, typing.Any]],
        type: builtins.str,
        description: typing.Optional[builtins.str] = None,
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
        :param name: The name of the customization specification is the unique identifier per vCenter Server instance. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#name GuestOsCustomization#name}
        :param spec: spec block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#spec GuestOsCustomization#spec}
        :param type: The type of customization specification: One among: Windows, Linux. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#type GuestOsCustomization#type}
        :param description: The description for the customization specification. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#description GuestOsCustomization#description}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#id GuestOsCustomization#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(spec, dict):
            spec = GuestOsCustomizationSpec(**spec)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f793f9f4ebcbd9454194ec17967a5d9f59eb792f4c77b7bdb230439f28fda2a)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument spec", value=spec, expected_type=type_hints["spec"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "spec": spec,
            "type": type,
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
        if description is not None:
            self._values["description"] = description
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
    def name(self) -> builtins.str:
        '''The name of the customization specification is the unique identifier per vCenter Server instance.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#name GuestOsCustomization#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def spec(self) -> "GuestOsCustomizationSpec":
        '''spec block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#spec GuestOsCustomization#spec}
        '''
        result = self._values.get("spec")
        assert result is not None, "Required property 'spec' is missing"
        return typing.cast("GuestOsCustomizationSpec", result)

    @builtins.property
    def type(self) -> builtins.str:
        '''The type of customization specification: One among: Windows, Linux.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#type GuestOsCustomization#type}
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The description for the customization specification.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#description GuestOsCustomization#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#id GuestOsCustomization#id}.

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
        return "GuestOsCustomizationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.guestOsCustomization.GuestOsCustomizationSpec",
    jsii_struct_bases=[],
    name_mapping={
        "dns_server_list": "dnsServerList",
        "dns_suffix_list": "dnsSuffixList",
        "ipv4_gateway": "ipv4Gateway",
        "ipv6_gateway": "ipv6Gateway",
        "linux_options": "linuxOptions",
        "network_interface": "networkInterface",
        "windows_options": "windowsOptions",
        "windows_sysprep_text": "windowsSysprepText",
    },
)
class GuestOsCustomizationSpec:
    def __init__(
        self,
        *,
        dns_server_list: typing.Optional[typing.Sequence[builtins.str]] = None,
        dns_suffix_list: typing.Optional[typing.Sequence[builtins.str]] = None,
        ipv4_gateway: typing.Optional[builtins.str] = None,
        ipv6_gateway: typing.Optional[builtins.str] = None,
        linux_options: typing.Optional[typing.Union["GuestOsCustomizationSpecLinuxOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        network_interface: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GuestOsCustomizationSpecNetworkInterface", typing.Dict[builtins.str, typing.Any]]]]] = None,
        windows_options: typing.Optional[typing.Union["GuestOsCustomizationSpecWindowsOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        windows_sysprep_text: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param dns_server_list: The list of DNS servers for a virtual network adapter with a static IP address. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#dns_server_list GuestOsCustomization#dns_server_list}
        :param dns_suffix_list: A list of DNS search domains to add to the DNS configuration on the virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#dns_suffix_list GuestOsCustomization#dns_suffix_list}
        :param ipv4_gateway: The IPv4 default gateway when using network_interface customization on the virtual machine. This address must be local to a static IPv4 address configured in an interface sub-resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#ipv4_gateway GuestOsCustomization#ipv4_gateway}
        :param ipv6_gateway: The IPv6 default gateway when using network_interface customization on the virtual machine. This address must be local to a static IPv4 address configured in an interface sub-resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#ipv6_gateway GuestOsCustomization#ipv6_gateway}
        :param linux_options: linux_options block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#linux_options GuestOsCustomization#linux_options}
        :param network_interface: network_interface block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#network_interface GuestOsCustomization#network_interface}
        :param windows_options: windows_options block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#windows_options GuestOsCustomization#windows_options}
        :param windows_sysprep_text: Use this option to specify a windows sysprep file directly. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#windows_sysprep_text GuestOsCustomization#windows_sysprep_text}
        '''
        if isinstance(linux_options, dict):
            linux_options = GuestOsCustomizationSpecLinuxOptions(**linux_options)
        if isinstance(windows_options, dict):
            windows_options = GuestOsCustomizationSpecWindowsOptions(**windows_options)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1471cf8997659e1b7974bfd9edceb5aa29eb76089d67b0ad083f085b525b19a0)
            check_type(argname="argument dns_server_list", value=dns_server_list, expected_type=type_hints["dns_server_list"])
            check_type(argname="argument dns_suffix_list", value=dns_suffix_list, expected_type=type_hints["dns_suffix_list"])
            check_type(argname="argument ipv4_gateway", value=ipv4_gateway, expected_type=type_hints["ipv4_gateway"])
            check_type(argname="argument ipv6_gateway", value=ipv6_gateway, expected_type=type_hints["ipv6_gateway"])
            check_type(argname="argument linux_options", value=linux_options, expected_type=type_hints["linux_options"])
            check_type(argname="argument network_interface", value=network_interface, expected_type=type_hints["network_interface"])
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
        if windows_options is not None:
            self._values["windows_options"] = windows_options
        if windows_sysprep_text is not None:
            self._values["windows_sysprep_text"] = windows_sysprep_text

    @builtins.property
    def dns_server_list(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The list of DNS servers for a virtual network adapter with a static IP address.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#dns_server_list GuestOsCustomization#dns_server_list}
        '''
        result = self._values.get("dns_server_list")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def dns_suffix_list(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of DNS search domains to add to the DNS configuration on the virtual machine.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#dns_suffix_list GuestOsCustomization#dns_suffix_list}
        '''
        result = self._values.get("dns_suffix_list")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def ipv4_gateway(self) -> typing.Optional[builtins.str]:
        '''The IPv4 default gateway when using network_interface customization on the virtual machine.

        This address must be local to a static IPv4 address configured in an interface sub-resource.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#ipv4_gateway GuestOsCustomization#ipv4_gateway}
        '''
        result = self._values.get("ipv4_gateway")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ipv6_gateway(self) -> typing.Optional[builtins.str]:
        '''The IPv6 default gateway when using network_interface customization on the virtual machine.

        This address must be local to a static IPv4 address configured in an interface sub-resource.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#ipv6_gateway GuestOsCustomization#ipv6_gateway}
        '''
        result = self._values.get("ipv6_gateway")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def linux_options(self) -> typing.Optional["GuestOsCustomizationSpecLinuxOptions"]:
        '''linux_options block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#linux_options GuestOsCustomization#linux_options}
        '''
        result = self._values.get("linux_options")
        return typing.cast(typing.Optional["GuestOsCustomizationSpecLinuxOptions"], result)

    @builtins.property
    def network_interface(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GuestOsCustomizationSpecNetworkInterface"]]]:
        '''network_interface block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#network_interface GuestOsCustomization#network_interface}
        '''
        result = self._values.get("network_interface")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GuestOsCustomizationSpecNetworkInterface"]]], result)

    @builtins.property
    def windows_options(
        self,
    ) -> typing.Optional["GuestOsCustomizationSpecWindowsOptions"]:
        '''windows_options block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#windows_options GuestOsCustomization#windows_options}
        '''
        result = self._values.get("windows_options")
        return typing.cast(typing.Optional["GuestOsCustomizationSpecWindowsOptions"], result)

    @builtins.property
    def windows_sysprep_text(self) -> typing.Optional[builtins.str]:
        '''Use this option to specify a windows sysprep file directly.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#windows_sysprep_text GuestOsCustomization#windows_sysprep_text}
        '''
        result = self._values.get("windows_sysprep_text")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GuestOsCustomizationSpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.guestOsCustomization.GuestOsCustomizationSpecLinuxOptions",
    jsii_struct_bases=[],
    name_mapping={
        "domain": "domain",
        "host_name": "hostName",
        "hw_clock_utc": "hwClockUtc",
        "script_text": "scriptText",
        "time_zone": "timeZone",
    },
)
class GuestOsCustomizationSpecLinuxOptions:
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
        :param domain: The domain name for this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#domain GuestOsCustomization#domain}
        :param host_name: The hostname for this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#host_name GuestOsCustomization#host_name}
        :param hw_clock_utc: Specifies whether or not the hardware clock should be in UTC or not. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#hw_clock_utc GuestOsCustomization#hw_clock_utc}
        :param script_text: The customization script to run before and or after guest customization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#script_text GuestOsCustomization#script_text}
        :param time_zone: Customize the time zone on the VM. This should be a time zone-style entry, like America/Los_Angeles. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#time_zone GuestOsCustomization#time_zone}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d92e5db54423ce8581ebd1cde0640e26d1987f74f24b8413739115b342f4356)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#domain GuestOsCustomization#domain}
        '''
        result = self._values.get("domain")
        assert result is not None, "Required property 'domain' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def host_name(self) -> builtins.str:
        '''The hostname for this virtual machine.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#host_name GuestOsCustomization#host_name}
        '''
        result = self._values.get("host_name")
        assert result is not None, "Required property 'host_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def hw_clock_utc(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Specifies whether or not the hardware clock should be in UTC or not.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#hw_clock_utc GuestOsCustomization#hw_clock_utc}
        '''
        result = self._values.get("hw_clock_utc")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def script_text(self) -> typing.Optional[builtins.str]:
        '''The customization script to run before and or after guest customization.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#script_text GuestOsCustomization#script_text}
        '''
        result = self._values.get("script_text")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def time_zone(self) -> typing.Optional[builtins.str]:
        '''Customize the time zone on the VM. This should be a time zone-style entry, like America/Los_Angeles.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#time_zone GuestOsCustomization#time_zone}
        '''
        result = self._values.get("time_zone")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GuestOsCustomizationSpecLinuxOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GuestOsCustomizationSpecLinuxOptionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.guestOsCustomization.GuestOsCustomizationSpecLinuxOptionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ee284f5055aab713d4f8d4998f2a2622bc165b3bab2d36132fe7e3f5338eed4b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__cb2122d8f5f9ae5a4633665ee684e751c7fd455438d253fc86554b6c748042ce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "domain", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="hostName")
    def host_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostName"))

    @host_name.setter
    def host_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5fea327808eb4317b0b6b2b33883a324d79ac0bb51cd921608bee90f3a117b96)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d82b40f0a03a908f5f7c4a62233307c47b8a5f670ee80817b412f3bbd4287f28)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hwClockUtc", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scriptText")
    def script_text(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scriptText"))

    @script_text.setter
    def script_text(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dfbe1d8ac8f04aa1b5bd9ed8024cba826442a732f9dbc5275e9104ab72b731db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scriptText", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="timeZone")
    def time_zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timeZone"))

    @time_zone.setter
    def time_zone(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca6bdfff7018b688007350bda833fa0b58b0e16bcf20d3381796adc789b621ca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timeZone", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[GuestOsCustomizationSpecLinuxOptions]:
        return typing.cast(typing.Optional[GuestOsCustomizationSpecLinuxOptions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GuestOsCustomizationSpecLinuxOptions],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6fb29245f0135f974eb1fc4ae261f56ee788414c3dc42bde6c7d5616667395b3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.guestOsCustomization.GuestOsCustomizationSpecNetworkInterface",
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
class GuestOsCustomizationSpecNetworkInterface:
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
        :param dns_domain: A DNS search domain to add to the DNS configuration on the virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#dns_domain GuestOsCustomization#dns_domain}
        :param dns_server_list: Network-interface specific DNS settings for Windows operating systems. Ignored on Linux. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#dns_server_list GuestOsCustomization#dns_server_list}
        :param ipv4_address: The IPv4 address assigned to this network adapter. If left blank, DHCP is used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#ipv4_address GuestOsCustomization#ipv4_address}
        :param ipv4_netmask: The IPv4 CIDR netmask for the supplied IP address. Ignored if DHCP is selected. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#ipv4_netmask GuestOsCustomization#ipv4_netmask}
        :param ipv6_address: The IPv6 address assigned to this network adapter. If left blank, default auto-configuration is used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#ipv6_address GuestOsCustomization#ipv6_address}
        :param ipv6_netmask: The IPv6 CIDR netmask for the supplied IP address. Ignored if auto-configuration is selected. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#ipv6_netmask GuestOsCustomization#ipv6_netmask}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__312174514cb4381046f3d1ac83450caae436814ece8f7f2dc132e46ea154aa64)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#dns_domain GuestOsCustomization#dns_domain}
        '''
        result = self._values.get("dns_domain")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dns_server_list(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Network-interface specific DNS settings for Windows operating systems. Ignored on Linux.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#dns_server_list GuestOsCustomization#dns_server_list}
        '''
        result = self._values.get("dns_server_list")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def ipv4_address(self) -> typing.Optional[builtins.str]:
        '''The IPv4 address assigned to this network adapter. If left blank, DHCP is used.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#ipv4_address GuestOsCustomization#ipv4_address}
        '''
        result = self._values.get("ipv4_address")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ipv4_netmask(self) -> typing.Optional[jsii.Number]:
        '''The IPv4 CIDR netmask for the supplied IP address. Ignored if DHCP is selected.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#ipv4_netmask GuestOsCustomization#ipv4_netmask}
        '''
        result = self._values.get("ipv4_netmask")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ipv6_address(self) -> typing.Optional[builtins.str]:
        '''The IPv6 address assigned to this network adapter. If left blank, default auto-configuration is used.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#ipv6_address GuestOsCustomization#ipv6_address}
        '''
        result = self._values.get("ipv6_address")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ipv6_netmask(self) -> typing.Optional[jsii.Number]:
        '''The IPv6 CIDR netmask for the supplied IP address. Ignored if auto-configuration is selected.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#ipv6_netmask GuestOsCustomization#ipv6_netmask}
        '''
        result = self._values.get("ipv6_netmask")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GuestOsCustomizationSpecNetworkInterface(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GuestOsCustomizationSpecNetworkInterfaceList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.guestOsCustomization.GuestOsCustomizationSpecNetworkInterfaceList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8446ae0f33215b084aa601ef348ae84e59be358b3f38f4776d05bcce69aa7c62)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GuestOsCustomizationSpecNetworkInterfaceOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__96c258c9668a2fa1d0631fe2c410002855ded805729afd725e219815fbddcf69)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GuestOsCustomizationSpecNetworkInterfaceOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__44b216343b19e37c7cfd8abad5a6ebbf962a9e8f034847009df7e38e90f5ed4f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e644317959df0206954467ff107ac9c5fa380b6e3b9093319d95084bb648bce0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__46aa1968894510bbd862a0fa84e69639ee62b9da5dcca8a14f6433d56b4a5cdd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GuestOsCustomizationSpecNetworkInterface]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GuestOsCustomizationSpecNetworkInterface]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GuestOsCustomizationSpecNetworkInterface]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94aa929d91e235d79886ce053d1bc2541f997d7a7cc1c9b403a9bcd313c159b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GuestOsCustomizationSpecNetworkInterfaceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.guestOsCustomization.GuestOsCustomizationSpecNetworkInterfaceOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d3d5df078013c66b87d8ab7dbe9d4c1f88a974d38c5f0813d36ea8a2b89f5e1d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e36a2f21a2daa4933bb4a2df42a2eaa05f18feef55c75abb983dfda021259b18)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dnsDomain", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dnsServerList")
    def dns_server_list(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "dnsServerList"))

    @dns_server_list.setter
    def dns_server_list(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ac18f9c6df3f3adedb4f25568c61899bfdb12defd24a8030c066e88b5c522c5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dnsServerList", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipv4Address")
    def ipv4_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipv4Address"))

    @ipv4_address.setter
    def ipv4_address(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac907fc0ccbb907377f3d0e65d349c0b37e478533eafc9ebfd9fcfcf0cd378cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipv4Address", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipv4Netmask")
    def ipv4_netmask(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ipv4Netmask"))

    @ipv4_netmask.setter
    def ipv4_netmask(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__01bfaeba2f11fc885f0e5f2774f3b72d4fd6589ce1bd6a28430e4d1aaefaf2ad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipv4Netmask", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipv6Address")
    def ipv6_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipv6Address"))

    @ipv6_address.setter
    def ipv6_address(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__65bfb0e939702d17be090ebd4fb3020e4627bb1a88e3deaae7f3802af57143b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipv6Address", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipv6Netmask")
    def ipv6_netmask(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ipv6Netmask"))

    @ipv6_netmask.setter
    def ipv6_netmask(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4853397a8de601781f53dc7ae8e5aa707eaf4b846376328be078b0e6ee20edf3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipv6Netmask", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GuestOsCustomizationSpecNetworkInterface]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GuestOsCustomizationSpecNetworkInterface]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GuestOsCustomizationSpecNetworkInterface]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__82b340c1ad33520cbac3acc1f41a997038331b4004f785bed681c00b30385b1e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GuestOsCustomizationSpecOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.guestOsCustomization.GuestOsCustomizationSpecOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__23f3020de053e4c67a568d01b5a0cc0cf7ed699f7ff09aab06cdb6ca692f67ae)
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
        :param domain: The domain name for this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#domain GuestOsCustomization#domain}
        :param host_name: The hostname for this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#host_name GuestOsCustomization#host_name}
        :param hw_clock_utc: Specifies whether or not the hardware clock should be in UTC or not. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#hw_clock_utc GuestOsCustomization#hw_clock_utc}
        :param script_text: The customization script to run before and or after guest customization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#script_text GuestOsCustomization#script_text}
        :param time_zone: Customize the time zone on the VM. This should be a time zone-style entry, like America/Los_Angeles. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#time_zone GuestOsCustomization#time_zone}
        '''
        value = GuestOsCustomizationSpecLinuxOptions(
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
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GuestOsCustomizationSpecNetworkInterface, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04d8eb85771e45bea787539a04a959c411744ce00da693d3412513a3bac9f2d3)
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
        :param computer_name: The host name for this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#computer_name GuestOsCustomization#computer_name}
        :param admin_password: The new administrator password for this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#admin_password GuestOsCustomization#admin_password}
        :param auto_logon: Specifies whether or not the VM automatically logs on as Administrator. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#auto_logon GuestOsCustomization#auto_logon}
        :param auto_logon_count: Specifies how many times the VM should auto-logon the Administrator account when auto_logon is true. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#auto_logon_count GuestOsCustomization#auto_logon_count}
        :param domain_admin_password: The password of the domain administrator used to join this virtual machine to the domain. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#domain_admin_password GuestOsCustomization#domain_admin_password}
        :param domain_admin_user: The user account of the domain administrator used to join this virtual machine to the domain. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#domain_admin_user GuestOsCustomization#domain_admin_user}
        :param domain_ou: The MachineObjectOU which specifies the full LDAP path name of the OU to which the virtual machine belongs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#domain_ou GuestOsCustomization#domain_ou}
        :param full_name: The full name of the user of this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#full_name GuestOsCustomization#full_name}
        :param join_domain: The domain that the virtual machine should join. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#join_domain GuestOsCustomization#join_domain}
        :param organization_name: The organization name this virtual machine is being installed for. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#organization_name GuestOsCustomization#organization_name}
        :param product_key: The product key for this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#product_key GuestOsCustomization#product_key}
        :param run_once_command_list: A list of commands to run at first user logon, after guest customization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#run_once_command_list GuestOsCustomization#run_once_command_list}
        :param time_zone: The new time zone for the virtual machine. This is a sysprep-dictated timezone code. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#time_zone GuestOsCustomization#time_zone}
        :param workgroup: The workgroup for this virtual machine if not joining a domain. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#workgroup GuestOsCustomization#workgroup}
        '''
        value = GuestOsCustomizationSpecWindowsOptions(
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

    @jsii.member(jsii_name="resetWindowsOptions")
    def reset_windows_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWindowsOptions", []))

    @jsii.member(jsii_name="resetWindowsSysprepText")
    def reset_windows_sysprep_text(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWindowsSysprepText", []))

    @builtins.property
    @jsii.member(jsii_name="linuxOptions")
    def linux_options(self) -> GuestOsCustomizationSpecLinuxOptionsOutputReference:
        return typing.cast(GuestOsCustomizationSpecLinuxOptionsOutputReference, jsii.get(self, "linuxOptions"))

    @builtins.property
    @jsii.member(jsii_name="networkInterface")
    def network_interface(self) -> GuestOsCustomizationSpecNetworkInterfaceList:
        return typing.cast(GuestOsCustomizationSpecNetworkInterfaceList, jsii.get(self, "networkInterface"))

    @builtins.property
    @jsii.member(jsii_name="windowsOptions")
    def windows_options(
        self,
    ) -> "GuestOsCustomizationSpecWindowsOptionsOutputReference":
        return typing.cast("GuestOsCustomizationSpecWindowsOptionsOutputReference", jsii.get(self, "windowsOptions"))

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
    ) -> typing.Optional[GuestOsCustomizationSpecLinuxOptions]:
        return typing.cast(typing.Optional[GuestOsCustomizationSpecLinuxOptions], jsii.get(self, "linuxOptionsInput"))

    @builtins.property
    @jsii.member(jsii_name="networkInterfaceInput")
    def network_interface_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GuestOsCustomizationSpecNetworkInterface]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GuestOsCustomizationSpecNetworkInterface]]], jsii.get(self, "networkInterfaceInput"))

    @builtins.property
    @jsii.member(jsii_name="windowsOptionsInput")
    def windows_options_input(
        self,
    ) -> typing.Optional["GuestOsCustomizationSpecWindowsOptions"]:
        return typing.cast(typing.Optional["GuestOsCustomizationSpecWindowsOptions"], jsii.get(self, "windowsOptionsInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__34c38005cfa329b1f8ff0850180b805e91be33a4f6d1ec2dd56e515c7fe0693a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dnsServerList", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dnsSuffixList")
    def dns_suffix_list(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "dnsSuffixList"))

    @dns_suffix_list.setter
    def dns_suffix_list(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ffe3263e1f38c51d25e28378eb6ad0f22e26e54ea955a23a5d779bfcfaae385c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dnsSuffixList", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipv4Gateway")
    def ipv4_gateway(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipv4Gateway"))

    @ipv4_gateway.setter
    def ipv4_gateway(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6683096d375e662ef8646e434d9855cd425cc1d15370cf40e25520664455de3e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipv4Gateway", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipv6Gateway")
    def ipv6_gateway(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipv6Gateway"))

    @ipv6_gateway.setter
    def ipv6_gateway(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0fe103357d5db3ef32441441221f7ba6c82bd00df391966b9a801097aca6dbbc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipv6Gateway", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="windowsSysprepText")
    def windows_sysprep_text(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "windowsSysprepText"))

    @windows_sysprep_text.setter
    def windows_sysprep_text(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f35b38fce2d6ee063a14e411d8511bb35d8f6a2207adbd09c5d379b0e386110a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "windowsSysprepText", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[GuestOsCustomizationSpec]:
        return typing.cast(typing.Optional[GuestOsCustomizationSpec], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[GuestOsCustomizationSpec]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f9f7e1f932bc3a3508e356366113ff43c77c945355c53b9d47808e147dcd586a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.guestOsCustomization.GuestOsCustomizationSpecWindowsOptions",
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
class GuestOsCustomizationSpecWindowsOptions:
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
        :param computer_name: The host name for this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#computer_name GuestOsCustomization#computer_name}
        :param admin_password: The new administrator password for this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#admin_password GuestOsCustomization#admin_password}
        :param auto_logon: Specifies whether or not the VM automatically logs on as Administrator. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#auto_logon GuestOsCustomization#auto_logon}
        :param auto_logon_count: Specifies how many times the VM should auto-logon the Administrator account when auto_logon is true. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#auto_logon_count GuestOsCustomization#auto_logon_count}
        :param domain_admin_password: The password of the domain administrator used to join this virtual machine to the domain. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#domain_admin_password GuestOsCustomization#domain_admin_password}
        :param domain_admin_user: The user account of the domain administrator used to join this virtual machine to the domain. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#domain_admin_user GuestOsCustomization#domain_admin_user}
        :param domain_ou: The MachineObjectOU which specifies the full LDAP path name of the OU to which the virtual machine belongs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#domain_ou GuestOsCustomization#domain_ou}
        :param full_name: The full name of the user of this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#full_name GuestOsCustomization#full_name}
        :param join_domain: The domain that the virtual machine should join. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#join_domain GuestOsCustomization#join_domain}
        :param organization_name: The organization name this virtual machine is being installed for. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#organization_name GuestOsCustomization#organization_name}
        :param product_key: The product key for this virtual machine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#product_key GuestOsCustomization#product_key}
        :param run_once_command_list: A list of commands to run at first user logon, after guest customization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#run_once_command_list GuestOsCustomization#run_once_command_list}
        :param time_zone: The new time zone for the virtual machine. This is a sysprep-dictated timezone code. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#time_zone GuestOsCustomization#time_zone}
        :param workgroup: The workgroup for this virtual machine if not joining a domain. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#workgroup GuestOsCustomization#workgroup}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__168ddc9acee643f9e1f774ff0f45529639e6d18e74a74a719f349f20e425028f)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#computer_name GuestOsCustomization#computer_name}
        '''
        result = self._values.get("computer_name")
        assert result is not None, "Required property 'computer_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def admin_password(self) -> typing.Optional[builtins.str]:
        '''The new administrator password for this virtual machine.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#admin_password GuestOsCustomization#admin_password}
        '''
        result = self._values.get("admin_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auto_logon(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Specifies whether or not the VM automatically logs on as Administrator.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#auto_logon GuestOsCustomization#auto_logon}
        '''
        result = self._values.get("auto_logon")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def auto_logon_count(self) -> typing.Optional[jsii.Number]:
        '''Specifies how many times the VM should auto-logon the Administrator account when auto_logon is true.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#auto_logon_count GuestOsCustomization#auto_logon_count}
        '''
        result = self._values.get("auto_logon_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def domain_admin_password(self) -> typing.Optional[builtins.str]:
        '''The password of the domain administrator used to join this virtual machine to the domain.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#domain_admin_password GuestOsCustomization#domain_admin_password}
        '''
        result = self._values.get("domain_admin_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def domain_admin_user(self) -> typing.Optional[builtins.str]:
        '''The user account of the domain administrator used to join this virtual machine to the domain.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#domain_admin_user GuestOsCustomization#domain_admin_user}
        '''
        result = self._values.get("domain_admin_user")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def domain_ou(self) -> typing.Optional[builtins.str]:
        '''The MachineObjectOU which specifies the full LDAP path name of the OU to which the virtual machine belongs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#domain_ou GuestOsCustomization#domain_ou}
        '''
        result = self._values.get("domain_ou")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def full_name(self) -> typing.Optional[builtins.str]:
        '''The full name of the user of this virtual machine.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#full_name GuestOsCustomization#full_name}
        '''
        result = self._values.get("full_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def join_domain(self) -> typing.Optional[builtins.str]:
        '''The domain that the virtual machine should join.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#join_domain GuestOsCustomization#join_domain}
        '''
        result = self._values.get("join_domain")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def organization_name(self) -> typing.Optional[builtins.str]:
        '''The organization name this virtual machine is being installed for.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#organization_name GuestOsCustomization#organization_name}
        '''
        result = self._values.get("organization_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def product_key(self) -> typing.Optional[builtins.str]:
        '''The product key for this virtual machine.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#product_key GuestOsCustomization#product_key}
        '''
        result = self._values.get("product_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def run_once_command_list(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of commands to run at first user logon, after guest customization.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#run_once_command_list GuestOsCustomization#run_once_command_list}
        '''
        result = self._values.get("run_once_command_list")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def time_zone(self) -> typing.Optional[jsii.Number]:
        '''The new time zone for the virtual machine. This is a sysprep-dictated timezone code.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#time_zone GuestOsCustomization#time_zone}
        '''
        result = self._values.get("time_zone")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def workgroup(self) -> typing.Optional[builtins.str]:
        '''The workgroup for this virtual machine if not joining a domain.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/guest_os_customization#workgroup GuestOsCustomization#workgroup}
        '''
        result = self._values.get("workgroup")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GuestOsCustomizationSpecWindowsOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GuestOsCustomizationSpecWindowsOptionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.guestOsCustomization.GuestOsCustomizationSpecWindowsOptionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c1e7d8fdc735015b9f93ec7d93a25f9d40b7677fa3434f696070d79e1a96f837)
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
            type_hints = typing.get_type_hints(_typecheckingstub__dd6e3c5e0715232961fe90cea9e6c828f9e87e4e58b73e3e2d156af248ba4475)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0c5f299187fe0581df21fa019fb26175070d1a168673d9d28f5fa6337f19548b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoLogon", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="autoLogonCount")
    def auto_logon_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "autoLogonCount"))

    @auto_logon_count.setter
    def auto_logon_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__31afa7771df6347fe49878025d175eda004611058ac92f2d07e175f1431471c7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoLogonCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="computerName")
    def computer_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "computerName"))

    @computer_name.setter
    def computer_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__947649aa658f2b3ffefe2d653fb386361bab60b953230d93191aee04a0dcdd14)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "computerName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="domainAdminPassword")
    def domain_admin_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domainAdminPassword"))

    @domain_admin_password.setter
    def domain_admin_password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1de63ca73df055b0afad32bb455dad800fa3e37d47d56b4b837de8a863c3be4c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "domainAdminPassword", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="domainAdminUser")
    def domain_admin_user(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domainAdminUser"))

    @domain_admin_user.setter
    def domain_admin_user(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3d518a8750053d9b6c236253c2c31dc749f744947943367229835fb2fd7dcf6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "domainAdminUser", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="domainOu")
    def domain_ou(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domainOu"))

    @domain_ou.setter
    def domain_ou(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64470888d2ae22b09689db61a2c6ecfc293f8316531fb9dd7eb3f43875a2abd1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "domainOu", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="fullName")
    def full_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fullName"))

    @full_name.setter
    def full_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8ecafc7f4dc072a0dfa38d009362c1387ea8438dbc4115e9b192b878e5149e0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fullName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="joinDomain")
    def join_domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "joinDomain"))

    @join_domain.setter
    def join_domain(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b142caec676b0568b2c1f1678245e8e333c1b3572eb47e91f6d89d508eae3dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "joinDomain", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="organizationName")
    def organization_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "organizationName"))

    @organization_name.setter
    def organization_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec3fde5b9e3687d84a5fb9959c5a53487ef42a0e01bf778ec8b69d153c002320)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "organizationName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="productKey")
    def product_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "productKey"))

    @product_key.setter
    def product_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d331b8387903d08726e062c20eb0e499e21c1836bc99477bcc10e561c54ef826)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "productKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="runOnceCommandList")
    def run_once_command_list(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "runOnceCommandList"))

    @run_once_command_list.setter
    def run_once_command_list(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3796ab64dc3349b96bebc7c9d31431cabb0a02bcdfc770d9abae2239acbbc7ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "runOnceCommandList", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="timeZone")
    def time_zone(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "timeZone"))

    @time_zone.setter
    def time_zone(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c3fe555d22636592f64932cc32d8c75b01ecac136015fdbaf58e9edd2549284)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timeZone", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workgroup")
    def workgroup(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workgroup"))

    @workgroup.setter
    def workgroup(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e05430f52009a7b3953f3eefb0ca7fe3fa432cdd9335f0db2ac999cf198a82d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workgroup", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[GuestOsCustomizationSpecWindowsOptions]:
        return typing.cast(typing.Optional[GuestOsCustomizationSpecWindowsOptions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GuestOsCustomizationSpecWindowsOptions],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a5540e9c9f8308f4196754152fd5b7eed49c772603be79252ed59af59b9f119)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "GuestOsCustomization",
    "GuestOsCustomizationConfig",
    "GuestOsCustomizationSpec",
    "GuestOsCustomizationSpecLinuxOptions",
    "GuestOsCustomizationSpecLinuxOptionsOutputReference",
    "GuestOsCustomizationSpecNetworkInterface",
    "GuestOsCustomizationSpecNetworkInterfaceList",
    "GuestOsCustomizationSpecNetworkInterfaceOutputReference",
    "GuestOsCustomizationSpecOutputReference",
    "GuestOsCustomizationSpecWindowsOptions",
    "GuestOsCustomizationSpecWindowsOptionsOutputReference",
]

publication.publish()

def _typecheckingstub__f7f4d26a0c2a85584648ff341ccf75385e7c9482ffd9428e3bc8f4fbc8d14a05(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    spec: typing.Union[GuestOsCustomizationSpec, typing.Dict[builtins.str, typing.Any]],
    type: builtins.str,
    description: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__e72c000958b374d71e1e7f3c9386da36d68a257a8054df388c6db8e94b064b10(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2878744098b51ea1c484b86e3f3803f5d4a60cfcd9133464461e2c32db859ec3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__234cdc1e12976d1638f0c84b00f6d7ea9d0c0d141f0dc0efa171289558d5f4f9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__343c50c7b6ac40f364da0dcc3c7f520fbc09b337d0163a4eb49ca0f27b9ea9d3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__767ba5a50877a479f1d79a17e8228f05b524f25e634b5818797fa58cc031d634(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f793f9f4ebcbd9454194ec17967a5d9f59eb792f4c77b7bdb230439f28fda2a(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    spec: typing.Union[GuestOsCustomizationSpec, typing.Dict[builtins.str, typing.Any]],
    type: builtins.str,
    description: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1471cf8997659e1b7974bfd9edceb5aa29eb76089d67b0ad083f085b525b19a0(
    *,
    dns_server_list: typing.Optional[typing.Sequence[builtins.str]] = None,
    dns_suffix_list: typing.Optional[typing.Sequence[builtins.str]] = None,
    ipv4_gateway: typing.Optional[builtins.str] = None,
    ipv6_gateway: typing.Optional[builtins.str] = None,
    linux_options: typing.Optional[typing.Union[GuestOsCustomizationSpecLinuxOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    network_interface: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GuestOsCustomizationSpecNetworkInterface, typing.Dict[builtins.str, typing.Any]]]]] = None,
    windows_options: typing.Optional[typing.Union[GuestOsCustomizationSpecWindowsOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    windows_sysprep_text: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d92e5db54423ce8581ebd1cde0640e26d1987f74f24b8413739115b342f4356(
    *,
    domain: builtins.str,
    host_name: builtins.str,
    hw_clock_utc: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    script_text: typing.Optional[builtins.str] = None,
    time_zone: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee284f5055aab713d4f8d4998f2a2622bc165b3bab2d36132fe7e3f5338eed4b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb2122d8f5f9ae5a4633665ee684e751c7fd455438d253fc86554b6c748042ce(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5fea327808eb4317b0b6b2b33883a324d79ac0bb51cd921608bee90f3a117b96(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d82b40f0a03a908f5f7c4a62233307c47b8a5f670ee80817b412f3bbd4287f28(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dfbe1d8ac8f04aa1b5bd9ed8024cba826442a732f9dbc5275e9104ab72b731db(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca6bdfff7018b688007350bda833fa0b58b0e16bcf20d3381796adc789b621ca(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6fb29245f0135f974eb1fc4ae261f56ee788414c3dc42bde6c7d5616667395b3(
    value: typing.Optional[GuestOsCustomizationSpecLinuxOptions],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__312174514cb4381046f3d1ac83450caae436814ece8f7f2dc132e46ea154aa64(
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

def _typecheckingstub__8446ae0f33215b084aa601ef348ae84e59be358b3f38f4776d05bcce69aa7c62(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96c258c9668a2fa1d0631fe2c410002855ded805729afd725e219815fbddcf69(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44b216343b19e37c7cfd8abad5a6ebbf962a9e8f034847009df7e38e90f5ed4f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e644317959df0206954467ff107ac9c5fa380b6e3b9093319d95084bb648bce0(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46aa1968894510bbd862a0fa84e69639ee62b9da5dcca8a14f6433d56b4a5cdd(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94aa929d91e235d79886ce053d1bc2541f997d7a7cc1c9b403a9bcd313c159b4(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GuestOsCustomizationSpecNetworkInterface]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3d5df078013c66b87d8ab7dbe9d4c1f88a974d38c5f0813d36ea8a2b89f5e1d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e36a2f21a2daa4933bb4a2df42a2eaa05f18feef55c75abb983dfda021259b18(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ac18f9c6df3f3adedb4f25568c61899bfdb12defd24a8030c066e88b5c522c5(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac907fc0ccbb907377f3d0e65d349c0b37e478533eafc9ebfd9fcfcf0cd378cc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01bfaeba2f11fc885f0e5f2774f3b72d4fd6589ce1bd6a28430e4d1aaefaf2ad(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65bfb0e939702d17be090ebd4fb3020e4627bb1a88e3deaae7f3802af57143b2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4853397a8de601781f53dc7ae8e5aa707eaf4b846376328be078b0e6ee20edf3(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82b340c1ad33520cbac3acc1f41a997038331b4004f785bed681c00b30385b1e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GuestOsCustomizationSpecNetworkInterface]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23f3020de053e4c67a568d01b5a0cc0cf7ed699f7ff09aab06cdb6ca692f67ae(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04d8eb85771e45bea787539a04a959c411744ce00da693d3412513a3bac9f2d3(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GuestOsCustomizationSpecNetworkInterface, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34c38005cfa329b1f8ff0850180b805e91be33a4f6d1ec2dd56e515c7fe0693a(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ffe3263e1f38c51d25e28378eb6ad0f22e26e54ea955a23a5d779bfcfaae385c(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6683096d375e662ef8646e434d9855cd425cc1d15370cf40e25520664455de3e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0fe103357d5db3ef32441441221f7ba6c82bd00df391966b9a801097aca6dbbc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f35b38fce2d6ee063a14e411d8511bb35d8f6a2207adbd09c5d379b0e386110a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9f7e1f932bc3a3508e356366113ff43c77c945355c53b9d47808e147dcd586a(
    value: typing.Optional[GuestOsCustomizationSpec],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__168ddc9acee643f9e1f774ff0f45529639e6d18e74a74a719f349f20e425028f(
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

def _typecheckingstub__c1e7d8fdc735015b9f93ec7d93a25f9d40b7677fa3434f696070d79e1a96f837(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd6e3c5e0715232961fe90cea9e6c828f9e87e4e58b73e3e2d156af248ba4475(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c5f299187fe0581df21fa019fb26175070d1a168673d9d28f5fa6337f19548b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31afa7771df6347fe49878025d175eda004611058ac92f2d07e175f1431471c7(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__947649aa658f2b3ffefe2d653fb386361bab60b953230d93191aee04a0dcdd14(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1de63ca73df055b0afad32bb455dad800fa3e37d47d56b4b837de8a863c3be4c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3d518a8750053d9b6c236253c2c31dc749f744947943367229835fb2fd7dcf6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64470888d2ae22b09689db61a2c6ecfc293f8316531fb9dd7eb3f43875a2abd1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8ecafc7f4dc072a0dfa38d009362c1387ea8438dbc4115e9b192b878e5149e0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b142caec676b0568b2c1f1678245e8e333c1b3572eb47e91f6d89d508eae3dc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec3fde5b9e3687d84a5fb9959c5a53487ef42a0e01bf778ec8b69d153c002320(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d331b8387903d08726e062c20eb0e499e21c1836bc99477bcc10e561c54ef826(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3796ab64dc3349b96bebc7c9d31431cabb0a02bcdfc770d9abae2239acbbc7ae(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c3fe555d22636592f64932cc32d8c75b01ecac136015fdbaf58e9edd2549284(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e05430f52009a7b3953f3eefb0ca7fe3fa432cdd9335f0db2ac999cf198a82d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a5540e9c9f8308f4196754152fd5b7eed49c772603be79252ed59af59b9f119(
    value: typing.Optional[GuestOsCustomizationSpecWindowsOptions],
) -> None:
    """Type checking stubs"""
    pass
