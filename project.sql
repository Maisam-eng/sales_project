SET FOREIGN_KEY_CHECKS = 0;

  -- drop database cosmetics_store_db;

-- Create the database
CREATE DATABASE IF NOT EXISTS cosmetics_store_db;
USE cosmetics_store_db;

-- Supplier table
CREATE TABLE Supplier (
    supplier_id INT PRIMARY KEY,
    email VARCHAR(255),
    company_name VARCHAR(255));

-- Branch table
CREATE TABLE Branch (
    branch_id INT PRIMARY KEY,
    b_name VARCHAR(255),
    location VARCHAR(255));

CREATE TABLE Branch_Contact (
    branch_id INT,
    contact_type VARCHAR(50),  -- e.g., Phone, Email
    contact_value VARCHAR(255),
    PRIMARY KEY (branch_id, contact_type, contact_value),
    FOREIGN KEY (branch_id) REFERENCES Branch(branch_id)
);


-- Product table
CREATE TABLE Product (
    product_id INT PRIMARY KEY,
    pname VARCHAR(255),
    price DECIMAL(10,2),
    num_of_purchases INT,
    is_trending BOOLEAN
);

-- Subtypes of Product
CREATE TABLE Fragrance (
    product_id INT PRIMARY KEY,
    is_alcohol_free BOOLEAN,
    fragrance_type VARCHAR(100),
    size_ml DECIMAL(6,2),
    lasting_hours DECIMAL(4,2),
    concentration VARCHAR(50),
    FOREIGN KEY (product_id) REFERENCES Product(product_id) on delete cascade
);
CREATE TABLE Fragrance_Season (
    product_id INT,
    season VARCHAR(50),
    PRIMARY KEY (product_id, season),
    FOREIGN KEY (product_id) REFERENCES Fragrance(product_id) on delete cascade
);

CREATE TABLE Fragrance_Time (
    product_id INT,
    recommended_time VARCHAR(50),
    PRIMARY KEY (product_id, recommended_time),
    FOREIGN KEY (product_id) REFERENCES Fragrance(product_id) on delete cascade
);

CREATE TABLE Fragrance_Scent_Note (
    product_id INT,
    scent_note VARCHAR(100),
    PRIMARY KEY (product_id, scent_note),
    FOREIGN KEY (product_id) REFERENCES Fragrance(product_id) on delete cascade
);

CREATE TABLE Fragrance_Gender (
    product_id INT,
    gender VARCHAR(20),
    PRIMARY KEY (product_id, gender),
    FOREIGN KEY (product_id) REFERENCES Fragrance(product_id) on delete cascade
);

CREATE TABLE Skincare_Product (
    product_id INT PRIMARY KEY,
    natural_or_organic BOOLEAN,
    type VARCHAR(100),
    fragrance_free BOOLEAN,
    packaging VARCHAR(100),
    FOREIGN KEY (product_id) REFERENCES Product(product_id) on delete cascade
);
CREATE TABLE Skincare_Skin_Type (
    product_id INT,
    skin_type VARCHAR(50),
    PRIMARY KEY (product_id, skin_type),
    FOREIGN KEY (product_id) REFERENCES Skincare_Product(product_id) on delete cascade
);

CREATE TABLE Skincare_Ingredient (
    product_id INT,
    ingredient VARCHAR(100),
    PRIMARY KEY (product_id, ingredient),
    FOREIGN KEY (product_id) REFERENCES Skincare_Product(product_id) on delete cascade
);

CREATE TABLE Hair_Product (
    product_id INT PRIMARY KEY,
    natural_or_organic BOOLEAN,
    fragrance_free BOOLEAN,
    sulfate_free BOOLEAN,
    packaging VARCHAR(100),
    FOREIGN KEY (product_id) REFERENCES Product(product_id) on delete cascade
);
CREATE TABLE Hair_Hair_Type (
    product_id INT,
    hair_type VARCHAR(50),
    PRIMARY KEY (product_id, hair_type),
    FOREIGN KEY (product_id) REFERENCES Hair_Product(product_id) on delete cascade
);

CREATE TABLE Hair_Scalp_Type (
    product_id INT,
    scalp_type VARCHAR(50),
    PRIMARY KEY (product_id, scalp_type),
    FOREIGN KEY (product_id) REFERENCES Hair_Product(product_id) on delete cascade
);

