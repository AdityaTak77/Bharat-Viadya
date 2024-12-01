import sqlite3

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('products.db')
cursor = conn.cursor()

# Create the products table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_category TEXT NOT NULL,
        product_name TEXT NOT NULL,
        price REAL NOT NULL,
        link TEXT NOT NULL,
        ingredients TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# Insert sample data into the products table
cursor.execute('''
    INSERT INTO products (product_category, product_name, price, link, ingredients)
    VALUES (
        'Hair Oil', 
        'Mahaneel Tailam', 
        900.00, 
        'https://ashtveda.org/product/anti-greying-anti-hairfall-oil-mahaneel-tailam/', 
        'vast, Mainfal, katsraiya, bhringraj, Loh churan, Triphala, Arjun, Neel, Til Tail, Parad Bhasam, Mahanila Taila'
    )
''')

# Commit changes and close the connection
conn.commit()
conn.close()
