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
ykl_subfields AS (
	SELECT *
	FROM sierra_view.subfield
	WHERE sierra_view.subfield.marc_tag = '084' AND sierra_view.subfield.tag = '2' AND sierra_view.subfield.content = 'ykl'
),
authorative_classifications AS (
	SELECT
		sierra_view.varfield.record_id,
		(array_agg(sierra_view.varfield.id ORDER BY sierra_view.varfield.occ_num ASC))[1] as varfield_id
	FROM sierra_view.varfield
	LEFT JOIN ykl_subfields ON ykl_subfields.varfield_id = sierra_view.varfield.id
	WHERE 
		sierra_view.varfield.marc_tag = '084' AND 
		sierra_view.varfield.marc_ind1 != '9' AND
		ykl_subfields.marc_tag = '084' AND
		ykl_subfields.tag = '2' AND
		ykl_subfields.content = 'ykl'
	GROUP BY sierra_view.varfield.record_id
	ORDER BY sierra_view.varfield.record_id
),
classifications AS (
	SELECT varfield_id, content as ykl
	FROM sierra_view.subfield
	WHERE sierra_view.subfield.marc_tag = '084' AND sierra_view.subfield.tag = 'a'
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
	classifications.ykl,
	isbns.isbn
	FROM circ_trans
    LEFT JOIN stat_groups ON stat_groups.code_num = circ_trans.stat_group_code_num
	LEFT JOIN item_types ON circ_trans.itype_code_num = item_types.code
	LEFT JOIN bibs ON circ_trans.bib_record_id = bibs.record_id
	LEFT JOIN authorative_classifications ON authorative_classifications.record_id = bibs.record_id
	LEFT JOIN classifications ON classifications.varfield_id = authorative_classifications.varfield_id
	LEFT JOIN isbns ON isbns.record_id = bibs.record_id