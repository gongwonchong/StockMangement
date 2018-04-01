CREATE DATABASE productdb;
USE productdb;
CREATE TABLE productdb.product_table (
    id INT NOT NULL AUTO_INCREMENT,
    product_date DATE NOT NULL,
    name VARCHAR(255) NOT NULL,
    incnt INT ZEROFILL NOT NULL,
    outcnt INT ZEROFILL NOT NULL,
    person VARCHAR(255) NOT NULL,
    note VARCHAR(255) NOT NULL,
    PRIMARY KEY(id)
);
SHOW COLUMNS FROM productdb.product_table;
CREATE TABLE productdb.product (
    name VARCHAR(255) NOT NULL,
    detail VARCHAR(255),
    UNIQUE (name)
);
SHOW COLUMNS FROM productdb.product;
ALTER TABLE productdb.product CONVERT TO CHARACTER SET 'utf8';
ALTER TABLE productdb.product_table CONVERT TO CHARACTER SET 'utf8';
SELECT "INSTALLATION COMPLETE";