---
license: cc0-1.0
---

# ICE 287(g) agreements and agencies in DuckDB

Agreement history and agency records for ICE’s 287(g) immigration-enforcement partnerships, assembled by the Deportation Data Project. Use the 3,257 agreement records and 2,535 agency records to study recorded participation, agreement models and timing. Signing dates span July 2002–November 2026, with listings through November 10, 2026. Status is snapshot-specific. Removal timing is bounded by recorded dates where available; some bounds are missing. Agreement counts do not measure arrests or enforcement intensity.

## Start querying

Count agreement records by recorded status. Agreement counts differ from participating-agency counts.

Choose R or Python. Install datapond once: use `install.packages("datapond")` in R, or run `python -m pip install datapond` in a terminal.

### R

```r
library(datapond)
con <- dp_connect("ice-287g")
tryCatch({
  DBI::dbExecute(con, "SET threads=1")
  DBI::dbExecute(con, "SET memory_limit='128MiB'")
  DBI::dbExecute(con, "SET max_temp_directory_size='0B'")
  print(DBI::dbGetQuery(con, "SELECT status,count(*) AS agreements FROM agreements GROUP BY status ORDER BY status"))
}, finally = dp_disconnect(con))
```

### Python

```python
import datapond
con = datapond.connect('ice-287g')
try:
    con.execute("SET threads=1")
    con.execute("SET memory_limit='128MiB'")
    con.execute("SET max_temp_directory_size='0B'")
    print(con.execute("""SELECT status,count(*) AS agreements FROM agreements GROUP BY status ORDER BY status""").fetchall())
finally:
    con.close()
```

Queries run on your computer and read the byte ranges they need. A small result can still require a large scan. These examples limit DuckDB to one thread and a 128 MiB buffer pool with disk spill disabled; that is not a limit on the entire R or Python process. Larger analyses may need more memory or a local download with enough disk space.

<a id="coverage-fields-and-sources"></a>
<a id="additional-dataset-notes"></a>

## Tables, fields and joins

The two tables add policy participation, timing and jurisdiction information to the existing enforcement-event database. The dataset identifier is available in the live Datapond catalog.

See the [data dictionary](https://huggingface.co/datasets/Nason/ice-287g-database/resolve/5e82acce6a20c3f2a73e2c6b504ed60cf9e40b48/DICTIONARY.md) for column definitions.

| Table | Unit | Rows |
|---|---|---:|
| `agreements` | One agreement, including renewed and superseded agreements | 3,257 |
| `agencies` | One participating agency, with agreement summaries | 2,535 |

The total of 5,792 table rows mixes units; it is not a count
of people or unique participating places. There are 2,725 active, 273 removed and
203 superseded agreements in this snapshot.

The latest observed listing is November 10, 2026; signing dates span July 2, 2002 through November 8, 2026. These observation dates are distinct from the November 16 build date.

Join the tables using `agency_id` within this snapshot. `agreement_id` is unique
in `agreements`; `agency_id` is unique in `agencies`. An agency may have several
models or renewals, with overlapping times and jurisdictions. No person linkage
to EOIR, USCIS or the ICE enforcement records is asserted.

`ORI9` means the publisher-matched Originating Agency Identifier(s). FIPS fields are geographic codes for states or counties; preserve them as text. `support_type` identifies the agreement model: Task Force, Jail Enforcement, Warrant Service Officer or a historical combined model.

Geometry stores the mapped location or jurisdiction shape. This source uses WGS84/EPSG:4326; geometry coordinates follow the publisher’s WKB, and original Arrow/CRS metadata is preserved in `_geometry_metadata`. Empty geometry is not the same as SQL NULL.

[DICTIONARY.md](DICTIONARY.md) lists every field, its type, exact missing count and definition.

## Use and interpretation

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

<a id="advanced-access-local-queries"></a>
<a id="snapshot-files"></a>

## Other ways to connect

[Download the database](https://huggingface.co/datasets/Nason/ice-287g-database/resolve/main/ice-287g.duckdb), [browse its files](https://huggingface.co/datasets/Nason/ice-287g-database/tree/main), or inspect the [reproducible source](https://github.com/ian-nason/ice-287g-database).

The first-use examples above use the live catalog. Local examples work with the downloaded snapshot.

### Local DuckDB queries

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

### Additional catalog connection examples

The first query above is the recommended package start. These retained alternatives run the same question through the live catalog.

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

## Sources and maintenance

### Version and provenance

The 16,003,072-byte database contains `_metadata`, `_columns`, `_provenance` and `_geometry_metadata`.

Source: [Deportation Data Project (public records and FOIA)](https://deportationdata.org/docs/ice/codebook-287g.html). License: CC0-1.0 data.

Both inputs are pinned to publisher commit
`906601f9901555012fb49f19c66c569af1883a0b` (November 11, 2026). Complete file sizes, SHA-256 values and immutable URLs are recorded in
[source-manifest.json](source-manifest.json). Both source hashes were verified.

Sources: [publisher catalog](https://deportationdata.org/data/processed/ice.html),
[codebook](https://deportationdata.org/docs/ice/codebook-287g.html), and
[immutable source repository](https://github.com/deportationdata/ice-287g/tree/906601f9901555012fb49f19c66c569af1883a0b).
The repository's [CC0-1.0 data license](LICENSE-DATA) is retained. Cite the
Deportation Data Project, its source commit and Labia and Blair's 2026 codebook.

All source fields and rows are retained. The sole storage conversion is upstream `geometry` to `geometry_wkb`, a standard WKB BLOB produced by `ST_AsWKB`; no coordinates are transformed.

Snapshot SHA-256 `426cb943d67d3de5537dbe245f889b4e948d0e072d3de8699e3df4911c410970` (16,003,072 bytes). The registry pins immutable Hugging Face revisions; a later `main` may refer to a newer snapshot.

### Rebuild and checks

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

Public `datapond.connect('ice-287g')` and `dp_connect('ice-287g')` use the live Datapond catalog. Separately, the build's smoke runner tests the released clients against a temporary localhost registry and this exact artifact.

The retained build smoke scripts use an isolated registry with the same database.


### November 16, 2026 refresh

Refreshed both pinned publisher inputs through the November 10 listing. The schema is unchanged; all source rows and fields are retained with the documented geometry serialization. The build contains 3,257 agreements (2,774 Active, 279 Removed, 204 Superseded) and 2,535 agencies. Exact source equality, 11 integrity checks and five builder unit tests passed. Source pins and the complete per-field missingness record accompany this release.
