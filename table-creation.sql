-- Inventory Table
CREATE TABLE inventory_item (
  item_id SERIAL PRIMARY KEY,
  item_name TEXT NOT NULL,
  item_img TEXT NOT NULL,
  item_stock INT DEFAULT 0,
  item_is_consumable BOOLEAN DEFAULT false,
  item_desc TEXT
);

-- Student Requests Table (master request info)
CREATE TABLE student_request (
  request_id SERIAL PRIMARY KEY,
  item_id INTEGER REFERENCES inventory_item(item_id),
  student_id TEXT NOT NULL,
  student_name TEXT NOT NULL,
  course TEXT NOT NULL,
  section TEXT NOT NULL,
  prof_name TEXT NOT NULL,
  program TEXT NOT NULL CHECK (program IN ('Electronics', 'Science', 'Nursing', 'HTM', 'Criminology')),
  date_filed DATE NOT NULL,
  date_needed DATE NOT NULL,
  time_from TIME NOT NULL,
  time_to TIME NOT NULL,
  time_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- drop table student_request
-- drop table requested_items

-- Requested Items Table (items linked to a request)
CREATE TABLE requested_items (
  requested_item_id SERIAL PRIMARY KEY,
  request_id INTEGER NOT NULL REFERENCES student_request(request_id) ON DELETE CASCADE,
  item_id INTEGER NOT NULL REFERENCES inventory_item(item_id),
  quantity INTEGER NOT NULL CHECK (quantity > 0)
);

-- Table to store pending requests (before confirmation)
CREATE TABLE pending_requests (
    pending_request_id SERIAL PRIMARY KEY,
    student_name VARCHAR(100),
    student_id VARCHAR(20),
    prof_name VARCHAR(100),
    program VARCHAR(100),
    course VARCHAR(100),
    section VARCHAR(50),
    date_filed DATE,
    date_needed DATE,
    time_from TIME,
    time_to TIME,
    items JSONB,
    status VARCHAR(20) DEFAULT 'pending',
    submitted_at TIMESTAMP DEFAULT NOW(),
    time_created TIMESTAMP DEFAULT NOW()
);


-- Sample Data Insert (pictures are placeholders)
INSERT INTO inventory_item (item_name, item_img, item_stock, item_is_consumable, item_desc)
VALUES 
  ('Soldering Iron', 'https://picsum.photos/id/237/200/300', 15, false, 'A tool used for soldering electronic components.'),
  ('Multimeter', 'https://picsum.photos/id/1011/200/300', 10, false, 'Used for measuring voltage, current, and resistance.'),
  ('Breadboard', 'https://picsum.photos/id/1025/200/300', 25, false, 'A tool for prototyping circuits without soldering.'),
  ('Jumper Wires', 'https://picsum.photos/id/1027/200/300', 50, true, 'Flexible wires used for making temporary connections in a circuit.'),
  ('Resistor Pack', 'https://picsum.photos/id/1020/200/300', 100, true, 'Pack of assorted resistors for various projects.'),
  ('Capacitor Pack', 'https://picsum.photos/id/1035/200/300', 100, true, 'Pack of assorted capacitors for various projects.'),
  ('Arduino Uno', 'https://picsum.photos/id/1031/200/300', 20, false, 'An open-source microcontroller board for building electronics projects.'),
  ('Raspberry Pi', 'https://picsum.photos/id/1033/200/300', 15, false, 'A small, affordable computer for learning programming and building projects.'),
  ('USB Cable', 'https://picsum.photos/id/1037/200/300', 40, true, 'Standard USB cable for connecting devices to computers or power supplies.'),
  ('USB Cables', 'https://picsum.photos/id/1037/200/300', 40, true, 'Standard USB cable for connecting devices to computers or power supplies.'),
  ('Power Supply', 'https://picsum.photos/id/1041/200/300', 30, false, 'A power source for electronic projects, typically providing regulated voltage.');
  


----------------------------------------------- TEST QUERIES -----------------------------------------------

-- SELECT * FROM inventory_item;
-- DROP TABLE inventory_item CASCADE;

-- select * from pending_requests
-- SELECT jsonb_pretty(items) FROM pending_requests;

-- SELECT items->0->>'name' AS first_item_name FROM pending_requests;

-- SELECT
--     jsonb_array_elements(items)->>'name' AS item_name
-- FROM
--     pending_requests;

-- -- display item list borrowed per student
-- SELECT
--     student_name,
--     jsonb_array_elements(items)->>'name' AS item_name
-- FROM
--     pending_requests;
    
    
-- SELECT * FROM pending_requests WHERE status = 'pending';
-- SELECT * FROM pending_requests WHERE status = 'approved';
-- SELECT * FROM pending_requests WHERE status = 'denied';
