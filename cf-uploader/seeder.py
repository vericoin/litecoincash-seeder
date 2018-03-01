import logging
import sys

import config
import cf
from errors import SeedsNotFound


logger = logging.getLogger(__name__)


def read_hard_seeds(hard_seeds_file):

    """ Read the hard seed list from the file. Should just be new line separated list of IP Addresses. """

    logger.debug("Reading hard seeds file: {}".format(hard_seeds_file))

    hard_seeds = []
    with open(hard_seeds_file) as seed_lines:
        for line in seed_lines:
            stripped_line = line.strip()
            if stripped_line:
                if ':' in stripped_line:
                    hard_seed = stripped_line.split(':')[0]
                else:
                    hard_seed = stripped_line

                hard_seeds.append(hard_seed)

    logger.info("Found {} hard seeds.".format(len(hard_seeds)))

    if not hard_seeds:
        raise SeedsNotFound("No seeds read from the hard seeds list: {}".format(hard_seeds_file))

    return hard_seeds


def read_seed_dump(seeds_file, valid_port="62458"):

    """ Read the good ip addresses from the seeds dump. """

    logger.debug("Reading seeds dump file: {}".format(seeds_file))

    addresses = []
    with open(seeds_file) as seeds:

        for line in seeds:
            if line.startswith('#'):
                continue

            components = line.split()
            ip_addr, port = components[0].split(':')
            logger.debug("Read a seed from a file: IP {} PORT {}".format(ip_addr, port))

            if valid_port in port:
                is_good = components[1] == "1"
                if is_good:
                    addresses.append(ip_addr)

    logger.info("Found {} good ip addresses from dump file.".format(len(addresses)))

    if not addresses:
        raise SeedsNotFound("No good seeds read from seeds dump file: {}".format(seeds_file))

    return addresses


def main():

    """ Main entry point. """

    configuration = config.read_local_config()

    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    try:
        seed_candidates = read_seed_dump(configuration['seed_dump'])
        hard_seeds = read_hard_seeds(configuration['hard_seeds'])
    except SeedsNotFound as e:
        print("ERROR: Problem reading seeds - {}".format(e.message))
        sys.exit(-1)

    cloudflare = cf.CloudflareSeeder.from_configuration(configuration)
    current_seeds = cloudflare.get_seeds()

    stale_current_seeds = [seed for seed in current_seeds if seed not in seed_candidates and seed not in hard_seeds]

    if stale_current_seeds:
        cloudflare.delete_seeds(stale_current_seeds)

    new_seeds = [seed for seed in seed_candidates+hard_seeds if seed not in current_seeds]
    cloudflare.set_seeds(new_seeds)


if __name__ == "__main__":
    main()