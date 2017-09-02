import time
from datetime import datetime

__author__ = "Irfan Andriansyah"
__url__ = {
    "photo": {
        "hd": "@._V1_.jpg",
        "medium": "@._V1_UY317_CR121,0,214,317_AL_.jpg"
    },
    "media": {
        "hd": "@._V1_.jpg",
        "medium": "@._V1_SY1000_CR0,0,1502,1000_AL_.jpg"
    },
    "film-list": {
        "hd": "@._V1_.jpg",
        "medium": "@._V1_UX182_CR0,0,182,268_AL_.jpg",
        "small": "@._V1_UX67_CR0,0,67,98_AL_.jpg"
    }
}

def tic(tag=None):
    """Start timer function.

    :param tag : (String) used to link a tic to a later toc. Can be any dictionary-able key.
    """

    global TIC_TIME

    tag = "default" if tag is None else tag

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
    template = "Elapsed time is:"

    if tag is None:
        tag = "default"
    else:
        template = "{} {} - ".format(tag, template)

    try:
        TOC_TIME[tag] = time.time()
    except NameError:
        TOC_TIME = {tag : time.time()}

    if TIC_TIME:
        d = (TOC_TIME[tag] - TIC_TIME[tag])

        if fmt:
            print template + " %s" % time.strftime("%H:%M:%S", time.gmtime(d))
        else:
            print template + " %f seconds" % (d)

        if save:
            return d
    else:
        print "no tic() start time available. Check global var settings"

def convert_photo(url, mode="photo"):
    temp = url.split("@")
    picture = dict()

    if mode == "photo":
        picture = {
            k: "{}@{}".format(temp[0], v) if len(temp) > 2
            else "{}{}".format(temp[0], v)
            for k, v in __url__.get(mode).items()
        }

        picture.update({"small": url})

    elif mode == "media":
        picture.update({"media" : dict()})
        picture["media"] = {
            k: "{}@{}".format(temp[0], v) if len(temp) > 2
            else "{}{}".format(temp[0], v)
            for k, v in __url__.get(mode).items()
        }

        picture["media"].update({"small": url})
        picture.update({"mime_type": "image/jpeg"})
        picture.update({"type": "images"})

    elif mode == "film-list":
        picture = {
            k: "{}@{}".format(temp[0], v) if len(temp) > 2
            else "{}{}".format(temp[0], v)
            for k, v in __url__.get(mode).items()
            }


    return picture

def convert_date(timestring = "", format = None):
    try:
        response = dict()
        if format is not None and timestring is not None:
            if timestring != "":
                response.update({"iso": datetime.strptime(timestring, "%Y-%m-%d")})
                response.update({"day": int(response.get("iso").strftime("%d"))})
                response.update({"month": int(response.get("iso").strftime("%m"))})
                response.update({"year": int(response.get("iso").strftime("%Y"))})
                response.update({"text": str(response.get("iso").strftime("%B %d %Y"))})
            else:
                response.update({"iso": None})
                response.update({"day": None})
                response.update({"month": None})
                response.update({"year": None})
                response.update({"text": "Oops data not found"})

            return response
        else:
            raise ValueError("Format time is not defined")
    except Exception, e:
        print e
        return {"iso": None, "day": None, "month": None, "year": None, "text": "Oops data not found"}
