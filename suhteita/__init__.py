# [[[fill git_describe()]]]
__version__ = '2022.8.11+parent.8eb94737'
# [[[end]]] (checksum: bc998807c35e04a373e1726365ac0689)
__version_info__ = tuple(
    e if '-' not in e else e.split('-')[0] for part in __version__.split('+') for e in part.split('.') if e != 'parent'
)
