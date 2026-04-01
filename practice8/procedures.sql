-- A procedure to insert a new user by name and phone; if the user already exists, update their phone
CREATE OR REPLACE PROCEDURE insert_or_update_contact(
    p_name VARCHAR,
    p_phone VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    --We check if there is a contact with that name.
    IF EXISTS (SELECT 1 FROM contacts WHERE name = p_name) THEN
        --if the user already exists, update their phone
        UPDATE contacts 
        SET phone = p_phone
        WHERE name = p_name;
        RAISE NOTICE 'Contact updated: % - %', p_name, p_phone;
    ELSE
        --If not, insert a new contact.
        INSERT INTO contacts (name, phone) 
        VALUES (p_name, p_phone);
        RAISE NOTICE 'Contact inserted: % - %', p_name, p_phone;
    END IF;
END;
$$;

--A procedure to insert many new users from a list of names and phones - use a loop 
--and IF inside the procedure, validate phone correctness, and return all incorrect data
CREATE OR REPLACE PROCEDURE insert_many_contacts(
    contacts_data TEXT[]
)
LANGUAGE plpgsql
AS $$
DECLARE
    contact_record TEXT;
    contact_name VARCHAR;
    contact_phone VARCHAR;
    invalid_data TEXT := '';
BEGIN
    --We process each contact
    FOREACH contact_record IN ARRAY contacts_data
    LOOP
        --Dividing the string into name and phone (format: name,phone)
        contact_name := TRIM(split_part(contact_record, ',', 1));
        contact_phone := TRIM(split_part(contact_record, ',', 2));
        
        --Phone validation (must be 11-12 digits, start with 7 or 8)
        IF contact_phone !~ '^[78][0-9]{10}$' AND contact_phone !~ '^[0-9]{11}$' THEN
            invalid_data := invalid_data || contact_record || ' (Invalid phone format)\n';
            CONTINUE;
        END IF;
        
        --Name validation (not empty)
        IF contact_name = '' OR contact_name IS NULL THEN
            invalid_data := invalid_data || contact_record || ' (Name cannot be empty)\n';
            CONTINUE;
        END IF;
        
        --Inserting or updating a contact
        IF EXISTS (SELECT 1 FROM contacts WHERE name = contact_name) THEN
            UPDATE contacts 
            SET phone = contact_phone
            WHERE name = contact_name;
        ELSE
            INSERT INTO contacts (name, phone) 
            VALUES (contact_name, contact_phone);
        END IF;
        
    END LOOP;
    
    --Output incorrect data
    IF invalid_data != '' THEN
        RAISE NOTICE 'Invalid contacts:\n%', invalid_data;
    END IF;
END;
$$;

--A procedure to delete data from the table by username or phone
CREATE OR REPLACE PROCEDURE delete_contact_by_name_or_phone(
    p_identifier VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_deleted_count INTEGER;
BEGIN
    --Delete by name or phone number
    DELETE FROM contacts 
    WHERE name ILIKE p_identifier 
       OR phone = p_identifier;
    
    GET DIAGNOSTICS v_deleted_count = ROW_COUNT;
    
    IF v_deleted_count > 0 THEN
        RAISE NOTICE 'Deleted % contact(s)', v_deleted_count;
    ELSE
        RAISE NOTICE 'No contacts found matching: %', p_identifier;
    END IF;
END;
$$;