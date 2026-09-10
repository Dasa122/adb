-- Active: 1789035636905@@127.0.0.1@3306
CREATE DATABASE Petrik
    DEFAULT CHARACTER SET = 'utf8mb4';

USE Petrik;

CREATE TABLE Diakok (
    diak_id  INT PRIMARY KEY AUTO_INCREMENT,
    nev      VARCHAR(100),
    szul_ev  INT,
    osztaly  VARCHAR(10),
    atlag    FLOAT
);

CREATE TABLE Tanarok (
    tanar_id    INT PRIMARY KEY AUTO_INCREMENT,
    nev         VARCHAR(100),
    tantargy    VARCHAR(50),
    email       VARCHAR(100),
    tapasztalat INT
);

CREATE TABLE Tantermek (
    terem_id   INT PRIMARY KEY AUTO_INCREMENT,
    terem_szam VARCHAR(10),
    kapacitas  INT,
    emelet     INT,
    tipus      VARCHAR(50)
);

CREATE TABLE Tantargyak (
    targy_id INT PRIMARY KEY AUTO_INCREMENT,
    nev      VARCHAR(100),
    het_ora  INT,
    kredit   INT,
    kotelezo VARCHAR(4)
);

INSERT INTO Diakok (nev, szul_ev, osztaly, atlag) VALUES
    ('Kovács Péter', 2006, '12.A', 4.2),
    ('Nagy Eszter',  2007, '11.B', 3.8),
    ('Szabó Bence',  2006, '12.C', 4.7);

INSERT INTO Tanarok (nev, tantargy, email, tapasztalat) VALUES
    ('Dr. Varga Ilona', 'Matematika',   'varga.ilona@petrik.hu',  15),
    ('Fekete Gábor',    'Informatika',  'fekete.gabor@petrik.hu',  8),
    ('Tóth Mária',      'Magyar nyelv', 'toth.maria@petrik.hu',   22);

INSERT INTO Tantermek (terem_szam, kapacitas, emelet, tipus) VALUES
    ('A101', 32, 1, 'Előadóterem'),
    ('B204', 20, 2, 'Számítógépterem'),
    ('C310', 28, 3, 'Labor');

INSERT INTO Tantargyak (nev, het_ora, kredit, kotelezo) VALUES
    ('Matematika',        4, 5, 'Igen'),
    ('Programozás',       6, 6, 'Igen'),
    ('Digitális kultúra', 2, 3, 'Nem');