CREATE TABLE Hair_Ingredient (
    product_id INT,
    ingredient VARCHAR(100),
    PRIMARY KEY (product_id, ingredient),
    FOREIGN KEY (product_id) REFERENCES Hair_Product(product_id) on delete cascade
);

-- Purchase Order
CREATE TABLE Purchase_Order (
    po_id INT PRIMARY KEY,
    supplier_id INT,
    branch_id INT,
    order_date DATE,
    FOREIGN KEY (supplier_id) REFERENCES Supplier(supplier_id),
    FOREIGN KEY (branch_id) REFERENCES Branch(branch_id)
);

-- PO_Product: Order-Product junction
CREATE TABLE PO_Product (
    po_id INT,
    product_id INT,
    quantity INT,
    PRIMARY KEY (po_id, product_id),
    FOREIGN KEY (po_id) REFERENCES Purchase_Order(po_id),
    FOREIGN KEY (product_id) REFERENCES Product(product_id) on delete cascade
);

-- Customer table
CREATE TABLE Customer (
    customer_id INT PRIMARY KEY,
    cname VARCHAR(255),
    gender VARCHAR(10),
    date_of_birth DATE
);

CREATE TABLE Customer_Email (
    email_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    email VARCHAR(255),
    is_primary BOOLEAN,
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
);
CREATE TABLE Customer_Phone (
    phone_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    phone_number VARCHAR(20),
    type VARCHAR(50),
    is_primary BOOLEAN,
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
);
CREATE TABLE Customer_Address (
    address_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    address VARCHAR(255),
    address_type VARCHAR(50),
    is_primary BOOLEAN,
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
);

-- Shopping Cart
CREATE TABLE Shopping_Cart (
    cart_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT,
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
);
ALTER TABLE Shopping_Cart
ADD COLUMN cart_status VARCHAR(20) DEFAULT 'Active';
ALTER TABLE Shopping_Cart
ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP;

-- Cart_Product
CREATE TABLE Cart_Product (
    cart_id INT,
    product_id INT,
    quantity INT,
    date_added DATE,
    PRIMARY KEY (cart_id, product_id),
    FOREIGN KEY (cart_id) REFERENCES Shopping_Cart(cart_id),
    FOREIGN KEY (product_id) REFERENCES Product(product_id) on delete cascade
);

-- Sales Order
CREATE TABLE Sales_Order (
    order_id INT PRIMARY KEY,
    cart_id INT,
    order_date DATETIME,
    expected_receive_date DATE,
    shipment_date DATE,
    total_price DECIMAL(10,2),
    credit_card_details VARCHAR(255),
    payment_status VARCHAR(50),
    FOREIGN KEY (cart_id) REFERENCES Shopping_Cart(cart_id)
);
ALTER TABLE Sales_Order
ADD COLUMN address_id INT;

ALTER TABLE Sales_Order
ADD FOREIGN KEY (address_id) REFERENCES Customer_Address(address_id);

-- Order Line
CREATE TABLE Order_Line (
    order_id INT,
    product_id INT,
    quantity INT,
    price_at_order_time DECIMAL(10,2),
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (order_id) REFERENCES Sales_Order(order_id),
    FOREIGN KEY (product_id) REFERENCES Product(product_id) on delete cascade
);

-- Payment
CREATE TABLE Payment (
    payment_id INT PRIMARY KEY,
    order_id INT,
    amount DECIMAL(10,2),
    payment_date DATE,
    payment_method VARCHAR(50),
    payment_status VARCHAR(50),
    FOREIGN KEY (order_id) REFERENCES Sales_Order(order_id)
);

-- Employee
CREATE TABLE Employee (
    employee_id INT PRIMARY KEY,
    employee_name VARCHAR(255),
    employee_role VARCHAR(100),
    hire_date DATE,
    working_hours_per_week INT,
    branch_id INT,
    is_manager BOOLEAN,
    FOREIGN KEY (branch_id) REFERENCES Branch(branch_id)
);

CREATE TABLE Employee_Contact (
    employee_id INT,
    contact_type VARCHAR(50),
    contact_value VARCHAR(255),
    PRIMARY KEY (employee_id, contact_type, contact_value),
    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id)
);


-- Subtypes
CREATE TABLE PartTime_Employee (
    employee_id INT PRIMARY KEY,
    hourly_wage DECIMAL(6,2),
    max_hours_per_week INT,
    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id)
);

CREATE TABLE FullTime_Employee (
    employee_id INT PRIMARY KEY,
    salary DECIMAL(10,2),
    benefits TEXT,
    concentration VARCHAR(255),
    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id)
);

