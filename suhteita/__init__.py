# [[[fill git_describe()]]]
__version__ = '2022.8.9+parent.e993ed8d'
# [[[end]]] (checksum: cafdbfe5183e9c0eb29058360b7259c0)
__version_info__ = tuple(
    e if '-' not in e else e.split('-')[0] for part in __version__.split('+') for e in part.split('.') if e != 'parent'
)
