# [[[fill git_describe()]]]
__version__ = '2022.8.23+parent.12740600'
# [[[end]]] (checksum: f66e31adcd4cddb5196c2a2cac91e425)
__version_info__ = tuple(
    e if '-' not in e else e.split('-')[0] for part in __version__.split('+') for e in part.split('.') if e != 'parent'
)
