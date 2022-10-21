from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
import warnings
import pandas as pd


versionlist = {
    "webmasters": "v3",
    "analyticsreporting": "v4",
    "sheets": "v4"
}


class GoogleAPIservice():
    def __init__(self, servicename: "sheets, analyticsreporting, webmasters" = None, scope: "url" = None, sa_path=None, version='v4'):
        if not servicename and not scope:
            raise ValueError("Either scope or servicename must be specified")
        self.sa_path = sa_path or os.path.expandvars(os.environ.get(
            "SERVICE_ACCOUNT_JSON_PATH", "$HOME/.credentials/ga-service-account.json"))
        if not os.path.exists(self.sa_path):
            raise ValueError(
                f"Service account file {self.sa_path} does not exist")
        self.servicemap = {
            "sheets": "https://www.googleapis.com/auth/spreadsheets.readonly",
            "analyticsreporting": "https://www.googleapis.com/auth/analytics.readonly",
            "webmasters": "https://www.googleapis.com/auth/webmasters.readonly"
        }
        self.service = None
        self.version = version
        if servicename:
            self.servicename = servicename
            self.scopes = [self.servicemap[servicename]]
        else:
            self.scopes = [scope]
            self.servicename = self.servicemap[scope]
        if self.servicename in self.servicemap:
            self.version = versionlist[self.servicename]
            self.rebuild(self.servicename)
        else:
            availableservers = ", ".join(self.servicemap.keys())
            warnings.warn(
                f'servicename not in servicemap, use rebuild to set an available service in {availableservers}', DeprecationWarning, stacklevel=2)

    def rebuild(self, servicename: "sheets, analyticsreporting, webmasters"):

        if self.servicename == servicename and self.service and self.version <= versionlist[servicename]:
            return
        if servicename not in self.servicemap:
            raise ValueError(
                f"Service name {servicename} not in {self.servicemap}")
        self.version = versionlist[servicename]
        self.scopes = [self.servicemap[servicename]]
        self.credentials = service_account.Credentials.from_service_account_file(
            self.sa_path, scopes=self.scopes)
        self.service = build(servicename, self.version,
                             credentials=self.credentials)

    def readSheets(self, SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME,
                   dedupCol=None, skiprows=0, valueRenderOption='UNFORMATTED_VALUE'):
        self.rebuild("sheets")
        sheet = self.service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=SAMPLE_RANGE_NAME,
                                    valueRenderOption=valueRenderOption).execute().get('values', [])
        databody = result[skiprows+1:]
        maxdatacol = max([len(a) for a in databody])
        colnames = result[skiprows]
        if maxdatacol >= len(result[0]):
            colnames = colnames[:maxdatacol]
        else:
            colnames = colnames + \
                [f"Unnamed_{i}" for i in range(maxdatacol-len(colnames))]

        df = pd.DataFrame(databody, columns=colnames)
        if dedupCol and dedupCol in df.columns:
            df = df.dropna(subset=[dedupCol]).reset_index()
        return df

    def readAnalytics(self, view_id,  metrics, dimensions,segments=[],
                      start_date='7daysAgo', end_date='today',
                      filters_expression=None, page_size=100000,
                      pagetoken='0', columnHeader=None, df=pd.DataFrame()):

        self.rebuild("analyticsreporting")
        analytics = self.service.reports()
        if segments and 'ga:segment' not in dimensions:
            dimensions.append('ga:segment')
        body = {
            'reportRequests': [
                {
                    'viewId': view_id,
                    'dateRanges': [{'startDate': start_date, 'endDate': end_date}],
                    'metrics': [{'expression': mtr} for mtr in metrics],
                    'dimensions': [{'name': dm} for dm in dimensions],
                    'pageSize': page_size,
                    'pageToken': pagetoken,
                    'segments': [{"segmentId": seg} for seg in segments],
                }]
        }
        if filters_expression:
            body['reportRequests'][0]['dimensionFilterClauses'] = [{'filters': [
                {'dimensionName': dimensions, 'operator': 'REGEXP', 'expressions': [filters_expression]}]}]
        response = analytics.batchGet(body=body).execute()
        pagetoken = response['reports'][0].get('nextPageToken', None)
        if not columnHeader:
            columnHeader = response.get("reports")[0].get('columnHeader', {})
        dimensionHeaders = columnHeader.get('dimensions', [])
        metricHeaders = columnHeader.get(
            'metricHeader', {}).get('metricHeaderEntries', [])
        datarows = response.get("reports")[0].get('data', {}).get('rows', [])
        nicerows = []
        for row in datarows:
            dic = {}
            dimensiondata = row.get('dimensions', [])
            metircData = row.get('metrics', [])
            for header, dimension in zip(dimensionHeaders, dimensiondata):
                dic[header] = dimension
            for values in metircData:
                for metric, value in zip(metricHeaders, values.get('values')):
                    if '.' in value:
                        dic[metric.get('name')] = float(value)
                    else:
                        dic[metric.get('name')] = int(value)
            nicerows.append(dic)
        startdflength = len(df)
        df = pd.concat([df, pd.DataFrame(list(nicerows))])
        while pagetoken and len(df) - startdflength == page_size:
            print(f"Reading page {pagetoken}","total rows",len(df))
            df = self.readAnalytics(view_id, metrics, dimensions,segments, start_date, end_date,
                                    filters_expression, segments, page_size, pagetoken, columnHeader, df)
        return df.reset_index(drop=True)

    def readSearchConcole(self, siteUrl, startDate='7daysAgo', endDate='today',
                          dimensions=["page", "query", "date"],  rowLimit=10000, startRow=0,
                          dfall=pd.DataFrame()):

        self.rebuild("webmasters")
        service = self.service.searchanalytics()
        body = {
            'startDate': startDate,
            'endDate': endDate,
            'dimensions': dimensions,
            'rowLimit': rowLimit,
            'startRow': startRow
        }
        response = service.query(siteUrl=siteUrl, body=body).execute()
        data = response.get('rows',[])
        if not data:
            print(response)
            return pd.DataFrame()
        df = pd.DataFrame(data)

        for i, dim in enumerate(body['dimensions']):
            df[dim] = df['keys'].apply(lambda x: x[i] if len(x) >= i else None)
        df.drop(columns='keys', inplace=True)
        startlength = len(dfall)
        dfall = pd.concat([dfall, df])
        while len(dfall) - startlength == rowLimit:
            print(f"Reading page {startRow}", "total rows", len(dfall))
            dfall = self.readSearchConcole(
                siteUrl, startDate, endDate, dimensions, rowLimit, startRow+rowLimit, dfall)
        return dfall.reset_index(drop=True)


if __name__ == "__main__":
    api = GoogleAPIservice('analyticsreporting', version='v3')
    view_id = "211915022"
    metrics = ['ga:goal1Completions']
    dimensions = ['ga:goalPreviousStep1', 'ga:date','ga:segment']
    start_date = '7daysAgo'
    end_date = 'today'

    service = api.service
    body = {
        'reportRequests': [
            {
                'viewId': view_id,
                'dateRanges': [{'startDate': start_date, 'endDate': end_date}],
                'metrics': [{'expression': mtr} for mtr in metrics],
                'dimensions': [{'name': dm} for dm in dimensions],
                'pageSize': 100000,
                'pageToken': "0",
                'segments': [{"segmentId":"gaid::-5"}],
            }]
    }
    response = service.reports().batchGet(body=body).execute()
