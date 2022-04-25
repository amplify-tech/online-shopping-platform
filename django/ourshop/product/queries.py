import psycopg2 as pg
from psycopg2.extras import execute_values
from django.contrib.auth.models import User
from psycopg2.sql import SQL,Identifier
from login.queries import connect_db
from datetime import datetime

################################################################	
def showProduct():
	valid,conn,cur = connect_db()
	if valid:
		cur.execute("""SELECT product.product_id,product_name,price,url
			FROM product
			INNER JOIN product_images ON product.product_id=product_images.product_id 
			;""")
		product_list = cur.fetchall()
		cur.close()
		conn.close()
		return product_list
	else:
		print("Something went wrong!")
		return []

def toSellerId(userid):
	valid,conn,cur = connect_db()
	if valid:
		cur.execute("SELECT seller_id FROM seller where user_id = %s", [userid])
		seller_id = cur.fetchone()
		cur.close()
		conn.close()
		if seller_id is None:
			return None
		else:
			return seller_id[0]
	else:
		print("Something went wrong!")
		return None

def addProduct(seller_id,product_name, product_price, product_detail,images_url_list):
	valid,conn,cur = connect_db()
	if valid:
		current = datetime.now()
		cur.execute("INSERT INTO product (product_name,price,seller_id,details,timestmp) VALUES (%s,%s,%s,%s,%s) RETURNING product_id;",
					[product_name, product_price, seller_id,product_detail,current])
		
		this_product_id = cur.fetchone()[0]

		for img_url in images_url_list:
			cur.execute("INSERT INTO product_images (product_id,url) VALUES (%s,%s);",
						[this_product_id, img_url])

		conn.commit()
		cur.close()
		conn.close()
		return True
	else:
		print("Something went wrong!")
		return False

def getProduct(product_id):
	valid,conn,cur = connect_db()
	if valid:
		cur.execute("SELECT * FROM product where product_id = %s", [product_id])
		product_data = cur.fetchone()
		cur.execute("SELECT url FROM product_images where product_id = %s", [product_id])
		product_photo = cur.fetchall()
		cur.close()
		conn.close()
		return product_data,product_photo
	else:
		print("Something went wrong!")
		return None,None
