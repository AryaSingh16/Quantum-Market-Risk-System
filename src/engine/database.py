import sqlite3
from datetime import datetime
from src.engine.config import DB_PATH

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Executions log
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS execution_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            mode TEXT NOT NULL,
            status TEXT NOT NULL,
            quantum_var_95 REAL,
            classical_var_95 REAL,
            quantum_cvar_95 REAL,
            classical_cvar_95 REAL
        )
    ''')
    
    # Backtesting results
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS backtest_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            quantum_exceptions INTEGER,
            classical_exceptions INTEGER,
            total_days INTEGER,
            basel_status TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def log_execution(mode, status, metrics=None):
    conn = get_connection()
    cursor = conn.cursor()
    
    timestamp = datetime.utcnow().isoformat()
    if metrics:
        cursor.execute('''
            INSERT INTO execution_logs (timestamp, mode, status, quantum_var_95, classical_var_95, quantum_cvar_95, classical_cvar_95)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            timestamp, mode, status,
            metrics.get("quantum_var_95"), metrics.get("classical_var_95"),
            metrics.get("quantum_cvar_95"), metrics.get("classical_cvar_95")
        ))
    else:
        cursor.execute('''
            INSERT INTO execution_logs (timestamp, mode, status)
            VALUES (?, ?, ?)
        ''', (timestamp, mode, status))
        
    log_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return log_id

def log_backtest(q_ex, c_ex, total_days, status):
    conn = get_connection()
    cursor = conn.cursor()
    
    timestamp = datetime.utcnow().isoformat()
    cursor.execute('''
        INSERT INTO backtest_results (timestamp, quantum_exceptions, classical_exceptions, total_days, basel_status)
        VALUES (?, ?, ?, ?, ?)
    ''', (timestamp, q_ex, c_ex, total_days, status))
    
    conn.commit()
    conn.close()

def get_recent_executions(limit=10):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM execution_logs ORDER BY timestamp DESC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    
    # get column names
    col_names = [description[0] for description in cursor.description]
    conn.close()
    
    return [dict(zip(col_names, row)) for row in rows]
