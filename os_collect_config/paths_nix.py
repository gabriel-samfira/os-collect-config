import os

CACHEDIR = "/var/lib/os-collect-config"
BACKUP_CACHEDIR = "/var/run/os-collect-config"

CFN_PATH = "/var/lib/heat-cfntools"
CFN_METADATA_SERVER = os.path.join(CFN_PATH, "cfn-metadata-server")
HEAT_METADATA_PATH = [os.path.join(CFN_PATH, 'cfn-init-data'),]
LOCAL_DEFAULT_PATHS = [os.path.join(CACHEDIR, 'local-data'), ]