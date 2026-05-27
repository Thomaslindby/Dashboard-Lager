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
    data={"grant_type":"client_credentials","client_id":CLIENT_ID,"client_secret":CLIENT_SECRET,"scope":"https://analysis.windows.net/powerbi/api/.default"}
)
token_resp.raise_for_status()
token = token_resp.json()["access_token"]

query_resp = requests.post(
    f"https://api.powerbi.com/v1.0/myorg/groups/{WORKSPACE_ID}/datasets/{DATASET_ID}/executeQueries",
    headers={"Authorization":f"Bearer {token}","Content-Type":"application/json"},
    json={"queries":[{"query":DAX}],"serializerSettings":{"includeNulls":False}}
)
query_resp.raise_for_status()

rows = query_resp.json()["results"][0]["tables"][0].get("rows",[])

data = []
for row in rows:
    keys = list(row.keys())
    name_col  = next((k for k in keys if "medarbej" in k.lower()),keys[0])
    pluk_col  = next((k for k in keys if "antalpluk" in k.lower().replace(" ","")),keys[1] if len(keys)>1 else keys[0])
    ordre_col = next((k for k in keys if "ordre" in k.lower()),None)
    data.append({
        "name":   row[name_col],
        "picks":  int(row.get(pluk_col,0) or 0),
        "orders": int(row.get(ordre_col,0) or 0) if ordre_col else 0
    })

data.sort(key=lambda x: x["picks"], reverse=True)

with open("data.json","w",encoding="utf-8") as f:
    json.dump({"updated":date.today().isoformat(),"data":data},f,ensure_ascii=False,indent=2)

print(f"✓ Gemt {len(data)} medarbejdere til data.json")
