# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import argparse
import json
from azureml.registry._rest_client.registry_management_client import RegistryManagementClient
from azureml.registry._rest_client.arm_client import ArmClient
from azureml.registry.mgmt.create_manifest import generate_syndication_manifest
from azureml.registry.mgmt.syndication_manifest import SyndicationManifest


def syndication_manifest_show(registry_name: str) -> dict:
    """Show the current syndication manifest for the specified registry and region.

    Args:
        registry_name (str): Name of the AzureML registry.

    Returns:
        dict: The manifest data.
    """
    return json.dumps(RegistryManagementClient(registry_name=registry_name).get_manifest())


def syndication_manifest_set(manifest_value: str, folder: str, dry_run: bool) -> None:
    """Set the syndication manifest for the specified registry and region.

    Args:
        manifest_value (str): Manifest value as a string (JSON or similar).
        folder (str): Path to the manifest folder.
        dry_run (bool): If True, do not perform any changes.
    """
    if manifest_value is not None:
        # for inline manifest value allow different casing of keys
        manifest = SyndicationManifest.from_dto(json.loads(manifest_value), normalize_keys=True)
    else:
        # Folder structure should have proper casing
        manifest = generate_syndication_manifest(folder)
    dto = manifest.to_dto()
    if dry_run:
        print(f"Dry run: Would set manifest to {dto}")
    else:
        client = RegistryManagementClient(registry_name=manifest.registry_name)
        client.create_or_update_manifest(dto)


def syndication_manifest_delete(registry_name: str, dry_run: bool) -> None:
    """Delete the syndication manifest for the specified registry.

    Args:
        registry_name (str): Name of the AzureML registry.
        dry_run (bool): If True, do not perform any changes.
    """
    if dry_run:
        print(f"Dry run: Would delete manifest for registry {registry_name}")
    else:
        RegistryManagementClient(registry_name=registry_name).delete_manifest()


def syndication_target_show(registry_name: str) -> object:
    """Show the current syndication target(s) for the specified registry and region.

    Args:
        registry_name (str): Name of the AzureML registry.

    Returns:
        list or str: List of syndicated registries or 'None'.
    """
    discovery = RegistryManagementClient(registry_name=registry_name).discovery()
    arm_resource_id = f"/subscriptions/{discovery.get('subscriptionId')}/resourceGroups/{discovery.get('resourceGroup')}/providers/Microsoft.MachineLearningServices/registries/{discovery.get('registryName')}"
    return ArmClient().get_resource(resource_id=arm_resource_id).get("properties", {}).get("syndicatedRegistries", "None")


def syndication_target_set(registry_name: str, registry_ids: list, dry_run: bool) -> None:
    """Set the syndication target(s) for the specified registry and region.

    Args:
        registry_name (str): Name of the AzureML registry.
        registry_ids (list): List of registry IDs to set as syndicated targets.
        dry_run (bool): If True, do not perform any changes.
    """
    discovery = RegistryManagementClient(registry_name=registry_name).discovery()
    arm_resource_id = f"/subscriptions/{discovery.get('subscriptionId')}/resourceGroups/{discovery.get('resourceGroup')}/providers/Microsoft.MachineLearningServices/registries/{discovery.get('registryName')}"
    arm_client = ArmClient()
    resource = arm_client.get_resource(resource_id=arm_resource_id)
    resource["properties"]["syndicatedRegistries"] = registry_ids
    if dry_run:
        print(f"Dry run: Would set {registry_ids} as SyndicatedRegistries for {registry_name}")
    else:
        arm_client.put_resource(resource_id=arm_resource_id, put_body=resource)


def show_command(registry_name: str, as_arm_object: bool) -> object:
    """Show registry discovery info or ARM object for the specified registry and region.

    Args:
        registry_name (str): Name of the AzureML registry.
        as_arm_object (bool): If True, show as ARM object.

    Returns:
        dict: Discovery info or ARM resource object.
    """
    discovery = RegistryManagementClient(registry_name=registry_name).discovery()
    if as_arm_object:
        arm_resource_id = f"/subscriptions/{discovery.get('subscriptionId')}/resourceGroups/{discovery.get('resourceGroup')}/providers/Microsoft.MachineLearningServices/registries/{discovery.get('registryName')}"
        return ArmClient().get_resource(resource_id=arm_resource_id)
    return discovery


def _add_common_args(p, arg_dicts=None):
    if arg_dicts is None:
        arg_dicts = []
    for arg in arg_dicts:
        p.add_argument(*arg["args"], **arg["kwargs"])


