WITH
bibs AS (
	SELECT *
	FROM sierra_view.bib_record
	LIMIT (%s)
),
leaderfields AS (
	SELECT * 
	FROM sierra_view.leader_field
	WHERE record_id IN (SELECT record_id FROM bibs)
	ORDER BY record_id ASC
),
controlfields AS (
	SELECT *
	FROM sierra_view.control_field
	WHERE record_id IN (SELECT record_id FROM bibs)
	ORDER BY record_id ASC
),
varfields AS (
	SELECT *
	FROM sierra_view.varfield
	WHERE record_id IN (SELECT record_id FROM bibs)
	ORDER BY record_id ASC
),
subfields AS (
	SELECT *
	FROM sierra_view.subfield
	WHERE record_id IN (SELECT record_id FROM bibs)
	ORDER BY record_id ASC
)
SELECT
	bibs.id,
	bibs.bcode1, bibs.bcode2, bibs.bcode3,
	bibs.language_code, bibs.country_code,
	bibs.is_suppressed,
	leaderfields.*,
	controlfields.*,
	varfields.occ_num, varfields.marc_tag, subfields.tag, subfields.content
	FROM bibs
	LEFT JOIN leaderfields ON leaderfields.record_id = bibs.record_id
	LEFT JOIN controlfields ON controlfields.record_id = bibs.record_id
	LEFT JOIN varfields ON varfields.record_id = bibs.record_id
	LEFT JOIN subfields ON subfields.varfield_id = varfields.id
--	GROUP BY bibs.id
--	HAVING MAX(CASE WHEN varfields.marc_tag = '336' THEN varfields.field_content ELSE '' END) = ''
	ORDER BY bibs.id, marc_tag, varfields.occ_num, tag
--	ORDER BY bibs.id