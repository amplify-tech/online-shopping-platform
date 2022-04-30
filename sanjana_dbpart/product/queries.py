import psycopg2 as pg
from psycopg2.extras import execute_values
from django.contrib.auth.models import User
from psycopg2.sql import SQL,Identifier
from login.queries import connect_db
from datetime import datetime
from decimal import *

################################################################   
rate_owner    = Decimal(0.05)
rate_seller   = Decimal(0.85)
rate_delivery = Decimal(0.10)

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
		try:
			cur.execute("SELECT customer_id FROM customer where user_id = %s", [userid])
			row = cur.fetchone()
			if row is not None:
				cur.execute("""DELETE FROM address where customer_id= %s and address_id= %s;""",
					[row.customer_id, address_id])
				conn.commit()
			
			cur.close()
			conn.close()
			return True
		except:
			return False
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

def getWishlist(userid):
	valid,conn,cur = connect_db()
	if valid:
		cur.execute("""SELECT product.product_id,product_name,price, url
				FROM customer
				INNER JOIN wishlist ON wishlist.customer_id = customer.customer_id
				INNER JOIN wishlist_product ON wishlist_product.wishlist_id = wishlist.wishlist_id
				INNER JOIN product ON product.product_id = wishlist_product.product_id
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

def deleteFromWishlist(userid,product_id):
	valid,conn,cur = connect_db()
	if valid:
		cur.execute("""DELETE FROM wishlist_product
				WHERE product_id = %s AND
				wishlist_id IN 
					( SELECT wishlist_id from wishlist
					INNER JOIN customer ON customer.customer_id=wishlist.customer_id
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
			return msz

		current = datetime.now()
		#  move prodcuts from cart to order table
		cur.execute("""INSERT INTO orders (product_id,customer_id,delivery_person_id,quantity,address_id,timestmp)
			SELECT product_id,customer.customer_id,%s,quantity,%s,%s
			FROM customer
			INNER JOIN cart ON cart.customer_id = customer.customer_id
			INNER JOIN cart_product ON cart_product.cart_id = cart.cart_id
			where user_id = %s
			RETURNING order_id;
			""",
			[row.delivery_person_id,address_id,current,userid])

		rows = cur.fetchall()
		orderid_list = tuple([x.order_id for x in rows])

		# emptying cart
		cur.execute("""DELETE FROM cart_product
			where cart_id in (
				SELECT cart_id
				FROM cart
				INNER JOIN customer ON cart.customer_id = customer.customer_id
				where user_id = %s);"""
			,[userid])
		

		#  distribute money
		cur.execute("""SELECT delivery_person_id,seller_id,price*quantity as total_price
			FROM orders
			INNER JOIN product ON product.product_id = orders.product_id
			where order_id in %s;""",
			[orderid_list])
		ls = cur.fetchall()

		for row in ls:
			# for each prodcut deduct/add money
			amount_customer = row.total_price 
			amount_seller   = row.total_price * rate_seller
			amount_del      = row.total_price * rate_delivery
			amount_owner    = row.total_price * rate_owner

			cur.execute("""UPDATE wallet SET balance = balance - %s
						where user_id= %s 
						RETURNING wallet.wallet_id;""",
						[amount_customer, userid])
			cwid = cur.fetchone()[0]

			cur.execute("""UPDATE wallet SET balance = balance + %s
						WHERE user_id IN 
						(SELECT user_id from seller where seller_id = %s)
						RETURNING wallet.wallet_id;""",
						[amount_seller, row.seller_id])
			swid = cur.fetchone()[0]

			cur.execute("""UPDATE wallet SET balance = balance + %s
						WHERE user_id IN 
						(SELECT user_id from delivery_person where delivery_person_id = %s)
						RETURNING wallet.wallet_id;""",
						[amount_del, row.delivery_person_id])
			dwid = cur.fetchone()[0]

			cur.execute("""UPDATE wallet SET balance = balance + %s
						where user_id= %s
						RETURNING wallet.wallet_id;""",
						[amount_owner, 0])
			owid = cur.fetchone()[0]

			#  handle   3 transactions
			current = datetime.now()
			cur.execute("INSERT INTO transactions (wallet_id_send,wallet_id_got,amount,timestmp) VALUES (%s,%s,%s,%s);",
						[cwid, swid, amount_seller,current])

			cur.execute("INSERT INTO transactions (wallet_id_send,wallet_id_got,amount,timestmp) VALUES (%s,%s,%s,%s);",
						[cwid, dwid, amount_del,current])

			cur.execute("INSERT INTO transactions (wallet_id_send,wallet_id_got,amount,timestmp) VALUES (%s,%s,%s,%s);",
						[cwid, owid, amount_owner,current])
			

		# add prodcut/order for tracking
		for order_id in orderid_list:
			cur.execute("INSERT INTO tracking (order_id,pincode,status,updated_by,timestmp) VALUES (%s,%s,%s,%s,%s);",
						[order_id, "999999", "Ordered",0,current])

		conn.commit()
		msz = "Order Placed!"
		cur.close()
		conn.close()
		return msz
	else:
		msz = "Something went wrong!"
		return msz

# history
def getOrderHistory(userid, role):
	valid,conn,cur = connect_db()
	if valid:
		history_data = None
		if role == 'b':
			cur.execute("""SELECT orders.order_id, url,product_name,price,tracking.pincode,status,tracking.timestmp as track_time,quantity, orders.timestmp as order_time 
				FROM tracking 
				INNER JOIN orders ON tracking.order_id=orders.order_id
				INNER JOIN product ON product.product_id=orders.product_id
				INNER JOIN product_images ON product_images.product_id=product.product_id
				INNER JOIN customer ON customer.customer_id=orders.customer_id
				where default_img = True 
					AND customer.user_id = %s
				ORDER BY orders.order_id DESC,tracking.timestmp DESC;""",
				[userid])
			history_data = cur.fetchall()

		elif role == 's':
			cur.execute("""SELECT orders.order_id, url,product_name,price,tracking.pincode,status,tracking.timestmp as track_time,quantity, orders.timestmp as order_time 
				FROM tracking 
				INNER JOIN orders ON tracking.order_id=orders.order_id
				INNER JOIN product ON product.product_id=orders.product_id
				INNER JOIN product_images ON product_images.product_id=product.product_id
				INNER JOIN seller ON seller.seller_id=product.seller_id
				where default_img = True 
					AND seller.user_id = %s
				ORDER BY orders.order_id DESC,tracking.timestmp DESC;""",
				[userid])
			history_data = cur.fetchall()

		elif role == 'd':
			cur.execute("""SELECT orders.order_id, url,product_name,price,tracking.pincode,status,tracking.timestmp as track_time,quantity, orders.timestmp as order_time 
				FROM tracking 
				INNER JOIN orders ON tracking.order_id=orders.order_id
				INNER JOIN product ON product.product_id=orders.product_id
				INNER JOIN product_images ON product_images.product_id=product.product_id
				INNER JOIN delivery_person ON delivery_person.delivery_person_id=orders.delivery_person_id
				where default_img = True 
					AND delivery_person.user_id = %s
				ORDER BY orders.order_id DESC,tracking.timestmp DESC;""",
				[userid])
			history_data = cur.fetchall()

		cur.close()
		conn.close()
		return history_data
	else:
		print("Something went wrong!")
		return None

def updateStatus(userid,role,order_id,status,pincode):
	valid,conn,cur = connect_db()
	if valid:
		current = datetime.now()
		cur.execute("INSERT INTO tracking (order_id,pincode,status,updated_by,timestmp) VALUES (%s,%s,%s,%s,%s);",
					[order_id, pincode,status,userid,current])
		conn.commit()
		cur.close()
		conn.close()
		return "Status Updated"
	else:
		return "Something went wrong!"

		