def main() -> None:
    """Azureml Registry Syndication CLI Extension.

    Examples:
      # Show the current manifest
      registry-mgmt syndication manifest show --registry-name myreg

      # Set manifest from a folder
      registry-mgmt syndication manifest set --path ./manifest_folder

      # Set manifest from a value
      registry-mgmt syndication manifest set --value '{"Manifest": "val"}'

      # Delete the current manifest
      registry-mgmt syndication manifest delete --registry-name myreg

      # Show the current target
      registry-mgmt syndication target show --registry-name myreg

      # Set target values
      registry-mgmt syndication target set --registry-name myreg -v reg1Id -v reg2Id

      # Show registry discovery info
      registry-mgmt show --registry-name myreg

      # Show registry as ARM object
      registry-mgmt show --registry-name myreg --as-arm-object

      # Dry run for any command
      registry-mgmt syndication manifest set --registry-name myreg --path ./manifest_folder --dry-run
    """
    parser = argparse.ArgumentParser(prog="registry-mgmt", description="AzureML Registry Syndication CLI Extension")
    subparsers = parser.add_subparsers(dest="command", required=True)

    registry_name_arg = {
        "args": ("-r", "--registry-name"),
        "kwargs": {
            "type": str,
            "required": True,
            "help": "Name of the AzureML registry."
        }
    }

    dry_run_arg = {
        "args": ("--dry-run",),
        "kwargs": {
            "action": "store_true",
            "help": "Perform a dry run without making changes."
        }
    }

    # syndication root command
    synd_parser = subparsers.add_parser("syndication", help="Syndication operations")
    synd_subparsers = synd_parser.add_subparsers(dest="synd_subcommand", required=True)

    # syndication manifest
    manifest_parser = synd_subparsers.add_parser("manifest", help="Manage syndication manifest.")
    manifest_subparsers = manifest_parser.add_subparsers(dest="manifest_subcommand", required=True)

    manifest_show_parser = manifest_subparsers.add_parser("show", help="Show the current manifest.")
    _add_common_args(manifest_show_parser, [registry_name_arg, dry_run_arg])

    manifest_set_parser = manifest_subparsers.add_parser("set", help="Set manifest values.")
    _add_common_args(manifest_set_parser, [dry_run_arg])
    group = manifest_set_parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-v", "--value", type=str, help="Manifest value.")
    group.add_argument("-p", "--path", type=str, help="Path to manifest root folder.")

    manifest_delete_parser = manifest_subparsers.add_parser("delete", help="Delete the current manifest.")
    _add_common_args(manifest_delete_parser, [registry_name_arg, dry_run_arg])

    # syndication target
    target_parser = synd_subparsers.add_parser("target", help="Manage syndication target.")
    target_subparsers = target_parser.add_subparsers(dest="target_subcommand", required=True)

    target_show_parser = target_subparsers.add_parser("show", help="Show the current target.")
    _add_common_args(target_show_parser, [registry_name_arg, dry_run_arg])

    target_set_parser = target_subparsers.add_parser("set", help="Set target values.")
    _add_common_args(target_set_parser, [registry_name_arg, dry_run_arg])
    target_set_parser.add_argument("-v", "--value", type=str, action="append", required=True, help="Target value (can be specified multiple times).")

    # show root command
    show_parser = subparsers.add_parser("show", help="Show syndication info.")
    _add_common_args(show_parser, [registry_name_arg, dry_run_arg])
    show_parser.add_argument("--as-arm-object", action="store_true", help="Show as ARM object.")

    args = parser.parse_args()

    # Command dispatch
    if args.command == "syndication":
        if args.synd_subcommand == "manifest":
            if args.manifest_subcommand == "show":
                print(syndication_manifest_show(args.registry_name))
            elif args.manifest_subcommand == "set":
                print(syndication_manifest_set(args.value, args.path, args.dry_run))
            elif args.manifest_subcommand == "delete":
                confirm = input(f"Proceed with manifest deletion for {args.registry_name}? [y/N]: ")
                if confirm.lower() == "y":
                    syndication_manifest_delete(args.registry_name, args.dry_run)
                else:
                    print("Manifest deletion cancelled.")
        elif args.synd_subcommand == "target":
            if args.target_subcommand == "show":
                print(syndication_target_show(args.registry_name))
            elif args.target_subcommand == "set":
                syndication_target_set(args.registry_name, args.value, args.dry_run)
    elif args.command == "show":
        print(show_command(args.registry_name, args.as_arm_object))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
