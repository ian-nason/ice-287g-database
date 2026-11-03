# ICE 287(g) agreements and agencies in DuckDB

This frozen Datapond snapshot packages the Deportation Data Project's agreement
history and agency reference table. It adds policy participation, timing and
jurisdiction information to the existing enforcement-event database. The catalog identifier requires the separate registry integration described below.

| Table | Unit | Rows |
|---|---|---:|
| `agreements` | One agreement, including renewed and superseded agreements | 3,201 |
| `agencies` | One participating agency, with agreement summaries | 2,491 |

The 15,478,784-byte database contains `_metadata`, `_columns`, `_provenance` and
`_geometry_metadata`. The total of 5,692 table rows mixes units; it is not a count
of people or unique participating places. There are 2,725 active, 273 removed and
203 superseded agreements in this snapshot.

## Version and provenance

Both inputs are pinned to publisher commit
`5f4b3630a0eedc5ecaff8e8c065d1ce1438e44b7` (November 1, 2026). The latest observed
listing is October 28; signing dates span July 2, 2002 through October 27, 2026.
These source observation dates are distinct from the November 2 local build date.
Complete file sizes, SHA-256 values and immutable URLs are recorded in
[source-manifest.json](source-manifest.json). Both source hashes were verified.

Sources: [publisher catalog](https://deportationdata.org/data/processed/ice.html),
[codebook](https://deportationdata.org/docs/ice/codebook-287g.html), and
[immutable source repository](https://github.com/deportationdata/ice-287g/tree/5f4b3630a0eedc5ecaff8e8c065d1ce1438e44b7).
The repository's [CC0-1.0 data license](LICENSE-DATA) is retained. Cite the
Deportation Data Project, its source commit and Labia and Blair's 2026 codebook.

## Use and interpretation

Join the tables using `agency_id` within this snapshot. `agreement_id` is unique
in `agreements`; `agency_id` is unique in `agencies`. An agency may have several
models or renewals, with overlapping times and jurisdictions. No person linkage
to EOIR, USCIS or the ICE enforcement records is asserted.

The dates `last_appeared_date` and `removed_by_date` bound a termination interval;
neither is an exact termination date. Historical intervals may be wide. Current
status describes this source snapshot, not today's status. Agency geography is
taken from its active or most recently listed agreement, not a historical panel.
All 2,725 Active agreements have no removal bound. One Superseded agreement also
has no `removed_by_date`; an unknown bound must not be converted into an exact
termination date or interpreted as still Active.

The records represent formal agreement scope, not enforcement intensity, arrests
or informal cooperation. Facility locations are approximations, and historical
facility coverage is incomplete. Geography is missing for some agreements. In
this release, 406 geometry values are **empty geometries**, even though none are
SQL NULL; testing only `geometry_wkb IS NULL` will miss them. Another 125 agreement
rows have no county FIPS and 141 have no ORI9. Some county/ORI fields contain
semicolon-separated associations in `county_fips` (96 rows) and `ORI9` (5 rows):
split them into a bridge before joining, preserving leading zeros. Check geographic vintage and jurisdiction before joins.
Agency `last_removed_by_date` is deliberately NULL while any agreement is Active;
other missing aggregate dates also do not establish that an agency was never listed.

All source fields and rows are retained. The sole storage conversion is upstream
`geometry` to `geometry_wkb`, a standard WKB BLOB produced by `ST_AsWKB`; no
coordinates are transformed. This source uses WGS84/EPSG:4326; geometry coordinates
follow the publisher's WKB, and original Arrow/CRS metadata is preserved in
`_geometry_metadata`. [DICTIONARY.md](DICTIONARY.md) lists every field, its type,
exact missing count and definition.

## Local queries

Python (DuckDB 1.5 or later):

```python
import duckdb
con = duckdb.connect('ice-287g.duckdb', read_only=True,
                     config={'memory_limit': '128MiB', 'threads': '1'})
try:
    print(con.sql('SELECT status, count(*) AS agreements FROM agreements GROUP BY status ORDER BY status').fetchall())
finally:
    con.close()
```

R:

```r
library(DBI)
con <- dbConnect(duckdb::duckdb(), dbdir='ice-287g.duckdb', read_only=TRUE)
tryCatch({
  dbExecute(con, "SET memory_limit='128MiB'")
  dbExecute(con, 'SET threads=1')
  print(dbGetQuery(con, 'SELECT status, count(*) AS agreements FROM agreements GROUP BY status ORDER BY status'))
}, finally=dbDisconnect(con, shutdown=TRUE))
```

Public `datapond.connect('ice-287g')` and `dp_connect('ice-287g')` require a future
catalog release. The separate smoke runner tests the released clients against a
temporary localhost registry and this exact artifact.

## Rebuild and checks

The build uses Python 3.11+, DuckDB 1.5.5 and the exact datapond-build dependency
revision in `pyproject.toml`. With those dependencies installed:

```sh
python -m unittest -v test_build
python build_database.py --output fresh-ice-287g.duckdb
```

Missing inputs download from pinned URLs, with a 16 MiB per-file cap and SHA-256
verification before parsing. Existing files are verified and reused. The builder
requires 1 GiB free on the actual filesystem, uses one thread, limits DuckDB memory
to 128 MiB and disables spill. It builds in a private directory, then publishes
locally with an atomic hard link that refuses an existing target. The filesystem
must support hard links; private intermediates remain for inspection and share
storage with the final file. Failed files are also preserved. Peak process memory
is not identical to DuckDB's limit.

Validation covers exact source equality, unique nonmissing keys, agency links,
summary counts, status values, termination interval ordering and WKB round trips.
Source updates may be frequent, but this is a manual frozen snapshot: refresh by
reviewing a new publisher commit, updating both source pins, auditing schema and
definitions, and repeating Python/R tests. No automatic update schedule is implied.

## Snapshot files

[Download the database](https://huggingface.co/datasets/Nason/ice-287g-database/resolve/main/ice-287g.duckdb), [browse its files](https://huggingface.co/datasets/Nason/ice-287g-database/tree/main), or inspect the [reproducible source](https://github.com/ian-nason/ice-287g-database). Verify the snapshot SHA-256 `78ce2f63df3c0f37877085d74eee52fdc167b5eec5ccd39f48a75eb1381426f0` (15,478,784 bytes). The registry PR pins immutable Hugging Face revisions; a later `main` may refer to a newer snapshot.

Once the separate catalog entry is merged, use the released clients:

```python
import datapond
con = datapond.connect("ice-287g")
try:
    print(con.sql("SELECT status,count(*) AS agreements FROM agreements GROUP BY status ORDER BY status").fetchall())
finally:
    con.close()
```

```r
library(datapond)
con <- dp_connect("ice-287g")
tryCatch(print(DBI::dbGetQuery(con, "SELECT status,count(*) AS agreements FROM agreements GROUP BY status ORDER BY status")), finally=DBI::dbDisconnect(con, shutdown=TRUE))
```

Until catalog integration, the local Python/R examples above work with the downloaded snapshot. The smoke scripts exercise both released clients with an isolated registry and this same database.
