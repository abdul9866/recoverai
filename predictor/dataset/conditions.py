from itertools import product
from common.schema import Filesystem, Medium

FILESYSTEMS = [Filesystem.FAT32, Filesystem.EXT4, Filesystem.NTFS, Filesystem.F2FS]
MEDIA = [Medium.HDD, Medium.SSD_TRIM_ON, Medium.SSD_TRIM_OFF]
DELAYS_SECONDS = [0, 600, 3600, 86400, 604800]     # 0, 10min, 1hr, 24hr, 1week
DISK_USAGE_LEVELS = [0.2, 0.5, 0.8]                 # 20%, 50%, 80% full

def all_conditions():
    """Yields every (fs, medium, delay, usage) combination to run."""
    for fs, medium, delay, usage in product(FILESYSTEMS, MEDIA, DELAYS_SECONDS, DISK_USAGE_LEVELS):
        yield {"filesystem": fs, "medium": medium, "delay_s": delay, "usage": usage}

if __name__ == "__main__":
    combos = list(all_conditions())
    print(f"{len(combos)} total condition combinations")
