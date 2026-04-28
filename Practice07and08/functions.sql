CREATE OR REPLACE FUNCTION search_phonebook(pattern TEXT)
RETURNS TABLE (
    id INT,
    first_name VARCHAR,
    phone VARCHAR
)
AS $$
BEGIN
    RETURN QUERY
    SELECT p.id, p.first_name, p.phone
    FROM phonebook p
    WHERE p.first_name ILIKE '%' || pattern || '%'
       OR p.phone ILIKE '%' || pattern || '%';
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION get_phonebook_paginated(lim INT, offs INT)
RETURNS TABLE (
    id INT,
    first_name VARCHAR,
    phone VARCHAR
)
AS $$
BEGIN
    RETURN QUERY
    SELECT p.id, p.first_name, p.phone
    FROM phonebook p
    ORDER BY p.id
    LIMIT lim OFFSET offs;
END;
$$ LANGUAGE plpgsql;