import argparse
import os

_PYCACHE_DIR_NAME = '__pycache__'
_PYCACHE_FILE_NAME_EXT = '.pyc'

def del_cache_dir(d:str):

    print(f'Directory: {repr(d)}')
    to_delete_dir = True
    for fn in os.listdir(d):

        if fn.endswith(_PYCACHE_FILE_NAME_EXT):

            print(f'    {repr(os.path.join(d, fn))}')

        else:

            to_delete_dir = False

    if to_delete_dir:

        #os.rmdir(d)
        print(f'Remove {repr(d)}')

def do_it(wd       :str,
          recursive:bool=False):
    
    if not recursive:

        del_cache_dir(wd)
        return
    
    for dp,dnn,fnn in os.walk(wd):

        for dn in dnn:

            if dn == _PYCACHE_DIR_NAME:

                del_cache_dir(os.path.join(dp, dn))

def main():

    ap = argparse.ArgumentParser(description=f'Delete Python cache ({repr(_PYCACHE_DIR_NAME)})')
    class A:

        WORKING_DIR = 'wd'
        RECURSIVE   = 'r'

    ap.add_argument(f'--{A.WORKING_DIR}')
    ap.add_argument(f'--{A.RECURSIVE}',
                    action='store_true')
    # read args
    get = ap.parse_args().__getattribute__
    wd = get(A.WORKING_DIR)
    r  = get(A.RECURSIVE)
    # do it
    do_it(wd       =wd if wd is not None else os.getcwd(),
          recursive=r)

if __name__ == '__main__': main()