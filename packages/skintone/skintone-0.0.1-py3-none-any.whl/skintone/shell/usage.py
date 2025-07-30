from time import ctime

from skintone import __version__


def run():
    cur_time = ctime()
    text = f"""
    # skintone
    
    version {__version__} ({cur_time} +0800)
    """
    print(text)
