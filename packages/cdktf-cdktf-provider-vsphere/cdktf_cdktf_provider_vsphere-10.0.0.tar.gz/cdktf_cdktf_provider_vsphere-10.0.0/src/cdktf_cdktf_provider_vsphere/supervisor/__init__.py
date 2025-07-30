r'''
# `vsphere_supervisor`

Refer to the Terraform Registry for docs: [`vsphere_supervisor`](https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor).
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


class Supervisor(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.supervisor.Supervisor",
):
    '''Represents a {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor vsphere_supervisor}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        cluster: builtins.str,
        content_library: builtins.str,
        dvs_uuid: builtins.str,
        edge_cluster: builtins.str,
        egress_cidr: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["SupervisorEgressCidr", typing.Dict[builtins.str, typing.Any]]]],
        ingress_cidr: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["SupervisorIngressCidr", typing.Dict[builtins.str, typing.Any]]]],
        main_dns: typing.Sequence[builtins.str],
        main_ntp: typing.Sequence[builtins.str],
        management_network: typing.Union["SupervisorManagementNetwork", typing.Dict[builtins.str, typing.Any]],
        pod_cidr: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["SupervisorPodCidr", typing.Dict[builtins.str, typing.Any]]]],
        search_domains: typing.Sequence[builtins.str],
        service_cidr: typing.Union["SupervisorServiceCidr", typing.Dict[builtins.str, typing.Any]],
        sizing_hint: builtins.str,
        storage_policy: builtins.str,
        worker_dns: typing.Sequence[builtins.str],
        worker_ntp: typing.Sequence[builtins.str],
        id: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["SupervisorNamespace", typing.Dict[builtins.str, typing.Any]]]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor vsphere_supervisor} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param cluster: ID of the vSphere cluster on which workload management will be enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#cluster Supervisor#cluster}
        :param content_library: ID of the subscribed content library. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#content_library Supervisor#content_library}
        :param dvs_uuid: The UUID (not ID) of the distributed switch. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#dvs_uuid Supervisor#dvs_uuid}
        :param edge_cluster: ID of the NSX Edge Cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#edge_cluster Supervisor#edge_cluster}
        :param egress_cidr: egress_cidr block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#egress_cidr Supervisor#egress_cidr}
        :param ingress_cidr: ingress_cidr block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#ingress_cidr Supervisor#ingress_cidr}
        :param main_dns: List of DNS servers to use on the Kubernetes API server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#main_dns Supervisor#main_dns}
        :param main_ntp: List of NTP servers to use on the Kubernetes API server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#main_ntp Supervisor#main_ntp}
        :param management_network: management_network block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#management_network Supervisor#management_network}
        :param pod_cidr: pod_cidr block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#pod_cidr Supervisor#pod_cidr}
        :param search_domains: List of DNS search domains. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#search_domains Supervisor#search_domains}
        :param service_cidr: service_cidr block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#service_cidr Supervisor#service_cidr}
        :param sizing_hint: Size of the Kubernetes API server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#sizing_hint Supervisor#sizing_hint}
        :param storage_policy: The name of a storage policy associated with the datastore where the container images will be stored. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#storage_policy Supervisor#storage_policy}
        :param worker_dns: List of DNS servers to use on the worker nodes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#worker_dns Supervisor#worker_dns}
        :param worker_ntp: List of NTP servers to use on the worker nodes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#worker_ntp Supervisor#worker_ntp}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#id Supervisor#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param namespace: namespace block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#namespace Supervisor#namespace}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__42bb64ccaeb776b2fa92b408ce34671880e0698548e105f3d47944aec0a74ae4)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = SupervisorConfig(
            cluster=cluster,
            content_library=content_library,
            dvs_uuid=dvs_uuid,
            edge_cluster=edge_cluster,
            egress_cidr=egress_cidr,
            ingress_cidr=ingress_cidr,
            main_dns=main_dns,
            main_ntp=main_ntp,
            management_network=management_network,
            pod_cidr=pod_cidr,
            search_domains=search_domains,
            service_cidr=service_cidr,
            sizing_hint=sizing_hint,
            storage_policy=storage_policy,
            worker_dns=worker_dns,
            worker_ntp=worker_ntp,
            id=id,
            namespace=namespace,
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
        '''Generates CDKTF code for importing a Supervisor resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the Supervisor to import.
        :param import_from_id: The id of the existing Supervisor that should be imported. Refer to the {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the Supervisor to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc1355035c9294a769a2cbad3bfd3b44cb962ee91bfddcc75524b2c636ed8be3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putEgressCidr")
    def put_egress_cidr(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["SupervisorEgressCidr", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a5d6e25b08583cb9e594dafeab8670d83688b2d3ad54d978e0589a772851265)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putEgressCidr", [value]))

    @jsii.member(jsii_name="putIngressCidr")
    def put_ingress_cidr(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["SupervisorIngressCidr", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f65aa19124bffbdf1f52fb47e6088cbc850acfbfec41ba58f5c581ddecc9d1e0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putIngressCidr", [value]))

    @jsii.member(jsii_name="putManagementNetwork")
    def put_management_network(
        self,
        *,
        address_count: jsii.Number,
        gateway: builtins.str,
        network: builtins.str,
        starting_address: builtins.str,
        subnet_mask: builtins.str,
    ) -> None:
        '''
        :param address_count: Number of addresses to allocate. Starts from 'starting_address'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#address_count Supervisor#address_count}
        :param gateway: Gateway IP address. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#gateway Supervisor#gateway}
        :param network: ID of the network. (e.g. a distributed port group). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#network Supervisor#network}
        :param starting_address: Starting address of the management network range. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#starting_address Supervisor#starting_address}
        :param subnet_mask: Subnet mask. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#subnet_mask Supervisor#subnet_mask}
        '''
        value = SupervisorManagementNetwork(
            address_count=address_count,
            gateway=gateway,
            network=network,
            starting_address=starting_address,
            subnet_mask=subnet_mask,
        )

        return typing.cast(None, jsii.invoke(self, "putManagementNetwork", [value]))

    @jsii.member(jsii_name="putNamespace")
    def put_namespace(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["SupervisorNamespace", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__991f70a1db6040a8e541069f201538b32708c29bca3b49f54de76413222a437b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putNamespace", [value]))

    @jsii.member(jsii_name="putPodCidr")
    def put_pod_cidr(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["SupervisorPodCidr", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d044350576e4be9f689486db9326347f0a67d3cf4b2ec59dc00f7d063be7d509)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putPodCidr", [value]))

    @jsii.member(jsii_name="putServiceCidr")
    def put_service_cidr(self, *, address: builtins.str, prefix: jsii.Number) -> None:
        '''
        :param address: Network address. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#address Supervisor#address}
        :param prefix: Subnet prefix. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#prefix Supervisor#prefix}
        '''
        value = SupervisorServiceCidr(address=address, prefix=prefix)

        return typing.cast(None, jsii.invoke(self, "putServiceCidr", [value]))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

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
    @jsii.member(jsii_name="egressCidr")
    def egress_cidr(self) -> "SupervisorEgressCidrList":
        return typing.cast("SupervisorEgressCidrList", jsii.get(self, "egressCidr"))

    @builtins.property
    @jsii.member(jsii_name="ingressCidr")
    def ingress_cidr(self) -> "SupervisorIngressCidrList":
        return typing.cast("SupervisorIngressCidrList", jsii.get(self, "ingressCidr"))

    @builtins.property
    @jsii.member(jsii_name="managementNetwork")
    def management_network(self) -> "SupervisorManagementNetworkOutputReference":
        return typing.cast("SupervisorManagementNetworkOutputReference", jsii.get(self, "managementNetwork"))

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> "SupervisorNamespaceList":
        return typing.cast("SupervisorNamespaceList", jsii.get(self, "namespace"))

    @builtins.property
    @jsii.member(jsii_name="podCidr")
    def pod_cidr(self) -> "SupervisorPodCidrList":
        return typing.cast("SupervisorPodCidrList", jsii.get(self, "podCidr"))

    @builtins.property
    @jsii.member(jsii_name="serviceCidr")
    def service_cidr(self) -> "SupervisorServiceCidrOutputReference":
        return typing.cast("SupervisorServiceCidrOutputReference", jsii.get(self, "serviceCidr"))

    @builtins.property
    @jsii.member(jsii_name="clusterInput")
    def cluster_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterInput"))

    @builtins.property
    @jsii.member(jsii_name="contentLibraryInput")
    def content_library_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "contentLibraryInput"))

    @builtins.property
    @jsii.member(jsii_name="dvsUuidInput")
    def dvs_uuid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dvsUuidInput"))

    @builtins.property
    @jsii.member(jsii_name="edgeClusterInput")
    def edge_cluster_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "edgeClusterInput"))

    @builtins.property
    @jsii.member(jsii_name="egressCidrInput")
    def egress_cidr_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["SupervisorEgressCidr"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["SupervisorEgressCidr"]]], jsii.get(self, "egressCidrInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="ingressCidrInput")
    def ingress_cidr_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["SupervisorIngressCidr"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["SupervisorIngressCidr"]]], jsii.get(self, "ingressCidrInput"))

    @builtins.property
    @jsii.member(jsii_name="mainDnsInput")
    def main_dns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "mainDnsInput"))

    @builtins.property
    @jsii.member(jsii_name="mainNtpInput")
    def main_ntp_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "mainNtpInput"))

    @builtins.property
    @jsii.member(jsii_name="managementNetworkInput")
    def management_network_input(
        self,
    ) -> typing.Optional["SupervisorManagementNetwork"]:
        return typing.cast(typing.Optional["SupervisorManagementNetwork"], jsii.get(self, "managementNetworkInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["SupervisorNamespace"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["SupervisorNamespace"]]], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="podCidrInput")
    def pod_cidr_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["SupervisorPodCidr"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["SupervisorPodCidr"]]], jsii.get(self, "podCidrInput"))

    @builtins.property
    @jsii.member(jsii_name="searchDomainsInput")
    def search_domains_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "searchDomainsInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceCidrInput")
    def service_cidr_input(self) -> typing.Optional["SupervisorServiceCidr"]:
        return typing.cast(typing.Optional["SupervisorServiceCidr"], jsii.get(self, "serviceCidrInput"))

    @builtins.property
    @jsii.member(jsii_name="sizingHintInput")
    def sizing_hint_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sizingHintInput"))

    @builtins.property
    @jsii.member(jsii_name="storagePolicyInput")
    def storage_policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "storagePolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="workerDnsInput")
    def worker_dns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "workerDnsInput"))

    @builtins.property
    @jsii.member(jsii_name="workerNtpInput")
    def worker_ntp_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "workerNtpInput"))

    @builtins.property
    @jsii.member(jsii_name="cluster")
    def cluster(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cluster"))

    @cluster.setter
    def cluster(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9406f3cbcdabf4a9d65a1419fcbc17955d9470cc6cd0a5a6497c0d4d3d15d29c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cluster", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="contentLibrary")
    def content_library(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "contentLibrary"))

    @content_library.setter
    def content_library(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33e0507f632885072296c4432909eeb06f06b1850e16497b6f27cc1ec06fdda7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "contentLibrary", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dvsUuid")
    def dvs_uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dvsUuid"))

    @dvs_uuid.setter
    def dvs_uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d6c92e3006fdaaecc8cdeab31a2ef76b18b4fc200a727d934f0702107570935)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dvsUuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="edgeCluster")
    def edge_cluster(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "edgeCluster"))

    @edge_cluster.setter
    def edge_cluster(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e2db014767be38804f03419e6fe26d7f286f0fcac53fcb74f17957d0ed9ba1f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "edgeCluster", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__673fb5f2badb3efc54456f78e2953ec2cd27000b655d6bc69b75151969168596)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="mainDns")
    def main_dns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "mainDns"))

    @main_dns.setter
    def main_dns(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3712e12b1604a0a18434549088319cf449072837d2e1bb51a5915e1f0238997)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mainDns", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="mainNtp")
    def main_ntp(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "mainNtp"))

    @main_ntp.setter
    def main_ntp(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e7dffc1f3a34ca1bb5b7addb869aa4b8da8ccb9faffab1cfb5394f2a5fc43d22)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mainNtp", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="searchDomains")
    def search_domains(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "searchDomains"))

    @search_domains.setter
    def search_domains(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4485230cb96b424ab817470e06b7bc0d21b5d968cc6fbda0b3616d3344d0b08a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "searchDomains", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sizingHint")
    def sizing_hint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sizingHint"))

    @sizing_hint.setter
    def sizing_hint(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1a1c4f44668c63e33edb62d7e262c82eabeee9971bbd5dc47d425c99dcb8a83)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sizingHint", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="storagePolicy")
    def storage_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storagePolicy"))

    @storage_policy.setter
    def storage_policy(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e663d90b3462b304da45e1e9868f76b116535d52d78853a1b1e6b1e59b2b4c53)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "storagePolicy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workerDns")
    def worker_dns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "workerDns"))

    @worker_dns.setter
    def worker_dns(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f1d5982479664eff14d70be3c656b703b3e3d490738988277c3ebe12dcff440)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workerDns", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workerNtp")
    def worker_ntp(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "workerNtp"))

    @worker_ntp.setter
    def worker_ntp(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__047d66d5c19389e45d44a9061ac0d88c0c91c08f62c0a2682c2a7a43ec8561c7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workerNtp", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.supervisor.SupervisorConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "cluster": "cluster",
        "content_library": "contentLibrary",
        "dvs_uuid": "dvsUuid",
        "edge_cluster": "edgeCluster",
        "egress_cidr": "egressCidr",
        "ingress_cidr": "ingressCidr",
        "main_dns": "mainDns",
        "main_ntp": "mainNtp",
        "management_network": "managementNetwork",
        "pod_cidr": "podCidr",
        "search_domains": "searchDomains",
        "service_cidr": "serviceCidr",
        "sizing_hint": "sizingHint",
        "storage_policy": "storagePolicy",
        "worker_dns": "workerDns",
        "worker_ntp": "workerNtp",
        "id": "id",
        "namespace": "namespace",
    },
)
class SupervisorConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        cluster: builtins.str,
        content_library: builtins.str,
        dvs_uuid: builtins.str,
        edge_cluster: builtins.str,
        egress_cidr: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["SupervisorEgressCidr", typing.Dict[builtins.str, typing.Any]]]],
        ingress_cidr: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["SupervisorIngressCidr", typing.Dict[builtins.str, typing.Any]]]],
        main_dns: typing.Sequence[builtins.str],
        main_ntp: typing.Sequence[builtins.str],
        management_network: typing.Union["SupervisorManagementNetwork", typing.Dict[builtins.str, typing.Any]],
        pod_cidr: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["SupervisorPodCidr", typing.Dict[builtins.str, typing.Any]]]],
        search_domains: typing.Sequence[builtins.str],
        service_cidr: typing.Union["SupervisorServiceCidr", typing.Dict[builtins.str, typing.Any]],
        sizing_hint: builtins.str,
        storage_policy: builtins.str,
        worker_dns: typing.Sequence[builtins.str],
        worker_ntp: typing.Sequence[builtins.str],
        id: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["SupervisorNamespace", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param cluster: ID of the vSphere cluster on which workload management will be enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#cluster Supervisor#cluster}
        :param content_library: ID of the subscribed content library. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#content_library Supervisor#content_library}
        :param dvs_uuid: The UUID (not ID) of the distributed switch. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#dvs_uuid Supervisor#dvs_uuid}
        :param edge_cluster: ID of the NSX Edge Cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#edge_cluster Supervisor#edge_cluster}
        :param egress_cidr: egress_cidr block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#egress_cidr Supervisor#egress_cidr}
        :param ingress_cidr: ingress_cidr block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#ingress_cidr Supervisor#ingress_cidr}
        :param main_dns: List of DNS servers to use on the Kubernetes API server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#main_dns Supervisor#main_dns}
        :param main_ntp: List of NTP servers to use on the Kubernetes API server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#main_ntp Supervisor#main_ntp}
        :param management_network: management_network block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#management_network Supervisor#management_network}
        :param pod_cidr: pod_cidr block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#pod_cidr Supervisor#pod_cidr}
        :param search_domains: List of DNS search domains. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#search_domains Supervisor#search_domains}
        :param service_cidr: service_cidr block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#service_cidr Supervisor#service_cidr}
        :param sizing_hint: Size of the Kubernetes API server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#sizing_hint Supervisor#sizing_hint}
        :param storage_policy: The name of a storage policy associated with the datastore where the container images will be stored. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#storage_policy Supervisor#storage_policy}
        :param worker_dns: List of DNS servers to use on the worker nodes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#worker_dns Supervisor#worker_dns}
        :param worker_ntp: List of NTP servers to use on the worker nodes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#worker_ntp Supervisor#worker_ntp}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#id Supervisor#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param namespace: namespace block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#namespace Supervisor#namespace}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(management_network, dict):
            management_network = SupervisorManagementNetwork(**management_network)
        if isinstance(service_cidr, dict):
            service_cidr = SupervisorServiceCidr(**service_cidr)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ee90cb4864bc34c360e0a774589f0db851b00317783a30cade14411164eb18e)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
            check_type(argname="argument content_library", value=content_library, expected_type=type_hints["content_library"])
            check_type(argname="argument dvs_uuid", value=dvs_uuid, expected_type=type_hints["dvs_uuid"])
            check_type(argname="argument edge_cluster", value=edge_cluster, expected_type=type_hints["edge_cluster"])
            check_type(argname="argument egress_cidr", value=egress_cidr, expected_type=type_hints["egress_cidr"])
            check_type(argname="argument ingress_cidr", value=ingress_cidr, expected_type=type_hints["ingress_cidr"])
            check_type(argname="argument main_dns", value=main_dns, expected_type=type_hints["main_dns"])
            check_type(argname="argument main_ntp", value=main_ntp, expected_type=type_hints["main_ntp"])
            check_type(argname="argument management_network", value=management_network, expected_type=type_hints["management_network"])
            check_type(argname="argument pod_cidr", value=pod_cidr, expected_type=type_hints["pod_cidr"])
            check_type(argname="argument search_domains", value=search_domains, expected_type=type_hints["search_domains"])
            check_type(argname="argument service_cidr", value=service_cidr, expected_type=type_hints["service_cidr"])
            check_type(argname="argument sizing_hint", value=sizing_hint, expected_type=type_hints["sizing_hint"])
            check_type(argname="argument storage_policy", value=storage_policy, expected_type=type_hints["storage_policy"])
            check_type(argname="argument worker_dns", value=worker_dns, expected_type=type_hints["worker_dns"])
            check_type(argname="argument worker_ntp", value=worker_ntp, expected_type=type_hints["worker_ntp"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cluster": cluster,
            "content_library": content_library,
            "dvs_uuid": dvs_uuid,
            "edge_cluster": edge_cluster,
            "egress_cidr": egress_cidr,
            "ingress_cidr": ingress_cidr,
            "main_dns": main_dns,
            "main_ntp": main_ntp,
            "management_network": management_network,
            "pod_cidr": pod_cidr,
            "search_domains": search_domains,
            "service_cidr": service_cidr,
            "sizing_hint": sizing_hint,
            "storage_policy": storage_policy,
            "worker_dns": worker_dns,
            "worker_ntp": worker_ntp,
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
        if id is not None:
            self._values["id"] = id
        if namespace is not None:
            self._values["namespace"] = namespace

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
    def cluster(self) -> builtins.str:
        '''ID of the vSphere cluster on which workload management will be enabled.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#cluster Supervisor#cluster}
        '''
        result = self._values.get("cluster")
        assert result is not None, "Required property 'cluster' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def content_library(self) -> builtins.str:
        '''ID of the subscribed content library.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#content_library Supervisor#content_library}
        '''
        result = self._values.get("content_library")
        assert result is not None, "Required property 'content_library' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def dvs_uuid(self) -> builtins.str:
        '''The UUID (not ID) of the distributed switch.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#dvs_uuid Supervisor#dvs_uuid}
        '''
        result = self._values.get("dvs_uuid")
        assert result is not None, "Required property 'dvs_uuid' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def edge_cluster(self) -> builtins.str:
        '''ID of the NSX Edge Cluster.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#edge_cluster Supervisor#edge_cluster}
        '''
        result = self._values.get("edge_cluster")
        assert result is not None, "Required property 'edge_cluster' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def egress_cidr(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["SupervisorEgressCidr"]]:
        '''egress_cidr block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#egress_cidr Supervisor#egress_cidr}
        '''
        result = self._values.get("egress_cidr")
        assert result is not None, "Required property 'egress_cidr' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["SupervisorEgressCidr"]], result)

    @builtins.property
    def ingress_cidr(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["SupervisorIngressCidr"]]:
        '''ingress_cidr block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#ingress_cidr Supervisor#ingress_cidr}
        '''
        result = self._values.get("ingress_cidr")
        assert result is not None, "Required property 'ingress_cidr' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["SupervisorIngressCidr"]], result)

    @builtins.property
    def main_dns(self) -> typing.List[builtins.str]:
        '''List of DNS servers to use on the Kubernetes API server.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#main_dns Supervisor#main_dns}
        '''
        result = self._values.get("main_dns")
        assert result is not None, "Required property 'main_dns' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def main_ntp(self) -> typing.List[builtins.str]:
        '''List of NTP servers to use on the Kubernetes API server.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#main_ntp Supervisor#main_ntp}
        '''
        result = self._values.get("main_ntp")
        assert result is not None, "Required property 'main_ntp' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def management_network(self) -> "SupervisorManagementNetwork":
        '''management_network block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#management_network Supervisor#management_network}
        '''
        result = self._values.get("management_network")
        assert result is not None, "Required property 'management_network' is missing"
        return typing.cast("SupervisorManagementNetwork", result)

    @builtins.property
    def pod_cidr(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["SupervisorPodCidr"]]:
        '''pod_cidr block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#pod_cidr Supervisor#pod_cidr}
        '''
        result = self._values.get("pod_cidr")
        assert result is not None, "Required property 'pod_cidr' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["SupervisorPodCidr"]], result)

    @builtins.property
    def search_domains(self) -> typing.List[builtins.str]:
        '''List of DNS search domains.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#search_domains Supervisor#search_domains}
        '''
        result = self._values.get("search_domains")
        assert result is not None, "Required property 'search_domains' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def service_cidr(self) -> "SupervisorServiceCidr":
        '''service_cidr block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#service_cidr Supervisor#service_cidr}
        '''
        result = self._values.get("service_cidr")
        assert result is not None, "Required property 'service_cidr' is missing"
        return typing.cast("SupervisorServiceCidr", result)

    @builtins.property
    def sizing_hint(self) -> builtins.str:
        '''Size of the Kubernetes API server.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#sizing_hint Supervisor#sizing_hint}
        '''
        result = self._values.get("sizing_hint")
        assert result is not None, "Required property 'sizing_hint' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def storage_policy(self) -> builtins.str:
        '''The name of a storage policy associated with the datastore where the container images will be stored.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#storage_policy Supervisor#storage_policy}
        '''
        result = self._values.get("storage_policy")
        assert result is not None, "Required property 'storage_policy' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def worker_dns(self) -> typing.List[builtins.str]:
        '''List of DNS servers to use on the worker nodes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#worker_dns Supervisor#worker_dns}
        '''
        result = self._values.get("worker_dns")
        assert result is not None, "Required property 'worker_dns' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def worker_ntp(self) -> typing.List[builtins.str]:
        '''List of NTP servers to use on the worker nodes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#worker_ntp Supervisor#worker_ntp}
        '''
        result = self._values.get("worker_ntp")
        assert result is not None, "Required property 'worker_ntp' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#id Supervisor#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["SupervisorNamespace"]]]:
        '''namespace block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#namespace Supervisor#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["SupervisorNamespace"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SupervisorConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.supervisor.SupervisorEgressCidr",
    jsii_struct_bases=[],
    name_mapping={"address": "address", "prefix": "prefix"},
)
class SupervisorEgressCidr:
    def __init__(self, *, address: builtins.str, prefix: jsii.Number) -> None:
        '''
        :param address: Network address. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#address Supervisor#address}
        :param prefix: Subnet prefix. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#prefix Supervisor#prefix}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__029ec7c182215e880c0f08f938cb720f8802bdb512a69ae1fc6aabefc8ab373f)
            check_type(argname="argument address", value=address, expected_type=type_hints["address"])
            check_type(argname="argument prefix", value=prefix, expected_type=type_hints["prefix"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "address": address,
            "prefix": prefix,
        }

    @builtins.property
    def address(self) -> builtins.str:
        '''Network address.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#address Supervisor#address}
        '''
        result = self._values.get("address")
        assert result is not None, "Required property 'address' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def prefix(self) -> jsii.Number:
        '''Subnet prefix.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#prefix Supervisor#prefix}
        '''
        result = self._values.get("prefix")
        assert result is not None, "Required property 'prefix' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SupervisorEgressCidr(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SupervisorEgressCidrList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.supervisor.SupervisorEgressCidrList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__981ea3ec194ff313f904ee7825f30515c6e809c60daa9fefd77c149d19b25d9e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "SupervisorEgressCidrOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a78e30af6b04bb1feb29c5cb5de7119b2f2e543cc933de078ae7f06ac57b8bec)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("SupervisorEgressCidrOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a40eb9c97904939ea6be8799ca3ebaa79338ac95e7cb3f5772255285baeff7b6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__52a5aa01543337495141d34744760969d14734e13dc3f549aa8b274d22dbb57e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0df5bb3dedd534999ba83ccca92f3a6822c697dc33c86bb62c91f43b4aa01354)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[SupervisorEgressCidr]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[SupervisorEgressCidr]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[SupervisorEgressCidr]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__350b259c7b39498dbf9dd295ef84f88d92eb56a91a226d5dc71c485e6653fe49)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class SupervisorEgressCidrOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.supervisor.SupervisorEgressCidrOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cdee6047fef5fcc2d305df3d6ab044fdf44903111b68c57e43cf82ee5d347499)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="addressInput")
    def address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "addressInput"))

    @builtins.property
    @jsii.member(jsii_name="prefixInput")
    def prefix_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "prefixInput"))

    @builtins.property
    @jsii.member(jsii_name="address")
    def address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "address"))

    @address.setter
    def address(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d17b9b59d98caf9fb8a8b0576a40713525f325fc770d5f8e90365e6ebf65c9d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "address", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="prefix")
    def prefix(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "prefix"))

    @prefix.setter
    def prefix(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d54b70c7f9df80f730daa7e38abcf8feb8374de0616cd99963cec509cee4e9da)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "prefix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, SupervisorEgressCidr]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, SupervisorEgressCidr]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, SupervisorEgressCidr]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c57f5c221981af3970dfa777b7f00c7a0e709d3c8e69f5ad51a59b2322a3273)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.supervisor.SupervisorIngressCidr",
    jsii_struct_bases=[],
    name_mapping={"address": "address", "prefix": "prefix"},
)
class SupervisorIngressCidr:
    def __init__(self, *, address: builtins.str, prefix: jsii.Number) -> None:
        '''
        :param address: Network address. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#address Supervisor#address}
        :param prefix: Subnet prefix. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#prefix Supervisor#prefix}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c14c4049a7970dd79d6704b789e1e9052b0f4775cf77133de32affc33e294d65)
            check_type(argname="argument address", value=address, expected_type=type_hints["address"])
            check_type(argname="argument prefix", value=prefix, expected_type=type_hints["prefix"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "address": address,
            "prefix": prefix,
        }

    @builtins.property
    def address(self) -> builtins.str:
        '''Network address.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#address Supervisor#address}
        '''
        result = self._values.get("address")
        assert result is not None, "Required property 'address' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def prefix(self) -> jsii.Number:
        '''Subnet prefix.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#prefix Supervisor#prefix}
        '''
        result = self._values.get("prefix")
        assert result is not None, "Required property 'prefix' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SupervisorIngressCidr(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SupervisorIngressCidrList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.supervisor.SupervisorIngressCidrList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e6fd85546f54a754e54d3b5571174bbce3100bd0cdfac70bb1b5ae2f8a34e87a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "SupervisorIngressCidrOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48fe94302280c337fd664fe5b705d4b1679b36a69d6e8c14854532f69ede35f2)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("SupervisorIngressCidrOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__96807b41c7b3cc71fcea612e4d12c5d7ace89947deb3c7a8151dcae19f06554e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__84a2c0c3724a56910cce3c04c07d55700d3b398865f3e1147b003559c3d0cca3)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9a59e2f4c58b0107aa51bf414855e2a97c39ca4687ad63c036f3f730dc723658)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[SupervisorIngressCidr]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[SupervisorIngressCidr]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[SupervisorIngressCidr]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a02cbe9f0ab7f876f152908f13a7491dd6ed5a8d432cbbf28025774a59a26afc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class SupervisorIngressCidrOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.supervisor.SupervisorIngressCidrOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__290f8aa88379dff893b73190c71b49f3aa62932a6ca816dcf0585a9ac4409d52)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="addressInput")
    def address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "addressInput"))

    @builtins.property
    @jsii.member(jsii_name="prefixInput")
    def prefix_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "prefixInput"))

    @builtins.property
    @jsii.member(jsii_name="address")
    def address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "address"))

    @address.setter
    def address(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee5caa392a115886cd73f6c0a8bc01e7b7deea0feb7fd0b3d7832074cc6dec9f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "address", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="prefix")
    def prefix(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "prefix"))

    @prefix.setter
    def prefix(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10aa83d649c14fef15dc8e09199acbb66612483d9c8ba4200628cf827507067f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "prefix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, SupervisorIngressCidr]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, SupervisorIngressCidr]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, SupervisorIngressCidr]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e21e1b4a8a74967f9d32b75c677a4cc79b2ade6d13620b175914b78d004ce15d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.supervisor.SupervisorManagementNetwork",
    jsii_struct_bases=[],
    name_mapping={
        "address_count": "addressCount",
        "gateway": "gateway",
        "network": "network",
        "starting_address": "startingAddress",
        "subnet_mask": "subnetMask",
    },
)
class SupervisorManagementNetwork:
    def __init__(
        self,
        *,
        address_count: jsii.Number,
        gateway: builtins.str,
        network: builtins.str,
        starting_address: builtins.str,
        subnet_mask: builtins.str,
    ) -> None:
        '''
        :param address_count: Number of addresses to allocate. Starts from 'starting_address'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#address_count Supervisor#address_count}
        :param gateway: Gateway IP address. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#gateway Supervisor#gateway}
        :param network: ID of the network. (e.g. a distributed port group). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#network Supervisor#network}
        :param starting_address: Starting address of the management network range. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#starting_address Supervisor#starting_address}
        :param subnet_mask: Subnet mask. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#subnet_mask Supervisor#subnet_mask}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__280e1dff9a942c8000be626bcdd909042295d90a4d84efa6418b7b3bd86cc363)
            check_type(argname="argument address_count", value=address_count, expected_type=type_hints["address_count"])
            check_type(argname="argument gateway", value=gateway, expected_type=type_hints["gateway"])
            check_type(argname="argument network", value=network, expected_type=type_hints["network"])
            check_type(argname="argument starting_address", value=starting_address, expected_type=type_hints["starting_address"])
            check_type(argname="argument subnet_mask", value=subnet_mask, expected_type=type_hints["subnet_mask"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "address_count": address_count,
            "gateway": gateway,
            "network": network,
            "starting_address": starting_address,
            "subnet_mask": subnet_mask,
        }

    @builtins.property
    def address_count(self) -> jsii.Number:
        '''Number of addresses to allocate. Starts from 'starting_address'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#address_count Supervisor#address_count}
        '''
        result = self._values.get("address_count")
        assert result is not None, "Required property 'address_count' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def gateway(self) -> builtins.str:
        '''Gateway IP address.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#gateway Supervisor#gateway}
        '''
        result = self._values.get("gateway")
        assert result is not None, "Required property 'gateway' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def network(self) -> builtins.str:
        '''ID of the network. (e.g. a distributed port group).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#network Supervisor#network}
        '''
        result = self._values.get("network")
        assert result is not None, "Required property 'network' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def starting_address(self) -> builtins.str:
        '''Starting address of the management network range.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#starting_address Supervisor#starting_address}
        '''
        result = self._values.get("starting_address")
        assert result is not None, "Required property 'starting_address' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subnet_mask(self) -> builtins.str:
        '''Subnet mask.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#subnet_mask Supervisor#subnet_mask}
        '''
        result = self._values.get("subnet_mask")
        assert result is not None, "Required property 'subnet_mask' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SupervisorManagementNetwork(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SupervisorManagementNetworkOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.supervisor.SupervisorManagementNetworkOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__216081e3c36a39d9c9713c43b9f09a1ea6db7973ad6995aff819592a7bd4c812)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="addressCountInput")
    def address_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "addressCountInput"))

    @builtins.property
    @jsii.member(jsii_name="gatewayInput")
    def gateway_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gatewayInput"))

    @builtins.property
    @jsii.member(jsii_name="networkInput")
    def network_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "networkInput"))

    @builtins.property
    @jsii.member(jsii_name="startingAddressInput")
    def starting_address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "startingAddressInput"))

    @builtins.property
    @jsii.member(jsii_name="subnetMaskInput")
    def subnet_mask_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subnetMaskInput"))

    @builtins.property
    @jsii.member(jsii_name="addressCount")
    def address_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "addressCount"))

    @address_count.setter
    def address_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e6e8cce898411d1cc64197877750a1f2b686d91a37378a0c0e4a00104dd1ae0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "addressCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="gateway")
    def gateway(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gateway"))

    @gateway.setter
    def gateway(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a003452b8ba50885bebf370f74986784e001d59d8d22bee02597daa1f2d344af)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gateway", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="network")
    def network(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "network"))

    @network.setter
    def network(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e0ca4229e9068cb3598aba8186bb3bf1361b82046d0a071f4c9dc43c5778a44)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "network", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="startingAddress")
    def starting_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "startingAddress"))

    @starting_address.setter
    def starting_address(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d41d10bd4db90877d9fa4693b8150d97509f8e9999f80ce9f625b50683bd74b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "startingAddress", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="subnetMask")
    def subnet_mask(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subnetMask"))

    @subnet_mask.setter
    def subnet_mask(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9cb3a655bbaabfb9dd66d4c4d6f3d52779089cc4a5f6dad3528e630019393f60)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subnetMask", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[SupervisorManagementNetwork]:
        return typing.cast(typing.Optional[SupervisorManagementNetwork], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[SupervisorManagementNetwork],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5f6e566dd098604e4df8cf2538b49a6f63c1f9ca892fd8cbaff27304fc83e75)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.supervisor.SupervisorNamespace",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "content_libraries": "contentLibraries",
        "vm_classes": "vmClasses",
    },
)
class SupervisorNamespace:
    def __init__(
        self,
        *,
        name: builtins.str,
        content_libraries: typing.Optional[typing.Sequence[builtins.str]] = None,
        vm_classes: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param name: The name of the namespace. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#name Supervisor#name}
        :param content_libraries: A list of content libraries. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#content_libraries Supervisor#content_libraries}
        :param vm_classes: A list of virtual machine classes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#vm_classes Supervisor#vm_classes}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__acc756e56826a895470e495930b4376948206a86595a15496fae8e1e87fa93a4)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument content_libraries", value=content_libraries, expected_type=type_hints["content_libraries"])
            check_type(argname="argument vm_classes", value=vm_classes, expected_type=type_hints["vm_classes"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
        }
        if content_libraries is not None:
            self._values["content_libraries"] = content_libraries
        if vm_classes is not None:
            self._values["vm_classes"] = vm_classes

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the namespace.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#name Supervisor#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def content_libraries(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of content libraries.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#content_libraries Supervisor#content_libraries}
        '''
        result = self._values.get("content_libraries")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def vm_classes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of virtual machine classes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#vm_classes Supervisor#vm_classes}
        '''
        result = self._values.get("vm_classes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SupervisorNamespace(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SupervisorNamespaceList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.supervisor.SupervisorNamespaceList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5875a03f62e70017bbbc1e2a83d80700dc9e33a2faf0717ca99ee3bc92638575)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "SupervisorNamespaceOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aeb5c68f1f04c9d9ebb5309927fc50e701e855d4b665fc6080992a0fbfe2b7df)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("SupervisorNamespaceOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fdc9e70a6b575b1b8314dd9fbb435310b614d857651cab9b9f4f9973ef21b708)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7748a1a2d500532b1c406667c83b93e74689a8d031387a9e080428b747f9b48f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c254ea69f28d4e560d9190584e9d66c63deb2c7df34808efcb3dcda08e9e4451)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[SupervisorNamespace]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[SupervisorNamespace]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[SupervisorNamespace]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__373f7612c241000ea5bbdf8b760a3ded3a56eb7309e43b9fed8a59958ca1633c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class SupervisorNamespaceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.supervisor.SupervisorNamespaceOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__11473446bc54a7045de007d865215eaf53b5df8b1c59ccfc6a3825517041a253)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetContentLibraries")
    def reset_content_libraries(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContentLibraries", []))

    @jsii.member(jsii_name="resetVmClasses")
    def reset_vm_classes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVmClasses", []))

    @builtins.property
    @jsii.member(jsii_name="contentLibrariesInput")
    def content_libraries_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "contentLibrariesInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="vmClassesInput")
    def vm_classes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "vmClassesInput"))

    @builtins.property
    @jsii.member(jsii_name="contentLibraries")
    def content_libraries(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "contentLibraries"))

    @content_libraries.setter
    def content_libraries(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a8df5f16a6d9877f2dcd2dfdfecf8140e49996b2dd6fc454274cc37867ba43c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "contentLibraries", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da6eec2fc81a24bd17b5899a397ecfd8a81cfd987de3103d746e008ea5de2356)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vmClasses")
    def vm_classes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "vmClasses"))

    @vm_classes.setter
    def vm_classes(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3cdf13a1719089addf33e54cbee10e6111012b4eb352520795a1bbbd4bcbacd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vmClasses", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, SupervisorNamespace]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, SupervisorNamespace]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, SupervisorNamespace]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6cbbf56e93c550a38d2982b46e5744f2109bbcb83c104282fa52ccefe7e71df)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.supervisor.SupervisorPodCidr",
    jsii_struct_bases=[],
    name_mapping={"address": "address", "prefix": "prefix"},
)
class SupervisorPodCidr:
    def __init__(self, *, address: builtins.str, prefix: jsii.Number) -> None:
        '''
        :param address: Network address. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#address Supervisor#address}
        :param prefix: Subnet prefix. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#prefix Supervisor#prefix}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c0fbae916ba04dbbc60fd3537061a3af24d26665e3d869a8cd7d7a758fd740a)
            check_type(argname="argument address", value=address, expected_type=type_hints["address"])
            check_type(argname="argument prefix", value=prefix, expected_type=type_hints["prefix"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "address": address,
            "prefix": prefix,
        }

    @builtins.property
    def address(self) -> builtins.str:
        '''Network address.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#address Supervisor#address}
        '''
        result = self._values.get("address")
        assert result is not None, "Required property 'address' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def prefix(self) -> jsii.Number:
        '''Subnet prefix.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#prefix Supervisor#prefix}
        '''
        result = self._values.get("prefix")
        assert result is not None, "Required property 'prefix' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SupervisorPodCidr(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SupervisorPodCidrList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.supervisor.SupervisorPodCidrList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__99274302087831e5983997c0233556aeb360bc98d1a43b76bebf503bf52d6fac)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "SupervisorPodCidrOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f37f76da960dce04fbe503bd5766684e01460f4e3bfc652700fc4e3bf451186)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("SupervisorPodCidrOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__994ab6248c5bcc905d4f7fd9820c466fa7d3d78ada47a6c68c1c59dace0f102b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6cea307942a20f9cf05eb560c143b1d7871cb17ddd2ef59fcd15ac9d334226e1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__514402d093059c3d7d5930f4e0200490dfe7fe21a0e0d0b408d8da552e5a37e9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[SupervisorPodCidr]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[SupervisorPodCidr]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[SupervisorPodCidr]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b967d9998efed683321616e51bf9d51a02ee5adca69432d9d64ed2e6e314867e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class SupervisorPodCidrOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.supervisor.SupervisorPodCidrOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__db066420f9b67064468fe873b0efdbc664eb5057cb6870048205296ff5cdfb4e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="addressInput")
    def address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "addressInput"))

    @builtins.property
    @jsii.member(jsii_name="prefixInput")
    def prefix_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "prefixInput"))

    @builtins.property
    @jsii.member(jsii_name="address")
    def address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "address"))

    @address.setter
    def address(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__448c263c67e4088256ea4b04fda274f6ce6c5227c1312e6b4e85d915dbc37160)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "address", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="prefix")
    def prefix(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "prefix"))

    @prefix.setter
    def prefix(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3688a69b8cee885f10bc16e44828956bb3a361549b61c715519ecc41257b7b86)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "prefix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, SupervisorPodCidr]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, SupervisorPodCidr]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, SupervisorPodCidr]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d15037033b007f20072ce661837c73ba355959ae421e5300e7be236a22d88219)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.supervisor.SupervisorServiceCidr",
    jsii_struct_bases=[],
    name_mapping={"address": "address", "prefix": "prefix"},
)
class SupervisorServiceCidr:
    def __init__(self, *, address: builtins.str, prefix: jsii.Number) -> None:
        '''
        :param address: Network address. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#address Supervisor#address}
        :param prefix: Subnet prefix. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#prefix Supervisor#prefix}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__91910d97ae216d25acda9bed456828ccfcb90e631edbb97462b73cc680f77ebe)
            check_type(argname="argument address", value=address, expected_type=type_hints["address"])
            check_type(argname="argument prefix", value=prefix, expected_type=type_hints["prefix"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "address": address,
            "prefix": prefix,
        }

    @builtins.property
    def address(self) -> builtins.str:
        '''Network address.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#address Supervisor#address}
        '''
        result = self._values.get("address")
        assert result is not None, "Required property 'address' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def prefix(self) -> jsii.Number:
        '''Subnet prefix.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs/resources/supervisor#prefix Supervisor#prefix}
        '''
        result = self._values.get("prefix")
        assert result is not None, "Required property 'prefix' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SupervisorServiceCidr(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SupervisorServiceCidrOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.supervisor.SupervisorServiceCidrOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__38539d34a68ea50c9b7c468fda916e24286d24dd187a57cfedc6c87de57646c3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="addressInput")
    def address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "addressInput"))

    @builtins.property
    @jsii.member(jsii_name="prefixInput")
    def prefix_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "prefixInput"))

    @builtins.property
    @jsii.member(jsii_name="address")
    def address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "address"))

    @address.setter
    def address(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c50f8056e361580c2dcb0bd5d41b5bfdf4fe2082da58414e6aaf4f683e220dfa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "address", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="prefix")
    def prefix(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "prefix"))

    @prefix.setter
    def prefix(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae8c69276f6bb454b6ec0003b96c2a6e45624d8371ebbc8157a453c736048b78)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "prefix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[SupervisorServiceCidr]:
        return typing.cast(typing.Optional[SupervisorServiceCidr], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[SupervisorServiceCidr]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd2062dd3ac854bd1a27829d0336aabee4646a111f4749487b3f3b2ee027febf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "Supervisor",
    "SupervisorConfig",
    "SupervisorEgressCidr",
    "SupervisorEgressCidrList",
    "SupervisorEgressCidrOutputReference",
    "SupervisorIngressCidr",
    "SupervisorIngressCidrList",
    "SupervisorIngressCidrOutputReference",
    "SupervisorManagementNetwork",
    "SupervisorManagementNetworkOutputReference",
    "SupervisorNamespace",
    "SupervisorNamespaceList",
    "SupervisorNamespaceOutputReference",
    "SupervisorPodCidr",
    "SupervisorPodCidrList",
    "SupervisorPodCidrOutputReference",
    "SupervisorServiceCidr",
    "SupervisorServiceCidrOutputReference",
]

publication.publish()

def _typecheckingstub__42bb64ccaeb776b2fa92b408ce34671880e0698548e105f3d47944aec0a74ae4(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    cluster: builtins.str,
    content_library: builtins.str,
    dvs_uuid: builtins.str,
    edge_cluster: builtins.str,
    egress_cidr: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[SupervisorEgressCidr, typing.Dict[builtins.str, typing.Any]]]],
    ingress_cidr: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[SupervisorIngressCidr, typing.Dict[builtins.str, typing.Any]]]],
    main_dns: typing.Sequence[builtins.str],
    main_ntp: typing.Sequence[builtins.str],
    management_network: typing.Union[SupervisorManagementNetwork, typing.Dict[builtins.str, typing.Any]],
    pod_cidr: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[SupervisorPodCidr, typing.Dict[builtins.str, typing.Any]]]],
    search_domains: typing.Sequence[builtins.str],
    service_cidr: typing.Union[SupervisorServiceCidr, typing.Dict[builtins.str, typing.Any]],
    sizing_hint: builtins.str,
    storage_policy: builtins.str,
    worker_dns: typing.Sequence[builtins.str],
    worker_ntp: typing.Sequence[builtins.str],
    id: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[SupervisorNamespace, typing.Dict[builtins.str, typing.Any]]]]] = None,
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

def _typecheckingstub__bc1355035c9294a769a2cbad3bfd3b44cb962ee91bfddcc75524b2c636ed8be3(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a5d6e25b08583cb9e594dafeab8670d83688b2d3ad54d978e0589a772851265(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[SupervisorEgressCidr, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f65aa19124bffbdf1f52fb47e6088cbc850acfbfec41ba58f5c581ddecc9d1e0(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[SupervisorIngressCidr, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__991f70a1db6040a8e541069f201538b32708c29bca3b49f54de76413222a437b(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[SupervisorNamespace, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d044350576e4be9f689486db9326347f0a67d3cf4b2ec59dc00f7d063be7d509(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[SupervisorPodCidr, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9406f3cbcdabf4a9d65a1419fcbc17955d9470cc6cd0a5a6497c0d4d3d15d29c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33e0507f632885072296c4432909eeb06f06b1850e16497b6f27cc1ec06fdda7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d6c92e3006fdaaecc8cdeab31a2ef76b18b4fc200a727d934f0702107570935(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e2db014767be38804f03419e6fe26d7f286f0fcac53fcb74f17957d0ed9ba1f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__673fb5f2badb3efc54456f78e2953ec2cd27000b655d6bc69b75151969168596(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3712e12b1604a0a18434549088319cf449072837d2e1bb51a5915e1f0238997(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7dffc1f3a34ca1bb5b7addb869aa4b8da8ccb9faffab1cfb5394f2a5fc43d22(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4485230cb96b424ab817470e06b7bc0d21b5d968cc6fbda0b3616d3344d0b08a(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1a1c4f44668c63e33edb62d7e262c82eabeee9971bbd5dc47d425c99dcb8a83(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e663d90b3462b304da45e1e9868f76b116535d52d78853a1b1e6b1e59b2b4c53(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f1d5982479664eff14d70be3c656b703b3e3d490738988277c3ebe12dcff440(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__047d66d5c19389e45d44a9061ac0d88c0c91c08f62c0a2682c2a7a43ec8561c7(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ee90cb4864bc34c360e0a774589f0db851b00317783a30cade14411164eb18e(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    cluster: builtins.str,
    content_library: builtins.str,
    dvs_uuid: builtins.str,
    edge_cluster: builtins.str,
    egress_cidr: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[SupervisorEgressCidr, typing.Dict[builtins.str, typing.Any]]]],
    ingress_cidr: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[SupervisorIngressCidr, typing.Dict[builtins.str, typing.Any]]]],
    main_dns: typing.Sequence[builtins.str],
    main_ntp: typing.Sequence[builtins.str],
    management_network: typing.Union[SupervisorManagementNetwork, typing.Dict[builtins.str, typing.Any]],
    pod_cidr: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[SupervisorPodCidr, typing.Dict[builtins.str, typing.Any]]]],
    search_domains: typing.Sequence[builtins.str],
    service_cidr: typing.Union[SupervisorServiceCidr, typing.Dict[builtins.str, typing.Any]],
    sizing_hint: builtins.str,
    storage_policy: builtins.str,
    worker_dns: typing.Sequence[builtins.str],
    worker_ntp: typing.Sequence[builtins.str],
    id: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[SupervisorNamespace, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__029ec7c182215e880c0f08f938cb720f8802bdb512a69ae1fc6aabefc8ab373f(
    *,
    address: builtins.str,
    prefix: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__981ea3ec194ff313f904ee7825f30515c6e809c60daa9fefd77c149d19b25d9e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a78e30af6b04bb1feb29c5cb5de7119b2f2e543cc933de078ae7f06ac57b8bec(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a40eb9c97904939ea6be8799ca3ebaa79338ac95e7cb3f5772255285baeff7b6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52a5aa01543337495141d34744760969d14734e13dc3f549aa8b274d22dbb57e(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0df5bb3dedd534999ba83ccca92f3a6822c697dc33c86bb62c91f43b4aa01354(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__350b259c7b39498dbf9dd295ef84f88d92eb56a91a226d5dc71c485e6653fe49(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[SupervisorEgressCidr]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cdee6047fef5fcc2d305df3d6ab044fdf44903111b68c57e43cf82ee5d347499(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d17b9b59d98caf9fb8a8b0576a40713525f325fc770d5f8e90365e6ebf65c9d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d54b70c7f9df80f730daa7e38abcf8feb8374de0616cd99963cec509cee4e9da(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c57f5c221981af3970dfa777b7f00c7a0e709d3c8e69f5ad51a59b2322a3273(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, SupervisorEgressCidr]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c14c4049a7970dd79d6704b789e1e9052b0f4775cf77133de32affc33e294d65(
    *,
    address: builtins.str,
    prefix: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6fd85546f54a754e54d3b5571174bbce3100bd0cdfac70bb1b5ae2f8a34e87a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48fe94302280c337fd664fe5b705d4b1679b36a69d6e8c14854532f69ede35f2(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96807b41c7b3cc71fcea612e4d12c5d7ace89947deb3c7a8151dcae19f06554e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84a2c0c3724a56910cce3c04c07d55700d3b398865f3e1147b003559c3d0cca3(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a59e2f4c58b0107aa51bf414855e2a97c39ca4687ad63c036f3f730dc723658(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a02cbe9f0ab7f876f152908f13a7491dd6ed5a8d432cbbf28025774a59a26afc(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[SupervisorIngressCidr]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__290f8aa88379dff893b73190c71b49f3aa62932a6ca816dcf0585a9ac4409d52(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee5caa392a115886cd73f6c0a8bc01e7b7deea0feb7fd0b3d7832074cc6dec9f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10aa83d649c14fef15dc8e09199acbb66612483d9c8ba4200628cf827507067f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e21e1b4a8a74967f9d32b75c677a4cc79b2ade6d13620b175914b78d004ce15d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, SupervisorIngressCidr]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__280e1dff9a942c8000be626bcdd909042295d90a4d84efa6418b7b3bd86cc363(
    *,
    address_count: jsii.Number,
    gateway: builtins.str,
    network: builtins.str,
    starting_address: builtins.str,
    subnet_mask: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__216081e3c36a39d9c9713c43b9f09a1ea6db7973ad6995aff819592a7bd4c812(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e6e8cce898411d1cc64197877750a1f2b686d91a37378a0c0e4a00104dd1ae0(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a003452b8ba50885bebf370f74986784e001d59d8d22bee02597daa1f2d344af(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e0ca4229e9068cb3598aba8186bb3bf1361b82046d0a071f4c9dc43c5778a44(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d41d10bd4db90877d9fa4693b8150d97509f8e9999f80ce9f625b50683bd74b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9cb3a655bbaabfb9dd66d4c4d6f3d52779089cc4a5f6dad3528e630019393f60(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5f6e566dd098604e4df8cf2538b49a6f63c1f9ca892fd8cbaff27304fc83e75(
    value: typing.Optional[SupervisorManagementNetwork],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__acc756e56826a895470e495930b4376948206a86595a15496fae8e1e87fa93a4(
    *,
    name: builtins.str,
    content_libraries: typing.Optional[typing.Sequence[builtins.str]] = None,
    vm_classes: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5875a03f62e70017bbbc1e2a83d80700dc9e33a2faf0717ca99ee3bc92638575(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aeb5c68f1f04c9d9ebb5309927fc50e701e855d4b665fc6080992a0fbfe2b7df(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fdc9e70a6b575b1b8314dd9fbb435310b614d857651cab9b9f4f9973ef21b708(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7748a1a2d500532b1c406667c83b93e74689a8d031387a9e080428b747f9b48f(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c254ea69f28d4e560d9190584e9d66c63deb2c7df34808efcb3dcda08e9e4451(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__373f7612c241000ea5bbdf8b760a3ded3a56eb7309e43b9fed8a59958ca1633c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[SupervisorNamespace]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__11473446bc54a7045de007d865215eaf53b5df8b1c59ccfc6a3825517041a253(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a8df5f16a6d9877f2dcd2dfdfecf8140e49996b2dd6fc454274cc37867ba43c(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da6eec2fc81a24bd17b5899a397ecfd8a81cfd987de3103d746e008ea5de2356(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3cdf13a1719089addf33e54cbee10e6111012b4eb352520795a1bbbd4bcbacd(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6cbbf56e93c550a38d2982b46e5744f2109bbcb83c104282fa52ccefe7e71df(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, SupervisorNamespace]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c0fbae916ba04dbbc60fd3537061a3af24d26665e3d869a8cd7d7a758fd740a(
    *,
    address: builtins.str,
    prefix: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99274302087831e5983997c0233556aeb360bc98d1a43b76bebf503bf52d6fac(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f37f76da960dce04fbe503bd5766684e01460f4e3bfc652700fc4e3bf451186(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__994ab6248c5bcc905d4f7fd9820c466fa7d3d78ada47a6c68c1c59dace0f102b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6cea307942a20f9cf05eb560c143b1d7871cb17ddd2ef59fcd15ac9d334226e1(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__514402d093059c3d7d5930f4e0200490dfe7fe21a0e0d0b408d8da552e5a37e9(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b967d9998efed683321616e51bf9d51a02ee5adca69432d9d64ed2e6e314867e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[SupervisorPodCidr]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db066420f9b67064468fe873b0efdbc664eb5057cb6870048205296ff5cdfb4e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__448c263c67e4088256ea4b04fda274f6ce6c5227c1312e6b4e85d915dbc37160(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3688a69b8cee885f10bc16e44828956bb3a361549b61c715519ecc41257b7b86(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d15037033b007f20072ce661837c73ba355959ae421e5300e7be236a22d88219(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, SupervisorPodCidr]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91910d97ae216d25acda9bed456828ccfcb90e631edbb97462b73cc680f77ebe(
    *,
    address: builtins.str,
    prefix: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38539d34a68ea50c9b7c468fda916e24286d24dd187a57cfedc6c87de57646c3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c50f8056e361580c2dcb0bd5d41b5bfdf4fe2082da58414e6aaf4f683e220dfa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae8c69276f6bb454b6ec0003b96c2a6e45624d8371ebbc8157a453c736048b78(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd2062dd3ac854bd1a27829d0336aabee4646a111f4749487b3f3b2ee027febf(
    value: typing.Optional[SupervisorServiceCidr],
) -> None:
    """Type checking stubs"""
    pass
