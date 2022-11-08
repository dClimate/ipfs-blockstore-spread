# This script spreads the directories in a given source across multiple given destination directories and symlinks to the new
# destinations in a given third directory. It is intended to be used to spread the ~/.ipfs/blocks directory across multiple
# external volumes to get around IPFS's requirement of the blocks being in a single folder. All directories specified as
# arguments must exist already.
#
# For example,
#
#     $ python3 spread-blockstore.py /tmp/original_blockstore/ /tmp/new_blockstore/ /tmp/vol1/ /tmp/vol2/ /tmp/vol3/
#
# This will take the folders in /tmp/original_blockstore and distribute them evenly into /tmp/vol1, /tmp/vol2, and /tmp/vol3
# as copies. Then /tmp/new_blockstore will contain a symlink to each of those new directories. A real world example might
# look like,
#
#     $ python3 spread-blockstore.py ~/.ipfs/blocks /mnt/vol1/.ipfs/blocks /mnt/vol1/blocks /mnt/vol2/blocks /mnt/vol3/blocks
#
# In this example, /mnt/vol1/.ipfs would be the new IPFS directory, containing everything normally contained within ~/.ipfs/,
# and after making sure everything has been copied, ~/.ipfs would be symlinked to /mnt/vol1/.ipfs.

import concurrent.futures, shutil, pathlib, argparse, os, multiprocessing, time

def copy_single_arg(tup):
    shutil.copytree(*tup)
    return f"copied {tup[0]} to {tup[1]}"

if __name__ == "__main__":

    # Set up and parse CLI
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=pathlib.Path, help="current blockstore which needs to be dispersed")
    parser.add_argument("store", type=pathlib.Path, help="new blockstore which will contain symlinks to the destination directories")
    parser.add_argument("destinations", nargs="+", type=pathlib.Path, help="one or more directories where the source block directories will be dispersed")
    parser.add_argument("--cores", type=int, default=max(1, multiprocessing.cpu_count() - 1), help="how hard do you wanna go")
    arguments = parser.parse_args()

    # Make sure all arguments are existing directories
    if arguments.source.is_dir() and all(d.is_dir() for d in arguments.destinations) and arguments.store.is_dir():
        directory_index = 0

        # Build a dict that maps an existing directory to its new location in one of the destinations
        mapping = {}
        for entry in sorted(arguments.source.iterdir()):
            if entry.is_dir():
                destination = arguments.destinations[directory_index].joinpath(entry.name)
                mapping[entry] = destination

                # Create a link in the new store that links to the new destination
                if not arguments.store.joinpath(entry.name).exists():
                    os.symlink(destination, arguments.store.joinpath(entry.name), target_is_directory=True)
                directory_index = (directory_index + 1) % len(arguments.destinations)

        # Copy files in parallel, one folder from the original source at a time
        with concurrent.futures.ProcessPoolExecutor(max_workers=arguments.cores) as executor:
            list_of_args = []
            for source_blockdir, destination in mapping.items():
                list_of_args.append((source_blockdir, destination))
                print(f"added {source_blockdir} -> {destination} to future")
            for res in executor.map(copy_single_arg, list_of_args):
                print(res)

    else:
        print("all location arguments must be existing directories")
