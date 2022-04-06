import psycopg2 as pg
from psycopg2.extras import execute_values
import argparse
import csv

parser = argparse.ArgumentParser(description='databse information')
parser.add_argument('--name', dest='db_name', type=str, help='databse name')
parser.add_argument('--user', dest='user', type=str, help='username')
parser.add_argument('--pswd', dest='pswd', type=str, help='password')
parser.add_argument('--host', dest='host', type=str, help='host_address')
parser.add_argument('--port', dest='port', type=str, help='port')
parser.add_argument('--ddl',  dest='ddl_file', type=str, help='path_to_ddl_file')
parser.add_argument('--data', dest='csvpath', type=str, help='path_to_folder_containing_csv_files')
args = parser.parse_args()

####################################################
try:
	# connet to database
	conn = pg.connect(dbname=args.db_name, user=args.user, 
		                  password=args.pswd, host=args.host, port=args.port
		                  )
	cur = conn.cursor()

	# read ddl and install tables
	f = open(args.ddl_file, "r")
	ddl_lines = f.read()
	f.close()
	cur.execute(ddl_lines)

	##########################################################
	# read all csv and insert into tables
	# this is harcoded so that we do not trouble with the foriegn key problem
	# this list is in the same order as of create table ...(ddl)
	table_name = ['auth_user ',
'owner_account ',
'customer ',
'seller ',
'delivery_person ',
'area_allocation',
'address ',
'product ',
'cart ',
'wishlist ',
'orders ',
'category',
'product_category ',
'product_images ',
'tracking ',
'wallet ',
'transactions ',
'review '
]

	# clear all tables
	# whoever have some foriegn key is deleted first
	for table in reversed(table_name):
		query_delete = "DELETE FROM " + table
		cur.execute(query_delete)

	for table in table_name:
		filename = args.csvpath + "/" + table + ".csv"
		query_insert = "INSERT INTO " + table + " VALUES %s"
		values_list = []
		
		# read csv line by line
		with open(filename, 'r') as csvfile:
			reader = csv.reader(csvfile)
			column_name = next(reader)

			for row in reader:
				#  handle NULL carefuly
				thisrow = []
				for x in row:
					if x.strip() == 'NULL' or x.strip() == 'null':
						thisrow.append(None)
					else:
						thisrow.append(x)

				values_list.append(tuple(thisrow))

		# efficiently insert
		execute_values(cur, query_insert, values_list)

	##########################################################
	# cur.execute("select * from venue;")
	# ans = cur.fetchall()
	# print(ans)

	conn.commit()
	cur.close()
	conn.close()

##########################################################
except Exception as e:
	print(e)
	print("there is some problem")
