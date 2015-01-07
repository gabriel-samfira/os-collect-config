import os


sysdrive = os.environ.get("SYSTEMDRIVE", "C:")
tripleo_root = os.path.join(sysdrive, "\\", "tripleo")
CACHEDIR = os.path.join(tripleo_root, "os-collect-config")
BACKUP_CACHEDIR = CACHEDIR

CFN_PATH = os.path.join(sysdrive, "\\" ,"cfn")
CFN_METADATA_SERVER = os.path.join(CFN_PATH, "cfn-metadata-server")
HEAT_METADATA_PATH = [os.path.join(CFN_PATH, "cfn-init-data"), ]
LOCAL_DEFAULT_PATHS = [os.path.join(CACHEDIR, 'local-data'), ]