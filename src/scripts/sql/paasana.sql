WITH
bibs AS (
	SELECT record_id
	FROM sierra_view.bib_record
),
bib_numbers AS (
	SELECT id, concat(concat('b',record_num),agency_code_num) as bib_number
	FROM sierra_view.record_metadata
	WHERE record_type_code = 'b'
),
raw_subfields AS (
	SELECT
		record_id,
		json_agg(
			json_build_object(
				'marc_tag', marc_tag,
				'marc_ind1', marc_ind1,
				'marc_ind2', marc_ind2,
				'field_type_code', field_type_code,
				'tag', tag,
				'content', content
			)
		) AS json,
		string_agg(content, ' ') AS raw_data
	FROM sierra_view.subfield
	WHERE marc_tag = '100' OR marc_tag = '110' OR marc_tag = '111' OR marc_tag = '130' OR marc_tag = '245'
	GROUP BY record_id
	ORDER BY record_id ASC
)
SELECT
	bib_numbers.bib_number,
	bibs.record_id as bib_record_id,
	sierra_view.bib_record_property.best_title AS bib_best_title,
	sierra_view.bib_record_property.best_author AS bib_best_author,
	raw_subfields.json
	FROM bibs
	LEFT JOIN raw_subfields ON raw_subfields.record_id = bibs.record_id
	LEFT JOIN bib_numbers ON bib_numbers.id = bibs.record_id
	LEFT JOIN sierra_view.bib_record_property ON sierra_view.bib_record_property.bib_record_id = bibs.record_id
	ORDER BY bib_number