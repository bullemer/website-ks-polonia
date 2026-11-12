-- Assign mitgliedsnummer to all members that don't have one yet
-- Format: POL-2026-NNNN using the member_number_seq sequence

DO $$
DECLARE
    r RECORD;
    v_seq BIGINT;
    v_nummer TEXT;
BEGIN
    FOR r IN
        SELECT id FROM members
        WHERE mitgliedsnummer IS NULL
        ORDER BY id
    LOOP
        v_seq := nextval('member_number_seq');
        v_nummer := 'POL-2026-' || LPAD(v_seq::text, 4, '0');
        UPDATE members SET mitgliedsnummer = v_nummer WHERE id = r.id;
    END LOOP;

    RAISE NOTICE 'Assigned mitgliedsnummer to % members', (SELECT count(*) FROM members WHERE mitgliedsnummer LIKE 'POL-2026-%');
END $$;
