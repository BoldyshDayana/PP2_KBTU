--1) insert_or_update_contact
-- Inserts a new contact or updates phone if name already exists.
CREATE OR REPLACE PROCEDURE insert_or_update_contact(
    p_name VARCHAR,
    p_phone VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_contact_id INTEGER;
BEGIN
    SELECT id INTO v_contact_id
    FROM contacts
    WHERE name ILIKE p_name
    LIMIT 1;

    IF v_contact_id IS NULL THEN
        INSERT INTO contacts (name, phone) VALUES (p_name, p_phone);
        RAISE NOTICE 'Contact "%" inserted.', p_name;
    ELSE
        UPDATE contacts SET phone = p_phone WHERE id = v_contact_id;
        RAISE NOTICE 'Contact "%" updated with phone %.', p_name, p_phone;
    END IF;
END;
$$;


-- 2) insert_many_contacts
-- Bulk-inserts contacts from an array of 'name,phone' strings.
CREATE OR REPLACE PROCEDURE insert_many_contacts(
    p_entries TEXT[]
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_entry  TEXT;
    v_parts  TEXT[];
    v_name   TEXT;
    v_phone  TEXT;
BEGIN
    FOREACH v_entry IN ARRAY p_entries LOOP
        v_parts := string_to_array(v_entry, ',');
        v_name  := trim(v_parts[1]);
        v_phone := trim(COALESCE(v_parts[2], ''));

        IF v_name = '' THEN
            RAISE NOTICE 'Skipping empty entry.';
            CONTINUE;
        END IF;

        INSERT INTO contacts (name, phone)
        VALUES (v_name, NULLIF(v_phone, ''))
        ON CONFLICT DO NOTHING;

        RAISE NOTICE 'Inserted: %', v_name;
    END LOOP;
END;
$$;


-- 3) delete_contact_by_name_or_phone
-- Deletes a contact matching by name OR phone (cascade removes phones rows).
CREATE OR REPLACE PROCEDURE delete_contact_by_name_or_phone(
    p_identifier VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_contact_id INTEGER;
BEGIN
    SELECT id INTO v_contact_id
    FROM contacts
    WHERE name ILIKE p_identifier
       OR phone ILIKE p_identifier
    LIMIT 1;

    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'No contact found matching "%".', p_identifier;
    END IF;

    DELETE FROM contacts WHERE id = v_contact_id;
    RAISE NOTICE 'Contact id=% deleted.', v_contact_id;
END;
$$;


-- 1. add_phone 
-- Adds a phone number to an existing contact.
CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone VARCHAR,
    p_type VARCHAR DEFAULT 'mobile'
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_contact_id INTEGER;
BEGIN
    -- Validate phone type
    IF p_type NOT IN ('home', 'work', 'mobile') THEN
        RAISE EXCEPTION 'Invalid phone type "%". Use home, work, or mobile.', p_type;
    END IF;
 
    -- Find contact
    SELECT id INTO v_contact_id
    FROM contacts
    WHERE name ILIKE p_contact_name
    LIMIT 1;
 
    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found.', p_contact_name;
    END IF;
 
    -- Check duplicate phone for this contact
    IF EXISTS (SELECT 1 FROM phones WHERE contact_id = v_contact_id AND phone = p_phone) THEN
        RAISE NOTICE 'Phone % already exists for contact %.', p_phone, p_contact_name;
        RETURN;
    END IF;
 
    INSERT INTO phones (contact_id, phone, type)
    VALUES (v_contact_id, p_phone, p_type);
 
    RAISE NOTICE 'Phone % (%) added to contact %.', p_phone, p_type, p_contact_name;
END;
$$;
 
 
-- 2. move_to_group 
-- Moves a contact to a group; creates the group if it does not exist.
CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_contact_id INTEGER;
    v_group_id INTEGER;
BEGIN
    -- Find contact
    SELECT id INTO v_contact_id
    FROM contacts
    WHERE name ILIKE p_contact_name
    LIMIT 1;
 
    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found.', p_contact_name;
    END IF;
 
    -- Find or create group
    SELECT id INTO v_group_id FROM groups WHERE name ILIKE p_group_name LIMIT 1;
 
    IF v_group_id IS NULL THEN
        INSERT INTO groups (name) VALUES (p_group_name) RETURNING id INTO v_group_id;
        RAISE NOTICE 'Group "%" created.', p_group_name;
    END IF;
 
    -- Move contact
    UPDATE contacts SET group_id = v_group_id WHERE id = v_contact_id;
 
    RAISE NOTICE 'Contact "%" moved to group "%".', p_contact_name, p_group_name;
END;
$$;
 
 
-- 3. search_contacts (function)
-- Extended search covering name, email, AND all rows in phones table.
CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE(
    id INTEGER,
    name VARCHAR,
    email VARCHAR,
    birthday DATE,
    group_name VARCHAR,
    phone VARCHAR,
    phone_type VARCHAR,
    created_at TIMESTAMP
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT ON (c.id, ph.phone)
           c.id,
           c.name,
           c.email,
           c.birthday,
           g.name AS group_name,
           ph.phone,
           ph.type AS phone_type,
           c.created_at
    FROM contacts c
    LEFT JOIN groups g ON g.id  = c.group_id
    LEFT JOIN phones ph ON ph.contact_id = c.id
    WHERE c.name  ILIKE '%' || p_query || '%'
       OR c.email ILIKE '%' || p_query || '%'
       OR ph.phone ILIKE '%' || p_query || '%'
    ORDER BY c.id, ph.phone;
END;
$$;