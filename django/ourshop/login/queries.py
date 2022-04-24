import psycopg2 as pg
from psycopg2.extras import execute_values
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
		cur = conn.cursor()
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


def register_new_user(username,fullname, role, password):
	valid,conn,cur = connect_db()
	if valid:
		new_user = User.objects.create_user(username=username,first_name=fullname, last_name=role, password=password)
		new_user.save()

		if role in ['b','s','d']:
			tablename = role_dict[role]

			# IMP Query 
			cur.execute(
			    SQL("INSERT INTO  {table} (user_id) VALUES (%s)")
			       .format(table=Identifier(tablename)),
			    [new_user.id])

			conn.commit()
			cur.close()
			conn.close()
	else:
		print("Something went wrong: User not registered!")
################################################################		


