# zackdbtool
a python package to connect db and data sources like google sheets

## Set up
make a json file that contains the database credentials. 

see example: dbcredentials_example.json (memory and filedb are for sqlite quick usage, you can add more like test1)

```
{
    "test1":{
        "conn_engine":"mysql+pymysql",
        "host":"192.168.0.12",
        "port":3306,
        "user":"test_user",
        "passwd":"********",
        "db":"public",
        "testtable":"user"
    },
    "memory":{
        "conn_engine":"sqlite",
        "host":"/:memory:",
        "port":"",
        "user":"",
        "passwd":"",
        "db":"test",
        "testtable":""
    },
    "filedb":{
        "conn_engine":"sqlite",
        "host":"/filedb.db",
        "port":"",
        "user":"",
        "passwd":"",
        "db":"test",
        "testtable":""
    }
}
```

save the file to a location, e.g. $HOME/.credentials/dbcredentials_example.json

save your google service account json file to a location e.g. $HOME/.credentials/service_account.json

add two environment variable for those two files:
```
DB_CREDENTIALS_PATH=$HOME/.credentials/dbcredentials_example.json
SERVICE_ACCOUNT_JSON_PATH=$HOME/.credentials/service_account.json
```

in linux/mac you can (NOTE: in vscode jupyter, it doesn't read the .bashrc, you can either add a .env or use the same file path below)
```
vi $HOME/.bashrc
```
inseart two rows to the end of the file and restart the terminal
```
export DB_CREDENTIALS_PATH=$HOME/.credentials/dbcredentials_example.json
export SERVICE_ACCOUNT_JSON_PATH=$HOME/.credentials/service_account.json
```

if you run your app as a systemd service:
```
vi /etc/systemd/system/YOURSERVICENAME.service
```

add environment variable 
```
[Service]
Environment=DB_CREDENTIALS_PATH=$HOME/.credentials/dbcredentials.json
Environment=SERVICE_ACCOUNT_JSON_PATH=$HOME/.credentials/ga-service-account.json
```
then reload daemon
```
systemctl daemon-reload
```

in windows, use the search bar to search "environment variable" add the two variables to user/system variables


if you want to build app in docker 
```
docker run -e DB_CREDENTIALS_PATH=dbcredentials.json -e SERVICE_ACCOUNT_JSON_PATH=ga-service-account.json dockerimagename
```



download the repository, and 

```
pip install .
```

or through pipy

```
pip install zackdbtool
```

## Connect a database

```
from zackdbtool import db_engine
import pandas as pd
dbsource= 'mydb' 
engine = db_engine(dbsource, db='test')
df = pd.read_sql(f'SELECT * FROM user limit 10', engine)
print(df)
```

if you don't have a database running you can use memory or filedb to create a testing database without any setup
```
from zackdbtool import db_engine
import pandas as pd
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker

dbsource= 'memory' 
engine = db_engine(dbsource)
Base = declarative_base()
sesson = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)

Base.metadata.create_all(engine)

ed_user = User(name="ed", fullname="Ed Jones")
session.add(ed_user)
session.commit()

with engine.connect() as c:
    data = c.execute('select * from users').fetch_all()
    print(data)

```
## use google services
```
view_id = 'your site view id'
metrics = ['ga:users','ga:newUsers','ga:pageViews','ga:sessions']
# find more setting at https://ga-dev-tools.web.app/query-explorer/
dimensions = ['ga:month', 'ga:year']
start_date = '2000-01-01'
df = gareports(view_id, metrics, dimensions, start_date=start_date)
```

# google sheet
```
  SAMPLE_SPREADSHEET_ID_PV = 'your google sheet id'
  SAMPLE_RANGE_NAME_PV = 'your sheet name'
  dedupCol = 'idcolname' 
  skiprows = 0
  dfpv = readgooglesheets(SAMPLE_SPREADSHEET_ID_PV, SAMPLE_RANGE_NAME_PV,dedupCol = dedupCol, skiprows = skiprows)
  print(dfpv.head())
```