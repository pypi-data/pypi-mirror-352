r'''
# `provider`

Refer to the Terraform Registry for docs: [`vsphere`](https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs).
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


class VsphereProvider(
    _cdktf_9a9027ec.TerraformProvider,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vsphere.provider.VsphereProvider",
):
    '''Represents a {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs vsphere}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        password: builtins.str,
        user: builtins.str,
        alias: typing.Optional[builtins.str] = None,
        allow_unverified_ssl: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        api_timeout: typing.Optional[jsii.Number] = None,
        client_debug: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        client_debug_path: typing.Optional[builtins.str] = None,
        client_debug_path_run: typing.Optional[builtins.str] = None,
        persist_session: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        rest_session_path: typing.Optional[builtins.str] = None,
        vcenter_server: typing.Optional[builtins.str] = None,
        vim_keep_alive: typing.Optional[jsii.Number] = None,
        vim_session_path: typing.Optional[builtins.str] = None,
        vsphere_server: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs vsphere} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param password: The user password for vSphere API operations. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs#password VsphereProvider#password}
        :param user: The user name for vSphere API operations. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs#user VsphereProvider#user}
        :param alias: Alias name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs#alias VsphereProvider#alias}
        :param allow_unverified_ssl: If set, VMware vSphere client will permit unverifiable SSL certificates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs#allow_unverified_ssl VsphereProvider#allow_unverified_ssl}
        :param api_timeout: API timeout in minutes (Default: 5). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs#api_timeout VsphereProvider#api_timeout}
        :param client_debug: govmomi debug. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs#client_debug VsphereProvider#client_debug}
        :param client_debug_path: govmomi debug path for debug. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs#client_debug_path VsphereProvider#client_debug_path}
        :param client_debug_path_run: govmomi debug path for a single run. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs#client_debug_path_run VsphereProvider#client_debug_path_run}
        :param persist_session: Persist vSphere client sessions to disk. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs#persist_session VsphereProvider#persist_session}
        :param rest_session_path: The directory to save vSphere REST API sessions to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs#rest_session_path VsphereProvider#rest_session_path}
        :param vcenter_server: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs#vcenter_server VsphereProvider#vcenter_server}.
        :param vim_keep_alive: Keep alive interval for the VIM session in minutes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs#vim_keep_alive VsphereProvider#vim_keep_alive}
        :param vim_session_path: The directory to save vSphere SOAP API sessions to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs#vim_session_path VsphereProvider#vim_session_path}
        :param vsphere_server: The vSphere Server name for vSphere API operations. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs#vsphere_server VsphereProvider#vsphere_server}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee026a52613711b09c00984c1711ee0ea723e1281f3052e2fd4da2b6813e9712)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = VsphereProviderConfig(
            password=password,
            user=user,
            alias=alias,
            allow_unverified_ssl=allow_unverified_ssl,
            api_timeout=api_timeout,
            client_debug=client_debug,
            client_debug_path=client_debug_path,
            client_debug_path_run=client_debug_path_run,
            persist_session=persist_session,
            rest_session_path=rest_session_path,
            vcenter_server=vcenter_server,
            vim_keep_alive=vim_keep_alive,
            vim_session_path=vim_session_path,
            vsphere_server=vsphere_server,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a VsphereProvider resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the VsphereProvider to import.
        :param import_from_id: The id of the existing VsphereProvider that should be imported. Refer to the {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the VsphereProvider to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae647f05d64a24a4cc413cf7d9ba9bbd1b38ab1a75fd4e9bfeeb0f117d2a11cb)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAlias")
    def reset_alias(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlias", []))

    @jsii.member(jsii_name="resetAllowUnverifiedSsl")
    def reset_allow_unverified_ssl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowUnverifiedSsl", []))

    @jsii.member(jsii_name="resetApiTimeout")
    def reset_api_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApiTimeout", []))

    @jsii.member(jsii_name="resetClientDebug")
    def reset_client_debug(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClientDebug", []))

    @jsii.member(jsii_name="resetClientDebugPath")
    def reset_client_debug_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClientDebugPath", []))

    @jsii.member(jsii_name="resetClientDebugPathRun")
    def reset_client_debug_path_run(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClientDebugPathRun", []))

    @jsii.member(jsii_name="resetPersistSession")
    def reset_persist_session(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPersistSession", []))

    @jsii.member(jsii_name="resetRestSessionPath")
    def reset_rest_session_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRestSessionPath", []))

    @jsii.member(jsii_name="resetVcenterServer")
    def reset_vcenter_server(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVcenterServer", []))

    @jsii.member(jsii_name="resetVimKeepAlive")
    def reset_vim_keep_alive(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVimKeepAlive", []))

    @jsii.member(jsii_name="resetVimSessionPath")
    def reset_vim_session_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVimSessionPath", []))

    @jsii.member(jsii_name="resetVsphereServer")
    def reset_vsphere_server(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVsphereServer", []))

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
    @jsii.member(jsii_name="aliasInput")
    def alias_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aliasInput"))

    @builtins.property
    @jsii.member(jsii_name="allowUnverifiedSslInput")
    def allow_unverified_ssl_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "allowUnverifiedSslInput"))

    @builtins.property
    @jsii.member(jsii_name="apiTimeoutInput")
    def api_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "apiTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="clientDebugInput")
    def client_debug_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "clientDebugInput"))

    @builtins.property
    @jsii.member(jsii_name="clientDebugPathInput")
    def client_debug_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientDebugPathInput"))

    @builtins.property
    @jsii.member(jsii_name="clientDebugPathRunInput")
    def client_debug_path_run_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientDebugPathRunInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property
    @jsii.member(jsii_name="persistSessionInput")
    def persist_session_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "persistSessionInput"))

    @builtins.property
    @jsii.member(jsii_name="restSessionPathInput")
    def rest_session_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "restSessionPathInput"))

    @builtins.property
    @jsii.member(jsii_name="userInput")
    def user_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userInput"))

    @builtins.property
    @jsii.member(jsii_name="vcenterServerInput")
    def vcenter_server_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vcenterServerInput"))

    @builtins.property
    @jsii.member(jsii_name="vimKeepAliveInput")
    def vim_keep_alive_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "vimKeepAliveInput"))

    @builtins.property
    @jsii.member(jsii_name="vimSessionPathInput")
    def vim_session_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vimSessionPathInput"))

    @builtins.property
    @jsii.member(jsii_name="vsphereServerInput")
    def vsphere_server_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vsphereServerInput"))

    @builtins.property
    @jsii.member(jsii_name="alias")
    def alias(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "alias"))

    @alias.setter
    def alias(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85a5c7404c22e2662c8f2b36e7bac7c3c330755af050b318ea3270269facd5fc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alias", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowUnverifiedSsl")
    def allow_unverified_ssl(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "allowUnverifiedSsl"))

    @allow_unverified_ssl.setter
    def allow_unverified_ssl(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__efa987cfc550d9bd2c5835330213c9fcee3a796902fa8c4e5c6a567d25c9382b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowUnverifiedSsl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="apiTimeout")
    def api_timeout(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "apiTimeout"))

    @api_timeout.setter
    def api_timeout(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d49d1962d4c843bdc5b6559e73f4b084c4b70d0d6095e9df5cf25abb428444f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "apiTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clientDebug")
    def client_debug(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "clientDebug"))

    @client_debug.setter
    def client_debug(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7cae6e0d733c5b071ac17da413a7c5bc493ce13b5b796b2c5e8af127cb3ac16e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientDebug", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clientDebugPath")
    def client_debug_path(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientDebugPath"))

    @client_debug_path.setter
    def client_debug_path(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d4a4c3885a74541897f23aaf27d7b316a33faafd025e441e73f82230789dc3b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientDebugPath", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clientDebugPathRun")
    def client_debug_path_run(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientDebugPathRun"))

    @client_debug_path_run.setter
    def client_debug_path_run(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__017137ad0dd39052c7f9e0eda5e0706736e5179981fc2763a5440085c8ab25e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientDebugPathRun", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="password")
    def password(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "password"))

    @password.setter
    def password(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8d6ab5398e3ff1d9b079ef3ac803090a563fc1150bf33ba54693aab2798cdbf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "password", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="persistSession")
    def persist_session(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "persistSession"))

    @persist_session.setter
    def persist_session(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24e6a601113c7ec7d0d7ce3b407765402f397b51e33bf7c259d38d98cbb2650d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "persistSession", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="restSessionPath")
    def rest_session_path(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "restSessionPath"))

    @rest_session_path.setter
    def rest_session_path(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b27f34b61805c00af253b6df02b768883d159c15c46bcc8c546d3a561987131a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "restSessionPath", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="user")
    def user(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "user"))

    @user.setter
    def user(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d81d54af5728cb1a20ec1fda0589644e0697c48f1c2b8fc5ab341e53d5e19ca4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "user", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vcenterServer")
    def vcenter_server(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vcenterServer"))

    @vcenter_server.setter
    def vcenter_server(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bbbec703afa84abdf146fa976cc8187d65ff67fd45dc268b875e8372c4b39bf5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vcenterServer", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vimKeepAlive")
    def vim_keep_alive(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "vimKeepAlive"))

    @vim_keep_alive.setter
    def vim_keep_alive(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f66ec4c1c7d4a23480406c75d8cffe7c94f8b5f9980725dbd57f0b1d2843fd9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vimKeepAlive", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vimSessionPath")
    def vim_session_path(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vimSessionPath"))

    @vim_session_path.setter
    def vim_session_path(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fdf3b73ca434e2bb2e75400348a4f079b7c72997eff4f0cd08ca18625dbb6c73)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vimSessionPath", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vsphereServer")
    def vsphere_server(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vsphereServer"))

    @vsphere_server.setter
    def vsphere_server(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1954f991ead072d7913c4b8fe881f938a0ec15394dc06da3984df4d4af2e8ce9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vsphereServer", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vsphere.provider.VsphereProviderConfig",
    jsii_struct_bases=[],
    name_mapping={
        "password": "password",
        "user": "user",
        "alias": "alias",
        "allow_unverified_ssl": "allowUnverifiedSsl",
        "api_timeout": "apiTimeout",
        "client_debug": "clientDebug",
        "client_debug_path": "clientDebugPath",
        "client_debug_path_run": "clientDebugPathRun",
        "persist_session": "persistSession",
        "rest_session_path": "restSessionPath",
        "vcenter_server": "vcenterServer",
        "vim_keep_alive": "vimKeepAlive",
        "vim_session_path": "vimSessionPath",
        "vsphere_server": "vsphereServer",
    },
)
class VsphereProviderConfig:
    def __init__(
        self,
        *,
        password: builtins.str,
        user: builtins.str,
        alias: typing.Optional[builtins.str] = None,
        allow_unverified_ssl: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        api_timeout: typing.Optional[jsii.Number] = None,
        client_debug: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        client_debug_path: typing.Optional[builtins.str] = None,
        client_debug_path_run: typing.Optional[builtins.str] = None,
        persist_session: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        rest_session_path: typing.Optional[builtins.str] = None,
        vcenter_server: typing.Optional[builtins.str] = None,
        vim_keep_alive: typing.Optional[jsii.Number] = None,
        vim_session_path: typing.Optional[builtins.str] = None,
        vsphere_server: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param password: The user password for vSphere API operations. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs#password VsphereProvider#password}
        :param user: The user name for vSphere API operations. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs#user VsphereProvider#user}
        :param alias: Alias name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs#alias VsphereProvider#alias}
        :param allow_unverified_ssl: If set, VMware vSphere client will permit unverifiable SSL certificates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs#allow_unverified_ssl VsphereProvider#allow_unverified_ssl}
        :param api_timeout: API timeout in minutes (Default: 5). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs#api_timeout VsphereProvider#api_timeout}
        :param client_debug: govmomi debug. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs#client_debug VsphereProvider#client_debug}
        :param client_debug_path: govmomi debug path for debug. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs#client_debug_path VsphereProvider#client_debug_path}
        :param client_debug_path_run: govmomi debug path for a single run. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs#client_debug_path_run VsphereProvider#client_debug_path_run}
        :param persist_session: Persist vSphere client sessions to disk. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs#persist_session VsphereProvider#persist_session}
        :param rest_session_path: The directory to save vSphere REST API sessions to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs#rest_session_path VsphereProvider#rest_session_path}
        :param vcenter_server: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs#vcenter_server VsphereProvider#vcenter_server}.
        :param vim_keep_alive: Keep alive interval for the VIM session in minutes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs#vim_keep_alive VsphereProvider#vim_keep_alive}
        :param vim_session_path: The directory to save vSphere SOAP API sessions to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs#vim_session_path VsphereProvider#vim_session_path}
        :param vsphere_server: The vSphere Server name for vSphere API operations. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs#vsphere_server VsphereProvider#vsphere_server}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b3d3ddbf5e3b8ebcad247b5a75b14c872c731a5a99a03a31d3a90a237b8c26b)
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument user", value=user, expected_type=type_hints["user"])
            check_type(argname="argument alias", value=alias, expected_type=type_hints["alias"])
            check_type(argname="argument allow_unverified_ssl", value=allow_unverified_ssl, expected_type=type_hints["allow_unverified_ssl"])
            check_type(argname="argument api_timeout", value=api_timeout, expected_type=type_hints["api_timeout"])
            check_type(argname="argument client_debug", value=client_debug, expected_type=type_hints["client_debug"])
            check_type(argname="argument client_debug_path", value=client_debug_path, expected_type=type_hints["client_debug_path"])
            check_type(argname="argument client_debug_path_run", value=client_debug_path_run, expected_type=type_hints["client_debug_path_run"])
            check_type(argname="argument persist_session", value=persist_session, expected_type=type_hints["persist_session"])
            check_type(argname="argument rest_session_path", value=rest_session_path, expected_type=type_hints["rest_session_path"])
            check_type(argname="argument vcenter_server", value=vcenter_server, expected_type=type_hints["vcenter_server"])
            check_type(argname="argument vim_keep_alive", value=vim_keep_alive, expected_type=type_hints["vim_keep_alive"])
            check_type(argname="argument vim_session_path", value=vim_session_path, expected_type=type_hints["vim_session_path"])
            check_type(argname="argument vsphere_server", value=vsphere_server, expected_type=type_hints["vsphere_server"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "password": password,
            "user": user,
        }
        if alias is not None:
            self._values["alias"] = alias
        if allow_unverified_ssl is not None:
            self._values["allow_unverified_ssl"] = allow_unverified_ssl
        if api_timeout is not None:
            self._values["api_timeout"] = api_timeout
        if client_debug is not None:
            self._values["client_debug"] = client_debug
        if client_debug_path is not None:
            self._values["client_debug_path"] = client_debug_path
        if client_debug_path_run is not None:
            self._values["client_debug_path_run"] = client_debug_path_run
        if persist_session is not None:
            self._values["persist_session"] = persist_session
        if rest_session_path is not None:
            self._values["rest_session_path"] = rest_session_path
        if vcenter_server is not None:
            self._values["vcenter_server"] = vcenter_server
        if vim_keep_alive is not None:
            self._values["vim_keep_alive"] = vim_keep_alive
        if vim_session_path is not None:
            self._values["vim_session_path"] = vim_session_path
        if vsphere_server is not None:
            self._values["vsphere_server"] = vsphere_server

    @builtins.property
    def password(self) -> builtins.str:
        '''The user password for vSphere API operations.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs#password VsphereProvider#password}
        '''
        result = self._values.get("password")
        assert result is not None, "Required property 'password' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def user(self) -> builtins.str:
        '''The user name for vSphere API operations.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs#user VsphereProvider#user}
        '''
        result = self._values.get("user")
        assert result is not None, "Required property 'user' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def alias(self) -> typing.Optional[builtins.str]:
        '''Alias name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs#alias VsphereProvider#alias}
        '''
        result = self._values.get("alias")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def allow_unverified_ssl(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If set, VMware vSphere client will permit unverifiable SSL certificates.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs#allow_unverified_ssl VsphereProvider#allow_unverified_ssl}
        '''
        result = self._values.get("allow_unverified_ssl")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def api_timeout(self) -> typing.Optional[jsii.Number]:
        '''API timeout in minutes (Default: 5).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs#api_timeout VsphereProvider#api_timeout}
        '''
        result = self._values.get("api_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def client_debug(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''govmomi debug.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs#client_debug VsphereProvider#client_debug}
        '''
        result = self._values.get("client_debug")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def client_debug_path(self) -> typing.Optional[builtins.str]:
        '''govmomi debug path for debug.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs#client_debug_path VsphereProvider#client_debug_path}
        '''
        result = self._values.get("client_debug_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def client_debug_path_run(self) -> typing.Optional[builtins.str]:
        '''govmomi debug path for a single run.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs#client_debug_path_run VsphereProvider#client_debug_path_run}
        '''
        result = self._values.get("client_debug_path_run")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def persist_session(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Persist vSphere client sessions to disk.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs#persist_session VsphereProvider#persist_session}
        '''
        result = self._values.get("persist_session")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def rest_session_path(self) -> typing.Optional[builtins.str]:
        '''The directory to save vSphere REST API sessions to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs#rest_session_path VsphereProvider#rest_session_path}
        '''
        result = self._values.get("rest_session_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vcenter_server(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs#vcenter_server VsphereProvider#vcenter_server}.'''
        result = self._values.get("vcenter_server")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vim_keep_alive(self) -> typing.Optional[jsii.Number]:
        '''Keep alive interval for the VIM session in minutes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs#vim_keep_alive VsphereProvider#vim_keep_alive}
        '''
        result = self._values.get("vim_keep_alive")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def vim_session_path(self) -> typing.Optional[builtins.str]:
        '''The directory to save vSphere SOAP API sessions to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs#vim_session_path VsphereProvider#vim_session_path}
        '''
        result = self._values.get("vim_session_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vsphere_server(self) -> typing.Optional[builtins.str]:
        '''The vSphere Server name for vSphere API operations.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/vmware/vsphere/2.13.0/docs#vsphere_server VsphereProvider#vsphere_server}
        '''
        result = self._values.get("vsphere_server")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VsphereProviderConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "VsphereProvider",
    "VsphereProviderConfig",
]

publication.publish()

def _typecheckingstub__ee026a52613711b09c00984c1711ee0ea723e1281f3052e2fd4da2b6813e9712(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    password: builtins.str,
    user: builtins.str,
    alias: typing.Optional[builtins.str] = None,
    allow_unverified_ssl: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    api_timeout: typing.Optional[jsii.Number] = None,
    client_debug: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    client_debug_path: typing.Optional[builtins.str] = None,
    client_debug_path_run: typing.Optional[builtins.str] = None,
    persist_session: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    rest_session_path: typing.Optional[builtins.str] = None,
    vcenter_server: typing.Optional[builtins.str] = None,
    vim_keep_alive: typing.Optional[jsii.Number] = None,
    vim_session_path: typing.Optional[builtins.str] = None,
    vsphere_server: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae647f05d64a24a4cc413cf7d9ba9bbd1b38ab1a75fd4e9bfeeb0f117d2a11cb(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85a5c7404c22e2662c8f2b36e7bac7c3c330755af050b318ea3270269facd5fc(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efa987cfc550d9bd2c5835330213c9fcee3a796902fa8c4e5c6a567d25c9382b(
    value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d49d1962d4c843bdc5b6559e73f4b084c4b70d0d6095e9df5cf25abb428444f(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7cae6e0d733c5b071ac17da413a7c5bc493ce13b5b796b2c5e8af127cb3ac16e(
    value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d4a4c3885a74541897f23aaf27d7b316a33faafd025e441e73f82230789dc3b(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__017137ad0dd39052c7f9e0eda5e0706736e5179981fc2763a5440085c8ab25e8(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8d6ab5398e3ff1d9b079ef3ac803090a563fc1150bf33ba54693aab2798cdbf(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24e6a601113c7ec7d0d7ce3b407765402f397b51e33bf7c259d38d98cbb2650d(
    value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b27f34b61805c00af253b6df02b768883d159c15c46bcc8c546d3a561987131a(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d81d54af5728cb1a20ec1fda0589644e0697c48f1c2b8fc5ab341e53d5e19ca4(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bbbec703afa84abdf146fa976cc8187d65ff67fd45dc268b875e8372c4b39bf5(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f66ec4c1c7d4a23480406c75d8cffe7c94f8b5f9980725dbd57f0b1d2843fd9(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fdf3b73ca434e2bb2e75400348a4f079b7c72997eff4f0cd08ca18625dbb6c73(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1954f991ead072d7913c4b8fe881f938a0ec15394dc06da3984df4d4af2e8ce9(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b3d3ddbf5e3b8ebcad247b5a75b14c872c731a5a99a03a31d3a90a237b8c26b(
    *,
    password: builtins.str,
    user: builtins.str,
    alias: typing.Optional[builtins.str] = None,
    allow_unverified_ssl: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    api_timeout: typing.Optional[jsii.Number] = None,
    client_debug: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    client_debug_path: typing.Optional[builtins.str] = None,
    client_debug_path_run: typing.Optional[builtins.str] = None,
    persist_session: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    rest_session_path: typing.Optional[builtins.str] = None,
    vcenter_server: typing.Optional[builtins.str] = None,
    vim_keep_alive: typing.Optional[jsii.Number] = None,
    vim_session_path: typing.Optional[builtins.str] = None,
    vsphere_server: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
