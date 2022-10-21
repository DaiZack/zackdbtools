import json,os, time, requests, jwt

def token_from_service_account(scope, json_file_path=None):

    credpath = json_file_path or os.environ.get("SERVICE_ACCOUNT_JSON_PATH", "$HOME/.credentials/ga-service-account.json")

    if not os.path.exists(credpath):
        raise ValueError(f"No credentials found at {credpath}")

    with open(os.path.expandvars(credpath)) as f:
        credentials = json.load(f)

    auth_url = 'https://www.googleapis.com/oauth2/v4/token'

    payload = {
        "iss": credentials['client_email'],       # Issuer claim
        "aud": auth_url,    # Audience claim
        "iat": int(time.time()),      # Issued At claim
        "exp": int(time.time())+3600,     # Expire time
        "scope": scope      # Permissions
    }

    sig = jwt.encode(payload, credentials['private_key'], algorithm="RS256", headers={"alg": "RS256", "typ": "JWT"})

    params = {
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": sig
    }
    token = requests.post(auth_url, data=params).json().get('access_token')
    return token

if __name__ == "__main__":
    scope = 'https://www.googleapis.com/auth/analytics.readonly'
    token = token_from_service_account("https://www.googleapis.com/auth/spreadsheets")
    request_url = 'https://www.googleapis.com/analytics/v3/data/ga?ids=ga%3A211915022&dimensions=ga%3AgoalPreviousStep1%2Cga%3AgoalPreviousStep2%2Cga%3AgoalPreviousStep3&metrics=ga%3Agoal1Completions&segment=gaid%3A%3A-5&start-date=2022-01-01&end-date=2022-10-17&max-results=2000'
    headers={'Authorization': 'Bearer ' + token}
    twt = requests.get(request_url, headers).json()