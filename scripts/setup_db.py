#!/usr/bin/env python3
"""
Database setup script.
Initializes SQLite database schema.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.database import init_db, engine
from src.database.models import Base
from src.utils.logger import logger


def main():
    """Initialize database tables."""
    try:
        logger.info("database_setup_starting")
        
        # Create all tables
        init_db()
        
        logger.info(
            "database_setup_complete",
            tables=list(Base.metadata.tables.keys()),
        )
        
        print("✅ Database initialized successfully!")
        print(f"📊 Created tables: {', '.join(Base.metadata.tables.keys())}")
        
    except Exception as e:
        logger.error("database_setup_failed", error=str(e))
        print(f"❌ Database setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
