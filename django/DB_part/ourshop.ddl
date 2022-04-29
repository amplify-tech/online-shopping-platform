DROP TABLE IF EXISTS review;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS wallet;
DROP TABLE IF EXISTS tracking;
DROP TABLE IF EXISTS product_images;
DROP TABLE IF EXISTS product_category;
DROP TABLE IF EXISTS category;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS wishlist_product;
DROP TABLE IF EXISTS wishlist;
DROP TABLE IF EXISTS cart_product;
DROP TABLE IF EXISTS cart;
DROP TABLE IF EXISTS product;
DROP TABLE IF EXISTS address;
DROP TABLE IF EXISTS delivery_person;
DROP TABLE IF EXISTS area_allocation;
DROP TABLE IF EXISTS seller;
DROP TABLE IF EXISTS customer;
DROP TABLE IF EXISTS owner_account;

-------------------------------------------
-- django user  -- inbuilt 
-- CREATE TABLE auth_user (
--     id INT NOT NULL ,          -- user_id
--     password VARCHAR(128)   NOT NULL,
--     username VARCHAR(150)   NOT NULL,
--     first_name VARCHAR(30)   NOT NULL,
--     last_name VARCHAR(150)   NOT NULL,
--     email VARCHAR(254)   NOT NULL,
--     Primary Key(id)
-- );
-------------------------------------------
CREATE TABLE owner_account (
    owner_id INT NOT NULL,
    user_id INT NOT NULL,
    Primary Key(owner_id),
    FOREIGN key(user_id) references auth_user(id) on delete set NULL
);

CREATE TABLE customer (
    customer_id SERIAL NOT NULL,
    user_id INT NOT NULL,
    Primary Key(customer_id),
    FOREIGN key(user_id) references auth_user(id) on delete set NULL
);

CREATE TABLE seller (
    seller_id SERIAL NOT NULL,
    user_id INT NOT NULL,
    Primary Key(seller_id),
    FOREIGN key(user_id) references auth_user(id) on delete set NULL
);

-- area alocation 
CREATE TABLE area_allocation(
    pincode INT NOT NULL,
    Primary Key(pincode)
);

CREATE TABLE delivery_person (
    delivery_person_id SERIAL NOT NULL,
    user_id INT NOT NULL,
    pincode INT NOT NULL,
    Primary Key(delivery_person_id),
    FOREIGN key(user_id) references auth_user(id) on delete set NULL,
    FOREIGN key(pincode) references area_allocation(pincode) on delete set NULL
);


-- only for customer adress
CREATE TABLE address (
    address_id SERIAL NOT NULL,
    state VARCHAR NOT NULL,
    city VARCHAR NOT NULL,
    street VARCHAR NOT NULL,
    pincode INT NOT NULL,
    customer_id INT NOT NULL,
    Primary Key(address_id),
    FOREIGN key(customer_id ) references customer on delete set NULL
);
-------------------------------------------
CREATE TABLE product (
    product_id SERIAL NOT NULL,
    product_name TEXT NOT NULL,
    price decimal(10,2) NOT NULL,
    seller_id INT NOT NULL,
    details VARCHAR NOT NULL,
    timestmp TIMESTAMP,
    Primary Key(product_id),
    FOREIGN key(seller_id) references seller on delete set NULL
);

CREATE TABLE cart (
    cart_id SERIAL NOT NULL,
    customer_id INT NOT NULL,
    Primary Key(cart_id),
    FOREIGN key(customer_id) references customer on delete set NULL
);

CREATE TABLE cart_product (
    cart_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    Primary Key(cart_id,product_id),
    FOREIGN key(cart_id) references cart on delete set NULL,
    FOREIGN key(product_id) references product on delete set NULL
);

CREATE TABLE wishlist (
    wishlist_id SERIAL NOT NULL,
    customer_id INT NOT NULL,
    Primary Key(wishlist_id),
    FOREIGN key(customer_id) references customer on delete set NULL
);

CREATE TABLE wishlist_product (
    wishlist_id INT NOT NULL,
    product_id INT NOT NULL,
    Primary Key(wishlist_id,product_id),
    FOREIGN key(wishlist_id) references wishlist on delete set NULL,
    FOREIGN key(product_id) references product on delete set NULL
);

CREATE TABLE orders (
    order_id SERIAL NOT NULL,
    product_id INT NOT NULL,
    customer_id INT NOT NULL,
    delivery_person_id INT NOT NULL,
    quantity INT NOT NULL,
    address_id INT NOT NULL,
    timestmp TIMESTAMP,
    Primary Key(order_id),
    FOREIGN key(customer_id) references customer on delete set NULL,
    FOREIGN key(product_id) references product on delete set NULL,
    FOREIGN key(delivery_person_id) references delivery_person on delete set NULL,
    FOREIGN key(address_id) references address on delete set NULL
);

CREATE TABLE category(
    category_id SERIAL NOT NULL,
    category_name VARCHAR NOT NULL,
    Primary Key(category_id)
);

CREATE TABLE product_category (
    product_id INT NOT NULL,
    category_id INT NOT NULL,
    PRIMARY KEY (product_id, category_id),
    FOREIGN key(product_id) references product on delete set NULL,
    FOREIGN key(category_id) references category on delete set NULL
);

CREATE TABLE product_images (
    image_id SERIAL NOT NULL,
    product_id INT NOT NULL,
    url VARCHAR NOT NULL,
    default_img BOOLEAN NOT NULL,
    PRIMARY KEY (image_id),
    FOREIGN key(product_id) references product on delete set NULL
);

----------------------------------
CREATE TABLE tracking (
    tracking_id SERIAL NOT NULL,
    order_id INT NOT NULL,
    pincode INT NOT NULL,
    status VARCHAR,
    updated_by INT NOT NULL,
    timestmp TIMESTAMP,
    Primary key(tracking_id),
    FOREIGN KEY(order_id) references orders on delete set null,
    FOREIGN KEY(updated_by) references auth_user(id) on delete set null
);

----------------------------------
CREATE TABLE wallet (
    wallet_id SERIAL NOT NULL,
    user_id INT NOT NULL,
    balance decimal(10,2) NOT NULL,
    Primary key(wallet_id),
    FOREIGN KEY(user_id) references auth_user(id) on delete set null
);

CREATE TABLE transactions (
    transaction_id SERIAL NOT NULL,
    wallet_id_send INT NOT NULL,
    wallet_id_got INT NOT NULL,
    amount decimal(10,2) NOT NULL,
    timestmp TIMESTAMP,
    Primary key(transaction_id),
    FOREIGN KEY(wallet_id_send) references wallet(wallet_id) on delete set null,
    FOREIGN KEY(wallet_id_got) references wallet(wallet_id) on delete set null
);

----------------------------------
CREATE TABLE review (
    review_id SERIAL NOT NULL,
    customer_id INT NOT NULL,
    product_id INT NOT NULL,
    msz VARCHAR,
    rating INT CHECK(rating between 1 and 5) NOT NULL,
    timestmp TIMESTAMP,
    Primary key(review_id),
    FOREIGN KEY(customer_id) references customer on delete set null,
    FOREIGN KEY(product_id) references product on delete set null
);

----------------------------------

