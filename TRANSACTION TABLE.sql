CREATE TABLE transactions(
	transaction_id SERIAL PRIMARY KEY,
	amount NUMERIC NOT NULL,
	my_account_id INT REFERENCES my_account(account_id),
	person_id INT REFERENCES peoples(person_id),
	transaction_type VARCHAR(10), --PAID/RECEIVED
	transaction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	note TEXT
);