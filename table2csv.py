import os
import glob
import re
import csv
from bs4 import BeautifulSoup

#################################################
#  Constants and Methods
#################################################

TRANS_DICT = { 
        "." : ""
  ,     "," : ""
  ,     "/" : ""
  ,     "*" : ""
  ,     "'" : ""
  ,     "%" : ""
  ,     "+" : ""
  ,     "(" : ""
  ,     ")" : ""
  ,     " " : ""
  ,     ":" : ""
  ,     "<" : ""
  ,     ">" : ""
}

TRANS_TBL = str.maketrans(TRANS_DICT)

# TODO:Modify this method according to the style of html you want to parse.
def getCSVName(table):
  return table["id"]

def getNewRowspanColDict(row, row_num):
  rowspan_col_index_list = []
  rownum_affected_rowspan = 0
  col_index = 1
  for cell in row.findAll(["th","td"]):
    if "colspan" in str(cell):
      col_index = col_index + int(cell["colspan"]) - 1
    if "rowspan" in str(cell):
      rowspan_col_index_list.append(col_index)
      rownum_affected_rowspan = row_num + int(cell["rowspan"]) - 1
    col_index += 1
  return {rownum_affected_rowspan : rowspan_col_index_list}

def reflectRowspan(csv_row, row_num, rowspan_col_dict):
  if row_num in rowspan_col_dict:
    for rowspan_col_index in rowspan_col_dict[row_num]:
      csv_row.insert(rowspan_col_index - 1 ,"")
  return csv_row

def getTblData(row):
  csv_row = []
  for cell in row.findAll(["th","td"]):
    cell_data = cell.get_text().replace("\n" , "").replace("\xa0", "")
    csv_row.append(cell_data.translate(TRANS_TBL))
    if "colspan" in str(cell):
      for num in range(int(cell["colspan"]) - 1):
        csv_row.append("")
  return csv_row

#################################################
# Main processing starts here.
#################################################

os.makedirs("./csv", exist_ok=True)

html_files = glob.glob("./*.html")
csv_name_list = []
for html_file in html_files:
  html = open(html_file, "r")
  soup = BeautifulSoup(html, "html.parser")
  tables = soup.find_all("table")
  for table in tables:
    rows = table.find_all("tr")
    csv_name = getCSVName(table)
    with open( "./csv/" + csv_name + ".csv", "a", encoding="utf-8", newline="") as csv_file:
      writer = csv.writer(csv_file)
      row_num = 1
      rowspan_col_dict = {}
      for row in rows:
        if row.findAll("th") and csv_name in csv_name_list:
          row_num += 1
          continue
        csv_row = getTblData(row)
        if row.findAll("th"):
          csv_row = reflectRowspan(csv_row, row_num, rowspan_col_dict)
          rowspan_col_dict.update(getNewRowspanColDict(row, row_num))
        if csv_row:
          writer.writerow(csv_row)
        row_num += 1
    csv_file.close()
    csv_name_list.append(csv_name)