CREATE DATABASE IF NOT EXISTS test;

USE test;
ALTER TABLE USERS MODIFY COLUMN PASSWORD_HASH TEXT NOT NULL;

-- Create the USERS table
CREATE TABLE USERS (
    USER_ID INT AUTO_INCREMENT PRIMARY KEY,
    FIRST_NAME VARCHAR(50),
    LAST_NAME VARCHAR(50),
    EMAIL VARCHAR(100),
    PASSWORD_HASH CHAR(60) NOT NULL, 
    PHONE_NUMBER VARCHAR(20)
);

SELECT * FROM USERS;


-- Create the DESTINATIONS table
CREATE TABLE DESTINATIONS (
    DESTINATION_ID INT AUTO_INCREMENT PRIMARY KEY,
    NAME VARCHAR(100),
    DESCRIPTION VARCHAR(500),
    LOCATION VARCHAR(100),
    FLIGHT_PRICE DECIMAL(10, 2),
    DISTANCE DECIMAL(10, 2),
    HOTEL_NAME VARCHAR(100),
    HOTEL_PRICE DECIMAL(10, 2)
);

-- Insert destination data into the DESTINATIONS table
INSERT INTO DESTINATIONS (NAME, DESCRIPTION, LOCATION, FLIGHT_PRICE, DISTANCE, HOTEL_NAME, HOTEL_PRICE)
VALUES
('Miami', 'A vibrant city known for its beautiful beaches, lively nightlife, and diverse culture.', 'Florida', 200.00, 0.00, 'Beachfront Resort', 150.00),
('Las Vegas', 'The entertainment capital of the world, famous for its casinos, shows, and nightlife.', 'Nevada', 300.00, 0.00, 'Luxury Hotel & Casino', 200.00),
('Myrtle Beach', 'A popular beach destination known for its pristine coastline and family-friendly attractions.', 'South Carolina', 250.00, 0.00, 'Oceanfront Resort', 120.00),
('New Orleans', 'A city rich in history, culture, and cuisine, famous for its jazz music and Mardi Gras celebrations.', 'Louisiana', 350.00, 0.00, 'Historic Hotel', 180.00),
('Atlanta', 'A bustling metropolis with a thriving arts scene, historic sites, and diverse culinary offerings.', 'Georgia', 150.00, 0.00, 'Downtown Hotel', 100.00);

DELETE FROM DESTINATIONS
WHERE destination_id > 5;


DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_createUser`(
    IN p_first VARCHAR(20),
    IN p_last VARCHAR(20),
    IN p_username VARCHAR(20),
    IN p_password VARCHAR(20),
    IN p_phone VARCHAR(20)
)
BEGIN
    IF (SELECT EXISTS (SELECT 1 FROM USERS WHERE EMAIL = p_username)) THEN
        SELECT 'Username Exists !!';
    ELSE
        INSERT INTO USERS (FIRST_NAME, LAST_NAME, EMAIL, PASSWORD_HASH, PHONE_NUMBER)
        VALUES (p_first, p_last, p_username, p_password, p_phone);

    END IF;
END$$
DELIMITER ;

-- Create the TRIP table
CREATE TABLE TRIP (
    TRIP_ID INT AUTO_INCREMENT PRIMARY KEY,
    DESTINATION_ID INT,
    START_DATE DATE,
    END_DATE DATE,
    NUM_PEOPLE INT,
    PRICE_PER_PERSON DECIMAL(10, 2),
    FOREIGN KEY (DESTINATION_ID) REFERENCES DESTINATIONS(DESTINATION_ID)
);

ALTER TABLE TRIP ADD COLUMN USER_ID INT;
-- Create the EXPENSES table
CREATE TABLE EXPENSES (
    EXPENSE_ID INT AUTO_INCREMENT PRIMARY KEY,
    TRIP_ID INT,
    USER_ID INT,
    DESCRIPTION VARCHAR(255),
    AMOUNT DECIMAL(10, 2),
    DATE_INCURRED DATE,
    FOREIGN KEY (TRIP_ID) REFERENCES TRIP(TRIP_ID),
    FOREIGN KEY (USER_ID) REFERENCES USERS(USER_ID)
);


 SELECT * FROM TRIP;
 
 SELECT * FROM EXPENSES;