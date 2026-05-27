import requests
import json
import os
from datetime import date

TENANT_ID     = os.environ["PBI_TENANT_ID"]
CLIENT_ID     = os.environ["PBI_CLIENT_ID"]
CLIENT_SECRET = os.environ["PBI_CLIENT_SECRET"]
WORKSPACE_ID  = os.environ["PBI_WORKSPACE_ID"]
DATASET_ID    = os.environ["PBI_DATASET_ID"]

DAX = """
EVALUATE
SUMMARIZECOLUMNS(
    'LagerPluk'[Tildelt Lagermedarbejder],
    KEEPFILTERS(FILTER(
        ALL('LagerPluk'[Posting_Date]),
        'LagerPluk'[Posting_Date] = TODAY()
    )),
    "AntalPluk", COUNTROWS('LagerPluk'),
    "AntalOrdrer", DISTINCTCOUNT('LagerPluk'[Document_No])
)
"""

token_resp = requests.post(
    f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token",
    data={"grant_type":"client_credentials","client_id":CLIENT_ID,"client_secret":CLIENT_SECRET,"scope":"https://analysis.windows.net/powerbi/api
