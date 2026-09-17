-- Active: 1789035636905@@127.0.0.1@3306
USE Petrik;

SELECT * FROM Diakok;

SELECT nev, atlag
FROM Diakok
ORDER BY atlag DESC;

SELECT nev, osztaly
FROM Diakok
WHERE atlag > 4.0;

SELECT nev, tantargy
FROM Tanarok
WHERE tapasztalat > 10;

SELECT terem_szam, kapacitas
FROM Tantermek
ORDER BY kapacitas DESC;

SELECT 