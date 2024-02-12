WITH
items AS (
	SELECT id, record_id, icode1, checkout_statistic_group_code_num, location_code, last_checkin_gmt, last_checkout_gmt
	FROM sierra_view.item_record
),
last_checkouts AS (
	SELECT
		item_record_id,
		MAX(transaction_gmt) as last_checkout
	FROM sierra_view.circ_trans
	WHERE 
		op_code = 'o'
	GROUP BY item_record_id
),
last_checkins AS (
	SELECT
		item_record_id,
		MAX(transaction_gmt) as last_checkin
	FROM sierra_view.circ_trans
	WHERE 
		op_code = 'i'
	GROUP BY item_record_id
),
circ_trans AS (
	SELECT item_record_id, transaction_gmt, patron_record_id
	FROM sierra_view.circ_trans
	WHERE
		op_code = 'o'
),
act_12mo AS (
	SELECT
		patron_record_id,
		COUNT(transaction_gmt) as checkouts_last_12mo
	FROM sierra_view.circ_trans
	WHERE 
		op_code = 'o' AND
		transaction_gmt > NOW() - INTERVAL '1 year' 
	GROUP BY patron_record_id
),
bibs_items AS (
	SELECT item_record_id, bib_record_id
	FROM sierra_view.bib_record_item_record_link
),
bibs AS (
	SELECT *
	FROM sierra_view.bib_record
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
		string_agg(
			CASE WHEN sierra_view.subfield.marc_tag = '084' AND sierra_view.subfield.tag = 'a'
			THEN sierra_view.subfield.content
			ELSE ''
			END,'||'
		) AS ykl
	FROM sierra_view.subfield
	GROUP BY record_id
	ORDER BY record_id ASC
),
address AS (
		SELECT
			patron_record_id, string_agg(addr1,'||') as addr1, string_agg(addr2,'||') as addr2,
			string_agg(addr3,'||') as addr3, string_agg(village,'||') as village,
			string_agg(city,'||') as city, string_agg(region,'||') as region,
			string_agg(postal_code,'||') as postal_code, string_agg(country,'||') as country,
			string_agg(
				CASE
					WHEN patron_record_address_type_id = 1 THEN 'a'
					WHEN patron_record_address_type_id = 2 THEN 'h'
				END,
				'||') as address_type
		FROM sierra_view.patron_record_address
		GROUP BY patron_record_id
		ORDER BY patron_record_id ASC
),
patron_records AS (
	SELECT record_id, checkout_total, iii_language_pref_code, birth_date_gmt, pcode1 FROM sierra_view.patron_record
)
SELECT
	items.record_id,
	items.checkout_statistic_group_code_num	AS out_loc,
	items.location_code AS om_loc,
	(
		CASE 
		WHEN (last_checkouts.last_checkout  > items.last_checkin_gmt) THEN 1
		WHEN (last_checkouts.last_checkout IS NOT NULL) AND (items.last_checkin_gmt IS NULL) THEN 1
		ELSE 0
		END
	) AS lainassa,
	last_checkouts.last_checkout,
	items.icode1,
	bibs.bcode1, bibs.bcode2, bibs.bcode3,
	bibs.language_code,
	subfields.isbn,	subfields.ykl,
	act_12mo.checkouts_last_12mo,
	patron_records.checkout_total,
	patron_records.iii_language_pref_code,
	patron_records.birth_date_gmt,
	patron_records.pcode1,
	address.*
	FROM items
	LEFT JOIN bibs_items ON bibs_items.item_record_id = items.record_id
	LEFT JOIN bibs ON bibs.record_id = bibs_items.bib_record_id
	LEFT JOIN subfields ON subfields.record_id = bibs.record_id
	LEFT JOIN last_checkins ON last_checkins.item_record_id  = items.record_id
	LEFT JOIN last_checkouts ON last_checkouts.item_record_id  = items.record_id
	LEFT JOIN circ_trans ON items.record_id = circ_trans.item_record_id AND last_checkouts.last_checkout = circ_trans.transaction_gmt
	LEFT JOIN address ON circ_trans.patron_record_id = address.patron_record_id
	LEFT JOIN act_12mo ON circ_trans.patron_record_id = act_12mo.patron_record_id
	LEFT JOIN patron_records ON circ_trans.patron_record_id = patron_records.record_id
	ORDER BY items.id