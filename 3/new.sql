CREATE DATABASE uzlet;
USE uzlet;

CREATE TABLE zoldsegek (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nev VARCHAR(100),
    mennyiseg INT,
    ar DECIMAL(10, 2),
    szarmazasi_hely VARCHAR(100)
);

CREATE TABLE gyumolcsok (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nev VARCHAR(100),
    mennyiseg INT,
    ar DECIMAL(10, 2),
    szarmazasi_hely VARCHAR(100)
);

CREATE TABLE husok (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nev VARCHAR(100),
    mennyiseg INT,
    ar DECIMAL(10, 2),
    szarmazasi_hely VARCHAR(100)
);

CREATE TABLE tejtermekek (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nev VARCHAR(100),
    mennyiseg INT,
    ar DECIMAL(10, 2),
    szarmazasi_hely VARCHAR(100)
);

INSERT INTO zoldsegek (nev, mennyiseg, ar, szarmazasi_hely)
VALUES
    ('Paradicsom', 50, 400.00, 'Magyarország'),
    ('Krumpli', 100, 200.00, 'Lengyelország');

INSERT INTO gyumolcsok (nev, mennyiseg, ar, szarmazasi_hely)
VALUES
    ('Alma', 75, 350.00, 'Magyarország'),
    ('Banán', 50, 500.00, 'Ecuador');

INSERT INTO husok (nev, mennyiseg, ar, szarmazasi_hely)
VALUES
    ('Csirkemell', 30, 1200.00, 'Magyarország'),
    ('Sertéskaraj', 20, 1500.00, 'Ausztria');

INSERT INTO tejtermekek (nev, mennyiseg, ar, szarmazasi_hely)
VALUES
    ('Tej', 100, 250.00, 'Magyarország'),
    ('Sajt', 50, 2000.00, 'Franciaország');