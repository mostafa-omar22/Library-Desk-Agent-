-- Seed 10 Books
INSERT INTO books (isbn, title, author, price, stock) VALUES
('978-0132350884', 'Clean Code', 'Robert C. Martin', 35.99, 15),
('978-0201616224', 'The Pragmatic Programmer', 'Andrew Hunt', 42.00, 8),
('978-0134494166', 'Clean Architecture', 'Robert C. Martin', 32.50, 12),
('978-1617294532', 'Deep Learning with Python', 'Francois Chollet', 45.00, 5),
('978-0596007126', 'Head First Design Patterns', 'Eric Freeman', 38.00, 20),
('978-1491950296', 'Building Microservices', 'Sam Newman', 40.00, 3),
('978-0134685991', 'Effective Java', 'Joshua Bloch', 45.00, 10),
('978-0262033848', 'Introduction to Algorithms', 'Cormen et al.', 85.00, 7),
('978-1449331818', 'Learning Python', 'Mark Lutz', 50.00, 4),
('978-0596517748', 'JavaScript: The Good Parts', 'Douglas Crockford', 25.00, 25);

-- Seed 6 Customers
INSERT INTO customers (name, email) VALUES
('Alice Vance', 'alice@example.com'),
('Bob Smith', 'bob@example.com'),
('Charlie Day', 'charlie@example.com'),
('Diana Prince', 'diana@example.com'),
('Ethan Hunt', 'ethan@example.com'),
('Fiona Gallagher', 'fiona@example.com');

-- Seed 4 Orders
INSERT INTO orders (customer_id) VALUES (1), (2), (3), (4);
INSERT INTO order_items (order_id, isbn, quantity) VALUES
(1, '978-0132350884', 1),
(2, '978-0201616224', 2),
(3, '978-1617294532', 1),
(4, '978-0596007126', 1);