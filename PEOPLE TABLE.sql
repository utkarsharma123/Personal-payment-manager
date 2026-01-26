CREATE TABLE peoples(
	person_id SERIAL PRIMARY KEY,
	person_name VARCHAR(50) NOT NULL,
	create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	email VARCHAR(150),
	phone VARCHAR(20),
	CONSTRAINT unique_contact UNIQUE(email,phone)
);