-- Review
CREATE TABLE Review (
    customer_id INT,
    product_id INT,
    review_date DATE,
    rating INT,
    review_comment TEXT,
    PRIMARY KEY (customer_id, product_id),
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
    FOREIGN KEY (product_id) REFERENCES Product(product_id) on delete cascade
);

-- Product Return
CREATE TABLE Product_Return (
    customer_id INT,
    product_id INT,
    return_date DATE,
    quantity INT,
    reason TEXT,
    PRIMARY KEY (customer_id, product_id, return_date),
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
    FOREIGN KEY (product_id) REFERENCES Product(product_id) on delete cascade
);

-- Ternary relationship
CREATE TABLE Order_Assignment (
    order_id INT,
    customer_id INT,
    employee_id INT,
    assigned_date DATE,
    PRIMARY KEY (order_id, customer_id, employee_id),
    FOREIGN KEY (order_id) REFERENCES Sales_Order(order_id),
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id)
);

-- Product availability at branches
CREATE TABLE Branch_Product (
    branch_id INT,
    product_id INT,
    stock_quantity INT,
    PRIMARY KEY (branch_id, product_id),
    FOREIGN KEY (branch_id) REFERENCES Branch(branch_id),
    FOREIGN KEY (product_id) REFERENCES Product(product_id) ON DELETE CASCADE 
);

--  Sample Data
-- Suppliers
INSERT INTO Supplier VALUES
(1, 'contact@beautysupply.com', 'BeautySupply Ltd'),
(2, 'support@organicglow.com', 'Organic Glow Inc'),
(3, 'sales@fragranceworld.com', 'Fragrance World');

-- Branches
INSERT INTO Branch VALUES
(10, 'Downtown Branch', '123 Main St, City'),
(20, 'Uptown Branch', '456 North Ave, City'),
(30, 'Suburban Branch', '789 Suburb Rd, City');

-- Branch Contacts
INSERT INTO Branch_Contact VALUES
(10, 'Phone', '555-1234'),
(10, 'Email', 'downtown@cosmetics.com'),
(20, 'Phone', '555-5678'),
(20, 'Email', 'uptown@cosmetics.com'),
(30, 'Phone', '555-9012');

-- Products
INSERT INTO Product VALUES
(100, 'Rose Facial Cream', 29.99, 200, TRUE),
(101, 'Aloe Vera Gel', 15.50, 150, FALSE),
(102, 'Herbal Shampoo', 18.00, 180, TRUE),
(103, 'Argan Oil Conditioner', 22.00, 160, FALSE),
(104, 'Citrus Cologne', 35.00, 130, TRUE),
(105, 'Midnight Musk Perfume', 55.00, 120, TRUE);

-- Fragrance (Subtype) 
INSERT INTO Fragrance VALUES
(104, 1,  'Eau de Parfum', 50.00, 8.00, 'High'),
(105, 0, 'Eau de Parfum', 45.00, 10.00,'High');

-- Fragrance_Season
INSERT INTO Fragrance_Season VALUES
(104, 'Summer'),
(105, 'Winter');

-- Fragrance_Time
INSERT INTO Fragrance_Time VALUES
(104, 'Day'),
(105, 'Night');

-- Fragrance_Scent_Note
INSERT INTO Fragrance_Scent_Note VALUES
(104, 'Citrus'),
(105, 'Musk');

-- Fragrance_Gender
INSERT INTO Fragrance_Gender VALUES
(104, 'Unisex'),
(105, 'Male');


-- Skincare Products
INSERT INTO Skincare_Product VALUES
(100, TRUE, 'Moisturizer', FALSE, 'Tube'),
(101, TRUE, 'Gel', TRUE, 'Bottle');

-- Skincare Skin Type
INSERT INTO Skincare_Skin_Type VALUES
(100, 'Dry'),
(100, 'Normal'),
(101, 'Oily');

-- Skincare Ingredient
INSERT INTO Skincare_Ingredient VALUES
(100, 'Vitamin E'),
(101, 'Aloe Vera');

-- Hair Products
INSERT INTO Hair_Product VALUES
(102, TRUE, TRUE, FALSE, 'Bottle'),
(103, TRUE, FALSE, TRUE, 'Bottle');

-- Hair Hair Type
INSERT INTO Hair_Hair_Type VALUES
(102, 'Curly'),
(103, 'Straight');

