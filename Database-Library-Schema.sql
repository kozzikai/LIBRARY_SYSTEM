SET GLOBAL local_infile = 1;

DROP DATABASE IF EXISTS `LIBRARY`;
CREATE DATABASE `LIBRARY`;
USE `LIBRARY`;

DROP TABLE IF EXISTS BORROWER;
CREATE TABLE BORROWER(
Card_id VARCHAR(10) NOT NULL,
Ssn CHAR(11) NOT NULL,
Bname VARCHAR(30) NOT NULL,
Address VARCHAR(200) NOT NULL,
Phone CHAR(20) NOT NULL,
PRIMARY KEY(Card_id),
UNIQUE(Ssn));

DROP TABLE IF EXISTS AUTHORS;
CREATE TABLE AUTHORS(
Author_id INT AUTO_INCREMENT,
Name VARCHAR(110),
PRIMARY KEY(Author_id));

DROP TABLE IF EXISTS BOOK;
CREATE TABLE BOOK(
Isbn CHAR(10),
Title VARCHAR(250),
PRIMARY KEY(Isbn));

DROP TABLE IF EXISTS BOOK_AUTHORS;
CREATE TABLE BOOK_AUTHORS(
Author_id INT,
Isbn CHAR(10),
PRIMARY KEY(Author_id,Isbn),
FOREIGN KEY(Author_id) REFERENCES AUTHORS(Author_id),
FOREIGN KEY(Isbn) REFERENCES BOOK(Isbn));

DROP TABLE IF EXISTS BOOK_LOANS;
CREATE TABLE BOOK_LOANS(
Loan_id INT AUTO_INCREMENT,
Isbn CHAR(10),
Card_id VARCHAR(10) NOT NULL,
Date_out DATE,
Due_date DATE,
Date_in DATE,
PRIMARY KEY(Loan_id),
FOREIGN KEY(Isbn) REFERENCES BOOK(Isbn),
FOREIGN KEY(Card_id) REFERENCES BORROWER(Card_id));

DROP TABLE IF EXISTS FINES;
CREATE TABLE FINES(
Loan_id INT,
Fine_amt FLOAT DEFAULT 0,
Paid BOOLEAN DEFAULT False,
PRIMARY KEY(Loan_id),
FOREIGN KEY(Loan_id) REFERENCES BOOK_LOANS(Loan_id));