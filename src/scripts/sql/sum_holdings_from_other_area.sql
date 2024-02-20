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
	WHERE op_code = 'o'
)
SELECT
	circ_trans.transaction_gmt::date as tx_date,
	stat_groups.checkout_area,
    stat_groups.location_code,
	sum(
		CASE
		WHEN
			circ_trans.item_area != stat_groups.checkout_area AND
			NOT starts_with(circ_trans.item_location_code, 'hva') AND
			NOT starts_with(circ_trans.item_location_code, 'v34m')
		THEN 1
		ELSE 0
		END
	) AS ext_logi_sp,
	sum(
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
	) AS ext_logi_wh,
	sum(
		CASE
		WHEN 
			circ_trans.item_area = stat_groups.checkout_area AND
			NOT starts_with(circ_trans.item_location_code, 'hva') AND
			NOT starts_with(circ_trans.item_location_code, 'v34m') AND
			NOT starts_with(circ_trans.item_location_code, stat_groups.location_code)
		THEN 1
		ELSE 0
		END
	) AS int_logi_sp,
	sum(
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
	) AS int_logi_wh,
	sum(
		CASE
		WHEN
			starts_with(circ_trans.item_location_code, stat_groups.location_code)
		THEN 1
		ELSE 0
		END
	) AS local_logi
	FROM circ_trans
    LEFT JOIN stat_groups ON stat_groups.code_num = circ_trans.stat_group_code_num
	GROUP BY tx_date, stat_groups.checkout_area, stat_groups.location_code
	ORDER BY tx_date, stat_groups.checkout_area, stat_groups.location_code
