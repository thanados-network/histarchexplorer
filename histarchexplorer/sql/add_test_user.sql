DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM web.user WHERE username = 'Alice') THEN
        RAISE NOTICE 'User ''Alice'' already exists. Deleting...';
        DELETE FROM web.user WHERE username = 'Alice';
    END IF;
END $$;

-- Create test user
INSERT INTO web.user (group_id, username, password, active, email, password_reset_code, password_reset_date, unsubscribe_code)
VALUES
  ((SELECT id FROM web.group WHERE name = 'admin'), 'Alice', '$2b$12$yPQCBsSQdZxESEz79SFiOOZBLG2GZ9Cc2rzVMgZxXyW2y3T499LYK', True, 'alice@example.com', '123', current_timestamp, NULL),
  ((SELECT id FROM web.group WHERE name = 'admin'), 'Inactive', '$2b$12$yPQCBsSQdZxESEz79SFiOOZBLG2GZ9Cc2rzVMgZxXyW2y3T499LYK', False, 'inactive@example.com', NULL, NULL, NULL),
  ((SELECT id FROM web.group WHERE name = 'manager'), 'Manager', '$2b$12$yPQCBsSQdZxESEz79SFiOOZBLG2GZ9Cc2rzVMgZxXyW2y3T499LYK', True, 'manager@example.com', '5678', '2020-02-02', '123'),
  ((SELECT id FROM web.group WHERE name = 'contributor'), 'Contributor', '$2b$12$yPQCBsSQdZxESEz79SFiOOZBLG2GZ9Cc2rzVMgZxXyW2y3T499LYK', True, 'contirbutor@example.com', NULL, NULL, NULL),
  ((SELECT id FROM web.group WHERE name = 'editor'), 'Editor', '$2b$12$yPQCBsSQdZxESEz79SFiOOZBLG2GZ9Cc2rzVMgZxXyW2y3T499LYK', True, 'editor@example.com', NULL, NULL, NULL),
  ((SELECT id FROM web.group WHERE name = 'readonly'), 'Readonly', '$2b$12$yPQCBsSQdZxESEz79SFiOOZBLG2GZ9Cc2rzVMgZxXyW2y3T499LYK', True, 'readonly@example.com', NULL, NULL, NULL);
