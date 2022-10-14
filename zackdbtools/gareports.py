import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
import importlib.resources as importlib_resources
import os

SERVICE_ACCOUNT_JSON_PATH = os.path.expandvars(os.environ.get("SERVICE_ACCOUNT_JSON_PATH", None))

#Get one report page
def get_report(service, query):
    """
    The function takes in a service object and a query object, and returns the rows, the next page
    token, the dimension headers, and the metric headers.
    
    :param service: The service object created in the previous step
    :param query: The query parameters for the report
    :return: the rows, page token, dimension headers, and metric headers.
    """
    response = service.reports().batchGet(body=query).execute()
    pagetoken = response.get("reports")[0].get('nextPageToken', None)
    rowsNew = response.get("reports")[0].get('data', {}).get('rows', [])
    columnHeader = response.get("reports")[0].get('columnHeader', {})
    dimensionHeaders = columnHeader.get('dimensions', [])
    metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])
    return rowsNew, pagetoken, dimensionHeaders, metricHeaders

def rows2df(rows, dimensionHeaders, metricHeaders):
    """
    It takes the rows of data from the Google Analytics API, and turns them into a Pandas DataFrame.
    
    :param rows: the rows of data returned from the API
    :param dimensionHeaders: the dimension names
    :param metricHeaders: the metrics you want to get from the API
    :return: A dataframe with the dimensions and metrics
    """
    nicerows=[]
    for row in rows:
        dic={}
        dimensions = row.get('dimensions', [])
        dateRangeValues = row.get('metrics', [])

        for header, dimension in zip(dimensionHeaders, dimensions):
            dic[header] = dimension

        for i, values in enumerate(dateRangeValues):
            for metric, value in zip(metricHeaders, values.get('values')):
                if ',' in value or ',' in value:
                    dic[metric.get('name')] = float(value)
                else:
                    dic[metric.get('name')] = int(value)
        nicerows.append(dic)
    return pd.DataFrame(list(nicerows))


def gareports(view_id, metrics, dimensions, service_account_json=None, filters=None, start_date=None, end_date=None):
    """
    `gareports` takes a view id, a list of metrics, a list of dimensions, and optionally a list of
    filters, a start date, and an end date, and returns a dataframe of the results.
    
    :param view_id: the view id of the Google Analytics account you want to query
    :param metrics: a list of metrics to include in the report
    :param dimensions: a list of dimensions to include in the report
    :param filters: a list of dictionaries, each with a dimension and an expression
    :param start_date: The start date for fetching Analytics data. Requests can specify a start date
    formatted as YYYY-MM-DD, or as a relative date (e.g., today, yesterday, or NdaysAgo where N is a
    positive integer)
    :param end_date: The end date for fetching Analytics data. Request can specify a start date
    formatted as YYYY-MM-DD, or as a relative date (e.g., today, yesterday, or NdaysAgo where N is a
    positive integer). Default value is yesterday
    :return: A dataframe with the following columns:
        - date
        - pagePath
        - pageTitle
        - pageviews
        - uniquePageviews
        - users
        - sessions
        - avgSessionDuration
        - bounceRate
        - exitRate
        - pageValue
        - goalCompletionsAll
        - goalConversionRateAll
    """
    SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
    service_account_json = service_account_json or SERVICE_ACCOUNT_JSON_PATH
    credentials = service_account.Credentials.from_service_account_file(
          service_account_json, scopes=SCOPES)
    service = build('analyticsreporting', 'v4', credentials=credentials)

    #daterange
    daterange = None
    if start_date or end_date:
        start_date = start_date or '2000-01-01'
        end_date = end_date or 'today'
        daterange =[{'startDate': start_date, 'endDate': end_date}]

    # handle pagenation
    pagetoken = '0'
    rows = []
    while pagetoken != None:
        query = {
                "reportRequests": [
                    {
                        "viewId": view_id,
                        "dateRanges": daterange,
                        "metrics": [{"expression": mtr} for mtr in metrics],
                        "dimensions": [{"name": dm} for dm in dimensions],
                        "pageSize": 100000,
                        "pageToken": pagetoken
                    }]
                }
        rowsNew, pagetoken, dimensionHeaders, metricHeaders  = get_report(service, query)
        rows += rowsNew
        print("len(rows): " + str(len(rows)))
    return rows2df(rows, dimensionHeaders, metricHeaders)

if __name__ == '__main__':
    view_id = '264478000'
    metrics = ['ga:users','ga:newUsers','ga:pageViews','ga:sessions']
    dimensions = ['ga:month', 'ga:year']
    start_date = '2018-01-01'
    df = gareports(view_id, metrics, dimensions, start_date=start_date)
