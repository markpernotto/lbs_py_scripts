import requests
import json
from datetime import date, timedelta
import math
from ls import c
from db import db_connect

token_url = "https://cloud.lightspeedapp.com/oauth/access_token.php"
api_url = "https://api.lightspeedapp.com/API/Account/" + c["account_id"] + "/"
today = str(date.today()) + 'T07:00:00-00:00'
yesterday = str(date.today() - timedelta(days = 1)) + 'T07:00:00-00:00'

source = 'SaleLine.json?orderby=createTime&orderby_desc=1&createTime=><,'+yesterday+','+today+'&load_relations=["Item"]&Item.defaultVendorID=464'
bearer_token = None
session = requests.Session()
session.headers.update({'Accept': 'application/json'})

try:
    payload = {
        'refresh_token': c['refresh_token'],
        'client_secret': c['client_secret'],
        'client_id': c['client_id'],
        'grant_type': 'refresh_token',
    }
    response = session.post(token_url, data=payload)
    json = response.json()
    bearer_token = json["access_token"]
    session.headers.update({'Authorization': 'Bearer ' + bearer_token})
except:
    bearer_token = None

url = api_url + source

try:
    r = requests.request('GET', url, data=None, headers=session.headers)
    results = r.json()
    count = int(results['@attributes']['count'])
    print(count)

    loops = math.ceil(count/100)
    page = 0

    con = db_connect()
    cur = con.cursor()
#     cur.execute("DELETE FROM sales")
    item_sql = "INSERT INTO sales (itemID,count,time) VALUES (?,?,?)"

    while loops > 0:
        url=api_url+source+'&offset='+str(page)
        r = requests.request('GET', url, data=None, headers=session.headers)
        results = r.json()

        try:
            if isinstance(results['SaleLine'], list):
                for sales in results['SaleLine']:
                    cur.execute(
                        item_sql, (
                            sales['Item']['itemID'],
                            sales['unitQuantity'],
                            sales['createTime'],
                        )
                    )
        except KeyError:
            print('cannot find results["SaleLine"]')

        loops = loops - 1
        page = page + 100

    con.commit()
    con.close()

except requests.exceptions.HTTPError as e:
    print ("Error: ", str(e))