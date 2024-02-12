WITH
items AS (
	SELECT *
	FROM sierra_view.item_record
	LIMIT 100
),
bibs_items AS (
	SELECT bib_record_id, item_record_id
	FROM sierra_view.bib_record_item_record_link
),
bibs AS (
	SELECT *
	FROM sierra_view.bib_record
	LIMIT 100
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
	items.*,
	bibs.id,
	bibs.bcode1, bibs.bcode2, bibs.bcode3,
	bibs.language_code, bibs.country_code,
	bibs.is_suppressed,
	leaderfields.*,
	controlfields.*,
	varfields.occ_num, varfields.marc_tag, subfields.tag, subfields.content
	FROM items
	LEFT JOIN bibs_items ON bibs_items.item_record_id = items.record_id
	LEFT JOIN bibs ON bibs.record_id = bibs_items.item_record_id
	LEFT JOIN leaderfields ON leaderfields.record_id = bibs.record_id
	LEFT JOIN controlfields ON controlfields.record_id = bibs.record_id
	LEFT JOIN varfields ON varfields.record_id = bibs.record_id
	LEFT JOIN subfields ON subfields.varfield_id = varfields.id
	ORDER BY item.id