# Simple Retail POS System Design

This document describes a simple retail financial / POS system using only 3 database tables.

## 1. Table Structure

We use three tables to track products, suppliers, and all inventory movements.

### `products`
Stores unique product details.
*   **product_id**: Unique ID for the product (Primary Key).
*   **product_name**: Name of the product (e.g., "Lux Soap 150g").
*   **barcode**: The barcode printed on the product (must be unique).

### `suppliers`
Stores supplier details.
*   **supplier_id**: Unique ID for the supplier (Primary Key).
*   **supplier_name**: Name of the supplier.

### `product_transactions`
The main table that records every action (buying, selling, returning).
*   **transaction_id**: Unique ID for the transaction.
*   **product_id**: Links to the `products` table.
*   **supplier_id**: Links to the `suppliers` table (Optional, for Purchases).
*   **barcode**: Barcode of the product (for history/verification).
*   **mrp**: Maximum Retail Price (The price printed on the pack).
*   **quantity**: Number of items in this transaction.
*   **unit_price**: The actual price per item (Cost Price for purchases, Selling Price for sales).
*   **total_amount**: `quantity` × `unit_price`.
*   **transaction_type**: One of: `PURCHASE`, `SALE`, `DAMAGE`, `RETURN`.
*   **transaction_date**: When the transaction happened.

---

## 2. Lux Soap Example (Handling MRP Changes)

One of the key rules is that a product keeps the same barcode even if the MRP changes. Since we store `mrp` in the transaction table, we can track stock for different prices separately.

**Scenario:**
1.  **Product**: "Lux Soap 150g" (Barcode: `890123`).
2.  **Jan 1st**: You buy 50 soaps from the supplier. The MRP printed on them is **150/=.**
3.  **Feb 1st**: The price increases. You buy 30 new soaps. The MRP printed on them is **165/=**.

**In the Database:**

| Date | Type | Product | Barcode | MRP | Qty |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Jan 1 | PURCHASE | Lux Soap | 890123 | **150** | 50 |
| Feb 1 | PURCHASE | Lux Soap | 890123 | **165** | 30 |

The system now knows you have two "batches" of the same Lux Soap:
*   50 items at MRP 150
*   30 items at MRP 165

---

## 3. Stock Calculation Logic

To find out how many items you have in stock, we look at the transaction history. Since different MRPs are effectively different items on the shelf, we calculate stock **per MRP**.

**Formula:**
`Stock = (Total Purchased + Customer Returns) - (Total Sold + Damaged)`

**Example Calculation (Lux Soap):**

*   **MRP 150 Batch:**
    *   Purchased: 50
    *   Sold: 2
    *   Returned by Customer: 1
    *   **Stock**: 50 - 2 + 1 = **49**

*   **MRP 165 Batch:**
    *   Purchased: 30
    *   Sold: 1
    *   Damaged: 1
    *   **Stock**: 30 - 1 - 1 = **28**

---

## 4. Barcode POS Flow

This is how the system works when a cashier scans a product at the counter.

1.  **Scan Barcode**: The cashier scans `890123` (Lux Soap).
2.  **Lookup**: The system finds the product name "Lux Soap 150g".
3.  **Select MRP**: The system checks the current stock.
    *   If only one MRP exists in stock (e.g., only 150/=), it automatically selects it.
    *   If multiple MRPs exist (you have both 150/= and 165/= on the shelf), the system creates a popup asking the cashier: *"Which Price? 150 or 165?"*. The cashier checks the pack and selects the correct one.
4.  **Add to Bill**: The item is added to the bill with the selected MRP.
5.  **Checkout**: When the sale is finalized, a `SALE` transaction is saved to the `product_transactions` table, reducing the stock for that specific MRP.
