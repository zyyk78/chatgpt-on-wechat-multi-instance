# encoding:utf-8
"""
Channel utility functions for parsing channel names and getting instance configurations.
"""

from typing import Tuple, Dict, Any


def parse_channel_name(channel_name: str) -> Tuple[str, str]:
    """
    Parse channel name into (channel_type, instance_name).

    Examples:
        "weixin" -> ("weixin", "")
        "weixin:instance1" -> ("weixin", "instance1")
        "feishu:bot1" -> ("feishu", "bot1")
    """
    if ':' in channel_name:
        parts = channel_name.split(':', 1)
        return parts[0], parts[1]
    return channel_name, ""


def get_channel_instance_config(channel_type: str, instance_name: str, local_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get configuration for a specific channel instance.

    Priority:
    1. channel_instances list (for multi-instance configs)
    2. Top-level config keys (for backward compatibility)

    Args:
        channel_type: Channel type (e.g., "weixin", "feishu")
        instance_name: Instance name (e.g., "instance1", "" for default)
        local_config: The full configuration dict

    Returns:
        Configuration dict for this specific instance
    """
    # If no instance name, return default config (backward compatible)
    if not instance_name:
        return local_config

    # Look for instance config in channel_instances list
    channel_instances = local_config.get("channel_instances", [])
    if isinstance(channel_instances, list):
        for inst in channel_instances:
            if isinstance(inst, dict):
                inst_name = inst.get("name", "")
                inst_type = inst.get("type", "")
                # Match by name (e.g., "weixin:instance1") or by type+instance_name
                if inst_name == f"{channel_type}:{instance_name}":
                    # Merge: default config + instance-specific overrides
                    result = dict(local_config)
                    result.update(inst)
                    return result
                # Also check if it's stored as "type:instance" format
                if inst_type == channel_type and inst.get("instance_name") == instance_name:
                    result = dict(local_config)
                    result.update(inst)
                    return result

    # Fallback to default config
    return local_config