-- Hair Scalp Type
INSERT INTO Hair_Scalp_Type VALUES
(102, 'Dry'),
(103, 'Normal');

-- Hair Ingredient
INSERT INTO Hair_Ingredient VALUES
(102, 'Herbal Extracts'),
(103, 'Argan Oil');

-- Purchase Orders
INSERT INTO Purchase_Order VALUES
(5001, 1, 10, '2025-04-01'),
(5002, 2, 20, '2025-04-03');

-- PO_Product
INSERT INTO PO_Product VALUES
(5001, 100, 50),
(5001, 101, 40),
(5002, 102, 30);

-- Customers
INSERT INTO Customer VALUES
(1, 'Aisha Khalil', 'F', '1998-05-23'),
(2, 'Omar Talal', 'M', '1994-03-15'),
(3, 'Lina Ahmed', 'F', '2000-08-10'),
(25,"lela","F", '2000-08-10');

-- Customer Emails
INSERT INTO Customer_Email (customer_id, email, is_primary) VALUES
(1, 'aisha.khalil@example.com', TRUE),
(1, 'a.khalil@gmail.com', FALSE),
(2, 'omar.talal@example.com', TRUE),
(3, 'lina.ahmed@example.com', TRUE),
(25, "lela@gmail.com", TRUE);

-- Customer Phones
INSERT INTO Customer_Phone (customer_id, phone_number, type, is_primary) VALUES
(1, '555-1111', 'Mobile', TRUE),
(1, '555-2222', 'Home', FALSE),
(2, '555-3333', 'Mobile', TRUE),
(3, '555-4444', 'Mobile', TRUE);

-- Customer Addresses
INSERT INTO Customer_Address (customer_id, address, address_type, is_primary) VALUES
(1, '123 Blossom St, City', 'Home', TRUE),
(1, '456 Work Rd, City', 'Work', FALSE),
(2, '789 Maple Ave, City', 'Home', TRUE),
(3, '321 Oak St, City', 'Home', TRUE);

-- Shopping Cart
INSERT INTO Shopping_Cart (cart_id, customer_id, cart_status, created_at)
VALUES (1000, 25, 'Active', '2025-4-2'),
 (1001, 2, 'Active', '2025-4-2'),
 (1005, 1, 'Active', '2024-7-2'),
 (1003, 3, 'Active', '2023-4-2');

;


-- Cart_Product
INSERT INTO Cart_Product VALUES
(1000, 100, 2, '2025-04-05'),
(1000, 104, 1, '2025-04-05'),
(1001, 101, 1, '2025-04-06'),
(1002, 105, 3, '2025-04-07');

-- Sales Order
INSERT INTO Sales_Order(order_id , cart_id , order_date ,expected_receive_date,shipment_date ,total_price,credit_card_details, payment_status, address_id) VALUES
(2001, 1000, '2025-04-06 10:00:00', '2025-04-10', '2025-04-08', 65.00, '**** **** **** 1234', 'Paid',1 ),
(2002, 1001, '2025-04-07 11:30:00', '2025-04-11', '2025-03-15', 15.50 , '**** **** **** 5678', 'Pending', 1);
describe Sales_Order;
-- Order Line
INSERT INTO Order_Line VALUES
(2001, 100, 2, 29.99),
(2001, 104, 1, 35.00),
(2002, 101, 1, 15.50);

-- Payment
INSERT INTO Payment VALUES
(9001, 2001, 95.98, '2025-04-06', 'Credit Card', 'Pending'),
(9002, 2002, 15.50, '2025-04-07', 'Credit Card', 'Pending');

-- Employees
INSERT INTO Employee VALUES
(10, 'Leila M.', 'Cashier', '2022-01-10', 25, 10, FALSE),
(11, 'Ahmad N.', 'Manager', '2021-06-15', 40, 10, TRUE),
(12, 'Sara T.', 'Sales Associate', '2023-02-20', 30, 20, FALSE);

-- Employee Contacts
INSERT INTO Employee_Contact VALUES
(10, 'Phone', '555-1000'),
(11, 'Phone', '555-1001'),
(12, 'Phone', '555-1002'),
(12, 'Email', 'sara.t@cosmetics.com');

INSERT INTO Employee_Contact VALUES
(11, 'Email', 'Ahmad@gmail.com');

-- PartTime Employees
INSERT INTO PartTime_Employee VALUES
(10, 15.00, 25),
(12, 12.50, 30);

