import requests
import json
import sqlite3
from datetime import date
from db import db_connect

class Dates:
  def __init__(self, period, offset):
    self.period = period
    self.offset = offset

querySet = [Dates("threeMonth", -3), Dates("sixMonth", -6), Dates("twelveMonth", -12)]

try:
    con = db_connect()
    cur = con.cursor()

    for period in querySet:
        group_sql = "SELECT itemID, SUM(count) FROM sales WHERE time BETWEEN DATE('" + str(date.today()) + "', '" + str(period.offset) + " month') AND DATE('" + str(date.today()) + "') GROUP BY itemID"
        update_group_sql = "UPDATE inventory SET {p} = {s} WHERE itemID = {itmID}"

        cur.execute(
            group_sql
        )
        info = cur.fetchall()
        for i in info:
            try:
                cur.execute(
                    update_group_sql.format(p=period.period,s=i[1], itmID=i[0])
                )
            except sqlite3.Error as err:
                print('ERROR INSERT sales_sum: ', err)

    con.commit()
    con.close()

except sqlite3.Error as error:
    print ("ERROR SELECT from sales ", error)