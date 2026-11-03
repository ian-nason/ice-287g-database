# ICE 287(g) data dictionary

Source: [Deportation Data Project codebook](https://deportationdata.org/docs/ice/codebook-287g.html). The descriptions below explain the retained source columns; publisher classifications and free-text flags are not recoded.

Types and exact SQL NULL counts are measured from the built snapshot. Missing geometry is also represented by 406 empty WKB geometries, so its SQL NULL count of zero does not mean complete coverage. Agency geographic fields describe active or most recently listed agreement geography. See README for timing and linkage caveats.

## agreements

3,201 rows.

| Field | Type | Missing rows | Definition |
|---|---|---:|---|
| `agency` | VARCHAR | 0 | Law enforcement agency name, standardized by the publisher. |
| `agency_id` | VARCHAR | 0 | Publisher agency identifier; join the two tables within this snapshot. |
| `ORI9` | VARCHAR | 141 | Originating Agency Identifier(s) matched by the publisher; may be a semicolon-separated string or missing. Split associations explicitly before joining. |
| `agreement_id` | VARCHAR | 0 | Publisher identifier for one agreement; unique in this snapshot. |
| `support_type` | VARCHAR | 0 | Agreement model: Task Force, Jail Enforcement, Warrant Service Officer or historical combined model. |
| `jurisdiction` | VARCHAR | 2 | Publisher description of the jurisdiction covered by the agreement. |
| `jurisdiction_facilities` | VARCHAR | 2,449 | Publisher text describing facility locations covered by a facility-based agreement; often absent for other models. |
| `jurisdiction_level` | VARCHAR | 0 | Publisher classification of jurisdiction scope. |
| `jurisdiction_level_source` | VARCHAR | 0 | Source or method used to assign the jurisdiction level. |
| `status` | VARCHAR | 0 | Active, Removed or Superseded as of this source snapshot. |
| `signed_date` | DATE | 0 | Reported agreement signing date; not a measured implementation or training date. |
| `signed_source` | VARCHAR | 0 | Source supporting the signing date. |
| `first_appeared_date` | DATE | 1 | First observed listing date; in agencies, the source aggregate across agreements can preserve missing values. NULL does not mean never listed. |
| `first_appeared_source` | VARCHAR | 1 | Source supporting the first observed listing. |
| `last_appeared_date` | DATE | 1 | Last observed listing date; in agencies, the source aggregate can preserve missing values. Not an exact termination date; NULL does not mean never listed. |
| `removed_by_date` | DATE | 2,726 | First observation showing removal; upper bound on termination timing when present. |
| `removed_by_source` | VARCHAR | 2,726 | Source supporting the removal observation. |
| `removal_flag` | VARCHAR | 3,175 | Publisher review flag related to removal; preserve the original value and consult the codebook before recoding. |
| `moa` | VARCHAR | 3 | Link to the memorandum of agreement; some agreements lack an archived document. |
| `moa_pending` | BOOLEAN | 0 | Publisher flag for an agreement document that is pending. |
| `addendum` | VARCHAR | 3,042 | Link to a first agreement addendum, when present. |
| `addendum_second` | VARCHAR | 3,199 | Link to a second agreement addendum, when present. |
| `addendum_signed_date` | DATE | 3,042 | Signing date for the first addendum, when present. |
| `addendum_signed_date_second` | DATE | 3,199 | Signing date for the second addendum, when present. |
| `has_addendum` | BOOLEAN | 0 | Publisher indicator that an addendum exists. |
| `place` | VARCHAR | 1,960 | Mapped place name, where applicable; not an applicant or detainee residence. |
| `place_type` | VARCHAR | 1,960 | Publisher classification of the mapped place. |
| `place_geoid` | VARCHAR | 1,960 | Census place identifier where applicable; preserve leading zeros. |
| `county` | VARCHAR | 125 | Mapped county name; scope can extend beyond an individual county. |
| `county_fips` | VARCHAR | 125 | Mapped county FIPS text, possibly multiple semicolon-separated associations; preserve leading zeros and split before joins. |
| `state` | VARCHAR | 0 | Mapped state label. |
| `state_fips` | VARCHAR | 0 | State FIPS text; preserve leading zeros. |
| `geoid` | VARCHAR | 120 | Publisher geographic join identifier; interpret jointly with geoid_type. |
| `geoid_type` | VARCHAR | 120 | Geographic identifier level/type for geoid. |
| `ice_county` | VARCHAR | 510 | County text from the ICE source listing, which may differ from standardized geography. |
| `ice_type` | VARCHAR | 282 | Agency-type text from the ICE source listing. |
| `latest_sheet_row` | INTEGER | 1 | Row reference in the latest source spreadsheet used for the agreement. |
| `latest_sheet` | VARCHAR | 1 | Latest source spreadsheet identifier recorded by the publisher. |
| `latest_sheet_url` | VARCHAR | 1 | URL for that source spreadsheet. |
| `geometry_type` | VARCHAR | 406 | Publisher geometry-type label; missing for the 406 empty geometries. |
| `geometry_vintage` | INTEGER | 1,158 | Vintage year for the jurisdiction geometry, when reported; not the agreement year. |
| `geometry_wkb` | BLOB | 0 | OGC WKB BLOB converted from original geometry with ST_AsWKB. Empty geometries are preserved and are not SQL NULL. Original CRS metadata is retained. |

## agencies

2,491 rows.

| Field | Type | Missing rows | Definition |
|---|---|---:|---|
| `agency` | VARCHAR | 0 | Law enforcement agency name, standardized by the publisher. |
| `agency_id` | VARCHAR | 0 | Publisher agency identifier; join the two tables within this snapshot. |
| `ORI9` | VARCHAR | 117 | Originating Agency Identifier(s) matched by the publisher; may be a semicolon-separated string or missing. Split associations explicitly before joining. |
| `jurisdiction_level` | VARCHAR | 0 | Publisher classification of jurisdiction scope. |
| `has_active` | BOOLEAN | 0 | Whether the agency has at least one Active agreement in this snapshot. |
| `n_agreements` | INTEGER | 0 | Number of agreement rows for this agency, including historical rows. |
| `n_active` | INTEGER | 0 | Number of Active agreement rows for this agency. |
| `first_appeared_date` | DATE | 1 | First observed listing date; in agencies, the source aggregate across agreements can preserve missing values. NULL does not mean never listed. |
| `last_appeared_date` | DATE | 1 | Last observed listing date; in agencies, the source aggregate can preserve missing values. Not an exact termination date; NULL does not mean never listed. |
| `last_removed_by_date` | DATE | 2,339 | Latest removal-observation bound for agencies with no Active agreement. NULL while any agreement is Active, or when missing upstream; not an exact agency exit date. |
| `first_signed_date` | DATE | 0 | Earliest agreement signing date for the agency. |
| `last_signed_date` | DATE | 0 | Latest agreement signing date for the agency. |
| `models` | VARCHAR | 0 | Publisher summary of agreement models associated with the agency. |
| `model_history` | VARCHAR | 0 | Publisher text summarizing model history; retain its format rather than treating it as a new observation. |
| `place` | VARCHAR | 1,285 | Mapped place name, where applicable; not an applicant or detainee residence. |
| `place_type` | VARCHAR | 1,285 | Publisher classification of the mapped place. |
| `place_geoid` | VARCHAR | 1,285 | Census place identifier where applicable; preserve leading zeros. |
| `county` | VARCHAR | 93 | Mapped county name; scope can extend beyond an individual county. |
| `county_fips` | VARCHAR | 93 | Mapped county FIPS text, possibly multiple semicolon-separated associations; preserve leading zeros and split before joins. |
| `state` | VARCHAR | 0 | Mapped state label. |
| `state_fips` | VARCHAR | 0 | State FIPS text; preserve leading zeros. |
| `geoid` | VARCHAR | 110 | Publisher geographic join identifier; interpret jointly with geoid_type. |
| `geoid_type` | VARCHAR | 110 | Geographic identifier level/type for geoid. |
