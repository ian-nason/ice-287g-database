# November 16, 2026 validation

Both source files passed full SHA-256 verification. Both tables passed bidirectional EXCEPT ALL equality against the pinned Parquet inputs (geometry serialized to WKB only). All eleven build integrity checks and five unit tests passed. The source schema is unchanged. Exact row counts, types, missingness, geometry completeness, dates and source/artifact identities are recorded in [ice-287g.manifest.json](ice-287g.manifest.json).
