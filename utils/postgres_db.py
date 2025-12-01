"""
PostgreSQL Database Utilities for NexSupply AI
Handles PostgreSQL connection and analysis_logs table operations
"""

import os
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Connection pool (initialized on first use)
_connection_pool: Optional[SimpleConnectionPool] = None


def get_database_url() -> Optional[str]:
    """
    Get PostgreSQL database URL from environment variables.
    
    Priority:
    1. Streamlit Secrets (connections.postgresql or DATABASE_URL)
    2. Environment variables (DATABASE_URL or individual components)
    
    Returns:
        Database connection URL or None if not configured
    """
    # Try Streamlit Secrets first (for Streamlit Cloud)
    try:
        import streamlit as st
    except ImportError:
        st = None
    
    # Try Streamlit Secrets first (for Streamlit Cloud)
    if st and hasattr(st, 'secrets'):
        try:
            # Method 1: Full DATABASE_URL
            if 'DATABASE_URL' in st.secrets:
                return st.secrets['DATABASE_URL']
            
            # Method 2: connections.postgresql section (Streamlit native format)
            if 'connections' in st.secrets and 'postgresql' in st.secrets['connections']:
                pg_config = st.secrets['connections']['postgresql']
                host = pg_config.get('host')
                user = pg_config.get('username') or pg_config.get('user')
                password = pg_config.get('password')
                database = pg_config.get('database') or pg_config.get('db')
                port = str(pg_config.get('port', '5432'))
                if all([host, user, password, database]):
                    return f"postgresql://{user}:{password}@{host}:{port}/{database}"
            
            # Method 3: Individual components at root level
            if all(key in st.secrets for key in ['DATABASE_HOST', 'DATABASE_USER', 'DATABASE_PASSWORD', 'DATABASE_NAME']):
                host = st.secrets['DATABASE_HOST']
                user = st.secrets['DATABASE_USER']
                password = st.secrets['DATABASE_PASSWORD']
                database = st.secrets['DATABASE_NAME']
                port = st.secrets.get('DATABASE_PORT', '5432')
                return f"postgresql://{user}:{password}@{host}:{port}/{database}"
        except Exception as e:
            logger.debug(f"Could not read from Streamlit secrets: {e}")
    
    # Try environment variable
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url
    
    # Try individual components
    host = os.getenv("DATABASE_HOST")
    user = os.getenv("DATABASE_USER")
    password = os.getenv("DATABASE_PASSWORD")
    database = os.getenv("DATABASE_NAME")
    port = os.getenv("DATABASE_PORT", "5432")
    
    if all([host, user, password, database]):
        return f"postgresql://{user}:{password}@{host}:{port}/{database}"
    
    return None


def init_connection_pool(min_conn: int = 1, max_conn: int = 5) -> bool:
    """
    Initialize PostgreSQL connection pool.
    
    Args:
        min_conn: Minimum number of connections
        max_conn: Maximum number of connections
        
    Returns:
        True if pool initialized successfully, False otherwise
    """
    global _connection_pool
    
    database_url = get_database_url()
    if not database_url:
        logger.warning("DATABASE_URL not configured. PostgreSQL features disabled.")
        return False
    
    try:
        _connection_pool = SimpleConnectionPool(
            min_conn, max_conn, database_url
        )
        logger.info("PostgreSQL connection pool initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize PostgreSQL connection pool: {e}")
        return False


@contextmanager
def get_db_connection():
    """
    Context manager for database connections.
    Uses connection pool if available, otherwise creates a new connection.
    
    Usage:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM analysis_logs")
    """
    global _connection_pool
    
    database_url = get_database_url()
    if not database_url:
        raise ValueError("DATABASE_URL not configured")
    
    # Try to use connection pool
    if _connection_pool:
        try:
            conn = _connection_pool.getconn()
            try:
                yield conn
            finally:
                _connection_pool.putconn(conn)
            return
        except Exception as e:
            logger.warning(f"Connection pool error, creating new connection: {e}")
    
    # Fallback: create new connection
    conn = psycopg2.connect(database_url)
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        conn.close()


