WITH
items AS (
	SELECT id, record_id, icode1, checkout_statistic_group_code_num, location_code, last_checkin_gmt, last_checkout_gmt
	FROM sierra_view.item_record
	WHERE
		sierra_view.item_record.item_status_code != 'p'
),
bibs_items AS (
	SELECT item_record_id, bib_record_id
	FROM sierra_view.bib_record_item_record_link
),
bibs AS (
	SELECT record_id
	FROM sierra_view.bib_record
),
bib_numbers AS (
	SELECT id, concat(concat('b',record_num),agency_code_num) as bib_number
	FROM sierra_view.record_metadata
	WHERE record_type_code = 'b'
),
item_numbers AS (
	SELECT id, concat(concat('i',record_num),agency_code_num) as item_number
	FROM sierra_view.record_metadata
	WHERE record_type_code = 'i'
),
subfields AS (
	SELECT
		record_id,
		MAX(
			CASE WHEN sierra_view.subfield.marc_tag = '020' AND sierra_view.subfield.tag = 'a'
			THEN sierra_view.subfield.content
			ELSE ''
			END
		) AS isbn,
		MAX(
			CASE WHEN sierra_view.subfield.marc_tag = '091' AND sierra_view.subfield.tag = 'a'
			THEN sierra_view.subfield.content
			ELSE ''
			END
		) AS subject_classification,
		MAX(
			CASE WHEN sierra_view.subfield.marc_tag = '092' AND sierra_view.subfield.tag = 'a'
			THEN sierra_view.subfield.content
			ELSE ''
			END
		) AS vantaa_classification,
		MAX(
			CASE WHEN sierra_view.subfield.marc_tag = '093' AND sierra_view.subfield.tag = 'a'
			THEN sierra_view.subfield.content
			ELSE ''
			END
		) AS kauniainen_classification,
		MAX(
			CASE WHEN sierra_view.subfield.marc_tag = '094' AND sierra_view.subfield.tag = 'a'
			THEN sierra_view.subfield.content
			ELSE ''
			END
		) AS espoo_classification,
		MAX(
			CASE WHEN sierra_view.subfield.marc_tag = '095' AND sierra_view.subfield.tag = 'a'
			THEN sierra_view.subfield.content
			ELSE ''
			END
		) AS helsinki_classification
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
--	items.record_id as item_record_id,
--	sierra_view.item_record_property.barcode AS item_barcode,
--	sierra_view.item_record_property.call_number AS item_call_number,
	(array_agg(bib_numbers.bib_number))[1] as bib_number,
	bibs.record_id,
	(array_agg(sierra_view.bib_record_property.best_title))[1] AS bib_best_title,
	(array_agg(sierra_view.bib_record_property.best_author))[1] AS bib_best_author,
	(array_agg(subfields.isbn))[1] as isbn,
	COUNT(item_numbers.item_number) as item_count,
	(array_agg(subfields.subject_classification))[1] as subject_classification,
	(array_agg(classifications.ykl))[1] as ykl,
	(array_agg(subfields.vantaa_classification))[1] as vantaa_classification,
	(array_agg(subfields.kauniainen_classification))[1] as kauniainen_classification,
	(array_agg(subfields.espoo_classification))[1] as espoo_classification,
	(array_agg(subfields.helsinki_classification))[1] as helsinki_classification
	FROM items
	LEFT JOIN bibs_items ON bibs_items.item_record_id = items.record_id
	LEFT JOIN bibs ON bibs.record_id = bibs_items.bib_record_id
	LEFT JOIN authorative_classifications ON authorative_classifications.record_id = bibs.record_id
	LEFT JOIN classifications ON classifications.varfield_id = authorative_classifications.varfield_id
	LEFT JOIN subfields ON subfields.record_id = bibs.record_id
	LEFT JOIN bib_numbers ON bib_numbers.id = bibs.record_id
	LEFT JOIN item_numbers ON item_numbers.id = items.record_id
	LEFT JOIN sierra_view.item_record_property ON sierra_view.item_record_property.item_record_id = items.record_id
	LEFT JOIN sierra_view.bib_record_property ON sierra_view.bib_record_property.bib_record_id = bibs.record_id
	GROUP BY bibs.record_id
	ORDER BY bibs.record_id