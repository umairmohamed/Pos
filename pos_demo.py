import sqlite3
import datetime

DB_FILE = "pos_system.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    with open("schema.sql", "r") as f:
        conn.executescript(f.read())
    conn.close()

def add_product(name, barcode):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO products (product_name, barcode) VALUES (?, ?)", (name, barcode))
        conn.commit()
        print(f"Added Product: {name} ({barcode})")
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        print(f"Product with barcode {barcode} already exists.")
        cursor.execute("SELECT product_id FROM products WHERE barcode = ?", (barcode,))
        return cursor.fetchone()[0]
    finally:
        conn.close()

def add_supplier(name):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO suppliers (supplier_name) VALUES (?)", (name,))
    conn.commit()
    print(f"Added Supplier: {name}")
    pid = cursor.lastrowid
    conn.close()
    return pid

def add_transaction(product_id, supplier_id, barcode, mrp, quantity, unit_price, trans_type):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    total_amount = quantity * unit_price

    cursor.execute("""
        INSERT INTO product_transactions
        (product_id, supplier_id, barcode, mrp, quantity, unit_price, total_amount, transaction_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (product_id, supplier_id, barcode, mrp, quantity, unit_price, total_amount, trans_type))

    conn.commit()
    print(f"Transaction: {trans_type} | Product ID: {product_id} | MRP: {mrp} | Qty: {quantity}")
    conn.close()

def get_stock(product_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # We need to group by MRP because different MRPs are distinct stock items (effectively)
    cursor.execute("""
        SELECT mrp, transaction_type, SUM(quantity)
        FROM product_transactions
        WHERE product_id = ?
        GROUP BY mrp, transaction_type
    """, (product_id,))

    rows = cursor.fetchall()
    conn.close()

    stock_by_mrp = {}

    for mrp, t_type, qty in rows:
        if mrp not in stock_by_mrp:
            stock_by_mrp[mrp] = 0

        if t_type == 'PURCHASE':
            stock_by_mrp[mrp] += qty
        elif t_type == 'SALE':
            stock_by_mrp[mrp] -= qty
        elif t_type == 'RETURN': # Assuming Customer Return
            stock_by_mrp[mrp] += qty
        elif t_type == 'DAMAGE':
            stock_by_mrp[mrp] -= qty

    return stock_by_mrp

def main():
    # Initialize
    import os
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    init_db()

    print("--- Setting up Data ---")
    # Setup Data
    lux_id = add_product("Lux Soap 150g", "890123")
    sup_id = add_supplier("Unilever Distributor")

    print("\n--- 1. Purchase: Old MRP ---")
    # 1. Purchase Lux at 150 MRP
    # Buying 50 items. Unit price might be less than MRP (margin). Say 140.
    add_transaction(lux_id, sup_id, "890123", 150.0, 50, 140.0, "PURCHASE")

    print("\n--- 2. Purchase: New MRP (Price Change) ---")
    # 2. Purchase Lux at 165 MRP (Inflation)
    # Buying 30 items. Unit price 155.
    add_transaction(lux_id, sup_id, "890123", 165.0, 30, 155.0, "PURCHASE")

    print("\n--- Current Stock ---")
    stock = get_stock(lux_id)
    print(f"Stock for Lux Soap: {stock}")
    # Expected: {150.0: 50, 165.0: 30}

    print("\n--- 3. Sale: Selling Old Stock ---")
    # Customer buys 2 Lux soaps of MRP 150
    # Unit price for Sale is usually MRP, or discounted. Let's assume MRP.
    add_transaction(lux_id, None, "890123", 150.0, 2, 150.0, "SALE")

    print("\n--- 4. Sale: Selling New Stock ---")
    # Customer buys 1 Lux soap of MRP 165
    add_transaction(lux_id, None, "890123", 165.0, 1, 165.0, "SALE")

    print("\n--- 5. Customer Return ---")
    # Customer returns 1 Lux soap of MRP 150
    add_transaction(lux_id, None, "890123", 150.0, 1, 150.0, "RETURN")

    print("\n--- 6. Damage ---")
    # 1 Lux soap of MRP 165 is found damaged
    add_transaction(lux_id, None, "890123", 165.0, 1, 0.0, "DAMAGE") # Unit price 0 or cost? Keeping 0 for now as loss.

    print("\n--- Final Stock Calculation ---")
    stock = get_stock(lux_id)
    print(f"Final Stock for Lux Soap: {stock}")

    # Verification
    # 150 MRP: +50 (Purch) - 2 (Sale) + 1 (Return) = 49
    # 165 MRP: +30 (Purch) - 1 (Sale) - 1 (Damage) = 28

    assert stock[150.0] == 49
    assert stock[165.0] == 28
    print("Verification Successful!")

if __name__ == "__main__":
    main()