-- FullTime Employees
INSERT INTO FullTime_Employee VALUES
(11, 3500.00, 'Health insurance, Paid Leave', 'Retail Management');

-- Review
INSERT INTO Review VALUES
(1, 100, '2025-04-10', 5, 'Excellent moisturizing cream!'),
(2, 102, '2025-04-12', 4, 'Leaves hair soft and shiny.');

-- Product Return
INSERT INTO Product_Return VALUES
(1, 101, '2025-04-15', 1, 'Received wrong size');

-- Order Assignment
INSERT INTO Order_Assignment VALUES
(2001, 1, 10, '2025-04-06'),
(2002, 2, 12, '2025-04-07');

-- Branch Product
INSERT INTO Branch_Product VALUES
(10, 100, 30),
(10, 104, 20),
(20, 101, 25),
(20, 102, 15),
(30, 105, 10);
-- Product entries
INSERT INTO Product VALUES
(106, 'Green Tea Toner', 20.00, 90, TRUE),
(107, 'Vitamin C Serum', 25.00, 110, TRUE),
(108, 'Charcoal Face Wash', 18.50, 80, FALSE),
(109, 'Hyaluronic Acid Serum', 27.00, 95, TRUE),
(110, 'Shea Butter Cream', 22.00, 60, FALSE),
(111, 'Tea Tree Oil Gel', 19.00, 70, FALSE),
(112, 'Collagen Boost Cream', 30.00, 85, TRUE),
(113, 'Niacinamide Lotion', 23.00, 50, FALSE),
(114, 'Sunscreen SPF 50', 28.00, 140, TRUE),
(115, 'Retinol Night Cream', 26.00, 100, TRUE);

-- Skincare_Product entries
INSERT INTO Skincare_Product VALUES
(106, TRUE, 'Toner', TRUE, 'Bottle'),
(107, TRUE, 'Serum', FALSE, 'Dropper'),
(108, FALSE, 'Cleanser', TRUE, 'Tube'),
(109, TRUE, 'Serum', FALSE, 'Pump'),
(110, TRUE, 'Cream', FALSE, 'Jar'),
(111, TRUE, 'Gel', TRUE, 'Tube'),
(112, TRUE, 'Cream', FALSE, 'Pump'),
(113, TRUE, 'Lotion', FALSE, 'Bottle'),
(114, FALSE, 'Sunscreen', TRUE, 'Spray'),
(115, TRUE, 'Cream', FALSE, 'Tube');

-- Skincare_Skin_Type entries
INSERT INTO Skincare_Skin_Type VALUES
(106, 'Oily'),
(107, 'Dry'),
(108, 'Combination'),
(109, 'Dry'),
(110, 'Normal'),
(111, 'Oily'),
(112, 'Mature'),
(113, 'Sensitive'),
(114, 'All'),
(115, 'Mature');

-- Skincare_Ingredient entries
INSERT INTO Skincare_Ingredient VALUES
(106, 'Green Tea'),
(107, 'Vitamin C'),
(108, 'Charcoal'),
(109, 'Hyaluronic Acid'),
(110, 'Shea Butter'),
(111, 'Tea Tree Oil'),
(112, 'Collagen'),
(113, 'Niacinamide'),
(114, 'Zinc Oxide'),
(115, 'Retinol');
-- Hair Products (subtype of Product)
INSERT INTO Hair_Product (product_id, natural_or_organic, fragrance_free, sulfate_free, packaging) VALUES
(200, TRUE, TRUE, FALSE, 'Bottle'),
(201, FALSE, TRUE, TRUE, 'Tube'),
(202, TRUE, FALSE, TRUE, 'Jar'),
(203, FALSE, FALSE, FALSE, 'Pump');

-- Hair_Hair_Type (types of hair for each product)
INSERT INTO Hair_Hair_Type (product_id, hair_type) VALUES
(200, 'Curly'),
(200, 'Wavy'),
(201, 'Straight'),
(202, 'All'),
(203, 'Dry');

-- Hair_Scalp_Type (scalp type for each product)
INSERT INTO Hair_Scalp_Type (product_id, scalp_type) VALUES
(200, 'Dry'),
(201, 'Oily'),
(202, 'Normal'),
(203, 'Sensitive');

