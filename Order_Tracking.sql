use Order_Tracking;
-- MySQL dump 10.13  Distrib 8.0.31, for Win64 (x86_64)
--
-- Host: localhost    Database: rtots
-- ------------------------------------------------------
-- Server version 8.0.31

-- Disable foreign key checks before creating tables
SET FOREIGN_KEY_CHECKS = 0;

-- Drop existing tables if they exist
DROP TABLE IF EXISTS `contact_info`;
DROP TABLE IF EXISTS `customer`;
DROP TABLE IF EXISTS `delivery_vehicle`;
DROP TABLE IF EXISTS `order_history`;
DROP TABLE IF EXISTS `order_product`;
DROP TABLE IF EXISTS `orders`;
DROP TABLE IF EXISTS `payment`;
DROP TABLE IF EXISTS `product`;
DROP TABLE IF EXISTS `refers`;
DROP TABLE IF EXISTS `tracking_info`;

-- Table structure for `customer`
CREATE TABLE `customer` (
  `Customer_ID` int NOT NULL,
  `First_Name` varchar(50) DEFAULT NULL,
  `Middle_Name` varchar(50) DEFAULT NULL,
  `Last_Name` varchar(50) DEFAULT NULL,
  `Contact_Info` varchar(100) DEFAULT NULL,
  `House_No_Room_No` varchar(50) DEFAULT NULL,
  `Street` varchar(100) DEFAULT NULL,
  `City` varchar(100) DEFAULT NULL,
  `State` varchar(100) DEFAULT NULL,
  `Order_History` text,
  PRIMARY KEY (`Customer_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Table structure for `contact_info`
CREATE TABLE `contact_info` (
  `Customer_ID` int NOT NULL,
  `Contact_No` varchar(15) NOT NULL,
  PRIMARY KEY (`Customer_ID`, `Contact_No`),
  CONSTRAINT `contact_info_ibfk_1` FOREIGN KEY (`Customer_ID`) REFERENCES `customer` (`Customer_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Table structure for `delivery_vehicle`
CREATE TABLE `delivery_vehicle` (
  `Vehicle_ID` int NOT NULL,
  `Driver_Name` varchar(100) DEFAULT NULL,
  `Current_Location` varchar(100) DEFAULT NULL,
  `Capacity` int DEFAULT NULL,
  `Status` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`Vehicle_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Table structure for `order_history`
CREATE TABLE `order_history` (
  `Customer_ID` int NOT NULL,
  `Order_ID` int NOT NULL,
  PRIMARY KEY (`Customer_ID`, `Order_ID`),
  KEY `Order_ID` (`Order_ID`),
  CONSTRAINT `order_history_ibfk_1` FOREIGN KEY (`Customer_ID`) REFERENCES `customer` (`Customer_ID`),
  CONSTRAINT `order_history_ibfk_2` FOREIGN KEY (`Order_ID`) REFERENCES `orders` (`Order_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Table structure for `order_product`
CREATE TABLE `order_product` (
  `Order_ID` int NOT NULL,
  `Product_ID` int NOT NULL,
  PRIMARY KEY (`Order_ID`, `Product_ID`),
  KEY `Product_ID` (`Product_ID`),
  CONSTRAINT `order_product_ibfk_1` FOREIGN KEY (`Order_ID`) REFERENCES `orders` (`Order_ID`),
  CONSTRAINT `order_product_ibfk_2` FOREIGN KEY (`Product_ID`) REFERENCES `product` (`Product_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Table structure for `orders`
CREATE TABLE `orders` (
  `Order_ID` int NOT NULL,
  `Order_Status` varchar(50) DEFAULT NULL,
  `Expected_Delivery` date DEFAULT NULL,
  `Customer_ID` int DEFAULT NULL,
  `Special_Instructions` text,
  PRIMARY KEY (`Order_ID`),
  KEY `Customer_ID` (`Customer_ID`),
  CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`Customer_ID`) REFERENCES `customer` (`Customer_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Table structure for `payment`
CREATE TABLE `payment` (
  `Payment_ID` int NOT NULL,
  `Order_ID` int DEFAULT NULL,
  `Amount` decimal(10,2) DEFAULT NULL,
  `Date` date DEFAULT NULL,
  `Method` varchar(50) DEFAULT NULL,
  `Status` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`Payment_ID`),
  KEY `Order_ID` (`Order_ID`),
  CONSTRAINT `payment_ibfk_1` FOREIGN KEY (`Order_ID`) REFERENCES `orders` (`Order_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Table structure for `product`
CREATE TABLE `product` (
  `Product_ID` int NOT NULL,
  `Product_Name` varchar(100) DEFAULT NULL,
  `Category` varchar(100) DEFAULT NULL,
  `Price` decimal(10,2) DEFAULT NULL,
  `Stock` int DEFAULT NULL,
  PRIMARY KEY (`Product_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Table structure for `refers`contact_info
CREATE TABLE `refers` (
  `Referrer_Customer_ID` int NOT NULL,
  `Referee_Customer_ID` int NOT NULL,
  PRIMARY KEY (`Referrer_Customer_ID`, `Referee_Customer_ID`),
  KEY `Referee_Customer_ID` (`Referee_Customer_ID`),
  CONSTRAINT `refers_ibfk_1` FOREIGN KEY (`Referrer_Customer_ID`) REFERENCES `customer` (`Customer_ID`),
  CONSTRAINT `refers_ibfk_2` FOREIGN KEY (`Referee_Customer_ID`) REFERENCES `customer` (`Customer_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Table structure for `tracking_info`
CREATE TABLE `tracking_info` (
  `Tracking_ID` int NOT NULL,
  `Order_ID` int DEFAULT NULL,
  `Current_Location` varchar(100) DEFAULT NULL,
  `Timestamp` datetime DEFAULT NULL,
  `Vehicle_ID` int DEFAULT NULL,
  PRIMARY KEY (`Tracking_ID`),
  KEY `Order_ID` (`Order_ID`),
  KEY `Vehicle_ID` (`Vehicle_ID`),
  CONSTRAINT `tracking_info_ibfk_1` FOREIGN KEY (`Order_ID`) REFERENCES `orders` (`Order_ID`),
  CONSTRAINT `tracking_info_ibfk_2` FOREIGN KEY (`Vehicle_ID`) REFERENCES `delivery_vehicle` (`Vehicle_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Enable foreign key checks again
SET FOREIGN_KEY_CHECKS = 1;
-- Step 1: Disable foreign key checks
SET FOREIGN_KEY_CHECKS = 0;

-- Step 2: Drop tables with foreign key constraints that reference the customer table
DROP TABLE IF EXISTS `contact_info`;
DROP TABLE IF EXISTS `order_history`;
DROP TABLE IF EXISTS `orders`;
DROP TABLE IF EXISTS `refers`;

-- Step 3: Drop the customer table
DROP TABLE IF EXISTS `customer`;

-- Step 4: Recreate the customer table with the new fields
CREATE TABLE `customer` (
  `Customer_ID` int NOT NULL,
  `First_Name` varchar(50) DEFAULT NULL,
  `Middle_Name` varchar(50) DEFAULT NULL,
  `Last_Name` varchar(50) DEFAULT NULL,
  `Contact_Info` varchar(100) DEFAULT NULL,
  `House_No_Room_No` varchar(50) DEFAULT NULL,
  `Street` varchar(100) DEFAULT NULL,
  `City` varchar(100) DEFAULT NULL,
  `State` varchar(100) DEFAULT NULL,
  `Order_History` text,
  `Email` varchar(100) DEFAULT NULL, -- New Email field
  `Password` varchar(255) DEFAULT NULL, -- New Password field
  PRIMARY KEY (`Customer_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Step 5: Recreate the other tables and add the foreign key constraints back
CREATE TABLE `contact_info` (
  `Customer_ID` int NOT NULL,
  `Contact_No` varchar(15) NOT NULL,
  PRIMARY KEY (`Customer_ID`, `Contact_No`),
  CONSTRAINT `contact_info_ibfk_1` FOREIGN KEY (`Customer_ID`) REFERENCES `customer` (`Customer_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `order_history` (
  `Customer_ID` int NOT NULL,
  `Order_ID` int NOT NULL,
  PRIMARY KEY (`Customer_ID`, `Order_ID`),
  KEY `Order_ID` (`Order_ID`),
  CONSTRAINT `order_history_ibfk_1` FOREIGN KEY (`Customer_ID`) REFERENCES `customer` (`Customer_ID`),
  CONSTRAINT `order_history_ibfk_2` FOREIGN KEY (`Order_ID`) REFERENCES `orders` (`Order_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `orders` (
  `Order_ID` int NOT NULL,
  `Order_Status` varchar(50) DEFAULT NULL,
  `Expected_Delivery` date DEFAULT NULL,
  `Customer_ID` int DEFAULT NULL,
  `Special_Instructions` text,
  PRIMARY KEY (`Order_ID`),
  KEY `Customer_ID` (`Customer_ID`),
  CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`Customer_ID`) REFERENCES `customer` (`Customer_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `refers` (
  `Referrer_Customer_ID` int NOT NULL,
  `Referee_Customer_ID` int NOT NULL,
  PRIMARY KEY (`Referrer_Customer_ID`, `Referee_Customer_ID`),
  KEY `Referee_Customer_ID` (`Referee_Customer_ID`),
  CONSTRAINT `refers_ibfk_1` FOREIGN KEY (`Referrer_Customer_ID`) REFERENCES `customer` (`Customer_ID`),
  CONSTRAINT `refers_ibfk_2` FOREIGN KEY (`Referee_Customer_ID`) REFERENCES `customer` (`Customer_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Step 6: Enable foreign key checks again
SET FOREIGN_KEY_CHECKS = 0;
INSERT INTO customer (Customer_ID, First_Name, Middle_Name, Last_Name, Contact_Info, House_No_Room_No, Street, City, State, Order_History, Email, Password) VALUES
(1, 'John', 'A.', 'Doe', 'john@example.com', '101', 'Maple St', 'Los Angeles', 'California', '5,7,10', 'john.doe@example.com', 'password123'),
(2, 'Jane', NULL, 'Smith', 'jane@example.com', '202', 'Oak St', 'San Francisco', 'California', '3,6', 'jane.smith@example.com', 'securePass456'),
(3, 'Michael', 'B.', 'Johnson', 'michael@example.com', '303', 'Pine St', 'Seattle', 'Washington', '1,4,9', 'michael.j@example.com', 'myPassword789'),
(4, 'Alice', 'C.', 'Davis', 'alice@example.com', '404', 'Elm St', 'Portland', 'Oregon', '8,11,12', 'alice.davis@example.com', 'aliceSecure999'),
(5, 'Robert', 'D.', 'Taylor', 'robert@example.com', '505', 'Spruce St', 'Denver', 'Colorado', '2,13', 'robert.taylor@example.com', 'robertPass321');
INSERT INTO contact_info (Customer_ID, Contact_No) VALUES
(1, '1234567890'),
(1, '0987654321'),
(2, '2345678901'),
(3, '3456789012'),
(4, '4567890123'),
(5, '5678901234');

INSERT INTO orders (Order_ID, Order_Status, Expected_Delivery, Customer_ID, Special_Instructions) VALUES
(1, 'Delivered', '2024-10-01', 3, 'Leave at door'),
(2, 'Pending', '2024-10-10', 5, 'Ring the bell once'),
(3, 'Shipped', '2024-10-08', 2, NULL),
(4, 'Processing', '2024-10-12', 3, NULL),
(5, 'Delivered', '2024-09-28', 1, 'Fragile - Handle with care'),
(6, 'Shipped', '2024-10-07', 2, NULL),
(7, 'Cancelled', '2024-09-30', 1, 'Call before delivering'),
(8, 'Pending', '2024-10-15', 4, NULL),
(9, 'Delivered', '2024-09-25', 3, NULL),
(10, 'Delivered', '2024-09-28', 1, 'Do not knock'),
(11, 'Processing', '2024-10-14', 4, NULL),
(12, 'Shipped', '2024-10-12', 4, NULL),
(13, 'Delivered', '2024-09-27', 5, NULL);
INSERT INTO order_history (Customer_ID, Order_ID) VALUES
(1, 5),
(1, 7),
(1, 10),
(2, 3),
(2, 6),
(3, 1),
(3, 4),
(3, 9),
(4, 8),
(4, 11),
(4, 12),
(5, 2),
(5, 13);
INSERT INTO refers (Referrer_Customer_ID, Referee_Customer_ID) VALUES
(1, 2),
(3, 1),
(4, 5),
(2, 3),
(5, 4);





DELIMITER //

CREATE FUNCTION calculate_total_price(orderId INT) RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
  DECLARE total DECIMAL(10,2);
  SELECT SUM(p.Price * op.Quantity) INTO total
  FROM order_product op
  JOIN product p ON op.Product_ID = p.Product_ID
  WHERE op.Order_ID = orderId;
  RETURN total;
END; //

DELIMITER ;

DELIMITER //






INSERT INTO customer (
    Customer_ID, 
    First_Name, 
    Middle_Name, 
    Last_Name, 
    Contact_Info, 
    House_No_Room_No, 
    Street, 
    City, 
    State, 
    Order_History, 
    Email, 
    Password
) VALUES (
    999, -- Using 999 as a distinct ID for admin
    'System',
    'Admin',
    'Administrator',
    '+1-888-555-0000',
    'Suite 100',
    'Tech Plaza',
    'San Jose',
    'California',
    NULL,
    'admin@ordertracking.com',
    '$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewqtPhyuL/vdH/kW' -- This represents a properly hashed password for 'Admin@123'
);

-- Add admin's contact number to contact_info table
INSERT INTO contact_info (Customer_ID, Contact_No) VALUES
(999, '+1-888-555-0000');


ALTER TABLE orders MODIFY Order_ID INT NOT NULL AUTO_INCREMENT;
ALTER TABLE payment
MODIFY COLUMN Payment_ID int NOT NULL AUTO_INCREMENT;



alter table order_product add column quantity int;

DELIMITER //
CREATE PROCEDURE get_recent_orders(IN customer_id INT)
BEGIN
    SELECT o.Order_ID, o.Order_Status, 
           o.Expected_Delivery, o.Special_Instructions,
           p.Product_Name, p.Price,
           pay.Amount AS Payment_Amount,
           pay.Status AS Payment_Status
    FROM orders o
    JOIN order_product op ON o.Order_ID = op.Order_ID
    JOIN product p ON op.Product_ID = p.Product_ID
    LEFT JOIN payment pay ON o.Order_ID = pay.Order_ID
    WHERE o.Customer_ID = customer_id
    ORDER BY o.Expected_Delivery DESC
    LIMIT 5;
END //
DELIMITER ;

DELIMITER $$
CREATE TRIGGER check_stock_before_order
BEFORE INSERT ON order_product
FOR EACH ROW
BEGIN
    DECLARE stock_count INT;
    
    -- Get the current stock for the product
    SELECT Stock INTO stock_count
    FROM product
    WHERE Product_ID = NEW.Product_ID;
    
    -- Check if the stock is sufficient
    IF stock_count < NEW.Quantity THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Insufficient stock to place this order';
    END IF;
END $$
DELIMITER ;

DELIMITER $$
CREATE TRIGGER reduce_stock
BEFORE INSERT ON order_product
FOR EACH ROW
BEGIN
    DECLARE stock_left INT;
    SELECT Stock INTO stock_left FROM product WHERE Product_ID = NEW.Product_ID;
    
    IF stock_left < NEW.Quantity THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Insufficient stock';
    ELSE
        UPDATE product SET Stock = Stock - NEW.Quantity WHERE Product_ID = NEW.Product_ID;
    END IF;
END $$
DELIMITER ;


