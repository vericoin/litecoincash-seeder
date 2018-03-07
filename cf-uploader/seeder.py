import logging
import sys

import config
import cf
import errors
import parser


logger = logging.getLogger(__name__)


def main():

    """ Main entry point. """

    configuration = config.read_local_config()

    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    try:
        seed_candidates = parser.read_seed_dump(configuration['seed_dump'])
        hard_seeds = parser.read_hard_seeds(configuration['hard_seeds'])
    except errors.SeedsNotFound as e:
        print("ERROR: Problem reading seeds - {}".format(e.message))
        sys.exit(-1)

    cloudflare = cf.CloudflareSeeder.from_configuration(configuration)
    current_seeds = cloudflare.get_seeds()

    logger.debug("Detected current seeds in cloudflare: {}".format(current_seeds))

    stale_current_seeds = [seed for seed in current_seeds if seed not in seed_candidates and seed not in hard_seeds]

    if stale_current_seeds:
        cloudflare.delete_seeds(stale_current_seeds)

    new_seeds = [seed for seed in set(seed_candidates+hard_seeds) if seed not in current_seeds]
    cloudflare.set_seeds(new_seeds)


if __name__ == "__main__":
    main()