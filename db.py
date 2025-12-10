# db.py
import sqlite3
from datetime import date

DB_PATH = "client_tracker.db"


def get_connection():
    if "conn" not in globals():
        global conn
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT,
            status TEXT,
            po_date TEXT,
            initial_training_date TEXT,
            go_live_date TEXT,
            fame_version TEXT,
            pocket_fame INTEGER DEFAULT 0,
            state TEXT,
            initial_manpower INTEGER,
            num_users INTEGER,
            num_branches INTEGER,
            proforma_integration INTEGER DEFAULT 0,
            einvoice_integration INTEGER DEFAULT 0,
            kyc_aadhaar INTEGER DEFAULT 0,
            kyc_bank INTEGER DEFAULT 0,
            sms_integration INTEGER DEFAULT 0,
            sendmail_payslips INTEGER DEFAULT 0,
            sendmail_invoice INTEGER DEFAULT 0,
            bank_integration INTEGER DEFAULT 0,
            psf TEXT,
            contact_name TEXT,
            contact_designation TEXT,
            contact_phone TEXT,
            contact_email TEXT,
            notes TEXT
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS client_modules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            module_name TEXT NOT NULL,
            customizations TEXT,
            is_live INTEGER DEFAULT 0,
            FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS client_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            log_date TEXT,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT,
            owner TEXT,
            remarks TEXT,
            FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
        )
        """
    )

    conn.commit()


# ------- Clients -------
def get_all_clients():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM clients ORDER BY name COLLATE NOCASE;")
    return cur.fetchall()


def get_client_by_id(cid: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM clients WHERE id = ?;", (cid,))
    return cur.fetchone()


def create_client(data: dict):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO clients
        (name, code, status, po_date, initial_training_date, go_live_date,
         fame_version, pocket_fame, state,
         initial_manpower, num_users, num_branches,
         proforma_integration, einvoice_integration, kyc_aadhaar, kyc_bank,
         sms_integration, sendmail_payslips, sendmail_invoice, bank_integration,
         psf, contact_name, contact_designation, contact_phone, contact_email,
         notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data["name"],
            data.get("code"),
            data.get("status"),
            data.get("po_date"),
            data.get("initial_training_date"),
            data.get("go_live_date"),
            data.get("fame_version"),
            1 if data.get("pocket_fame") else 0,
            data.get("state"),
            data.get("initial_manpower"),
            data.get("num_users"),
            data.get("num_branches"),
            1 if data.get("proforma_integration") else 0,
            1 if data.get("einvoice_integration") else 0,
            1 if data.get("kyc_aadhaar") else 0,
            1 if data.get("kyc_bank") else 0,
            1 if data.get("sms_integration") else 0,
            1 if data.get("sendmail_payslips") else 0,
            1 if data.get("sendmail_invoice") else 0,
            1 if data.get("bank_integration") else 0,
            data.get("psf"),
            data.get("contact_name"),
            data.get("contact_designation"),
            data.get("contact_phone"),
            data.get("contact_email"),
            data.get("notes"),
        ),
    )
    conn.commit()


def update_client(cid: int, data: dict):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE clients
        SET name=?, code=?, status=?, po_date=?, initial_training_date=?,
            go_live_date=?, fame_version=?, pocket_fame=?, state=?,
            initial_manpower=?, num_users=?, num_branches=?,
            proforma_integration=?, einvoice_integration=?, kyc_aadhaar=?, kyc_bank=?,
            sms_integration=?, sendmail_payslips=?, sendmail_invoice=?, bank_integration=?,
            psf=?, contact_name=?, contact_designation=?, contact_phone=?, contact_email=?,
            notes=?
        WHERE id=?
        """,
        (
            data["name"],
            data.get("code"),
            data.get("status"),
            data.get("po_date"),
            data.get("initial_training_date"),
            data.get("go_live_date"),
            data.get("fame_version"),
            1 if data.get("pocket_fame") else 0,
            data.get("state"),
            data.get("initial_manpower"),
            data.get("num_users"),
            data.get("num_branches"),
            1 if data.get("proforma_integration") else 0,
            1 if data.get("einvoice_integration") else 0,
            1 if data.get("kyc_aadhaar") else 0,
            1 if data.get("kyc_bank") else 0,
            1 if data.get("sms_integration") else 0,
            1 if data.get("sendmail_payslips") else 0,
            1 if data.get("sendmail_invoice") else 0,
            1 if data.get("bank_integration") else 0,
            data.get("psf"),
            data.get("contact_name"),
            data.get("contact_designation"),
            data.get("contact_phone"),
            data.get("contact_email"),
            data.get("notes"),
            cid,
        ),
    )
    conn.commit()


def delete_client(cid: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM clients WHERE id=?;", (cid,))
    conn.commit()


# ------- Modules -------
def get_modules_for_client(cid: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM client_modules WHERE client_id=? ORDER BY module_name COLLATE NOCASE;",
        (cid,),
    )
    return cur.fetchall()


def create_module(cid: int, name: str, custom: str, is_live: bool):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO client_modules (client_id, module_name, customizations, is_live) VALUES (?, ?, ?, ?);",
        (cid, name, custom, 1 if is_live else 0),
    )
    conn.commit()

def update_module(mid: int, data: dict):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE client_modules
        SET module_name = ?, customizations = ?, is_live = ?
        WHERE id = ?
        """,
        (
            data["module_name"],
            data.get("customizations"),
            1 if data.get("is_live") else 0,
            mid,
        ),
    )
    conn.commit()


def delete_module(mid: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM client_modules WHERE id=?;", (mid,))
    conn.commit()


# ------- Logs -------
def get_all_logs(status_filter="All", client_id=None):
    conn = get_connection()
    cur = conn.cursor()
    query = "SELECT * FROM client_logs"
    cond = []
    params = []

    if status_filter != "All":
        cond.append("status = ?")
        params.append(status_filter)
    if client_id is not None:
        cond.append("client_id = ?")
        params.append(client_id)

    if cond:
        query += " WHERE " + " AND ".join(cond)
    query += " ORDER BY log_date DESC, id DESC;"

    cur.execute(query, tuple(params))
    return cur.fetchall()


def get_logs_for_client(cid: int):
    return get_all_logs(client_id=cid)


def get_log_by_id(lid: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM client_logs WHERE id=?;", (lid,))
    return cur.fetchone()


def create_log(data: dict):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO client_logs
        (client_id, log_date, title, description, status, owner, remarks)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data["client_id"],
            data.get("log_date"),
            data["title"],
            data.get("description"),
            data.get("status"),
            data.get("owner"),
            data.get("remarks"),
        ),
    )
    conn.commit()


def update_log(lid: int, data: dict):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE client_logs
        SET log_date=?, title=?, description=?, status=?, owner=?, remarks=?
        WHERE id=?
        """,
        (
            data.get("log_date"),
            data["title"],
            data.get("description"),
            data.get("status"),
            data.get("owner"),
            data.get("remarks"),
            lid,
        ),
    )
    conn.commit()


def delete_log(lid: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM client_logs WHERE id=?;", (lid,))
    conn.commit()

