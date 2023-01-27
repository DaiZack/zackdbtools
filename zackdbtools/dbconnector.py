
import json
import pandas as pd
from sqlalchemy.dialects.mysql import SMALLINT, INTEGER, BIGINT, FLOAT, DOUBLE, TEXT, VARCHAR, DATETIME, BOOLEAN
import os
from sqlalchemy import inspect, Table, Column, MetaData, engine


DB_CREDENTIALS_PATH = os.path.expandvars(os.environ.get('DB_CREDENTIALS_PATH','$HOME/.credentials/dbcredentials.json'))


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
            if df[dfcol].max() < 100 and df[dfcol].min() >= 0:
                sqldtypes[dfcol] = SMALLINT(unsigned = True)
                continue
            # elif df[dfcol].max() < 2147483647 and df[dfcol].min() >= -2147483648:
            elif df[dfcol].max() < 147483647 and df[dfcol].min() >= -147483648:
                sqldtypes[dfcol] = INTEGER
                continue
            else:
                sqldtypes[dfcol] = BIGINT
                continue
        if str(coltype).startswith('float'):
            # if df[dfcol].max() <= 3.40282e+38 and df[dfcol].min() >= -3.40282e+38:
            if df[dfcol].max() <= 3.40282e+30 and df[dfcol].min() >= -3.40282e+30:
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
        maxlen = 50 if maxlen < 50 else (((maxlen +100)// 250) + 1) * 250
        if maxlen <= 1000:
            sqldtypes[dfcol] = VARCHAR(maxlen, collation='utf8mb4_0900_ai_ci', charset='utf8mb4')
        else:
            sqldtypes[dfcol] = TEXT
    return sqldtypes

def df2sql( df : pd.DataFrame, tablename: str,engine: engine, replace=False, atuoid=True):
    """
    :param df: the dataframe you want to save
    :type df: pd.DataFrame
    :param tablename: the name of the table you want to create
    :type tablename: str
    :param engine: the engine object that you created in the previous section
    :type engine: engine
    :param replace: if the table already exists, drop it and create a new one, defaults to False
    (optional)
    :param atuoid: if True, the table will have an auto-incrementing id column, defaults to True
    (optional)
    """
    if 'id' in df.columns and atuoid:
        df = df.rename(columns={'id': '_id'})
    dtypes = getsqltype(df)
    inspector = inspect(engine)
    if replace:
        with engine.connect() as conn:
            conn.execute(f'DROP TABLE IF EXISTS {tablename}')
    elif tablename in inspector.get_table_names():
        df.to_sql(tablename, engine, if_exists='append', index=False, dtype=dtypes)
        return False

    metadata = MetaData()
    columns = []
    for col in dtypes:
        columns.append(Column(col, dtypes[col]))
    if atuoid:
        table = Table(tablename, metadata, Column('id', BIGINT(unsigned=True), primary_key=True, autoincrement=True), *columns)
    else:
        table = Table(tablename, metadata, *columns)
    metadata.create_all(engine)
    df.to_sql(tablename, engine, if_exists='append', index=False, dtype=dtypes)
    return True

if __name__ == '__main__':
    engine = db_engine('dwhwrite','dcdashboard')
    df = pd.DataFrame({'a': ['names', 'words', 'texts'], 'b': [4, 5, 6]})
    df2sql(df, 'testtable', engine, replace=False)