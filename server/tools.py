import sqlite3
import json
from langchain.tools import tool

DB_PATH = "db/library.db"

@tool
def find_books(q: str, by: str = "title"):
    """Search for books by title or author."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        query = f"SELECT * FROM books WHERE {by} LIKE ?"
        cursor.execute(query, (f"%{q}%",))
        return cursor.fetchall()

@tool
def create_order(customer_id: int, items: list):
    """Creates a new order and reduces stock. items: [{'isbn': str, 'qty': int}]"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO orders (customer_id) VALUES (?)", (customer_id,))
        order_id = cursor.lastrowid
        for item in items:
            cursor.execute("INSERT INTO order_items VALUES (?, ?, ?)", (order_id, item['isbn'], item['qty']))
            cursor.execute("UPDATE books SET stock = stock - ? WHERE isbn = ?", (item['qty'], item['isbn']))
        conn.commit()
        return f"Order {order_id} created successfully."

@tool
def restock_book(isbn: str, qty: int):
    """CRITICAL: Use this tool whenever you need to increase the stock level of a book in the database.
    You MUST call this tool to perform the update before confirming it to the user."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE books SET stock = stock + ? WHERE isbn = ?", (qty, isbn))
        conn.commit()
        return f"Stock updated for {isbn}."

@tool
def update_price(isbn: str, price: float):
    """Updates the price of a book."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE books SET price = ? WHERE isbn = ?", (price, isbn))
        conn.commit()
        return "Price updated."

@tool
def order_status(order_id: int):
    """Check the status and items of a specific order, including book titles."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        # Use a JOIN to get the title from the books table
        query = """
                SELECT b.title, oi.isbn, oi.quantity 
                FROM order_items oi
                JOIN books b ON oi.isbn = b.isbn
                WHERE oi.order_id = ?
            """
        cursor.execute(query, (order_id,))
        results = cursor.fetchall()

        if not results:
            return f"No items found for order ID {order_id}."

        return results

@tool
def inventory_summary():
    """Lists all low-stock titles (stock < 5)."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT title, stock FROM books WHERE stock < 5")
        return cursor.fetchall()

# List of tools to give to the agent
tools = [find_books, create_order, restock_book, update_price, order_status, inventory_summary]