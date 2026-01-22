# Simple Retail POS System

This is a simple retail Point of Sale (POS) system demonstration developed in Python using SQLite. It demonstrates handling inventory with multiple MRPs (Maximum Retail Prices) for the same product.

## Project Structure

*   `pos_demo.py`: The main script that initializes the database and runs a demonstration of transactions (Purchase, Sale, Return, Damage).
*   `schema.sql`: The SQL schema for the database tables (`products`, `suppliers`, `product_transactions`).
*   `DESIGN.md`: Detailed design document explaining the database structure and logic.

## Prerequisites

*   Python 3.x
*   No external dependencies are required (uses standard `sqlite3`, `datetime`, `os` libraries).

## How to Run

To run the demonstration script, execute the following command in your terminal:

```bash
python3 pos_demo.py
```

This will:
1.  Create a local SQLite database file `pos_system.db` (if it exists, it will be recreated).
2.  Initialize the database tables.
3.  Run a series of sample transactions.
4.  Print the results and stock calculations to the console.

## Troubleshooting

### `ERR_PNPM_NO_PKG_MANIFEST` or `npm install` errors

If you are trying to run `pnpm install` or `npm install`, please note that this is **not a Node.js project**. It is a Python project. There is no `package.json` file because there are no JavaScript dependencies to install. Please use the python command above to run the project.
