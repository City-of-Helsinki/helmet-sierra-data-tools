WITH
items AS (
	SELECT id, record_id, icode1, checkout_statistic_group_code_num, location_code, last_checkin_gmt, last_checkout_gmt
	FROM sierra_view.item_record
),
stat_groups AS (
	SELECT code_num, location_code,
	(
		CASE
			WHEN starts_with(location_code, 'h') THEN 'helsinki_vantaa'
			WHEN starts_with(location_code, 'v') THEN 'helsinki_vantaa'
			WHEN starts_with(location_code, 'e') THEN 'espoo_kauniainen'
			WHEN starts_with(location_code, 'k') THEN 'espoo_kauniainen'
			ELSE 'helsinki_vantaa'
		END
	) AS checkout_area
	FROM sierra_view.statistic_group
),
circ_trans AS (
	SELECT 
        *,
	(
		CASE
			WHEN starts_with(item_location_code, 'h') THEN 'helsinki_vantaa'
			WHEN starts_with(item_location_code, 'v') THEN 'helsinki_vantaa'
			WHEN starts_with(item_location_code, 'e') THEN 'espoo_kauniainen'
			WHEN starts_with(item_location_code, 'k') THEN 'espoo_kauniainen'
			ELSE 'helsinki_vantaa'
		END
	) AS item_area
	FROM sierra_view.circ_trans
	WHERE
		op_code = 'o'
),
item_types AS (
	SELECT code, name AS item_type_name
		FROM sierra_view.itype_property_myuser
),
patron_types AS (
	SELECT value, name AS patron_type_name
	FROM sierra_view.ptype_property_myuser
),
bibs AS (
	SELECT *
	FROM sierra_view.bib_record
),
isbns AS (
	SELECT
		record_id,
		MAX(
			CASE WHEN sierra_view.subfield.marc_tag = '020' AND sierra_view.subfield.tag = 'a'
			THEN sierra_view.subfield.content
			ELSE ''
			END
		) AS isbn
	FROM sierra_view.subfield
	GROUP BY record_id
	ORDER BY record_id ASC
),
subfields AS (
	SELECT *
	FROM sierra_view.subfield
),
varfields AS (
	SELECT
		sierra_view.varfield.record_id,
		split_part(string_agg(substring(split_part(sierra_view.varfield.field_content, '|', 2), 2), ','),',',1) as ykl
	FROM sierra_view.varfield
	LEFT JOIN subfields ON subfields.record_id = sierra_view.varfield.record_id
	WHERE 
		sierra_view.varfield.marc_tag = '084' AND
		subfields.marc_tag = '084' AND subfields.tag = '2' AND subfields.content = 'ykl'
	GROUP BY sierra_view.varfield.record_id
	ORDER BY sierra_view.varfield.record_id
)
SELECT
	circ_trans.transaction_gmt,
	stat_groups.checkout_area,
    stat_groups.location_code,
	circ_trans.ptype_code,
	(
		CASE WHEN circ_trans.item_area != stat_groups.checkout_area THEN 1
		ELSE 0
		END
	) AS is_seutu,
	(
		CASE WHEN starts_with(circ_trans.item_location_code, stat_groups.location_code) THEN 0
		ELSE 1
		END
	) AS is_logi,
	circ_trans.item_location_code,
	item_types.item_type_name,
	bibs.language_code,
	bibs.record_id as bib_id,
	varfields.ykl,
	isbns.isbn
	FROM circ_trans
    LEFT JOIN stat_groups ON stat_groups.code_num = circ_trans.stat_group_code_num
	LEFT JOIN item_types ON circ_trans.itype_code_num = item_types.code
	LEFT JOIN bibs ON circ_trans.bib_record_id = bibs.record_id
	LEFT JOIN varfields ON varfields.record_id = bibs.record_id
	LEFT JOIN isbns ON isbns.record_id = bibs.record_id
