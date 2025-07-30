__version__ = version = '1.0.0'
__version_tuple__ = version_tuple = (1, 0, 0)

fullversion = version
if len(version_tuple) == 2:
    versionname = version
else:
    versionname = 'UNKNOWN'

if len(version_tuple) == 4:
    gitrevision = revision = version_tuple[-1].split('.')[0][1:]
    localdiffs = len(version_tuple[-1].split(".")) == 2
else:
    gitrevision = revision = 'UNKNOWN'
    localdiffs = False

upstream_branch = 'UNKNOWN VCS'
upstream_url = 'UNKNOWN VCS'
