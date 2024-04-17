CREATE DATABASE IF NOT EXISTS test2;

USE test2;

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

-- Create the ADMIN table
CREATE TABLE ADMIN (
    USER_ID INT AUTO_INCREMENT PRIMARY KEY,
    FIRST_NAME VARCHAR(50),
    LAST_NAME VARCHAR(50),
    EMAIL VARCHAR(100),
    PASSWORD_HASH CHAR(60) NOT NULL, 
    ADMIN_ROLE VARCHAR(50)
);
INSERT INTO ADMIN (NAME, DESCRIPTION, LOCATION, FLIGHT_PRICE, DISTANCE, HOTEL_NAME, HOTEL_PRICE)
VALUES
('Laila' 'Eliotti', 'lailaeliotti1@gmail.com', 'test1234', 'Owner'),
('Madison' 'Jones', 'maddij123@gmail.com', 'test1234', 'Owner');

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
('Miami', 'A vibrant city known for its beautiful beaches, lively nightlife, and diverse culture.', 'Florida', 200.00, 910.4, 'Beachfront Resort', 150.00),
('Las Vegas', 'The entertainment capital of the world, famous for its casinos, shows, and nightlife.', 'Nevada', 300.00, 1790.6, 'Luxury Hotel & Casino', 200.00),
('Myrtle Beach', 'A popular beach destination known for its pristine coastline and family-friendly attractions.', 'South Carolina', 250.00, 590.4, 'Oceanfront Resort', 120.00),
('New Orleans', 'A city rich in history, culture, and cuisine, famous for its jazz music and Mardi Gras celebrations.', 'Louisiana', 350.00, 533.7, 'Historic Hotel', 180.00),
('Atlanta', 'A bustling metropolis with a thriving arts scene, historic sites, and diverse culinary offerings.', 'Georgia', 150.00, 248.6, 'Downtown Hotel', 100.00);

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
    USER_ID INT,
    START_DATE DATE,
    END_DATE DATE,
    FOREIGN KEY (USER_ID) REFERENCES USERS(USER_ID),
    FOREIGN KEY (DESTINATION_ID) REFERENCES DESTINATIONS(DESTINATION_ID)
);


-- Create the PLANS table
CREATE TABLE IF NOT EXISTS PLANS (
    PLANS_ID INT AUTO_INCREMENT PRIMARY KEY,
    TRIP_ID INT,
    NUM_OF_PEOPLE INT,
    FOREIGN KEY (TRIP_ID) REFERENCES TRIP(TRIP_ID)
);

ALTER TABLE PLANS
ADD COLUMN FLIGHT VARCHAR(3);

CREATE TABLE IMAGES (
    IMAGE_ID INT AUTO_INCREMENT PRIMARY KEY,
    DESTINATION_ID INT,
    IMAGE_URL VARCHAR(255),
    FOREIGN KEY (DESTINATION_ID) REFERENCES DESTINATIONS(DESTINATION_ID)
);

INSERT INTO IMAGES (DESTINATION_ID, IMAGE_URL) 
VALUES 
(1, 'https://www.mayflower.com/wp-content/uploads/2022/05/Miami-City-Guide_Header-scaled.jpg'),
(2, 'https://imageio.forbes.com/specials-images/imageserve/656df61cc3a44648c235dde3/Las-Vegas--Nevada--USA-at-the-Welcome-Sign/960x0.jpg?format=jpg&width=1440'),
(3, 'https://sanddunesmb.com/wp-content/uploads/2020/04/Myrtle-Beach-Boardwalk-400x267.jpg'),
(4, 'https://assets.simpleviewinc.com/simpleview/image/upload/c_fill,h_560,q_60,w_960/v1/clients/neworleans/easter_5512c82b-353f-4e60-b216-c766a743e9cb.jpg'),
(5, 'https://a.cdn-hotels.com/gdcs/production114/d1629/63a8dbe5-e678-4fe4-957a-ad367913a3fa.jpg?impolicy=fcrop&w=1600&h=1066&q=medium');

SELECT * FROM IMAGES;



SELECT * FROM TRIP;

SELECT * FROM USERS;
SELECT * FROM DESTINATIONS;

