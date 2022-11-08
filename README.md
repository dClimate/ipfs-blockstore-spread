ipfs-blockstore-spread
======================

*WARNING* this has not been used in production and requires a custom IPFS binary to get working at all. It should only be used as a starting point for spreading the IPFS blockstore or for generally spreading data in a non-IPFS context.

IPFS is currently limited to storing block data on a single volume in the `~.ipfs` directory. This script can be used to hack support for multiple disks of storage into IPFS. 

It spreads a directory of directories across multiple destination directories and connects symlinks to the new destinations in a third directory. It is intended to be used to spread `~/.ipfs/blocks` across multiple external volumes to get around IPFS's requirement of the blocks being in a single folder.

All directories specified as arguments must exist already.

IPFS binary
-----------

This script requires a custom IPFS binary that includes support for symlinks. The binary can be compiled using a forked version of `go-ds-flatfs` from <https://github.com/dClimate/go-ds-flatfs>.

Example
-------

    $ python3 spread-blockstore.py /tmp/original_blockstore/ /tmp/new_blockstore/ /tmp/vol1/ /tmp/vol2/ /tmp/vol3/

This will take the folders in `/tmp/original_blockstore` and distribute them evenly into `/tmp/vol1`, `/tmp/vol2`, and `/tmp/vol3`as copies. Then, `/tmp/new_blockstore` will contain a symlink to each of those new directories. A real world example might look like,

    $ python3 spread-blockstore.py ~/.ipfs/blocks /mnt/vol1/.ipfs/blocks /mnt/vol1/blocks /mnt/vol2/blocks /mnt/vol3/blocks

In this example, `/mnt/vol1/.ipfs` would be the new IPFS directory, containing everything normally contained within `~/.ipfs/`, and after making sure everything has been copied, `~/.ipfs` would be symlinked to `/mnt/vol1/.ipfs`.
