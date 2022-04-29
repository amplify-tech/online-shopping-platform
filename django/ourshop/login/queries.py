import psycopg2 as pg
from psycopg2.extras import execute_values,NamedTupleCursor
from django.contrib.auth.models import User
from psycopg2.sql import SQL,Identifier

# role code to table name mapping
role_dict = {
	'o':"owner",
	'a':"admin",
	'b':"customer",
	's':"seller",
	'd': "delivery_person"
}

def connect_db():
	try:
		# connect to database
		conn = pg.connect(dbname='ourshop_db1', user='postgres', 
			             password='ak123987', host='localhost', port='5432'
			             )
		cur = conn.cursor(cursor_factory=NamedTupleCursor)
		return True, conn, cur


	except Exception as e:
		print(e)
		print("There is some problem in connecting to DATABASE")
		return False, conn, cur

################################################################		
# for loading testing
def clear_dbdata():
	valid,conn,cur = connect_db()
	if valid:
		cur.execute("DELETE FROM delivery_person;")
		cur.execute("DELETE FROM seller;")
		cur.execute("DELETE FROM customer;")
		conn.commit()
		cur.close()
		conn.close()
		User.objects.exclude(id__in=[0,1]).delete()
	else:
		print("Something went wrong : DATABASE unchanged!")

def register_owner():
	valid,conn,cur = connect_db()
	if valid:
		if User.objects.filter(id=0).count() ==0:
			# register owner and admin (o,a) special_id
			new_user = User.objects.create_user(id=0,username="9999999999o",first_name="flipkart owner", last_name="o", password="jgQ#k%(gd57j")
			new_user.save()
			new_user = User.objects.create_user(id=-1,username="9999999999a",first_name="flipkart admin", last_name="a", password="jgQ#k%(gd57j")
			new_user.save()
			print("owner registered")
			# other initialisation
			# owner account
			cur.execute("INSERT INTO owner_account (owner_id,user_id) VALUES (0,0);")
			# wallet
			cur.execute("INSERT INTO wallet (user_id, balance) VALUES (0,0);")
			conn.commit()

		# else:
		# 	print("owner already exist")
		cur.close()
		conn.close()
	else:
		print("Something went wrong: User not registered!")

def register_new_user(username,fullname, role, password,pincode):
	valid,conn,cur = connect_db()
	if valid:
		# django user
		new_user = User.objects.create_user(username=username,first_name=fullname, last_name=role, password=password)
		new_user.save()

		# our user table
		if   role=='s':
			cur.execute("INSERT INTO seller (user_id) VALUES (%s)", [new_user.id])
		
		elif role=='d':
			cur.execute("INSERT INTO delivery_person (user_id,pincode) VALUES (%s,%s)", [new_user.id,pincode])

		elif role=='b':
			cur.execute("INSERT INTO customer (user_id) VALUES (%s) RETURNING customer_id", [new_user.id])
			customer_id = cur.fetchone()[0]
			
			# cart 
			cur.execute("INSERT INTO cart (customer_id) VALUES (%s);",
						[customer_id])
			# wishlist
			cur.execute("INSERT INTO wishlist (customer_id) VALUES (%s);",
						[customer_id])


		# wallet for all
		cur.execute("INSERT INTO wallet (user_id, balance) VALUES (%s,%s);",
					[new_user.id, 0])

		conn.commit()
		cur.close()
		conn.close()
	else:
		print("Something went wrong: User not registered!")

################################################################		
# area allocation
def savePincode(pincode_list):
	valid,conn,cur = connect_db()
	if valid:
		query_insert = "INSERT INTO area_allocation VALUES %s  ON CONFLICT DO NOTHING" 		
		execute_values(cur, query_insert, pincode_list)
		conn.commit()
		cur.close()
		conn.close()
		return True
	else:
		print("Something went wrong!")
		return False



