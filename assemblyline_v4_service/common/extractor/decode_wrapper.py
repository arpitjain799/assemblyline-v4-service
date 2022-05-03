from __future__ import annotations

from collections import defaultdict
from typing import Any, Optional

from multidecoder.multidecoder import Multidecoder
from multidecoder.query import invert_tree


STATIC_TAG_MAP = {
    'network.domain': 'network.static.domain',
    'network.ip': 'network.static.ip',
    'network.url': 'network.static.uri'
}

DYNAMIC_TAG_MAP = {
    'network.domain': 'network.dynamic.domain',
    'network.ip': 'network.dynamic.ip',
    'network.url': 'network.dynamic.uri',
}

TAG_MAP = {
    'network.email': 'network.email.address',
    'powershell.cmdlet': 'file.powershell.cmdlet',
}

BLACKLIST = {
    'archive',
    'av.name',
    'cryptography',
    'debugger.device.name',
    'enable_content',
    'environment.windows',
    'event',
    'guid',
    'network.protocol',
    'network.string',
    'oid',
    'privilege',
    'ransomware.string',
    'sandbox.id',
    'security_identifier',
    'vba.name',
    'windows.registry'
}


def map_tag_type(tag_type: str, dynamic=False) -> Optional[str]:
    if tag_type in TAG_MAP:
        return TAG_MAP[tag_type]
    if tag_type in STATIC_TAG_MAP:
        return DYNAMIC_TAG_MAP[tag_type] if dynamic else STATIC_TAG_MAP[tag_type]
    if tag_type in BLACKLIST:
        return 'file.string.blacklisted'
    if tag_type.startswith('api'):
        return 'file.string.api'
    if tag_type.startswith('filename'):
        return 'file.name.extracted'
    return None


def get_tree_tags(tree: list[dict[str, Any]], dynamic=False) -> dict[str, set[bytes]]:
    tags: dict[str, set[bytes]] = defaultdict(set)
    nodes = invert_tree(tree)
    for node in nodes:
        tag_type = map_tag_type(node.type, dynamic)
        if tag_type:
            tags[tag_type].add(node.value)
    return tags


class DecoderWrapper():
    def __init__(self) -> None:
        self.multidecoder = Multidecoder()

    def ioc_tags(self, data: bytes, dynamic=False) -> dict[str, set[bytes]]:
        tree = self.multidecoder.scan(data)
        return get_tree_tags(tree, dynamic)
