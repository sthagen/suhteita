# [[[fill git_describe()]]]
__version__ = '2022.8.24+parent.48ceea5e'
# [[[end]]] (checksum: af6ef5820c89892f0cfbfa74f48a9dd8)
__version_info__ = tuple(
    e if '-' not in e else e.split('-')[0] for part in __version__.split('+') for e in part.split('.') if e != 'parent'
)
