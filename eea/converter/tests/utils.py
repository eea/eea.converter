""" Test utilities
"""
import os

def get_filedata(rel_filename='data/chart.svg', as_string=True):
    """ Get file data
    """
    storage_path = os.path.join(os.path.dirname(__file__))
    file_path = os.path.join(storage_path, rel_filename)
    file_ob = open(file_path, 'rb')
    if as_string:
        return file_ob.read()
    return file_ob
