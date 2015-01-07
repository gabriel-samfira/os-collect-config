import platform

if platform.system() == "Windows":
	from paths_windows import *
else:
	from paths_nix import *

