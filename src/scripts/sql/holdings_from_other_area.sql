WITH
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
		op_code = 'o' AND transaction_gmt > NOW() - INTERVAL '1 month' 
),
item_types AS (
	SELECT code, name AS item_type_name
		FROM sierra_view.itype_property_myuser
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
	substr(text(circ_trans.transaction_gmt), 1, 10) AS tx_date,
	stat_groups.checkout_area,
    stat_groups.location_code,
	circ_trans.ptype_code,
	(
		CASE
		WHEN
			circ_trans.item_area != stat_groups.checkout_area AND
			NOT starts_with(circ_trans.item_location_code, 'hva') AND
			NOT starts_with(circ_trans.item_location_code, 'v34m')
		THEN 1
		ELSE 0
		END

	) AS is_ext_logi_sp,
	(
		CASE
		WHEN
			circ_trans.item_area != stat_groups.checkout_area AND
			starts_with(circ_trans.item_location_code, 'hva')
		THEN 1
		WHEN
			circ_trans.item_area != stat_groups.checkout_area AND
			starts_with(circ_trans.item_location_code, 'v34m')
		THEN 1
		ELSE 0
		END
	) AS is_ext_logi_wh,
	(
		CASE
		WHEN 
			circ_trans.item_area = stat_groups.checkout_area AND
			NOT starts_with(circ_trans.item_location_code, 'hva') AND
			NOT starts_with(circ_trans.item_location_code, 'v34m') AND
			NOT starts_with(circ_trans.item_location_code, stat_groups.location_code)
		THEN 1
		ELSE 0
		END
	) AS is_int_logi_sp,
	(
		CASE
		WHEN
			circ_trans.item_area = stat_groups.checkout_area AND
			starts_with(circ_trans.item_location_code, 'hva') AND
			NOT starts_with(circ_trans.item_location_code, stat_groups.location_code)
		THEN 1
		WHEN
			circ_trans.item_area = stat_groups.checkout_area AND
			starts_with(circ_trans.item_location_code, 'v34m') AND
			NOT starts_with(circ_trans.item_location_code, stat_groups.location_code)
		THEN 1
		ELSE 0
		END
	) AS is_int_logi_wh,
	(
		CASE
		WHEN
			starts_with(circ_trans.item_location_code, stat_groups.location_code)
		THEN 1
		ELSE 0
		END
	) AS is_local_logi,
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
