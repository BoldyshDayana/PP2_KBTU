-- A function that returns all records matching a pattern (part of name, surname, or phone number)
CREATE OR REPLACE FUNCTION search_contacts_pattern(
    search_pattern TEXT
)
RETURNS TABLE(
    id INTEGER,
    name VARCHAR,
    phone VARCHAR,
    created_at TIMESTAMP
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT c.id, c.name, c.phone, c.created_at
    FROM contacts c
    WHERE c.name ILIKE '%' || search_pattern || '%'
       OR c.phone ILIKE '%' || search_pattern || '%'
    ORDER BY c.name;
END;
$$;

-- A function that queries data from the table with pagination (by LIMIT and OFFSET)
CREATE OR REPLACE FUNCTION get_contacts_paginated(
    p_limit INTEGER,
    p_offset INTEGER
)
RETURNS TABLE(
    id INTEGER,
    name VARCHAR,
    phone VARCHAR,
    created_at TIMESTAMP,
    total_count BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_total BIGINT;
BEGIN
    -- We get the total number of records
    SELECT COUNT(*) INTO v_total FROM contacts;
    
    -- Returning the data page
    RETURN QUERY
    SELECT c.id, c.name, c.phone, c.created_at, v_total
    FROM contacts c
    ORDER BY c.name
    LIMIT p_limit
    OFFSET p_offset;
END;
$$;