-- Hair_Ingredient (ingredients in each hair product)
INSERT INTO Hair_Ingredient (product_id, ingredient) VALUES
(200, 'Argan Oil'),
(200, 'Keratin'),
(201, 'Shea Butter'),
(202, 'Tea Tree Oil'),
(202, 'Aloe Vera'),
(203, 'Coconut Oil');
INSERT INTO Product (product_id, pname, price, num_of_purchases, is_trending) VALUES
(200, 'Hydrating Curl Cream', 24.99, 100, TRUE),
(201, 'Sulfate-Free Shampoo', 19.99, 150, TRUE),
(202, 'Nourishing Hair Mask', 29.99, 90, FALSE),
(203, 'Scalp Soothing Serum', 21.50, 60, TRUE);

----
-- تأكد أولاً أن جدول Fragrance يحتوي على العمود concentration_level
-- ALTER TABLE Fragrance ADD concentration_level VARCHAR(10);

-- ================== PRODUCTS ==================
INSERT INTO Product VALUES
(222, 'Amber Oud Elixir', 68.00, 90, TRUE),
(223, 'Fresh Marine Splash', 42.50, 75, FALSE),
(224, 'Blooming Petals', 47.00, 105, TRUE),
(230, 'Citrus Breeze', 45.00, 80, TRUE),
(231, 'Lavender Dream', 55.00, 70, TRUE),
(232, 'Vanilla Sunset', 60.00, 30, FALSE),
(233, 'Ocean Mist', 50.00, 90, TRUE),
(234, 'Jasmine Whisper', 65.00, 55, TRUE);

-- ================== FRAGRANCE ==================
INSERT INTO Fragrance(
    product_id ,
    is_alcohol_free ,
    fragrance_type ,
    size_ml,
    lasting_hours ,
    concentration 
) VALUES
(222, 0, 'Parfum', 75.00, 12.00 , 'High'),
(223, 1,  'Eau de Toilette', 60.00, 6.50, 'Medium'),
(224, 1, 'Eau de Parfum', 50.00, 7.00, 'High'),
(230, 1, 'Eau de Toilette', 6.00, 4.50, 'Medium'),
(231, 0, 'Eau de Parfum', 8.00, 5.00, 'High'),
(232, 1, 'Parfum', 10.00, 6.00, 'High'),
(233, 1, 'Eau de Toilette', 5.00, 3.50, 'Medium'),
(234, 0, 'Eau de Parfum', 9.00, 5.50, 'High');
select * from Fragrance;

-- ================== FRAGRANCE_SEASON ==================
INSERT INTO Fragrance_Season VALUES
(222, 'Winter'),
(222, 'Fall'),
(223, 'Summer'),
(223, 'Spring'),
(224, 'Spring'),
(230, 'Spring'),
(230, 'Summer'),
(231, 'Spring'),
(232, 'Autumn'),
(233, 'Summer'),
(234, 'Spring'),
(234, 'Summer');

-- ================== FRAGRANCE_TIME ==================
INSERT INTO Fragrance_Time VALUES
(222, 'Evening'),
(222, 'Night'),
(223, 'Day'),
(224, 'Day'),
(230, 'Day'),
(231, 'Evening'),
(232, 'Night'),
(233, 'Day'),
(234, 'Evening');

-- ================== FRAGRANCE_SCENT_NOTE ==================
INSERT INTO Fragrance_Scent_Note VALUES
(222, 'Amber'),
(222, 'Spice'),
(223, 'Marine'),
(223, 'Citrus'),
(224, 'Rose'),
(224, 'Peony'),
(224, 'Musk'),
(230, 'Lemon'),
(230, 'Bergamot'),
(231, 'Lavender'),
(232, 'Vanilla'),
(232, 'Caramel'),
(233, 'Sea Salt'),
(234, 'Jasmine'),
(234, 'Musk');

-- ================== FRAGRANCE_GENDER ==================
INSERT INTO Fragrance_Gender VALUES
(222, 'Unisex'),
(223, 'Male'),
(224, 'Female'),
(230, 'Unisex'),
(231, 'Female'),
(232, 'Unisex'),
(233, 'Unisex'),
(234, 'Female');
select * from  Fragrance;

CREATE TABLE User_Login (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    user_type ENUM('customer', 'manager') NOT NULL,
    reference_id INT NOT NULL,  -- إما customer_id أو employee_id
    FOREIGN KEY (reference_id) REFERENCES Customer(customer_id) ON DELETE CASCADE
        -- هذه العلاقة سيتم تعديلها لاحقًا ديناميكيًا حسب user_type
);

