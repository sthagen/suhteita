# [[[fill git_describe()]]]
__version__ = '2022.8.17+parent.92bb348d'
# [[[end]]] (checksum: 92eca776109e9a4db4c6cefb635891bc)
__version_info__ = tuple(
    e if '-' not in e else e.split('-')[0] for part in __version__.split('+') for e in part.split('.') if e != 'parent'
)
