USE uzlet;

SELECT *
FROM husok;

SELECT *
FROM husok
WHERE ar = (SELECT MAX(ar) FROM husok);

SELECT *
FROM husok
WHERE mennyiseg = (SELECT MAX(mennyiseg) FROM husok);

SELECT szarmazasi_hely,
       COUNT(*) AS darab,
       SUM(mennyiseg) AS ossz_mennyiseg
FROM husok
GROUP BY szarmazasi_hely;

(SELECT *
 FROM tejtermekek
 ORDER BY ar DESC
 LIMIT 2)
UNION
(SELECT *
 FROM tejtermekek
 ORDER BY mennyiseg DESC
 LIMIT 1);

SET @atlag_tejtermek_ar = (SELECT AVG(ar) FROM tejtermekek);

SELECT @atlag_tejtermek_ar AS atlag_tejtermek_ar;

SELECT tabla, nev, mennyiseg
FROM (
    SELECT 'zoldsegek' AS tabla, nev, mennyiseg FROM zoldsegek
    UNION ALL
    SELECT 'gyumolcsok', nev, mennyiseg FROM gyumolcsok
    UNION ALL
    SELECT 'husok', nev, mennyiseg FROM husok
    UNION ALL
    SELECT 'tejtermekek', nev, mennyiseg FROM tejtermekek
) AS termekek
ORDER BY mennyiseg ASC
LIMIT 1;

SELECT id, nev
FROM zoldsegek;
