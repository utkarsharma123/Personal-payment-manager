CREATE TABLE my_account(
	account_id SERIAL PRIMARY KEY,
	account_name VARCHAR(50) NOT NULL,
	balance NUMERIC DEFAULT 0
);
