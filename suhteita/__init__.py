# [[[fill git_describe()]]]
__version__ = '2022.8.16+parent.165a9467'
# [[[end]]] (checksum: d7316d337a2d6e8a115536e86bd2f793)
__version_info__ = tuple(
    e if '-' not in e else e.split('-')[0] for part in __version__.split('+') for e in part.split('.') if e != 'parent'
)
