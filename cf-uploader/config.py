""" Simple config reading. """

import os
import logging
import ConfigParser

logger = logging.getLogger(__name__)

CONF_FILE_LOCATIONS = [
    '/etc/seeder.conf',
    os.path.expanduser('~/.seeder/seeder.conf'),
]


def get_conf_file():

    """ Find the first occurrence of a conf file and return it, or None if they don't exist. """

    for conf_file in CONF_FILE_LOCATIONS:
        if os.path.exists(conf_file):
            logger.info("Found conf file {}".format(conf_file))
            return conf_file

    return None


def read_config_section(config, section):

    """ Read a section of a config file into a dict and return it. """

    logger.info("Reading section {} from config.".format(section))

    configuration = {}
    options = config.options(section)

    for option in options:

        try:
            configuration[option] = config.get(section, option)
            logger.debug("Successfully read option {}: {}".format(option, configuration[option]))

        except ConfigParser.NoOptionError:
            logger.warning("Could not read config option {} from section {}".format(option, section))
            configuration[option] = None

    return configuration


def read_local_config():
    config_parser = ConfigParser.ConfigParser()
    config_parser.read(get_conf_file())
    return read_config_section(config_parser, "general")







