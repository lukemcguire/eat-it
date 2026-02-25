"""Tests for sqlite-vec extension loading."""


def test_sqlite_vec_loaded_in_test_engine(test_engine):
    """Verify sqlite-vec extension is loaded in test fixtures."""
    conn = test_engine.raw_connection()
    try:
        result = conn.execute("SELECT vec_version()").fetchone()
        assert result is not None
        assert len(result) == 1
        # Version should be a string starting with 'v'
        version = result[0]
        assert isinstance(version, str)
        assert version.startswith("v")
    finally:
        conn.close()


def test_sqlite_vec_vector_operations(test_engine):
    """Verify basic vector operations work with sqlite-vec."""
    conn = test_engine.raw_connection()
    try:
        # Create a simple vector table
        conn.execute(
            "CREATE VIRTUAL TABLE test_vec USING vec0("
            "  embedding FLOAT[3]"
            ")"
        )
        # Insert a vector
        conn.execute(
            "INSERT INTO test_vec(rowid, embedding) VALUES (1, '[1.0, 2.0, 3.0]')"
        )
        # Query the vector
        result = conn.execute(
            "SELECT embedding FROM test_vec WHERE rowid = 1"
        ).fetchone()
        assert result is not None
        # Clean up
        conn.execute("DROP TABLE test_vec")
    finally:
        conn.close()