def insert_analysis_log(
            user_input: Optional[str] = None,
            user_email: Optional[str] = None,
            product_name: Optional[str] = None,
    origin_country: Optional[str] = None,
    destination_country: Optional[str] = None,
    quantity: Optional[int] = None,
    target_retail_price: Optional[float] = None,
    target_retail_currency: str = "USD",
    landed_cost_per_unit: Optional[float] = None,
    net_margin_percent: Optional[float] = None,
    success_probability: Optional[float] = None,
    overall_risk_score: Optional[int] = None,
    price_risk: int = 0,
    lead_time_risk: int = 0,
    compliance_risk: int = 0,
    reputation_risk: int = 0,
    verdict: Optional[str] = None,
    used_fallbacks: Optional[List[str]] = None,
    reference_transaction_count: int = 0,
    full_result: Optional[Dict[str, Any]] = None,
    status: str = "success",
    error_message: Optional[str] = None
) -> Optional[str]:
    """
    Insert a new analysis log entry into the analysis_logs table.
    
    Args:
        user_input: Original user input text
        product_name: Detected product name
        origin_country: Origin country
        destination_country: Destination country
        quantity: Quantity/volume
        target_retail_price: Target retail price
        target_retail_currency: Currency (default: USD)
        landed_cost_per_unit: Calculated landed cost per unit
        net_margin_percent: Net profit margin percentage
        success_probability: Success probability (0.0-1.0)
        overall_risk_score: Overall risk score (0-100)
        price_risk: Price volatility risk (0-100)
        lead_time_risk: Lead time risk (0-100)
        compliance_risk: Compliance risk (0-100)
        reputation_risk: Reputation risk (0-100)
        verdict: Final verdict (Go, Conditional Go, No-Go, Strong Go)
        used_fallbacks: List of fallback types used
        reference_transaction_count: Number of reference transactions used
        full_result: Complete analysis result as dictionary
        status: Status ('success', 'failed', 'partial')
        error_message: Error message if failed
        
    Returns:
        UUID of inserted record, or None if insertion failed
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Prepare full_result as JSONB
            full_result_json = json.dumps(full_result) if full_result else None
            
            # Insert query
            insert_query = """
                INSERT INTO analysis_logs (
                    user_input, user_email, product_name, origin_country, destination_country,
                    quantity, target_retail_price, target_retail_currency,
                    landed_cost_per_unit, net_margin_percent, success_probability,
                    overall_risk_score, price_risk, lead_time_risk, compliance_risk,
                    reputation_risk, verdict, used_fallbacks, reference_transaction_count,
                    full_result, status, error_message
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                ) RETURNING id
            """
            
            cursor.execute(insert_query, (
                user_input, user_email, product_name, origin_country, destination_country,
                quantity, target_retail_price, target_retail_currency,
                landed_cost_per_unit, net_margin_percent, success_probability,
                overall_risk_score, price_risk, lead_time_risk, compliance_risk,
                reputation_risk, verdict, used_fallbacks, reference_transaction_count,
                full_result_json, status, error_message
            ))
            
            record_id = cursor.fetchone()[0]
            conn.commit()
            
            logger.info(f"Analysis log inserted successfully: {record_id}")
            return str(record_id)
            
    except Exception as e:
        logger.error(f"Failed to insert analysis log: {e}", exc_info=True)
        return None


def get_recent_analysis_logs(limit: int = 100) -> List[Dict[str, Any]]:
    """
    Retrieve recent analysis logs from the database.
    
    Args:
        limit: Maximum number of records to retrieve
        
    Returns:
        List of analysis log records as dictionaries
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT * FROM analysis_logs
                ORDER BY created_at DESC
                LIMIT %s
            """, (limit,))
            
            records = cursor.fetchall()
            return [dict(record) for record in records]
            
    except Exception as e:
        logger.error(f"Failed to retrieve analysis logs: {e}", exc_info=True)
        return []


def is_postgresql_available() -> bool:
    """
    Check if PostgreSQL is configured and available.
    
    Returns:
        True if PostgreSQL is available, False otherwise
    """
    database_url = get_database_url()
    if not database_url:
        return False
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            return True
    except Exception:
        return False

