-- Create Tables

CREATE TABLE IF NOT EXISTS sections (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    next_section_id INTEGER REFERENCES sections(id)
);

CREATE TABLE IF NOT EXISTS workers (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    section_id INTEGER REFERENCES sections(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS items (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    unit TEXT NOT NULL,
    default_target INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS production_logs (
    id SERIAL PRIMARY KEY,
    worker_id INTEGER REFERENCES workers(id),
    item_id INTEGER REFERENCES items(id),
    section_id INTEGER REFERENCES sections(id),
    date DATE NOT NULL,
    target INTEGER NOT NULL,
    actual INTEGER NOT NULL,
    input_material FLOAT NOT NULL,
    output_material FLOAT NOT NULL,
    wastage FLOAT NOT NULL,
    overtime_hours FLOAT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS attendance (
    id SERIAL PRIMARY KEY,
    worker_id INTEGER REFERENCES workers(id),
    section_id INTEGER REFERENCES sections(id),
    date DATE NOT NULL,
    present BOOLEAN NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS machine_downtime (
    id SERIAL PRIMARY KEY,
    section_id INTEGER REFERENCES sections(id),
    machine_name TEXT NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    remarks TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS requisitions (
    id SERIAL PRIMARY KEY,
    item_id INTEGER REFERENCES items(id),
    section_id INTEGER REFERENCES sections(id),
    quantity INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    remarks TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Sample Data

INSERT INTO sections (name, next_section_id) VALUES
    ('Raw Material', 2),
    ('Processing', NULL);

INSERT INTO workers (name, section_id) VALUES
    ('Beer Bahadur', 1),
    ('Gita Devi', 1),
    ('Ram Prasad', 2),
    ('Sita Kumari', 2),
    ('Hari Krishna', 1);

INSERT INTO items (name, unit, default_target) VALUES
    ('Khada Butta 6 inch', 'pieces', 100),
    ('Corn Flour 1kg', 'kg', 50),
    ('Soybean 500g', 'kg', 75),
    ('Wheat Grain 2kg', 'kg', 120),
    ('Rice 1kg', 'kg', 90),
    ('Sugar 500g', 'kg', 60),
    ('Salt 1kg', 'kg', 80),
    ('Cooking Oil 1L', 'liter', 40),
    ('Spices 200g', 'pieces', 30),
    ('Packaging Material', 'pieces', 200);

INSERT INTO production_logs (worker_id, item_id, section_id, date, target, actual, input_material, output_material, wastage, overtime_hours) VALUES
    (1, 1, 1, CURRENT_DATE, 100, 75, 400.0, 350.0, 50.0, 0.0),
    (2, 2, 1, CURRENT_DATE, 50, 60, 200.0, 180.0, 20.0, 2.0),
    (3, 3, 2, CURRENT_DATE, 75, 70, 150.0, 140.0, 10.0, 0.0),
    (4, 4, 2, CURRENT_DATE, 120, 130, 250.0, 240.0, 10.0, 0.67),
    (1, 5, 1, CURRENT_DATE, 90, 85, 300.0, 280.0, 20.0, 0.0);

INSERT INTO attendance (worker_id, section_id, date, present) VALUES
    (1, 1, CURRENT_DATE, TRUE),
    (2, 1, CURRENT_DATE, TRUE),
    (3, 2, CURRENT_DATE, TRUE),
    (4, 2, CURRENT_DATE, TRUE),
    (5, 1, CURRENT_DATE, FALSE);

INSERT INTO machine_downtime (section_id, machine_name, start_time, end_time, remarks) VALUES
    (1, 'Machine1', NOW() - INTERVAL '2 hours', NOW() - INTERVAL '1 hour', 'Routine maintenance'),
    (2, 'Machine2', NOW() - INTERVAL '30 minutes', NOW(), 'Minor fault');

INSERT INTO requisitions (item_id, section_id, quantity, status) VALUES
    (1, 1, 10, 'pending'),
    (2, 2, 5, 'approved');


