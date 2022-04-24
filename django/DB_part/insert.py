import psycopg2 as pg
from psycopg2.extras import execute_values
import csv

ddl_file = 'ourshop.ddl'
csv_folder = 'csv/'

####################################################
try:
	# connect to database
	conn = pg.connect(dbname='ourshop_db1', user='postgres', 
		                  password='ak123987', host='localhost', port='5432'
		                  )
	cur = conn.cursor()

	# read ddl and install tables
	f = open(ddl_file, "r")
	ddl_lines = f.read()
	f.close()
	cur.execute(ddl_lines)

	##########################################################
	# read all csv and insert into tables
	# this is harcoded so that we do not trouble with the foriegn key problem
	# this list is in the same order as of create table ...(ddl)
	table_name = [
		'owner_account'
		,'customer'
		,'seller'
		,'delivery_person'
		,'area_allocation'
		,'address'
		,'product'
		,'cart'
		,'wishlist'
		,'orders'
		,'category'
		,'product_category'
		# ,'product_images'
		# ,'tracking'
		,'wallet'
		,'transactions'
		,'review'
	]

	# clear all tables
	# whoever have some foriegn key is deleted first
	for table in reversed(table_name):
		query_delete = "DELETE FROM " + table
		cur.execute(query_delete)

	for table in table_name:
		filename = csv_folder + table + ".csv"
		query_insert = "INSERT INTO " + table + " VALUES %s" 
		values_list = []
		
		# read csv line by line
		with open(filename, 'r') as csvfile:
			print(filename)
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
