CREATE TABLE inventory_item (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  image_url TEXT,
  amount_in_stock INT DEFAULT 0
  consumable BOOLEAN DEFAULT false,
  short_description TEXT
);

-- Table to store student requests
CREATE TABLE student_requests (
    id SERIAL PRIMARY KEY,
    student_name TEXT NOT NULL,
    student_id TEXT NOT NULL,
    professor_name TEXT NOT NULL,
    course TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table to store requested items per request
CREATE TABLE requested_items (
    id SERIAL PRIMARY KEY,
    request_id INTEGER NOT NULL REFERENCES student_requests(id) ON DELETE CASCADE,
    item_id INTEGER NOT NULL REFERENCES inventory_item(id),
    quantity INTEGER NOT NULL CHECK (quantity > 0)
);

CREATE TABLE student_request (
  id SERIAL PRIMARY KEY,
  student_id TEXT NOT NULL,
  student_name TEXT NOT NULL,
  course TEXT NOT NULL,
  section TEXT NOT NULL,
  program TEXT NOT NULL CHECK (program IN ('Electronics', 'Science', 'Nursing', 'HTM', 'Criminology')),
  date_filed DATE NOT NULL,
  date_needed DATE NOT NULL,
  time_needed_from TIME NOT NULL,
  time_needed_to TIME NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

drop table request_form

INSERT INTO inventory_item (name, image_url, amount_in_stock, consumable, short_description)
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
  ('Power Supply', 'https://picsum.photos/id/1041/200/300', 30, false, 'A power source for electronic projects, typically providing regulated voltage.');


SELECT * FROM inventory_item;
DROP TABLE inventory_item
