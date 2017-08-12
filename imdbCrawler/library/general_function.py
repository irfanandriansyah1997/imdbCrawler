import os
import time
from ConfigParser import ConfigParser

__author__ = 'Irfan Andriansyah'

def tic(tag=None):
    """Start timer function.

    :param tag : (String) used to link a tic to a later toc. Can be any dictionary-able key.
    """

    global TIC_TIME

    tag = 'default' if tag is None else tag

    try:
        TIC_TIME[tag] = time.time()

    except NameError:
        TIC_TIME = {tag : time.time()}


def toc(tag=None, save=False, fmt=False):
    """Timer ending function

    :param tag : (String) used to link a toc to a previous tic. Allows multipler timers, nesting timers.
    :param save : (Boolean) if True, returns float time to out (in seconds)
    :param fmt : (Boolean) if True, formats time in H:M:S, if False just seconds.
    """

    global TOC_TIME
    template = 'Elapsed time is:'

    if tag is None:
        tag = 'default'
    else:
        template = '{} {} - '.format(tag, template)

    try:
        TOC_TIME[tag] = time.time()
    except NameError:
        TOC_TIME = {tag : time.time()}

    if TIC_TIME:
        d = (TOC_TIME[tag] - TIC_TIME[tag])

        if fmt:
            print template + ' %s' % time.strftime('%H:%M:%S', time.gmtime(d))
        else:
            print template + ' %f seconds' % (d)

        if save:
            return d
    else:
        print "no tic() start time available. Check global var settings"


