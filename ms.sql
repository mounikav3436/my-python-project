use pharmacy_store_db;
ALTER TABLE orders
ADD COLUMN shipping_city VARCHAR(50),
ADD COLUMN shipping_state VARCHAR(50),
ADD COLUMN shipping_pincode VARCHAR(10);
DESCRIBE orders;
ALTER TABLE orders ADD COLUMN requested_date DATETIME DEFAULT CURRENT_TIMESTAMP;

SELECT * FROM users;
DELETE FROM users WHERE id = 1;
SET SQL_SAFE_UPDATES = 0;

UPDATE products
SET category = TRIM(LOWER(category));
SET SQL_SAFE_UPDATES = 1;
-- Disable safe update mode if needed
SET SQL_SAFE_UPDATES = 0;

-- Remove leading/trailing spaces, make lowercase
UPDATE products
SET category = TRIM(LOWER(category));


UPDATE products
SET category = 'personal care'
WHERE category IN ('personalcare', 'Personalcare', 'Personal care');

UPDATE products SET category = 'nutrition' WHERE category IN ('Nutrition', 'nutritions');
UPDATE products SET category = 'health care' WHERE category IN ('healthcare', 'HealthCare');
-- Turn safe mode off if needed
SET SQL_SAFE_UPDATES = 0;

-- Normalize subcategory values
UPDATE products
SET subcategory = TRIM(LOWER(subcategory));

UPDATE products SET subcategory = 'Skin Care' WHERE subcategory = 'skin care';
UPDATE products SET subcategory = 'Hair Care' WHERE subcategory = 'hair care';
UPDATE products SET subcategory = 'Oral Care' WHERE subcategory = 'oral care';
UPDATE products SET subcategory = 'Hand and Foot Care' WHERE subcategory = 'hand and foot care';
UPDATE products SET subcategory = 'Skincare' WHERE subcategory = 'skincare'; -- pick only one preferred name!

UPDATE products SET category = 'Personal Care' WHERE category = 'personal care';
select * from orders;
select * from products;
