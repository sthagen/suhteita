# [[[fill git_describe()]]]
__version__ = '2022.8.16+parent.a91606ef'
# [[[end]]] (checksum: d22f9437be6378ce9a9679fbe559c468)
__version_info__ = tuple(
    e if '-' not in e else e.split('-')[0] for part in __version__.split('+') for e in part.split('.') if e != 'parent'
)
