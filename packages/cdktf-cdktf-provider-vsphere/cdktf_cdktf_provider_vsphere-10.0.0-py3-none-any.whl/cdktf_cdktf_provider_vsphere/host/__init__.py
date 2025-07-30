r'''
# `vsphere_host`

Refer to the Terraform Registry for docs: [`vsphere_host`](https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host).
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


class Host(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.host.Host",
):
    '''Represents a {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host vsphere_host}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        hostname: builtins.str,
        password: builtins.str,
        username: builtins.str,
        cluster: typing.Optional[builtins.str] = None,
        cluster_managed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        connected: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        custom_attributes: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        datacenter: typing.Optional[builtins.str] = None,
        force: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        license: typing.Optional[builtins.str] = None,
        lockdown: typing.Optional[builtins.str] = None,
        maintenance: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        services: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["HostServices", typing.Dict[builtins.str, typing.Any]]]]] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        thumbprint: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host vsphere_host} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param hostname: FQDN or IP address of the host. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#hostname Host#hostname}
        :param password: Password of the administration account of the host. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#password Host#password}
        :param username: Username of the administration account of the host. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#username Host#username}
        :param cluster: ID of the vSphere cluster the host will belong to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#cluster Host#cluster}
        :param cluster_managed: Must be set if host is a member of a managed compute_cluster resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#cluster_managed Host#cluster_managed}
        :param connected: Set the state of the host. If set to false then the host will be asked to disconnect. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#connected Host#connected}
        :param custom_attributes: A list of custom attributes to set on this resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#custom_attributes Host#custom_attributes}
        :param datacenter: ID of the vSphere datacenter the host will belong to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#datacenter Host#datacenter}
        :param force: Force add the host to the vSphere inventory even if it's already managed by a different vCenter Server instance. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#force Host#force}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#id Host#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param license: License key that will be applied to this host. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#license Host#license}
        :param lockdown: Set the host's lockdown status. Default is disabled. Valid options are 'disabled', 'normal', 'strict'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#lockdown Host#lockdown}
        :param maintenance: Set the host's maintenance mode. Default is false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#maintenance Host#maintenance}
        :param services: services block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#services Host#services}
        :param tags: A list of tag IDs to apply to this object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#tags Host#tags}
        :param thumbprint: Host's certificate SHA-1 thumbprint. If not set then the CA that signed the host's certificate must be trusted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#thumbprint Host#thumbprint}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18656f2bce55e9eb067beb47951917f71009e8a54839905a64a063ce5611d366)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = HostConfig(
            hostname=hostname,
            password=password,
            username=username,
            cluster=cluster,
            cluster_managed=cluster_managed,
            connected=connected,
            custom_attributes=custom_attributes,
            datacenter=datacenter,
            force=force,
            id=id,
            license=license,
            lockdown=lockdown,
            maintenance=maintenance,
            services=services,
            tags=tags,
            thumbprint=thumbprint,
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
        '''Generates CDKTF code for importing a Host resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the Host to import.
        :param import_from_id: The id of the existing Host that should be imported. Refer to the {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the Host to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d2b6d7d39b6e13fc59c5e4020c0c93baecb42aa66e830ccd378d6be85978b17)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putServices")
    def put_services(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["HostServices", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73d44d063f0c1595d069d5bd50777ece6feb65a7d29377e8c5b665e51d2717e1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putServices", [value]))

    @jsii.member(jsii_name="resetCluster")
    def reset_cluster(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCluster", []))

    @jsii.member(jsii_name="resetClusterManaged")
    def reset_cluster_managed(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterManaged", []))

    @jsii.member(jsii_name="resetConnected")
    def reset_connected(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConnected", []))

    @jsii.member(jsii_name="resetCustomAttributes")
    def reset_custom_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomAttributes", []))

    @jsii.member(jsii_name="resetDatacenter")
    def reset_datacenter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatacenter", []))

    @jsii.member(jsii_name="resetForce")
    def reset_force(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForce", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetLicense")
    def reset_license(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLicense", []))

    @jsii.member(jsii_name="resetLockdown")
    def reset_lockdown(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLockdown", []))

    @jsii.member(jsii_name="resetMaintenance")
    def reset_maintenance(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaintenance", []))

    @jsii.member(jsii_name="resetServices")
    def reset_services(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServices", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetThumbprint")
    def reset_thumbprint(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThumbprint", []))

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
    @jsii.member(jsii_name="services")
    def services(self) -> "HostServicesList":
        return typing.cast("HostServicesList", jsii.get(self, "services"))

    @builtins.property
    @jsii.member(jsii_name="clusterInput")
    def cluster_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterManagedInput")
    def cluster_managed_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "clusterManagedInput"))

    @builtins.property
    @jsii.member(jsii_name="connectedInput")
    def connected_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "connectedInput"))

    @builtins.property
    @jsii.member(jsii_name="customAttributesInput")
    def custom_attributes_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "customAttributesInput"))

    @builtins.property
    @jsii.member(jsii_name="datacenterInput")
    def datacenter_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "datacenterInput"))

    @builtins.property
    @jsii.member(jsii_name="forceInput")
    def force_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "forceInput"))

    @builtins.property
    @jsii.member(jsii_name="hostnameInput")
    def hostname_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostnameInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="licenseInput")
    def license_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "licenseInput"))

    @builtins.property
    @jsii.member(jsii_name="lockdownInput")
    def lockdown_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "lockdownInput"))

    @builtins.property
    @jsii.member(jsii_name="maintenanceInput")
    def maintenance_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "maintenanceInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property
    @jsii.member(jsii_name="servicesInput")
    def services_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["HostServices"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["HostServices"]]], jsii.get(self, "servicesInput"))

    @builtins.property
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property
    @jsii.member(jsii_name="thumbprintInput")
    def thumbprint_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "thumbprintInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property
    @jsii.member(jsii_name="cluster")
    def cluster(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cluster"))

    @cluster.setter
    def cluster(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c2ae23185c4b164fa5caf37e8e4b1837d6c21c574074aaed36f76ca42551b71c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cluster", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clusterManaged")
    def cluster_managed(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "clusterManaged"))

    @cluster_managed.setter
    def cluster_managed(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d15b567c94b54dbee0dfdb3bf440d4dd9c794e704ffdef1b46176a07ce7ddf4a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clusterManaged", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="connected")
    def connected(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "connected"))

    @connected.setter
    def connected(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33283475422b342868979da570a10f398a65dff50b47753ca3d2d2bf62b78720)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connected", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__ba7050dff28aa22cacaf2f1f31ec9dc41e257bd2ccc53371b619287da977a5f5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customAttributes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="datacenter")
    def datacenter(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "datacenter"))

    @datacenter.setter
    def datacenter(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c8a16c1d3c290cafdc00b1e512b42aff8daa961961d3db08de383cf56eaa5d6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "datacenter", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="force")
    def force(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "force"))

    @force.setter
    def force(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__848ef7aa26ea97b467f84931dbc2aec8c00bb1e94edae9bb2fac128555de1f95)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "force", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="hostname")
    def hostname(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostname"))

    @hostname.setter
    def hostname(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__45b56bf89d96eed7e70fdfda3a06ddae67e325fe70e3be6ea49fca18d13596c3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hostname", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__722a4132e51ca38aa4ad983a4caf5d5e820239bde04a0f89375f94656a4b3e37)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="license")
    def license(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "license"))

    @license.setter
    def license(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6eeae5a5d7cd7ab5fb0c8679c98fa9f11271081601e870da3265b48a6a30fea2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "license", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="lockdown")
    def lockdown(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lockdown"))

    @lockdown.setter
    def lockdown(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a658533825a21aa287defd85c5195c27cae0ffda63adc2333525ef5cf57b18ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lockdown", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maintenance")
    def maintenance(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "maintenance"))

    @maintenance.setter
    def maintenance(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2231c4494c6d04b160868e358d41f327816e2a15e351c66e041501e2b8672241)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maintenance", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__39951c2a9439e0fe784575b006260bea839e2004f2e9114a13af26d0f96cf6e0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "password", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89ec46c6f242a273c70a902123b2348e5c996e77a5206c6b1d2990ed7a162a6a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="thumbprint")
    def thumbprint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "thumbprint"))

    @thumbprint.setter
    def thumbprint(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f13cf599b236b2961ecce667030e74017c4c3a9cc90ddf73aa51a02f84971e9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "thumbprint", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc85a8ec8948a1119a52bdbb259bddc2479b9a2b8753725d602bbc62a209d7da)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "username", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.host.HostConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "hostname": "hostname",
        "password": "password",
        "username": "username",
        "cluster": "cluster",
        "cluster_managed": "clusterManaged",
        "connected": "connected",
        "custom_attributes": "customAttributes",
        "datacenter": "datacenter",
        "force": "force",
        "id": "id",
        "license": "license",
        "lockdown": "lockdown",
        "maintenance": "maintenance",
        "services": "services",
        "tags": "tags",
        "thumbprint": "thumbprint",
    },
)
class HostConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        hostname: builtins.str,
        password: builtins.str,
        username: builtins.str,
        cluster: typing.Optional[builtins.str] = None,
        cluster_managed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        connected: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        custom_attributes: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        datacenter: typing.Optional[builtins.str] = None,
        force: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        license: typing.Optional[builtins.str] = None,
        lockdown: typing.Optional[builtins.str] = None,
        maintenance: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        services: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["HostServices", typing.Dict[builtins.str, typing.Any]]]]] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        thumbprint: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param hostname: FQDN or IP address of the host. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#hostname Host#hostname}
        :param password: Password of the administration account of the host. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#password Host#password}
        :param username: Username of the administration account of the host. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#username Host#username}
        :param cluster: ID of the vSphere cluster the host will belong to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#cluster Host#cluster}
        :param cluster_managed: Must be set if host is a member of a managed compute_cluster resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#cluster_managed Host#cluster_managed}
        :param connected: Set the state of the host. If set to false then the host will be asked to disconnect. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#connected Host#connected}
        :param custom_attributes: A list of custom attributes to set on this resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#custom_attributes Host#custom_attributes}
        :param datacenter: ID of the vSphere datacenter the host will belong to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#datacenter Host#datacenter}
        :param force: Force add the host to the vSphere inventory even if it's already managed by a different vCenter Server instance. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#force Host#force}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#id Host#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param license: License key that will be applied to this host. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#license Host#license}
        :param lockdown: Set the host's lockdown status. Default is disabled. Valid options are 'disabled', 'normal', 'strict'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#lockdown Host#lockdown}
        :param maintenance: Set the host's maintenance mode. Default is false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#maintenance Host#maintenance}
        :param services: services block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#services Host#services}
        :param tags: A list of tag IDs to apply to this object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#tags Host#tags}
        :param thumbprint: Host's certificate SHA-1 thumbprint. If not set then the CA that signed the host's certificate must be trusted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#thumbprint Host#thumbprint}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a580e90e332f6218a0bbcd037feafe747086bd89743b8a299c1b96f2e80e7c61)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument hostname", value=hostname, expected_type=type_hints["hostname"])
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
            check_type(argname="argument cluster_managed", value=cluster_managed, expected_type=type_hints["cluster_managed"])
            check_type(argname="argument connected", value=connected, expected_type=type_hints["connected"])
            check_type(argname="argument custom_attributes", value=custom_attributes, expected_type=type_hints["custom_attributes"])
            check_type(argname="argument datacenter", value=datacenter, expected_type=type_hints["datacenter"])
            check_type(argname="argument force", value=force, expected_type=type_hints["force"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument license", value=license, expected_type=type_hints["license"])
            check_type(argname="argument lockdown", value=lockdown, expected_type=type_hints["lockdown"])
            check_type(argname="argument maintenance", value=maintenance, expected_type=type_hints["maintenance"])
            check_type(argname="argument services", value=services, expected_type=type_hints["services"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument thumbprint", value=thumbprint, expected_type=type_hints["thumbprint"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "hostname": hostname,
            "password": password,
            "username": username,
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
        if cluster is not None:
            self._values["cluster"] = cluster
        if cluster_managed is not None:
            self._values["cluster_managed"] = cluster_managed
        if connected is not None:
            self._values["connected"] = connected
        if custom_attributes is not None:
            self._values["custom_attributes"] = custom_attributes
        if datacenter is not None:
            self._values["datacenter"] = datacenter
        if force is not None:
            self._values["force"] = force
        if id is not None:
            self._values["id"] = id
        if license is not None:
            self._values["license"] = license
        if lockdown is not None:
            self._values["lockdown"] = lockdown
        if maintenance is not None:
            self._values["maintenance"] = maintenance
        if services is not None:
            self._values["services"] = services
        if tags is not None:
            self._values["tags"] = tags
        if thumbprint is not None:
            self._values["thumbprint"] = thumbprint

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
    def hostname(self) -> builtins.str:
        '''FQDN or IP address of the host.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#hostname Host#hostname}
        '''
        result = self._values.get("hostname")
        assert result is not None, "Required property 'hostname' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def password(self) -> builtins.str:
        '''Password of the administration account of the host.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#password Host#password}
        '''
        result = self._values.get("password")
        assert result is not None, "Required property 'password' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def username(self) -> builtins.str:
        '''Username of the administration account of the host.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#username Host#username}
        '''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cluster(self) -> typing.Optional[builtins.str]:
        '''ID of the vSphere cluster the host will belong to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#cluster Host#cluster}
        '''
        result = self._values.get("cluster")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cluster_managed(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Must be set if host is a member of a managed compute_cluster resource.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#cluster_managed Host#cluster_managed}
        '''
        result = self._values.get("cluster_managed")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def connected(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Set the state of the host. If set to false then the host will be asked to disconnect.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#connected Host#connected}
        '''
        result = self._values.get("connected")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def custom_attributes(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''A list of custom attributes to set on this resource.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#custom_attributes Host#custom_attributes}
        '''
        result = self._values.get("custom_attributes")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def datacenter(self) -> typing.Optional[builtins.str]:
        '''ID of the vSphere datacenter the host will belong to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#datacenter Host#datacenter}
        '''
        result = self._values.get("datacenter")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def force(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Force add the host to the vSphere inventory even if it's already managed by a different vCenter Server instance.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#force Host#force}
        '''
        result = self._values.get("force")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#id Host#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def license(self) -> typing.Optional[builtins.str]:
        '''License key that will be applied to this host.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#license Host#license}
        '''
        result = self._values.get("license")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lockdown(self) -> typing.Optional[builtins.str]:
        '''Set the host's lockdown status. Default is disabled. Valid options are 'disabled', 'normal', 'strict'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#lockdown Host#lockdown}
        '''
        result = self._values.get("lockdown")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maintenance(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Set the host's maintenance mode. Default is false.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#maintenance Host#maintenance}
        '''
        result = self._values.get("maintenance")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def services(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["HostServices"]]]:
        '''services block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#services Host#services}
        '''
        result = self._values.get("services")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["HostServices"]]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of tag IDs to apply to this object.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#tags Host#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def thumbprint(self) -> typing.Optional[builtins.str]:
        '''Host's certificate SHA-1 thumbprint. If not set then the CA that signed the host's certificate must be trusted.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#thumbprint Host#thumbprint}
        '''
        result = self._values.get("thumbprint")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HostConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.host.HostServices",
    jsii_struct_bases=[],
    name_mapping={"ntpd": "ntpd"},
)
class HostServices:
    def __init__(
        self,
        *,
        ntpd: typing.Optional[typing.Union["HostServicesNtpd", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param ntpd: ntpd block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#ntpd Host#ntpd}
        '''
        if isinstance(ntpd, dict):
            ntpd = HostServicesNtpd(**ntpd)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__29315a3149a21affaae54e08af2a7bc65ebfe5e3a68a74cfe327efed80797508)
            check_type(argname="argument ntpd", value=ntpd, expected_type=type_hints["ntpd"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if ntpd is not None:
            self._values["ntpd"] = ntpd

    @builtins.property
    def ntpd(self) -> typing.Optional["HostServicesNtpd"]:
        '''ntpd block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#ntpd Host#ntpd}
        '''
        result = self._values.get("ntpd")
        return typing.cast(typing.Optional["HostServicesNtpd"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HostServices(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class HostServicesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.host.HostServicesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__abac3b8493096d49e3f64854261317880a8a9d8c0eb1179587b1e36bbe7fb896)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "HostServicesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__545ef3f42915433758a2b6bbed7883f75bf492264c82b93417a4fded691b5bec)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("HostServicesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e59ef0a089db2314670b8f5ae63b08c9418222529aac6c386cf056c5eba58fa)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3b14637e29a9326d2f6fa5e319dc516282f2aaed303b56d2d723b852905bdc0e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4964bba948b9b207a12f3e80f7f69db974fa3aa3f3871256eb8e1c1a8d6cf19f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[HostServices]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[HostServices]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[HostServices]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06ff588729d1f6e43a35389d68d60b07e1942bfc1f6f0a0a1fddf89def2fc528)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.host.HostServicesNtpd",
    jsii_struct_bases=[],
    name_mapping={
        "enabled": "enabled",
        "ntp_servers": "ntpServers",
        "policy": "policy",
    },
)
class HostServicesNtpd:
    def __init__(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ntp_servers: typing.Optional[typing.Sequence[builtins.str]] = None,
        policy: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enabled: Whether the NTP service is enabled. Default is false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#enabled Host#enabled}
        :param ntp_servers: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#ntp_servers Host#ntp_servers}.
        :param policy: The policy for the NTP service. Valid values are 'Start and stop with host', 'Start and stop manually', 'Start and stop with port usage'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#policy Host#policy}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5bc2984d0213f3b6a7808bc64e17d95dbd20eb828463933140005db7aaf3181)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument ntp_servers", value=ntp_servers, expected_type=type_hints["ntp_servers"])
            check_type(argname="argument policy", value=policy, expected_type=type_hints["policy"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if enabled is not None:
            self._values["enabled"] = enabled
        if ntp_servers is not None:
            self._values["ntp_servers"] = ntp_servers
        if policy is not None:
            self._values["policy"] = policy

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether the NTP service is enabled. Default is false.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#enabled Host#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def ntp_servers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#ntp_servers Host#ntp_servers}.'''
        result = self._values.get("ntp_servers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def policy(self) -> typing.Optional[builtins.str]:
        '''The policy for the NTP service.

        Valid values are 'Start and stop with host', 'Start and stop manually', 'Start and stop with port usage'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#policy Host#policy}
        '''
        result = self._values.get("policy")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HostServicesNtpd(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class HostServicesNtpdOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.host.HostServicesNtpdOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b36440816340bb1a29714169ea4f32e9739a868ab7a367271cd751fe72b91bde)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetNtpServers")
    def reset_ntp_servers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNtpServers", []))

    @jsii.member(jsii_name="resetPolicy")
    def reset_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPolicy", []))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="ntpServersInput")
    def ntp_servers_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "ntpServersInput"))

    @builtins.property
    @jsii.member(jsii_name="policyInput")
    def policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyInput"))

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__078e7ce1dcc1b1b7d9d7c13b709d5c374af5bf39801fc38cc7d795e4f16dbf89)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ntpServers")
    def ntp_servers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "ntpServers"))

    @ntp_servers.setter
    def ntp_servers(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__90e143473cee2cc93dcc233db170fcc8fca6c3a3c6a41d6a40217225aec16180)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ntpServers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="policy")
    def policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policy"))

    @policy.setter
    def policy(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f0d3d2f221de69440608dd25f7bd918f0af2d5e8421fe2235707f966c6edcc04)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "policy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[HostServicesNtpd]:
        return typing.cast(typing.Optional[HostServicesNtpd], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[HostServicesNtpd]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51a340a838bcbe6a87ab9ca664731a8bbd5b58bbbe1ce330030e4b3a157cc7ad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class HostServicesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.host.HostServicesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5fb18dc59a5e1d29cf17edd2851b94df3126a32cb4e98b5c13c818bfa3ba2364)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putNtpd")
    def put_ntpd(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ntp_servers: typing.Optional[typing.Sequence[builtins.str]] = None,
        policy: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enabled: Whether the NTP service is enabled. Default is false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#enabled Host#enabled}
        :param ntp_servers: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#ntp_servers Host#ntp_servers}.
        :param policy: The policy for the NTP service. Valid values are 'Start and stop with host', 'Start and stop manually', 'Start and stop with port usage'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/host#policy Host#policy}
        '''
        value = HostServicesNtpd(
            enabled=enabled, ntp_servers=ntp_servers, policy=policy
        )

        return typing.cast(None, jsii.invoke(self, "putNtpd", [value]))

    @jsii.member(jsii_name="resetNtpd")
    def reset_ntpd(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNtpd", []))

    @builtins.property
    @jsii.member(jsii_name="ntpd")
    def ntpd(self) -> HostServicesNtpdOutputReference:
        return typing.cast(HostServicesNtpdOutputReference, jsii.get(self, "ntpd"))

    @builtins.property
    @jsii.member(jsii_name="ntpdInput")
    def ntpd_input(self) -> typing.Optional[HostServicesNtpd]:
        return typing.cast(typing.Optional[HostServicesNtpd], jsii.get(self, "ntpdInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, HostServices]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, HostServices]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, HostServices]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f1e28eab6af68c08c9a9de3ae7fd8006e8a477dd887c7a6a095e205961cc94e2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "Host",
    "HostConfig",
    "HostServices",
    "HostServicesList",
    "HostServicesNtpd",
    "HostServicesNtpdOutputReference",
    "HostServicesOutputReference",
]

publication.publish()

def _typecheckingstub__18656f2bce55e9eb067beb47951917f71009e8a54839905a64a063ce5611d366(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    hostname: builtins.str,
    password: builtins.str,
    username: builtins.str,
    cluster: typing.Optional[builtins.str] = None,
    cluster_managed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    connected: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    custom_attributes: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    datacenter: typing.Optional[builtins.str] = None,
    force: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    license: typing.Optional[builtins.str] = None,
    lockdown: typing.Optional[builtins.str] = None,
    maintenance: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    services: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[HostServices, typing.Dict[builtins.str, typing.Any]]]]] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    thumbprint: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__6d2b6d7d39b6e13fc59c5e4020c0c93baecb42aa66e830ccd378d6be85978b17(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73d44d063f0c1595d069d5bd50777ece6feb65a7d29377e8c5b665e51d2717e1(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[HostServices, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2ae23185c4b164fa5caf37e8e4b1837d6c21c574074aaed36f76ca42551b71c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d15b567c94b54dbee0dfdb3bf440d4dd9c794e704ffdef1b46176a07ce7ddf4a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33283475422b342868979da570a10f398a65dff50b47753ca3d2d2bf62b78720(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba7050dff28aa22cacaf2f1f31ec9dc41e257bd2ccc53371b619287da977a5f5(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c8a16c1d3c290cafdc00b1e512b42aff8daa961961d3db08de383cf56eaa5d6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__848ef7aa26ea97b467f84931dbc2aec8c00bb1e94edae9bb2fac128555de1f95(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45b56bf89d96eed7e70fdfda3a06ddae67e325fe70e3be6ea49fca18d13596c3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__722a4132e51ca38aa4ad983a4caf5d5e820239bde04a0f89375f94656a4b3e37(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6eeae5a5d7cd7ab5fb0c8679c98fa9f11271081601e870da3265b48a6a30fea2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a658533825a21aa287defd85c5195c27cae0ffda63adc2333525ef5cf57b18ed(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2231c4494c6d04b160868e358d41f327816e2a15e351c66e041501e2b8672241(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39951c2a9439e0fe784575b006260bea839e2004f2e9114a13af26d0f96cf6e0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89ec46c6f242a273c70a902123b2348e5c996e77a5206c6b1d2990ed7a162a6a(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f13cf599b236b2961ecce667030e74017c4c3a9cc90ddf73aa51a02f84971e9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc85a8ec8948a1119a52bdbb259bddc2479b9a2b8753725d602bbc62a209d7da(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a580e90e332f6218a0bbcd037feafe747086bd89743b8a299c1b96f2e80e7c61(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    hostname: builtins.str,
    password: builtins.str,
    username: builtins.str,
    cluster: typing.Optional[builtins.str] = None,
    cluster_managed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    connected: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    custom_attributes: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    datacenter: typing.Optional[builtins.str] = None,
    force: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    license: typing.Optional[builtins.str] = None,
    lockdown: typing.Optional[builtins.str] = None,
    maintenance: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    services: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[HostServices, typing.Dict[builtins.str, typing.Any]]]]] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    thumbprint: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__29315a3149a21affaae54e08af2a7bc65ebfe5e3a68a74cfe327efed80797508(
    *,
    ntpd: typing.Optional[typing.Union[HostServicesNtpd, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__abac3b8493096d49e3f64854261317880a8a9d8c0eb1179587b1e36bbe7fb896(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__545ef3f42915433758a2b6bbed7883f75bf492264c82b93417a4fded691b5bec(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e59ef0a089db2314670b8f5ae63b08c9418222529aac6c386cf056c5eba58fa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b14637e29a9326d2f6fa5e319dc516282f2aaed303b56d2d723b852905bdc0e(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4964bba948b9b207a12f3e80f7f69db974fa3aa3f3871256eb8e1c1a8d6cf19f(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06ff588729d1f6e43a35389d68d60b07e1942bfc1f6f0a0a1fddf89def2fc528(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[HostServices]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5bc2984d0213f3b6a7808bc64e17d95dbd20eb828463933140005db7aaf3181(
    *,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ntp_servers: typing.Optional[typing.Sequence[builtins.str]] = None,
    policy: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b36440816340bb1a29714169ea4f32e9739a868ab7a367271cd751fe72b91bde(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__078e7ce1dcc1b1b7d9d7c13b709d5c374af5bf39801fc38cc7d795e4f16dbf89(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__90e143473cee2cc93dcc233db170fcc8fca6c3a3c6a41d6a40217225aec16180(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0d3d2f221de69440608dd25f7bd918f0af2d5e8421fe2235707f966c6edcc04(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51a340a838bcbe6a87ab9ca664731a8bbd5b58bbbe1ce330030e4b3a157cc7ad(
    value: typing.Optional[HostServicesNtpd],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5fb18dc59a5e1d29cf17edd2851b94df3126a32cb4e98b5c13c818bfa3ba2364(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1e28eab6af68c08c9a9de3ae7fd8006e8a477dd887c7a6a095e205961cc94e2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, HostServices]],
) -> None:
    """Type checking stubs"""
    pass
