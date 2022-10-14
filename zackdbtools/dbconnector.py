
import json
import importlib.resources as importlib_resources
import pandas as pd
from sqlalchemy.dialects.mysql import SMALLINT, INTEGER, BIGINT, FLOAT, DOUBLE, TEXT, NVARCHAR, DATETIME, BOOLEAN
import os


DB_CREDENTIALS_PATH = os.path.expandvars(os.environ.get('DB_CREDENTIALS_PATH'))


def db_engine(cred : 'devmysql,tymbrel,dwh,dwhwrite,memory,filedb', db=None):
    """
    It creates a database engine using the credentials in the dbcredentials.json file.
    
    :param cred: which credential to use. options: e.g.memory,filedb,devmysql, tymbrel,dwh, dwhwrite .The name of the credential in the dbcredentials.json file
    :param db: The name of the database you want to connect to
    :return: The function db_engine is returning the value of the variable engine.
    """
    from sqlalchemy import create_engine
    with open(DB_CREDENTIALS_PATH) as dbc:
        dbcredentials = json.load(dbc)
    # dbcredentials = json.loads(importlib_resources.read_text('zackdbtools','dbcredentials.json'))
    if cred not in dbcredentials:
        raise Exception('Credential not found in dbcredentials.json')
    credpair = dbcredentials[cred]
    conn_engine = credpair['conn_engine']
    # Assigning the value of the key 'user' in the dictionary credpair to the variable user.
    user = credpair['user']
    passwd = ':'+credpair['passwd'] if credpair['passwd'] else ''
    host = '@'+credpair['host'] if conn_engine != 'sqlite' else credpair['host']
    port = ':'+str(credpair['port']) if credpair['port'] else ''
    db = '/'+db if db else ''
    credstr =  f'{conn_engine}://{user}{passwd}{host}{port}{db}'
    engine = create_engine(credstr)
    return engine



def getsqltype(df : pd.DataFrame) -> dict:
    """
    It takes a pandas dataframe and returns a dictionary of sqlalchemy column types
    
    :param df: the dataframe you want to write to the database
    :type df: pd.DataFrame
    :return: A dictionary of column names and their corresponding SQLAlchemy data types.
    """
    sqldtypes = {}
    for dfcol in df.columns:
        coltype = df[dfcol].dtypes
        if str(coltype.name) == 'bool':
            sqldtypes[dfcol] = BOOLEAN
            continue
        if str(coltype).startswith('int'):
            if df[dfcol].max() < 65535 and df[dfcol].min() >= 0:
                sqldtypes[dfcol] = SMALLINT(unsigned = True)
                continue
            elif df[dfcol].max() < 2147483647 and df[dfcol].min() >= -2147483648:
                sqldtypes[dfcol] = INTEGER
                continue
            else:
                sqldtypes[dfcol] = BIGINT
                continue
        if str(coltype).startswith('float'):
            if df[dfcol].max() <= 3.40282e+38 and df[dfcol].min() >= -3.40282e+38:
                sqldtypes[dfcol] = FLOAT
                continue
            else:
                sqldtypes[dfcol] = DOUBLE
                continue
        if str(coltype).startswith('datetime'):
            sqldtypes[dfcol] = DATETIME
            continue
        # if str(coltype).startswith('string') or str(coltype).startswith('object'):
        maxlen = df[dfcol].astype('str').str.len().max()
        maxlen = 50 if maxlen < 50 else maxlen +100
        if maxlen <= 65535:
            sqldtypes[dfcol] = NVARCHAR(maxlen)
        else:
            sqldtypes[dfcol] = TEXT
    return sqldtypes