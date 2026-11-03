# Local validation

Candidate data: 3,201 agreements and 2,491 agencies; 15,478,784 bytes.
SHA-256: 78ce2f63df3c0f37877085d74eee52fdc167b5eec5ccd39f48a75eb1381426f0.
Both source payloads are completely SHA-256 verified at the pinned publisher commit.

Eleven build invariants pass. Independent Codex checks also find zero symmetric
EXCEPT ALL differences for both tables, preserving source fields and rows. The
geometry parser independently consumed all 3,201 WKB blobs: 406 empty collections,
1,696 polygons, 347 multipolygons, 675 points and 77 multipoints.

Five offline fixture tests pass. Independent race reproductions confirm that a
concurrently created source or database is preserved byte-for-byte, and publication
raises FileExistsError. Private work files are retained.

Released Python datapond 0.1.5 with DuckDB 1.5.6, and R datapond 0.1.0 with DuckDB
1.5.5, pass through an isolated localhost range server and temporary registry.
Checks include counts, metadata, field descriptions, WKB transfer, empty geometry
and leading-zero codes. The exact README Python and R examples also execute.

Python smoke checks now raise explicit errors even with Python optimization enabled; five builder fixture tests and one negative optimized-client regression passed, followed by both released clients on the unchanged database. The additional NULL removal bound belongs to one Superseded agreement; semicolon fields contain 96 county-FIPS lists and five ORI9 lists.

Geometry equality compares DuckDB-decoded source geometry to stored standard WKB, not independently recovered physical Parquet bytes. The installed Arrow reader cannot decode this newer native geometry logical type. Existing full WKB parsing and roundtrip checks passed; no coordinate transformation is performed. The source Arrow metadata declares EPSG:4326.

The initial independent Claude source review completed under included Max usage and identified these corrections. Final corrected-source review is required before publication. These validation claims distinguish executed local checks from that separate source review. Public URL verification is recorded after upload; registry approval or merge is separate.
