from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from datetime import datetime
import pandas as pd
import os

# sample yaml file https://github.com/googleads/google-ads-python/blob/main/google-ads.yaml
GOOGLE_ADS_YAML_PATH = os.path.expandvars(os.environ.get("GOOGLE_ADS_YAML_PATH", "$HOME/.credentials/google-ads.yml"))

def map_locations_ids_to_resource_names(client, location_ids):
    """Converts a list of location IDs to resource names.
    Args:
        client: an initialized GoogleAdsClient instance.
        location_ids: a list of location ID strings.
    Returns:
        a list of resource name strings using the given location IDs.
    """
    build_resource_name = client.get_service(
        "GeoTargetConstantService"
    ).geo_target_constant_path
    return [build_resource_name(location_id) for location_id in location_ids]


def keywordIdea(keyword_texts:list[str], startdate:datetime.date = None, enddate:datetime.date = None, location_ids : list = ["2124"],language_id = "1000",customer_id='5051885307', page_url=None, google_ads_yaml=GOOGLE_ADS_YAML_PATH):
    enddate = enddate or datetime.today()
    startdate = startdate or datetime.date(enddate.year, 1, 1)
    print(f'date range: {startdate} to {enddate}')
    client = GoogleAdsClient.load_from_storage(google_ads_yaml)
    keyword_plan_idea_service = client.get_service("KeywordPlanIdeaService")
    monthemum = (None,
                client.get_type("MonthOfYearEnum").MonthOfYear.JANUARY,
                client.get_type("MonthOfYearEnum").MonthOfYear.FEBRUARY,
                client.get_type("MonthOfYearEnum").MonthOfYear.MARCH,
                client.get_type("MonthOfYearEnum").MonthOfYear.APRIL,
                client.get_type("MonthOfYearEnum").MonthOfYear.MAY,
                client.get_type("MonthOfYearEnum").MonthOfYear.JUNE,
                client.get_type("MonthOfYearEnum").MonthOfYear.JULY,
                client.get_type("MonthOfYearEnum").MonthOfYear.AUGUST,
                client.get_type("MonthOfYearEnum").MonthOfYear.SEPTEMBER,
                client.get_type("MonthOfYearEnum").MonthOfYear.OCTOBER,
                client.get_type("MonthOfYearEnum").MonthOfYear.NOVEMBER,
                client.get_type("MonthOfYearEnum").MonthOfYear.DECEMBER)

    keyword_competition_level_enum = (
        client.enums.KeywordPlanCompetitionLevelEnum
    )
    keyword_plan_network = (
        client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH_AND_PARTNERS
    )
    location_rns = map_locations_ids_to_resource_names(client, location_ids)
    language_rn = client.get_service("GoogleAdsService").language_constant_path(
        language_id
    )

    # Either keywords or a page_url are required to generate keyword ideas
    # so this raises an error if neither are provided.
    if not (keyword_texts or page_url):
        raise ValueError(
            "At least one of keywords or page URL is required, "
            "but neither was specified."
        )

    # Only one of the fields "url_seed", "keyword_seed", or
    # "keyword_and_url_seed" can be set on the request, depending on whether
    # keywords, a page_url or both were passed to this function.
    request = client.get_type("GenerateKeywordIdeasRequest")
    request.customer_id = customer_id
    request.language = language_rn
    request.geo_target_constants.extend(location_rns)
    request.include_adult_keywords = False
    request.keyword_plan_network = keyword_plan_network
    request.historical_metrics_options.year_month_range.start.year = startdate.year
    request.historical_metrics_options.year_month_range.start.month= monthemum[startdate.month]
    request.historical_metrics_options.year_month_range.end.year = enddate.year
    request.historical_metrics_options.year_month_range.end.month= monthemum[enddate.month]
    if keyword_texts and not page_url:
        request.keyword_seed.keywords.extend(keyword_texts)

    if not keyword_texts and page_url:
        request.url_seed.url = page_url

    if keyword_texts and page_url:
        request.keyword_and_url_seed.url = page_url
        request.keyword_and_url_seed.keywords.extend(keyword_texts)

    ideas = keyword_plan_idea_service.generate_keyword_ideas(
        request=request
    )
    ideasdata = [{"keyword":i.text, "avg_monthly_searches":i.keyword_idea_metrics.avg_monthly_searches, "lot_bid_micros":i.keyword_idea_metrics.low_top_of_page_bid_micros,"high_bid_micros":i.keyword_idea_metrics.high_top_of_page_bid_micros} for i in ideas]
    df = pd.DataFrame(ideasdata)
    df['start_date'] = startdate.strftime("%Y-%m-%d")
    df['end_date'] = enddate.strftime('%Y-%m-%d')
    df['location_ids'] = str(location_ids)
    return df


if __name__ == "__main__":
    startdate = datetime(2022, 1, 1)
    enddate = datetime(2022,10,31)
    df = keywordIdea(["dentist"], startdate=startdate, enddate=enddate, location_ids=["2124"], language_id="1000", customer_id='5051885307')
    print(df)