import logging

#logging.basicConfig(format='OpenTLDR Logging: %(message)s', level=logging.WARN)

logging.basicConfig(format='%(name)-12s: %(levelname)-8s %(message)s', level=logging.WARN)

log=logging.getLogger("OpenTLDR")
