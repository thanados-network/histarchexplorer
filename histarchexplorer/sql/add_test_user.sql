DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM web.user WHERE username = 'Alice') THEN
        RAISE NOTICE 'User ''Alice'' already exists. Deleting...';
        DELETE FROM web.user WHERE username = 'Alice';
    END IF;
END $$;

INSERT INTO web.user (group_id, username, password, active, email, password_reset_code, password_reset_date, unsubscribe_code)
VALUES
  ((SELECT id FROM web.group WHERE name = 'admin'), 'Alice', '$2b$12$yPQCBsSQdZxESEz79SFiOOZBLG2GZ9Cc2rzVMgZxXyW2y3T499LYK', True, 'alice@example.com', '123', current_timestamp, NULL);