CREATE TABLE Customer_Auth (
    customer_id INT PRIMARY KEY,
    password VARCHAR(255),
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
);

CREATE TABLE Manager_Auth (
    employee_id INT PRIMARY KEY,
    password VARCHAR(255),
    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id)
);
INSERT INTO User_Login (username, password, user_type, reference_id)
VALUES ('ahmad', 'ahmad12', 'manager', 11);  -- 11 هو employee_id من جدول Employee


  
DESCRIBE Customer;
SELECT 
    c.customer_id, 
    c.cname, 
    SUM(so.total_price) AS total_spending
FROM Customer c
JOIN Shopping_Cart sc ON c.customer_id = sc.customer_id
JOIN Sales_Order so ON sc.cart_id = so.cart_id
WHERE so.payment_status = 'Paid'
GROUP BY c.customer_id, c.cname
ORDER BY total_spending DESC
LIMIT 9;
-- عميل 1
INSERT INTO Customer (customer_id, cname, gender, date_of_birth)
VALUES (555, 'Alaa Saleh', 'M', '1995-02-15');

INSERT INTO Shopping_Cart (cart_id, customer_id, cart_status, created_at)
VALUES (101, 555, 'Active', CURDATE());

INSERT INTO Sales_Order (order_id, cart_id, order_date, total_price, payment_status)
VALUES (1001, 101, CURDATE(), 120.50, 'Paid');


-- عميل 2
INSERT INTO Customer (customer_id, cname, gender, date_of_birth)
VALUES (20, 'Sara Ahmed', 'F', '1990-07-20');

INSERT INTO Shopping_Cart (cart_id, customer_id, cart_status, created_at)
VALUES (102, 2, 'Active', CURDATE());

INSERT INTO Sales_Order (order_id, cart_id, order_date, total_price, payment_status)
VALUES (1002, 102, CURDATE(), 350.00, 'Paid');


-- عميل 3
INSERT INTO Customer (customer_id, cname, gender, date_of_birth)
VALUES (30, 'Rami Zaid', 'M', '1988-11-05');

INSERT INTO Shopping_Cart (cart_id, customer_id, cart_status, created_at)
VALUES (103, 3, 'Active', CURDATE());

INSERT INTO Sales_Order (order_id, cart_id, order_date, total_price, payment_status)
VALUES (1003, 103, CURDATE(), 220.00, 'Paid');
SELECT
  so.cart_id,
  sc.customer_id,
  c.*
FROM Sales_Order so
JOIN Shopping_Cart sc ON so.cart_id = sc.cart_id
JOIN Customer c ON sc.customer_id = c.customer_id;
INSERT INTO User_Login (username, password, user_type, reference_id)
VALUES ('nina', '1234', 'Customer', 45);  -- 11 هو employee_id من جدول Employee
INSERT INTO Customer_Email (customer_id, email, is_primary) VALUES(45, "nina@gmail.com", TRUE);
INSERT INTO Customer VALUES (45, 'nina', 'F', '1998-05-23');
select * from Employee_Contact ;
select * from Manager_Auth;
insert into Manager_Auth values (11,"ahmad12");
select * from Customer;
select * from Shopping_Cart;
 select * from Customer_Email;
  select * from User_Login;

  select * from Customer_Auth,Customer_Email;
  select * from Customer_Email;

insert into Customer_Auth values (25,"1234" );
INSERT INTO Branch_Product (branch_id, product_id, stock_quantity) VALUES
-- Downtown Branch (10)
(10, 101, 40),
(10, 102, 55),
(10, 103, 30),
(10, 105, 25),
(10, 106, 35),
(10, 107, 50),
(10, 108, 20),
(10, 109, 40),
(10, 110, 0),
(10, 111, 15),
(10, 112, 25),
(10, 113, 0),
(10, 114, 35),
(10, 115, 40),

-- Uptown Branch (20)
(20, 100, 45),
(20, 103, 0),
(20, 104, 40),
(20, 105, 35),
(20, 106, 20),
(20, 107, 40),
(20, 108, 30),
(20, 109, 45),
(20, 110, 20),
(20, 111, 25),
(20, 112, 0),
(20, 113, 15),
(20, 114, 50),
(20, 115, 35),

-- Suburban Branch (30)
(30, 100, 30),
(30, 101, 20),
(30, 102, 40),
(30, 103, 15),
(30, 104, 20),
(30, 106, 25),
(30, 107, 0),
(30, 108, 15),
(30, 109, 35),
(30, 110, 25),
(30, 111, 10),
(30, 112, 20),
(30, 113, 5),
(30, 114, 0),
(30, 115, 20);

