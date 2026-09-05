-- Migration 008: Update Basketball U10 to U12 and set Finkenau as location
UPDATE teams
SET 
    nummer = 'BB-U12',
    mannschaftsart = 'Jugend U12',
    mannschaftsname = 'Basketball U12 (Jugend)',
    webpage_url = '/seiten/basketball-jugend-u12',
    training_location = 'Sporthalle am Sportplatz Finkenau, Finkenau 38, 22081 Hamburg'
WHERE mannschaftsname ILIKE '%Basketball%U10%' OR nummer = 'BB-U10';

UPDATE teams
SET 
    training_times = 'Dienstag, 18:00 – 19:30 Uhr',
    training_location = 'Sporthalle am Sportplatz Finkenau, Finkenau 38, 22081 Hamburg'
WHERE mannschaftsname ILIKE '%Basketball%Ü35%' OR mannschaftsname ILIKE '%Basketball%Ue35%' OR nummer = 'BB-UE35';

UPDATE divisions
SET description = 'Basketball – Kinder U12 und Herren Ü35'
WHERE name = 'Basketball';
