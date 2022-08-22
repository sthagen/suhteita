# [[[fill git_describe()]]]
__version__ = '2022.8.22+parent.cf7eead9'
# [[[end]]] (checksum: 9945df48b52994eed750cc280f65a8cd)
__version_info__ = tuple(
    e if '-' not in e else e.split('-')[0] for part in __version__.split('+') for e in part.split('.') if e != 'parent'
)
