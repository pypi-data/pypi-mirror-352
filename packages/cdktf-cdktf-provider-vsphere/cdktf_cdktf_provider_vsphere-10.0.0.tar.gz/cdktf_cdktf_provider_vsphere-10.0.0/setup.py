import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdktf-cdktf-provider-vsphere",
    "version": "10.0.0",
    "description": "Prebuilt vsphere Provider for Terraform CDK (cdktf)",
    "license": "MPL-2.0",
    "url": "https://github.com/cdktf/cdktf-provider-vsphere.git",
    "long_description_content_type": "text/markdown",
    "author": "HashiCorp",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/cdktf/cdktf-provider-vsphere.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdktf_cdktf_provider_vsphere",
        "cdktf_cdktf_provider_vsphere._jsii",
        "cdktf_cdktf_provider_vsphere.compute_cluster",
        "cdktf_cdktf_provider_vsphere.compute_cluster_host_group",
        "cdktf_cdktf_provider_vsphere.compute_cluster_vm_affinity_rule",
        "cdktf_cdktf_provider_vsphere.compute_cluster_vm_anti_affinity_rule",
        "cdktf_cdktf_provider_vsphere.compute_cluster_vm_dependency_rule",
        "cdktf_cdktf_provider_vsphere.compute_cluster_vm_group",
        "cdktf_cdktf_provider_vsphere.compute_cluster_vm_host_rule",
        "cdktf_cdktf_provider_vsphere.content_library",
        "cdktf_cdktf_provider_vsphere.content_library_item",
        "cdktf_cdktf_provider_vsphere.custom_attribute",
        "cdktf_cdktf_provider_vsphere.data_vsphere_compute_cluster",
        "cdktf_cdktf_provider_vsphere.data_vsphere_compute_cluster_host_group",
        "cdktf_cdktf_provider_vsphere.data_vsphere_content_library",
        "cdktf_cdktf_provider_vsphere.data_vsphere_content_library_item",
        "cdktf_cdktf_provider_vsphere.data_vsphere_custom_attribute",
        "cdktf_cdktf_provider_vsphere.data_vsphere_datacenter",
        "cdktf_cdktf_provider_vsphere.data_vsphere_datastore",
        "cdktf_cdktf_provider_vsphere.data_vsphere_datastore_cluster",
        "cdktf_cdktf_provider_vsphere.data_vsphere_datastore_stats",
        "cdktf_cdktf_provider_vsphere.data_vsphere_distributed_virtual_switch",
        "cdktf_cdktf_provider_vsphere.data_vsphere_dynamic",
        "cdktf_cdktf_provider_vsphere.data_vsphere_folder",
        "cdktf_cdktf_provider_vsphere.data_vsphere_guest_os_customization",
        "cdktf_cdktf_provider_vsphere.data_vsphere_host",
        "cdktf_cdktf_provider_vsphere.data_vsphere_host_base_images",
        "cdktf_cdktf_provider_vsphere.data_vsphere_host_pci_device",
        "cdktf_cdktf_provider_vsphere.data_vsphere_host_thumbprint",
        "cdktf_cdktf_provider_vsphere.data_vsphere_host_vgpu_profile",
        "cdktf_cdktf_provider_vsphere.data_vsphere_license",
        "cdktf_cdktf_provider_vsphere.data_vsphere_network",
        "cdktf_cdktf_provider_vsphere.data_vsphere_ovf_vm_template",
        "cdktf_cdktf_provider_vsphere.data_vsphere_resource_pool",
        "cdktf_cdktf_provider_vsphere.data_vsphere_role",
        "cdktf_cdktf_provider_vsphere.data_vsphere_storage_policy",
        "cdktf_cdktf_provider_vsphere.data_vsphere_tag",
        "cdktf_cdktf_provider_vsphere.data_vsphere_tag_category",
        "cdktf_cdktf_provider_vsphere.data_vsphere_vapp_container",
        "cdktf_cdktf_provider_vsphere.data_vsphere_virtual_machine",
        "cdktf_cdktf_provider_vsphere.data_vsphere_vmfs_disks",
        "cdktf_cdktf_provider_vsphere.datacenter",
        "cdktf_cdktf_provider_vsphere.datastore_cluster",
        "cdktf_cdktf_provider_vsphere.datastore_cluster_vm_anti_affinity_rule",
        "cdktf_cdktf_provider_vsphere.distributed_port_group",
        "cdktf_cdktf_provider_vsphere.distributed_virtual_switch",
        "cdktf_cdktf_provider_vsphere.distributed_virtual_switch_pvlan_mapping",
        "cdktf_cdktf_provider_vsphere.dpm_host_override",
        "cdktf_cdktf_provider_vsphere.drs_vm_override",
        "cdktf_cdktf_provider_vsphere.entity_permissions",
        "cdktf_cdktf_provider_vsphere.file",
        "cdktf_cdktf_provider_vsphere.folder",
        "cdktf_cdktf_provider_vsphere.guest_os_customization",
        "cdktf_cdktf_provider_vsphere.ha_vm_override",
        "cdktf_cdktf_provider_vsphere.host",
        "cdktf_cdktf_provider_vsphere.host_port_group",
        "cdktf_cdktf_provider_vsphere.host_virtual_switch",
        "cdktf_cdktf_provider_vsphere.license_resource",
        "cdktf_cdktf_provider_vsphere.nas_datastore",
        "cdktf_cdktf_provider_vsphere.offline_software_depot",
        "cdktf_cdktf_provider_vsphere.provider",
        "cdktf_cdktf_provider_vsphere.resource_pool",
        "cdktf_cdktf_provider_vsphere.role",
        "cdktf_cdktf_provider_vsphere.storage_drs_vm_override",
        "cdktf_cdktf_provider_vsphere.supervisor",
        "cdktf_cdktf_provider_vsphere.tag",
        "cdktf_cdktf_provider_vsphere.tag_category",
        "cdktf_cdktf_provider_vsphere.vapp_container",
        "cdktf_cdktf_provider_vsphere.vapp_entity",
        "cdktf_cdktf_provider_vsphere.virtual_disk",
        "cdktf_cdktf_provider_vsphere.virtual_machine",
        "cdktf_cdktf_provider_vsphere.virtual_machine_class",
        "cdktf_cdktf_provider_vsphere.virtual_machine_snapshot",
        "cdktf_cdktf_provider_vsphere.vm_storage_policy",
        "cdktf_cdktf_provider_vsphere.vmfs_datastore",
        "cdktf_cdktf_provider_vsphere.vnic"
    ],
    "package_data": {
        "cdktf_cdktf_provider_vsphere._jsii": [
            "provider-vsphere@10.0.0.jsii.tgz"
        ],
        "cdktf_cdktf_provider_vsphere": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "cdktf>=0.20.0, <0.21.0",
        "constructs>=10.3.0, <11.0.0",
        "jsii>=1.111.0, <2.0.0",
        "publication>=0.0.3",
        "typeguard>=2.13.3,<4.3.0"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Typing :: Typed",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
