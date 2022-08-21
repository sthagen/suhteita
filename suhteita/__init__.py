# [[[fill git_describe()]]]
__version__ = '2022.8.21+parent.dc77e154'
# [[[end]]] (checksum: 3fc9a6f9a48c72a68249c46666d48295)
__version_info__ = tuple(
    e if '-' not in e else e.split('-')[0] for part in __version__.split('+') for e in part.split('.') if e != 'parent'
)
