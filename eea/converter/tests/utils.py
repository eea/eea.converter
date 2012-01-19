""" Test utilities
"""
import os

def get_filedata(rel_filename='data/chart.svg'):
    """ Get file data
    """
    storage_path = os.path.join(os.path.dirname(__file__))
    file_path = os.path.join(storage_path, rel_filename)
    file_ob = open(file_path, 'rb')
    return file_ob.read()
