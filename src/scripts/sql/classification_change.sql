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
	GROUP BY record_id
	ORDER BY record_id ASC
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
	bib_numbers.bib_number,
	bibs.record_id as bib_record_id,
	sierra_view.bib_record_property.best_title AS bib_best_title,
	sierra_view.bib_record_property.best_author AS bib_best_author,
	subfields.isbn,
	classifications.ykl,
	subfields.subject_classification,
	subfields.vantaa_classification,
	subfields.kauniainen_classification,
	subfields.espoo_classification,
	subfields.helsinki_classification,
	raw_subfields.raw_data
	FROM bibs
	LEFT JOIN authorative_classifications ON authorative_classifications.record_id = bibs.record_id
	LEFT JOIN classifications ON classifications.varfield_id = authorative_classifications.varfield_id
	LEFT JOIN subfields ON subfields.record_id = bibs.record_id
	LEFT JOIN raw_subfields ON raw_subfields.record_id = bibs.record_id
	LEFT JOIN bib_numbers ON bib_numbers.id = bibs.record_id
	LEFT JOIN sierra_view.bib_record_property ON sierra_view.bib_record_property.bib_record_id = bibs.record_id
	ORDER BY bib_number