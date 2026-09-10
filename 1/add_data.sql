USE Petrik;
INSERT INTO Diakok (nev, szul_ev, osztaly, atlag) VALUES
    ('Tóth Anna',      2007, '11.A', 4.5),
    ('Horváth Máté',   2006, '12.B', 3.9),
    ('Varga Zsófia',   2008, '10.C', 4.8),
    ('Kiss Dániel',    2007, '11.B', 3.4),
    ('Molnár Lilla',   2006, '12.A', 4.1),
    ('Németh Balázs',  2008, '10.A', 3.7),
    ('Szalai Réka',    2007, '11.C', 4.3),
    ('Farkas Ádám',    2008, '10.B', 3.6),
    ('Papp Vivien',    2006, '12.C', 4.6),
    ('Juhász Levente', 2007, '11.A', 3.2);

INSERT INTO Tanarok (nev, tantargy, email, tapasztalat) VALUES
    ('Szűcs Andrea',  'Fizika',      'szucs.andrea@petrik.hu',  10),
    ('Balogh Tamás',  'Testnevelés', 'balogh.tamas@petrik.hu',   6),
    ('Lakatos Éva',   'Kémia',       'lakatos.eva@petrik.hu',   18),
    ('Simon Zoltán',  'Angol nyelv', 'simon.zoltan@petrik.hu',   9),
    ('Nagy Krisztina','Biológia',    'nagy.krisztina@petrik.hu', 14),
    ('Fodor Attila',  'Földrajz',    'fodor.attila@petrik.hu',    7),
    ('Török Ildikó',  'Német nyelv', 'torok.ildiko@petrik.hu',   11),
    ('Bíró Csaba',    'Informatika', 'biro.csaba@petrik.hu',      5),
    ('Szabó Emese',   'Matematika',  'szabo.emese@petrik.hu',    20),
    ('Katona Péter',  'Történelem',  'katona.peter@petrik.hu',   13);


INSERT INTO Tantermek (terem_szam, kapacitas, emelet, tipus) VALUES
    ('A102', 24, 1, 'Előadóterem'),
    ('B105', 18, 2, 'Labor'),
    ('D001', 60, 0, 'Tornaterem'),
    ('B210', 15, 2, 'Könyvtár'),
    ('A201', 26, 2, 'Előadóterem'),
    ('C112', 22, 1, 'Számítógépterem'),
    ('C205', 16, 2, 'Labor'),
    ('D002', 45, 0, 'Tornaterem'),
    ('A305', 12, 3, 'Könyvtár'),
    ('B302', 30, 3, 'Előadóterem');

INSERT INTO Tantargyak (nev, het_ora, kredit, kotelezo) VALUES
    ('Történelem',  3, 4, 'Igen'),
    ('Fizika',      3, 4, 'Igen'),
    ('Angol nyelv', 4, 4, 'Igen'),
    ('Testnevelés', 5, 2, 'Igen'),
    ('Rajz',        1, 2, 'Nem'),
    ('Biológia',    2, 3, 'Igen'),
    ('Földrajz',    2, 3, 'Igen'),
    ('Német nyelv', 3, 3, 'Nem'),
    ('Kémia',       2, 3, 'Igen'),
    ('Ének-zene',   1, 2, 'Nem');