-- Downtown Branch (branch_id = 10)
INSERT INTO Employee VALUES
(1, 'Lina Ahmad', 'Sales Assistant', '2022-03-10', 40, 10, FALSE),
(2, 'Hani Qassem', 'Cashier', '2021-11-05', 35, 10, FALSE),
(3, 'Rania Khaled', 'Stock Coordinato', '2020-01-15', 45, 10, TRUE);

-- Uptown Branch (branch_id = 20)
INSERT INTO Employee VALUES
(4, 'Sami Nasser', 'Sales Representative', '2023-06-12', 40, 20, FALSE),
(5, 'Mona Alami', 'Stock Coordinator', '2022-08-22', 38, 20, FALSE),
(6, 'Tariq Abu Salem', 'Branch Manager', '2019-12-01', 48, 20, TRUE);

-- Suburban Branch (branch_id = 30)
INSERT INTO Employee VALUES
(7, 'Dana Yousef', 'Customer Support', '2021-05-30', 36, 30, FALSE),
(8, 'Fadi Saleh', 'Security', '2020-09-18', 30, 30, FALSE),
(9, 'Layla Haddad', 'Store Manager', '2018-02-25', 42, 30, TRUE);


show tables;
select * from Sales_Order ;
select * from Customer_Address;
  select * from PO_Product;
 select * from  order_line;
 select * from   Order_Assignment ;
 INSERT INTO Order_Line (order_id, product_id, quantity, price_at_order_time)
VALUES (2010, 2, 3, 19.99);

select * from Shopping_Cart;
select * from  Sales_Order;
describe employee;
show tables;
SELECT DISTINCT payment_status FROM Sales_Order;
use cosmetics_store_db;
INSERT INTO Customer (customer_id, cname, gender, date_of_birth) VALUES
(10, 'John Doe', 'M', '1990-05-15'),
(250, 'Jane Smith', 'F', '1985-08-22'),
(35, 'Mike Johnson', 'M', '1995-03-10'),
(46, 'Sarah Williams', 'F', '1988-11-30'),
(515, 'David Brown', 'M', '1992-07-18');


-- Shopping carts for these customers
INSERT INTO Shopping_Cart (cart_id, customer_id, created_at) VALUES
(1010, 10, '2023-01-10'),
(1020, 10, '2023-06-15'),
(1030, 250, '2022-11-20'),
(1040, 35, '2023-03-05'),
(1050, 46, '2021-12-18'),
(1060, 515, '2023-08-01');

-- Sales orders with 'Paid' status and varied dates
INSERT INTO Sales_Order (order_id, cart_id, order_date, total_price, payment_status) VALUES
(10010, 1010, '2023-01-15', 150.00, 'Paid'),   -- John (active)
(10020, 1020, '2023-06-20', 200.00, 'Paid'),   -- John (active)
(10030, 1030, '2022-11-25', 75.00, 'Paid'),    -- Jane (inactive since 2022)
(10040, 1040, '2023-03-10', 300.00, 'Paid'),   -- Mike (moderately active)
(10050, 1050, '2021-12-20', 50.00, 'Paid'),    -- Sarah (very inactive)
(10060, 1060, '2023-08-05', 400.00, 'Paid');   -- David (very recent)

-- Special cases
-- Customer with no orders (should appear as inactive)
INSERT INTO Customer (customer_id, cname, gender, date_of_birth) VALUES
(60, 'Emily Davis', 'F', '1993-04-25');

-- Customer with pending order (shouldn't count as activity)
INSERT INTO Shopping_Cart (cart_id, customer_id, created_at) VALUES
(1070, 250, '2023-09-01');
INSERT INTO Sales_Order (order_id, cart_id, order_date, total_price, payment_status) VALUES
(10070, 1070, '2023-09-05', 100.00, 'Pending');
-- Find customers inactive since 2023-01-01:
SELECT c.customer_id, c.cname, MAX(so.order_date) as last_order_date
FROM Customer c
LEFT JOIN Shopping_Cart sc ON c.customer_id = sc.customer_id
LEFT JOIN Sales_Order so ON sc.cart_id = so.cart_id AND so.payment_status = 'Paid'
GROUP BY c.customer_id, c.cname
HAVING MAX(so.order_date) < '2023-01-01' OR MAX(so.order_date) IS NULL;