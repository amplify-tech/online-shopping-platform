import psycopg2 as pg
from psycopg2.extras import execute_values
from django.contrib.auth.models import User
from psycopg2.sql import SQL,Identifier
from login.queries import connect_db
from datetime import datetime


################################################################   
rate_owner    = 0.05
rate_seller   = 0.85
rate_delivery = 0.10

################################################################    
def showProduct():
	valid,conn,cur = connect_db()
	if valid:
		cur.execute("""SELECT product.product_id,product_name,price,url
			FROM product
			INNER JOIN product_images ON product.product_id=product_images.product_id 
			where default_img = True
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

		is_default = True
		for img_url in images_url_list:
			cur.execute("INSERT INTO product_images (product_id,url,default_img) VALUES (%s,%s,%s);",
						[this_product_id, img_url,is_default])
			is_default = False

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


def getWallet(userid):
	valid,conn,cur = connect_db()
	if valid:
		cur.execute("SELECT balance FROM wallet where user_id = %s", [userid])
		wallet_data = cur.fetchone()
		cur.close()
		conn.close()
		return wallet_data
	else:
		print("Something went wrong!")
		return None

def getAddress(userid):
	valid,conn,cur = connect_db()
	if valid:
		cur.execute("""SELECT address_id,state,city,street,pincode 
			FROM address 
			INNER JOIN customer ON address.customer_id = customer.customer_id
			where user_id = %s""",
			[userid])
		address_data = cur.fetchall()
		cur.close()
		conn.close()
		return address_data
	else:
		print("Something went wrong!")
		return None

def addWalletMoney(userid,amount):
	valid,conn,cur = connect_db()
	if valid:
		cur.execute("""UPDATE wallet SET balance = balance + %s
					where user_id= %s""",
					[amount, userid])
		conn.commit()
		cur.close()
		conn.close()
		return True
	else:
		print("Something went wrong!")
		return False


def addaddressDB(userid, state, city, street,pincode):
	msz = "ok"
	valid,conn,cur = connect_db()
	if valid:
		cur.execute("SELECT customer_id FROM customer where user_id = %s", [userid])
		customer_id = cur.fetchone().customer_id

		cur.execute("SELECT pincode FROM area_allocation where pincode = %s", [pincode])
		row = cur.fetchone()

		if row is None:
			msz = "This area (pincode = {}) is not deliverable!".format(pincode)
		else:
			cur.execute("""INSERT INTO address (state,city,street,pincode,customer_id) VALUES (%s,%s,%s,%s,%s);""",
				[state,city,street,pincode,customer_id])
			conn.commit()
			msz = "Address Added"
		
		cur.close()
		conn.close()
		return msz
	else:
		msz = "Something went wrong : Address not added!!"
		return msz

def deleteaddressDB(userid, address_id):
	valid,conn,cur = connect_db()
	if valid:
		cur.execute("SELECT customer_id FROM customer where user_id = %s", [userid])
		row = cur.fetchone()
		if row is not None:
			cur.execute("""DELETE FROM address where customer_id= %s and address_id= %s;""",
				[row.customer_id, address_id])
			conn.commit()
		
		cur.close()
		conn.close()
		return True
	else:
		print("Something went wrong!")
		return False

def addtoCart(userid,product_id):
	valid,conn,cur = connect_db()
	if valid:
		cur.execute("""SELECT cart_id FROM cart 
				INNER JOIN customer ON customer.customer_id=cart.customer_id
				where user_id = %s""",
				[userid])
		row = cur.fetchone()
		result=False
		if row is not None:
			cur.execute("""DO $$ BEGIN
				IF EXISTS (SELECT FROM product WHERE product_id = %s) THEN
				INSERT INTO cart_product (cart_id,product_id,quantity) VALUES (%s,%s,1) ON CONFLICT DO NOTHING;
				END IF;
				END;$$""",
				[product_id, row.cart_id,product_id])
			conn.commit()
			result=True
		cur.close()
		conn.close()
		return result
	else:
		print("Something went wrong!")
		return False

def addtoWish(userid,product_id):
	valid,conn,cur = connect_db()
	if valid:
		cur.execute("""SELECT wishlist_id FROM wishlist 
				INNER JOIN customer ON customer.customer_id=wishlist.customer_id
				where user_id = %s""",
				[userid])
		row = cur.fetchone()
		result=False
		if row is not None:
			cur.execute("""DO $$ BEGIN
				IF EXISTS (SELECT FROM product WHERE product_id = %s) THEN
				INSERT INTO wishlist_product (wishlist_id,product_id) VALUES (%s,%s) ON CONFLICT DO NOTHING;
				END IF;
				END;$$""",
				[product_id, row.wishlist_id,product_id])
			conn.commit()
			result=True
		cur.close()
		conn.close()
		return result
	else:
		print("Something went wrong!")
		return False

def getCart(userid):
	valid,conn,cur = connect_db()
	if valid:
		cur.execute("""SELECT product.product_id,product_name,price,quantity,price*quantity as total_price, url
				FROM customer
				INNER JOIN cart ON cart.customer_id = customer.customer_id
				INNER JOIN cart_product ON cart_product.cart_id = cart.cart_id
				INNER JOIN product ON product.product_id = cart_product.product_id
				INNER JOIN product_images ON product_images.product_id = product.product_id
				where customer.user_id = %s AND default_img = True""",
			[userid])
		product_data = cur.fetchall()
		cur.close()
		conn.close()
		return product_data
	else:
		print("Something went wrong!")
		return None


def deleteFromCart(userid,product_id):
	valid,conn,cur = connect_db()
	if valid:
		cur.execute("""DELETE FROM cart_product
				WHERE product_id = %s AND
				cart_id IN 
					( SELECT cart_id from cart
					INNER JOIN customer ON customer.customer_id=cart.customer_id
					where user_id = %s
					);""",
				[product_id, userid])
		conn.commit()
		cur.close()
		conn.close()
		return True
	else:
		print("Something went wrong!")
		return False

def updateQuantity(userid,product_id,quantity): 
	valid,conn,cur = connect_db()
	if valid:
		cur.execute("""UPDATE cart_product SET quantity = %s
				WHERE product_id = %s AND
				cart_id IN 
					( SELECT cart_id from cart
					INNER JOIN customer ON customer.customer_id=cart.customer_id
					where user_id = %s
					);""",
					[quantity,product_id, userid])
		conn.commit()
		cur.close()
		conn.close()
		return True
	else:
		print("Something went wrong!")
		return False


def payNow(userid, address_id):
	msz = ""
	valid,conn,cur = connect_db()
	if valid:
		cur.execute("""SELECT delivery_person_id
				FROM delivery_person
				INNER JOIN address ON address.pincode = delivery_person.pincode
				where address_id = %s 
				ORDER BY RANDOM()
				LIMIT 1""", [address_id])
		row = cur.fetchone()

		if row is None:
			msz = "Something went wrong!"
		else:
			current = datetime.now()
			#  move prodcuts from cart to order table
			cur.execute("""INSERT INTO orders (product_id,customer_id,delivery_person_id,quantity,address_id,timestmp)
				SELECT product_id,customer.customer_id,%s,quantity,%s,%s
				FROM customer
				INNER JOIN cart ON cart.customer_id = customer.customer_id
				INNER JOIN cart_product ON cart_product.cart_id = cart.cart_id
				where user_id = %s;
				""",
				[row.delivery_person_id,address_id,current,userid])

			# emptying cart
			cur.execute("""DELETE FROM cart_product
				where cart_id in (
					SELECT cart_id
					FROM cart
					INNER JOIN customer ON cart.customer_id = customer.customer_id
					where user_id = %s);"""
				,[userid])
			
			# deduct money

			conn.commit()
			msz = "Order Placed!"
		cur.close()
		conn.close()
		return msz
	else:
		msz = "Something went wrong!"
		return msz


