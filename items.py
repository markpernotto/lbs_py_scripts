import requests
import json
from datetime import date, timedelta
import math
from ls import c
from db import db_connect

token_url = "https://cloud.lightspeedapp.com/oauth/access_token.php"
api_url = "https://api.lightspeedapp.com/API/Account/" + c["account_id"] + "/"
today = str(date.today()) + 'T07:00:00-00:00'
yesterday = str(date.today() - timedelta(days = 365)) + 'T07:00:00-00:00'

source = 'Item.json?load_relations=["ItemShops","TagRelations.Tag","Category","Manufacturer"]&timeStamp=><,'+yesterday+','+today+'&defaultVendorID=464&archived=false'
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
    # cur.execute("DELETE FROM inventory")
    item_sql = "INSERT INTO inventory (itemID,description,title,author,storeQty,reorderPoint,reorderLevel,price,isbnList,category,subcategory1,subcategory2,cost,warehouseQty,systemSku,createTime,updateTime) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"

    while loops > 0:
        url=api_url+source+'&offset='+str(page)
        r = requests.request('GET', url, data=None, headers=session.headers)
        results = r.json()

        for item in results['Item']:
            descSplit = item['description'].split('|')
            title = ""
            author = ""
            desc = ""
            if len(descSplit) > 0:
                desc = descSplit[0]
            if len(descSplit) > 1:
                desc = desc + " " + descSplit[1]
            if len(descSplit) > 2:
                title = descSplit[2]
            if len(descSplit) > 3:
                author = descSplit[3]

            itemShop = next((x for x in item['ItemShops']['ItemShop'] if x['shopID'] == "1"), None)
            price = next((x for x in item['Prices']['ItemPrice'] if x['useType'] == "Default"), None)
            isbn_list = []
            if 'Tags' in item:
                if isinstance(item['Tags']['tag'], list):
                    for isbn in item['Tags']['tag']:
                        if len(isbn) == 13 and isbn.isdigit():
                            isbn_list.append(isbn)
                else:
                    if len(item['Tags']['tag']) == 13 and item['Tags']['tag'].isdigit():
                        isbn_list.append(item['Tags']['tag'])

            isbn_string = ','.join(isbn_list)
            category = ''
            subcategory1 = ''
            subcategory2 = ''
            warehouseQty = 0
            if item['manufacturerSku'].isdigit():
                warehouseQty = item['manufacturerSku']
            else :
                warehouseQty = 0

            if 'Category' in item:
                categories = item['Category']['fullPathName'].split('/')
                if categories:
                    if len(categories) > 1:
                        category = categories[1]
                    if len(categories) > 2:
                        subcategory1 = categories[2]
                    if len(categories) > 3:
                        subcategory2 = categories[3]

            splitCreateTime = item['createTime'].split('T')
            createTime = splitCreateTime[0]
            splitUpdateTime = item['timeStamp'].split('T')
            updateTime = splitUpdateTime[0]

            cur.execute(
                item_sql, (
                    item['itemID'],
                    desc,
                    title,
                    author,
                    itemShop['qoh'],
                    itemShop['reorderPoint'],
                    itemShop['reorderLevel'],
                    price['amount'],
                    isbn_string,
                    category,
                    subcategory1,
                    subcategory2,
                    item['defaultCost'],
                    warehouseQty,
                    item['systemSku'],
                    createTime,
                    updateTime
                )
            )

        loops = loops - 1
        page = page + 100

    con.commit()
    cur.close()

except requests.exceptions.HTTPError as e:
    print ("Error: ", str(e))
