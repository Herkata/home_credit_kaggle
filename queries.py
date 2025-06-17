

BUREUAU_BALANCE_STATUSES = ['C', 'X', '0', '1', '2', '3', '4', '5']
BUREAU_ACTIVE_STATUSES = ['Active', 'Closed', 'Sold']
BUREAU_CURRENCIES = ['currency 1', 'currency 2', 'currency 3', 'currency 4']
status_list = "', '".join(BUREAU_ACTIVE_STATUSES)

bureau_balance_status_query = """
SELECT 
    SK_ID_BUREAU, 
    COUNT(*) AS bureau_balance_total_months_count, 
    """ + ",\n    ".join([
        f"SUM(CASE WHEN STATUS = '{status}' THEN 1 ELSE 0 END) AS bureau_balance_count_status_{status}" 
        for status in BUREUAU_BALANCE_STATUSES
    ]) + """
FROM 
    bureau_balance
GROUP BY 
    SK_ID_BUREAU;
"""

bureau_balance_status_change_query = """
WITH category_changes AS (
    SELECT 
        SK_ID_BUREAU, 
        STATUS, 
        LAG(STATUS) OVER (PARTITION BY SK_ID_BUREAU ORDER BY MONTHS_BALANCE DESC) AS bureau_balance_prev_status
    FROM bureau_balance
)
SELECT 
    SK_ID_BUREAU, 
    COUNT(*) FILTER (WHERE STATUS <> bureau_balance_prev_status) AS bureau_balance_status_switches
FROM category_changes
WHERE bureau_balance_prev_status IS NOT NULL
GROUP BY SK_ID_BUREAU;
"""

bureau_active_status_query = f"""
SELECT 
    SK_ID_CURR,
    COUNT(*) AS bureau_earlier_credits_count, 
    {', '.join([ 
        f"SUM(CASE WHEN CREDIT_ACTIVE = '{status}' THEN 1 ELSE 0 END) / COUNT(*) AS bureau_pct_{status}" 
        for status in BUREAU_ACTIVE_STATUSES
    ])},
    SUM(CASE WHEN CREDIT_ACTIVE NOT IN ({', '.join([f"'{status}'" for status in BUREAU_ACTIVE_STATUSES])}) THEN 1 ELSE 0 END) / COUNT(*) AS bureau_pct_other
FROM 
    bureau
GROUP BY 
    SK_ID_CURR;
"""

bureau_currency_query = f"""
SELECT  
    SK_ID_CURR, 
    {", ".join([
        f"SUM(CASE WHEN CREDIT_CURRENCY = '{currency}' THEN 1 ELSE 0 END) AS bureau_count_{currency.replace(' ', '_')}" 
        for currency in BUREAU_CURRENCIES
    ])},
    
    CASE 
        WHEN (
            { " + ".join([
                f"CASE WHEN SUM(CASE WHEN CREDIT_CURRENCY = '{currency}' THEN 1 ELSE 0 END) > 0 THEN 1 ELSE 0 END"
                for currency in BUREAU_CURRENCIES
            ]) } 
        ) > 1 THEN 1 ELSE 0 
    END AS bureau_multiple_currencies,
    
    CASE 
        WHEN (
            { " + ".join([
                f"CASE WHEN SUM(CASE WHEN CREDIT_CURRENCY = '{currency}' THEN 1 ELSE 0 END) > 0 THEN 1 ELSE 0 END"
                for currency in BUREAU_CURRENCIES if currency != 'currency 1'
            ]) }
        ) > 0 THEN 1 ELSE 0
    END AS bureau_non_dominant_currency

FROM
    bureau
GROUP BY SK_ID_CURR;
"""

bureau_credit_days_query = """
WITH credit_diffs AS (
    SELECT 
        SK_ID_CURR,
        DAYS_CREDIT,
        LEAD(DAYS_CREDIT) OVER (PARTITION BY SK_ID_CURR ORDER BY DAYS_CREDIT) - DAYS_CREDIT AS bureau_days_credit_diff
    FROM bureau
)
SELECT 
    SK_ID_CURR,
    AVG(bureau_days_credit_diff) AS bureau_days_credit_diff_avg,
    MIN(bureau_days_credit_diff) AS bureau_days_credit_diff_min,
    MAX(bureau_days_credit_diff) AS bureau_days_credit_diff_max
FROM credit_diffs
WHERE bureau_days_credit_diff IS NOT NULL
GROUP BY SK_ID_CURR
ORDER BY SK_ID_CURR;
"""

bureau_enddate_query = """
SELECT 
    SK_ID_CURR,
    AVG(diff) AS bureau_enddate_diff_days_avg,
    MIN(diff) AS bureau_enddate_diff_days_min,
    MAX(diff) AS bureau_enddate_diff_days_max
FROM (
    SELECT
        SK_ID_CURR,
        (DAYS_CREDIT_ENDDATE - DAYS_ENDDATE_FACT) AS diff
    FROM bureau
    WHERE 
        DAYS_CREDIT_ENDDATE IS NOT NULL
        AND DAYS_ENDDATE_FACT IS NOT NULL
        AND DAYS_CREDIT_ENDDATE > -39000
        AND DAYS_ENDDATE_FACT > -39000
) AS filtered
GROUP BY SK_ID_CURR
ORDER BY SK_ID_CURR;
"""

bureau_overdue_days_query = """
SELECT 
    SK_ID_CURR,
    AVG(CREDIT_DAY_OVERDUE) AS bureau_credit_day_overdue_avg,
    MIN(CREDIT_DAY_OVERDUE) AS bureau_credit_day_overdue_min,
    MAX(CREDIT_DAY_OVERDUE) AS bureau_credit_day_overdue_max,
    SUM(CREDIT_DAY_OVERDUE) AS bureau_credit_day_overdue_sum
FROM
    bureau
GROUP BY SK_ID_CURR
ORDER BY SK_ID_CURR;
"""

bureau_credit_debt_sum_query = """
SELECT
    SK_ID_CURR,
    SUM(AMT_CREDIT_SUM_DEBT) AS bureau_total_credit_debt,
    AVG(AMT_CREDIT_SUM_DEBT) AS bureau_avg_credit_debt,
    MIN(AMT_CREDIT_SUM_DEBT) AS bureau_min_credit_debt,
    MAX(AMT_CREDIT_SUM_DEBT) AS bureau_max_credit_debt,

    SUM(AMT_CREDIT_SUM_OVERDUE) AS bureau_total_credit_overdue,
    AVG(AMT_CREDIT_SUM_OVERDUE) AS bureau_avg_credit_overdue,
    MIN(AMT_CREDIT_SUM_OVERDUE) AS bureau_min_credit_overdue,
    MAX(AMT_CREDIT_SUM_OVERDUE) AS bureau_max_credit_overdue

FROM
    bureau
GROUP BY SK_ID_CURR
ORDER BY SK_ID_CURR;
"""

bureau_credit_debt_left_query = """
SELECT
    SK_ID_CURR,
    SUM(AMT_CREDIT_SUM) AS bureau_total_credit_sum,
    SUM(AMT_CREDIT_SUM_DEBT) AS bureau_total_credit_debt,
    (SUM(AMT_CREDIT_SUM) - SUM(AMT_CREDIT_SUM_DEBT)) / NULLIF(SUM(AMT_CREDIT_SUM), 0) AS bureau_proportion_left
FROM
    bureau
GROUP BY SK_ID_CURR
ORDER BY SK_ID_CURR;
"""

bureau_prolong_max_debt_query = """
SELECT
    SK_ID_CURR,
    MAX(AMT_CREDIT_MAX_OVERDUE) AS bureau_max_overdue,
    SUM(CNT_CREDIT_PROLONG) AS bureau_prolong_count,
    MAX(AMT_CREDIT_SUM_LIMIT) AS bureau_max_card_limit
FROM
    bureau
GROUP BY SK_ID_CURR;
"""    

bureau_credit_type_query = f"""
SELECT
    SK_ID_CURR,
    SUM(CASE WHEN CREDIT_TYPE = 'Consumer credit' THEN 1 ELSE 0 END) AS bureau_credit_type_consumer_credit,
    SUM(CASE WHEN CREDIT_TYPE = 'Credit card' THEN 1 ELSE 0 END) AS bureau_credit_type_credit_card,
    SUM(CASE WHEN CREDIT_TYPE = 'Car loan' THEN 1 ELSE 0 END) AS bureau_credit_type_car_loan,
    SUM(CASE WHEN CREDIT_TYPE NOT IN ('Consumer credit', 'Credit card', 'Car loan') THEN 1 ELSE 0 END) AS bureau_credit_type_other
FROM
    bureau
GROUP BY SK_ID_CURR;
"""

bureau_credit_update_query = """
SELECT
    SK_ID_CURR,
    MAX(DAYS_CREDIT_UPDATE) AS bureau_last_credit_update
FROM
    bureau      
GROUP BY SK_ID_CURR;
"""

bureau_annuity_query = """
SELECT
    SK_ID_CURR,
    MAX(CASE WHEN CREDIT_ACTIVE = 'Active' THEN AMT_ANNUITY ELSE NULL END) AS bureau_max_active_annuity,
    MAX(CASE WHEN CREDIT_ACTIVE = 'Closed' THEN AMT_ANNUITY ELSE NULL END) AS bureau_max_closed_annuity
FROM
    bureau  
GROUP BY SK_ID_CURR;
"""

bureau_balance_agg_query = """
SELECT
    SK_ID_CURR,
    SUM(bureau_balance_status_switches) AS bureau_balance_status_switches_sum,
    1.0 * SUM(bureau_balance_status_switches) / NULLIF(SUM(bureau_balance_total_months_count), 0) AS bureau_balance_switches_per_month_weighted,
    SUM(bureau_balance_count_status_C) AS bureau_balance_count_status_closed,
    SUM(bureau_balance_count_status_X) AS bureau_balance_count_status_unknown,
    SUM(bureau_balance_count_status_0) AS bureau_balance_count_status_never_late,
    SUM(bureau_balance_count_status_1) AS bureau_balance_count_status_once_late,
    SUM(
        bureau_balance_count_status_2 +
        bureau_balance_count_status_3 +
        bureau_balance_count_status_4 +
        bureau_balance_count_status_5
    ) AS bureau_balance_count_status_repeated_late
FROM
    bureau_middle
GROUP BY
    SK_ID_CURR
ORDER BY
    SK_ID_CURR;
"""

prev_pos_term_prop = """
WITH freshest_rows AS (
    SELECT 
        *
    FROM 
        pos_cash_balance
    QUALIFY 
        ROW_NUMBER() OVER (PARTITION BY SK_ID_CURR ORDER BY MONTHS_BALANCE DESC) = 1
)
SELECT 
    SK_ID_CURR,
    CNT_INSTALMENT as prev_pos_inst_latest,
    CNT_INSTALMENT_FUTURE / CNT_INSTALMENT AS pos_months_proportion_left,
    CASE 
        WHEN CNT_INSTALMENT_FUTURE < ABS(MONTHS_BALANCE) THEN 1
        ELSE 0
    END AS pos_terms_possibly_completed,
    CASE
        WHEN ABS(MONTHS_BALANCE) > CNT_INSTALMENT THEN 1
        ELSE 0
    END AS pos_stale_balance
FROM 
    freshest_rows
"""

prev_pos_status_query = """
WITH freshest_rows AS (
    SELECT 
        *
    FROM 
        pos_cash_balance
    QUALIFY 
        ROW_NUMBER() OVER (PARTITION BY SK_ID_CURR ORDER BY MONTHS_BALANCE DESC) = 1
),
status_frequency AS (
    SELECT 
        NAME_CONTRACT_STATUS,
        COUNT(*) * 1.0 / (SELECT COUNT(*) FROM pos_cash_balance) AS pos_status_frequency
    FROM 
        pos_cash_balance
    GROUP BY 
        NAME_CONTRACT_STATUS
)
SELECT 
    pcb.SK_ID_CURR,
    pcb.NAME_CONTRACT_STATUS,
    sf.pos_status_frequency
FROM 
    freshest_rows pcb
LEFT JOIN 
    status_frequency sf
ON 
    pcb.NAME_CONTRACT_STATUS = sf.NAME_CONTRACT_STATUS
"""

prev_pos_dpd_query = """
    SELECT 
        SK_ID_CURR,
        AVG(SK_DPD) AS prev_pos_avg_dpd,
        MAX(SK_DPD) AS prev_pos_max_dpd,
        MIN(SK_DPD) AS prev_pos_min_dpd,
        AVG(SK_DPD_DEF) AS prev_pos_avg_dpd_def,
        MAX(SK_DPD_DEF) AS prev_pos_max_dpd_def,
        MIN(SK_DPD_DEF) AS prev_pos_min_dpd_def
    FROM 
        pos_cash_balance
    GROUP BY 
        SK_ID_CURR
"""

prev_inst_version_query = """
SELECT
    SK_ID_CURR,
    MAX(DISTINCT NUM_INSTALMENT_VERSION) AS prev_schedule_changes,
    CASE WHEN prev_schedule_changes > 0 THEN 0 ELSE 1 END AS prev_is_credit_card
FROM   
    installments_payments
GROUP BY
    SK_ID_CURR
""" 
prev_inst_payment_query = """
SELECT
    SK_ID_CURR,
    AVG(AMT_PAYMENT / NULLIF(AMT_INSTALMENT, 0)) AS prev_inst_payment_ratio_avg,
    SUM(CASE
        WHEN AMT_PAYMENT < AMT_INSTALMENT THEN 1
        ELSE 0
    END) AS prev_inst_underpayment_count,
    SUM(CASE
        WHEN AMT_PAYMENT > AMT_INSTALMENT THEN 1
        ELSE 0
    END) AS prev_inst_overpayment_count,
    AVG(DAYS_ENTRY_PAYMENT - DAYS_INSTALMENT) AS prev_inst_payment_delay_avg,
    SUM(CASE 
        WHEN DAYS_ENTRY_PAYMENT > DAYS_INSTALMENT THEN 1
        ELSE 0
    END) AS prev_inst_payment_delayed_count,
    SUM(CASE
        WHEN DAYS_ENTRY_PAYMENT < DAYS_INSTALMENT THEN 1
        ELSE 0
    END) AS prev_inst_payment_early_count,
    CASE 
        WHEN 
            SUM(AMT_PAYMENT - NULLIF(AMT_INSTALMENT, 0)) > 0 THEN 1 
        ELSE 0
    END AS prev_inst_overpaid_in_total
FROM
    installments_payments
GROUP BY
    SK_ID_CURR
"""

prev_inst_missing_inst_query = """
WITH inst_number AS (
SELECT
    SK_ID_CURR,
    NUM_INSTALMENT_NUMBER,
    LAG(NUM_INSTALMENT_NUMBER) OVER (PARTITION BY SK_ID_CURR ORDER BY NUM_INSTALMENT_NUMBER) AS prev_installment_number,
    CASE
        WHEN NUM_INSTALMENT_NUMBER - LAG(NUM_INSTALMENT_NUMBER) OVER (PARTITION BY SK_ID_CURR ORDER BY NUM_INSTALMENT_NUMBER) = 1 THEN 0
        ELSE 1
    END AS prev_inst_number_skipped
FROM
    installments_payments
)

SELECT
    SK_ID_CURR,
    SUM(prev_inst_number_skipped) AS prev_inst_number_skipped_total
FROM 
    inst_number
GROUP BY
    SK_ID_CURR;
"""

prev_inst_rate_increase_query = """
WITH inst_rate AS (
SELECT
    SK_ID_CURR,
    AMT_INSTALMENT,
    LAG(AMT_INSTALMENT) OVER (PARTITION BY SK_ID_CURR ORDER BY NUM_INSTALMENT_NUMBER) AS prev_instalment_amt
FROM
    installments_payments
)

SELECT
    SK_ID_CURR,
    SUM(CASE
        WHEN AMT_INSTALMENT > prev_instalment_amt THEN 1
        ELSE 0
    END) AS prev_inst_amt_increases_total
FROM
    inst_rate

GROUP BY
    SK_ID_CURR
"""

prev_inst_number_query = """
SELECT
    SK_ID_CURR,
    AVG(NUM_INSTALMENT_NUMBER * (AMT_INSTALMENT - AMT_PAYMENT)) AS prev_inst_unpaid_time_factor
FROM
    installments_payments
GROUP BY
    SK_ID_CURR
"""

prev_card_ranked_balance_query = """
WITH RankedBalances AS (
    SELECT
        SK_ID_CURR,
        MONTHS_BALANCE,
        AMT_BALANCE,
        AMT_PAYMENT_CURRENT,
        ROW_NUMBER() OVER (PARTITION BY SK_ID_CURR ORDER BY MONTHS_BALANCE DESC) AS rn
    FROM
        credit_card_balance
),
BalanceChanges AS (
    SELECT
        SK_ID_CURR,
        AVG(CASE WHEN rn <= 3 THEN AMT_BALANCE END) AS prev_card_avg_balance_last_3m,
        AVG(CASE WHEN rn <= 6 THEN AMT_BALANCE END) AS prev_card_avg_balance_last_6m,
        AVG(CASE WHEN rn <= 3 THEN AMT_PAYMENT_CURRENT END) as prev_card_avg_payment_last_3m,
        AVG(CASE WHEN rn <= 6 THEN AMT_PAYMENT_CURRENT END) as prev_card_avg_payment_last_6m,
        (AVG(CASE WHEN rn <= 3 THEN AMT_BALANCE END) - AVG(CASE WHEN rn <= 6 THEN AMT_BALANCE END)) AS prev_card_balance_change_3m_vs_6m,
        (AVG(CASE WHEN rn <= 3 THEN AMT_PAYMENT_CURRENT END) - AVG(CASE WHEN rn <= 6 THEN AMT_PAYMENT_CURRENT END)) as prev_card_payment_change_3m_vs_6m
    FROM
        RankedBalances
    GROUP BY
        SK_ID_CURR
)

SELECT
    SK_ID_CURR,
    prev_card_avg_balance_last_3m,
    prev_card_avg_balance_last_6m,
    prev_card_balance_change_3m_vs_6m,
    prev_card_avg_payment_last_3m,
    prev_card_avg_payment_last_6m,
    prev_card_payment_change_3m_vs_6m
FROM
    BalanceChanges;
"""

prev_card_delinq_patt_query= """
WITH DelinquencyPatterns AS (
    SELECT
        SK_ID_CURR,
        SUM(CASE WHEN SK_DPD > 0 THEN 1 ELSE 0 END) AS prev_card_num_dpd_months,
        AVG(CASE WHEN SK_DPD > 0 THEN SK_DPD ELSE NULL END) AS prev_card_avg_dpd_months,
        MAX(SK_DPD) as prev_card_max_dpd_months,
        AVG(CASE WHEN SK_DPD_DEF > 0 THEN SK_DPD_DEF ELSE NULL END) as prev_card_avg_dpd_def_months,
        MAX(SK_DPD_DEF) as prev_card_max_dpd_def_months,
        AVG(CASE WHEN SK_DPD > 0 and SK_DPD_DEF = 0 THEN SK_DPD ELSE NULL END) as prev_card_avg_dpd_no_def_months
    FROM
        credit_card_balance
    GROUP BY
        SK_ID_CURR
)
SELECT
    SK_ID_CURR,
    prev_card_num_dpd_months,
    prev_card_avg_dpd_months,
    prev_card_max_dpd_months,
    prev_card_avg_dpd_def_months,
    prev_card_max_dpd_def_months,
    prev_card_avg_dpd_no_def_months
FROM
    DelinquencyPatterns;

WITH Utilization AS (
    SELECT
        SK_ID_CURR,
        AVG(AMT_BALANCE / AMT_CREDIT_LIMIT_ACTUAL) AS prev_card_avg_utilization,
        STDDEV(AMT_BALANCE / AMT_CREDIT_LIMIT_ACTUAL) AS prev_card_stddev_utilization,
        MAX(AMT_BALANCE / AMT_CREDIT_LIMIT_ACTUAL) as prev_card_max_utilization
    FROM
        credit_card_balance
    WHERE
        AMT_CREDIT_LIMIT_ACTUAL > 0
    GROUP BY
        SK_ID_CURR
)
SELECT
    SK_ID_CURR,
    prev_card_avg_utilization,
    prev_card_stddev_utilization,
    prev_card_max_utilization
FROM
    Utilization;
"""

prev_card_drawings_query="""
SELECT
    SK_ID_CURR,
    AVG(AMT_DRAWINGS_ATM_CURRENT  / AMT_DRAWINGS_CURRENT) AS prev_card_pct_atm_drawings,
    AVG(AMT_DRAWINGS_POS_CURRENT / AMT_DRAWINGS_CURRENT) AS prev_card_pct_pos_drawings,
    AVG(AMT_DRAWINGS_OTHER_CURRENT / AMT_DRAWINGS_CURRENT) AS prev_card_pct_other_drawings
FROM
    credit_card_balance
WHERE
    AMT_DRAWINGS_CURRENT > 0 -- Avoid division by zero
GROUP BY
    SK_ID_CURR;
"""


prev_card_payments_query="""
SELECT
    SK_ID_CURR,
    AMT_INST_MIN_REGULARITY,
    AMT_PAYMENT_CURRENT,
    AMT_PAYMENT_TOTAL_CURRENT,
    AMT_PAYMENT_CURRENT / AMT_INST_MIN_REGULARITY AS prev_card_payment_coverage_ratio,
    AMT_PAYMENT_TOTAL_CURRENT - AMT_PAYMENT_CURRENT AS prev_card_extra_payment_amount,
    AMT_PAYMENT_TOTAL_CURRENT / AMT_INST_MIN_REGULARITY AS prev_card_total_payment_vs_min,
    AMT_PAYMENT_CURRENT - AMT_INST_MIN_REGULARITY as prev_card_payment_deviation
FROM
    credit_card_balance
WHERE
    AMT_INST_MIN_REGULARITY > 0; -- Avoid division by zero
"""

prev_card_monthly_tendencies_query = """
WITH MonthlyTendencies AS (
    SELECT
        SK_ID_CURR,
        MONTHS_BALANCE,
        AMT_RECEIVABLE_PRINCIPAL,
        AMT_RECIVABLE,
        AMT_TOTAL_RECEIVABLE,
        (AMT_RECIVABLE - AMT_RECEIVABLE_PRINCIPAL) / AMT_RECEIVABLE_PRINCIPAL AS prev_card_interest_fees_ratio,
        AMT_RECIVABLE / AMT_RECEIVABLE_PRINCIPAL AS prev_card_total_debt_vs_principal,
        AMT_TOTAL_RECEIVABLE - AMT_RECIVABLE AS prev_card_receivable_difference,
        (LAG(AMT_RECEIVABLE_PRINCIPAL, 1, AMT_RECEIVABLE_PRINCIPAL) OVER (PARTITION BY SK_ID_CURR ORDER BY MONTHS_BALANCE) - AMT_RECEIVABLE_PRINCIPAL) / LAG(AMT_RECEIVABLE_PRINCIPAL, 1, AMT_RECEIVABLE_PRINCIPAL) OVER (PARTITION BY SK_ID_CURR ORDER BY MONTHS_BALANCE) as prev_card_principal_reduction_rate,
        AMT_RECIVABLE - AMT_RECEIVABLE_PRINCIPAL as prev_card_non_principal_amount
    FROM
        credit_card_balance
    WHERE
        AMT_RECEIVABLE_PRINCIPAL > 0 -- Avoid division by zero
),
AggregatedTendencies AS (
    SELECT
        SK_ID_CURR,
        AVG(prev_card_interest_fees_ratio) AS prev_card_avg_interest_fees_ratio,
        AVG(prev_card_total_debt_vs_principal) AS prev_card_avg_total_debt_vs_principal,
        AVG(prev_card_receivable_difference) AS prev_card_avg_receivable_difference,
        AVG(prev_card_principal_reduction_rate) AS prev_card_avg_principal_reduction_rate,
        AVG(prev_card_non_principal_amount) AS prev_card_avg_non_principal_amount,
        MAX(prev_card_interest_fees_ratio) AS prev_card_max_interest_fees_ratio,
        MAX(prev_card_total_debt_vs_principal) AS prev_card_max_total_debt_vs_principal,
        MAX(prev_card_receivable_difference) AS prev_card_max_receivable_difference,
        MAX(prev_card_principal_reduction_rate) AS prev_card_max_principal_reduction_rate,
        MAX(prev_card_non_principal_amount) AS prev_card_max_non_principal_amount,
        MIN(prev_card_interest_fees_ratio) AS prev_card_min_interest_fees_ratio,
        MIN(prev_card_total_debt_vs_principal) AS prev_card_min_total_debt_vs_principal,
        MIN(prev_card_receivable_difference) AS prev_card_min_receivable_difference,
        MIN(prev_card_principal_reduction_rate) AS prev_card_min_principal_reduction_rate,
        MIN(prev_card_non_principal_amount) AS prev_card_min_non_principal_amount
    FROM
        MonthlyTendencies
    GROUP BY
        SK_ID_CURR
)
SELECT * FROM AggregatedTendencies;
"""

prev_card_monthly_changes_query="""
WITH MonthlyChanges AS (
    SELECT
        SK_ID_CURR,
        MONTHS_BALANCE,
        AMT_DRAWINGS_CURRENT,
        AMT_PAYMENT_CURRENT,
        AMT_RECEIVABLE_PRINCIPAL,
        CNT_DRAWINGS_CURRENT,
        AMT_INST_MIN_REGULARITY,
        AMT_PAYMENT_TOTAL_CURRENT,
        AMT_DRAWINGS_ATM_CURRENT,
        AMT_DRAWINGS_POS_CURRENT,
        AMT_DRAWINGS_OTHER_CURRENT
    FROM
        credit_card_balance
),
MonthlyTendencies AS (
    SELECT
        SK_ID_CURR,
        MONTHS_BALANCE,
        AMT_DRAWINGS_CURRENT - LAG(AMT_DRAWINGS_CURRENT, 1, AMT_DRAWINGS_CURRENT) OVER (PARTITION BY SK_ID_CURR ORDER BY MONTHS_BALANCE) AS prev_card_drawings_change,
        AMT_PAYMENT_CURRENT - LAG(AMT_PAYMENT_CURRENT, 1, AMT_PAYMENT_CURRENT) OVER (PARTITION BY SK_ID_CURR ORDER BY MONTHS_BALANCE) AS prev_card_payment_change,
        AMT_RECEIVABLE_PRINCIPAL - LAG(AMT_RECEIVABLE_PRINCIPAL, 1, AMT_RECEIVABLE_PRINCIPAL) OVER (PARTITION BY SK_ID_CURR ORDER BY MONTHS_BALANCE) AS prev_card_principal_change,
        CNT_DRAWINGS_CURRENT - LAG(CNT_DRAWINGS_CURRENT, 1, CNT_DRAWINGS_CURRENT) OVER (PARTITION BY SK_ID_CURR ORDER BY MONTHS_BALANCE) AS prev_card_cnt_drawings_change,
        (AMT_PAYMENT_CURRENT - LAG(AMT_PAYMENT_CURRENT, 1, AMT_PAYMENT_CURRENT) OVER (PARTITION BY SK_ID_CURR ORDER BY MONTHS_BALANCE)) / NULLIF(LAG(AMT_INST_MIN_REGULARITY, 1, AMT_INST_MIN_REGULARITY) OVER (PARTITION BY SK_ID_CURR ORDER BY MONTHS_BALANCE), 0) AS prev_card_payment_coverage_change,
        (AMT_PAYMENT_TOTAL_CURRENT - LAG(AMT_PAYMENT_TOTAL_CURRENT, 1, AMT_PAYMENT_TOTAL_CURRENT) OVER (PARTITION BY SK_ID_CURR ORDER BY MONTHS_BALANCE)) / NULLIF(LAG(AMT_INST_MIN_REGULARITY, 1, AMT_INST_MIN_REGULARITY) OVER (PARTITION BY SK_ID_CURR ORDER BY MONTHS_BALANCE), 0) as prev_card_total_payment_coverage_change,
        (AMT_DRAWINGS_ATM_CURRENT - LAG(AMT_DRAWINGS_ATM_CURRENT, 1, AMT_DRAWINGS_ATM_CURRENT) OVER (PARTITION BY SK_ID_CURR ORDER BY MONTHS_BALANCE)) / NULLIF(LAG(AMT_DRAWINGS_CURRENT, 1, AMT_DRAWINGS_CURRENT) OVER (PARTITION BY SK_ID_CURR ORDER BY MONTHS_BALANCE), 0) as prev_card_atm_drawings_percentage_change,
        (AMT_DRAWINGS_POS_CURRENT - LAG(AMT_DRAWINGS_POS_CURRENT, 1, AMT_DRAWINGS_POS_CURRENT) OVER (PARTITION BY SK_ID_CURR ORDER BY MONTHS_BALANCE)) / NULLIF(LAG(AMT_DRAWINGS_CURRENT, 1, AMT_DRAWINGS_CURRENT) OVER (PARTITION BY SK_ID_CURR ORDER BY MONTHS_BALANCE), 0) as prev_card_pos_drawings_percentage_change,
        (AMT_DRAWINGS_OTHER_CURRENT - LAG(AMT_DRAWINGS_OTHER_CURRENT, 1, AMT_DRAWINGS_OTHER_CURRENT) OVER (PARTITION BY SK_ID_CURR ORDER BY MONTHS_BALANCE)) / NULLIF(LAG(AMT_DRAWINGS_CURRENT, 1, AMT_DRAWINGS_CURRENT) OVER (PARTITION BY SK_ID_CURR ORDER BY MONTHS_BALANCE), 0) as prev_card_other_drawings_percentage_change
    FROM
        MonthlyChanges
),
AggregatedTendencies AS (
    SELECT
        SK_ID_CURR,
        AVG(prev_card_drawings_change) AS prev_card_avg_drawings_change,
        AVG(prev_card_payment_change) AS prev_card_avg_payment_change,
        AVG(prev_card_principal_change) AS prev_card_avg_principal_change,
        AVG(prev_card_cnt_drawings_change) AS prev_card_avg_cnt_drawings_change,
        AVG(prev_card_payment_coverage_change) as prev_card_avg_payment_coverage_change,
        AVG(prev_card_total_payment_coverage_change) as prev_card_avg_total_payment_coverage_change,
        AVG(prev_card_atm_drawings_percentage_change) as prev_card_avg_atm_drawings_percentage_change,
        AVG(prev_card_pos_drawings_percentage_change) as prev_card_avg_pos_drawings_percentage_change,
        AVG(prev_card_other_drawings_percentage_change) as prev_card_avg_other_drawings_percentage_change,
        MAX(prev_card_drawings_change) as prev_card_max_drawings_change,
        MIN(prev_card_drawings_change) as prev_card_min_drawings_change,
        MAX(prev_card_payment_change) as prev_card_max_payment_change,
        MIN(prev_card_payment_change) as prev_card_min_payment_change
    FROM
        MonthlyTendencies
    GROUP BY
        SK_ID_CURR
)
SELECT * FROM AggregatedTendencies;
"""

prev_card_avg_drawings_query="""
WITH AvgDrawings AS (
    SELECT
        SK_ID_CURR,
        MONTHS_BALANCE,
        CASE 
            WHEN CNT_DRAWINGS_ATM_CURRENT > 0 THEN AMT_DRAWINGS_ATM_CURRENT / CNT_DRAWINGS_ATM_CURRENT 
            ELSE 0 
        END AS avg_drawings_atm,
        CASE 
            WHEN CNT_DRAWINGS_POS_CURRENT > 0 THEN AMT_DRAWINGS_POS_CURRENT / CNT_DRAWINGS_POS_CURRENT 
            ELSE 0 
        END AS avg_drawings_pos,
        CASE 
            WHEN CNT_DRAWINGS_OTHER_CURRENT > 0 THEN AMT_DRAWINGS_OTHER_CURRENT / CNT_DRAWINGS_OTHER_CURRENT 
            ELSE 0 
        END AS avg_drawings_other
    FROM
        credit_card_balance
)
SELECT
    SK_ID_CURR,
    MIN(avg_drawings_atm) AS prev_card_min_drawings_atm,
    MAX(avg_drawings_atm) AS prev_card_max_drawings_atm,
    AVG(avg_drawings_atm) AS prev_card_avg_drawings_atm,
    MIN(avg_drawings_pos) AS prev_card_min_drawings_pos,
    MAX(avg_drawings_pos) AS prev_card_max_drawings_pos,
    AVG(avg_drawings_pos) AS prev_card_avg_drawings_pos,
    MIN(avg_drawings_other) AS prev_card_min_drawings_other,
    MAX(avg_drawings_other) AS prev_card_max_drawings_other,
    AVG(avg_drawings_other) AS prev_card_avg_drawings_other
FROM
    AvgDrawings
GROUP BY
    SK_ID_CURR;
"""

prev_card_dpd_query="""
SELECT
    SK_ID_CURR,
    MAX(SK_DPD) AS prev_card_max_dpd,
    MAX(SK_DPD_DEF) AS prev_card_max_dpd_def,
    AVG(SK_DPD) AS prev_card_avg_dpd,
    AVG(SK_DPD_DEF) AS prev_card_avg_dpd_def,
    COUNT(CASE WHEN SK_DPD > 0 THEN 1 END) AS prev_card_count_dpd,
    COUNT(CASE WHEN SK_DPD_DEF > 0 THEN 1 END) AS prev_card_count_dpd_def,
    COUNT(CASE WHEN SK_DPD > 0 THEN 1 END) * 1.0 / COUNT(MONTHS_BALANCE) AS prev_card_delinquency_rate,
    AVG(CASE WHEN SK_DPD_DEF > 0 THEN SK_DPD_DEF ELSE NULL END) / AVG(CASE WHEN SK_DPD > 0 THEN SK_DPD ELSE NULL END) AS prev_card_delinquency_severity,
    MIN(CASE WHEN SK_DPD > 0 THEN MONTHS_BALANCE ELSE NULL END) as prev_card_recent_dpd
FROM
    credit_card_balance

GROUP BY
    SK_ID_CURR;
"""

prev_card_contract_status_query = """
WITH freshest_rows AS (
    SELECT
        *
    FROM
        credit_card_balance
    QUALIFY
        ROW_NUMBER() OVER (PARTITION BY SK_ID_CURR ORDER BY MONTHS_BALANCE DESC) = 1
),
status_frequency AS (
    SELECT
        NAME_CONTRACT_STATUS,
        COUNT(*) * 1.0 / (SELECT COUNT(*) FROM credit_card_balance) AS status_frequency
    FROM
        credit_card_balance
    GROUP BY
        NAME_CONTRACT_STATUS
)
SELECT
    fr.SK_ID_CURR,
    sf.status_frequency as prev_card_status_frequency,
    CASE 
        WHEN fr.NAME_CONTRACT_STATUS = 'Active' THEN 1
        ELSE 0
    END AS prev_card_latest_active_status,
FROM
    freshest_rows fr
LEFT JOIN
    status_frequency sf
ON
    fr.NAME_CONTRACT_STATUS = sf.NAME_CONTRACT_STATUS
"""

prev_app_query = """
WITH numerical_agg AS (
    SELECT
        SK_ID_CURR,
        COUNT(*) AS prev_app_count,

        AVG(AMT_ANNUITY) AS avg_amt_annuity,
        MAX(AMT_ANNUITY) AS max_amt_annuity,
        MIN(AMT_ANNUITY) AS min_amt_annuity,

        AVG(AMT_APPLICATION) AS avg_amt_application,
        MAX(AMT_APPLICATION) AS max_amt_application,
        MIN(AMT_APPLICATION) AS min_amt_application,

        AVG(AMT_CREDIT) AS avg_amt_credit,
        MAX(AMT_CREDIT) AS max_amt_credit,
        MIN(AMT_CREDIT) AS min_amt_credit,

        AVG(AMT_DOWN_PAYMENT) AS avg_amt_down_payment,
        AVG(AMT_GOODS_PRICE) AS avg_amt_goods_price,

        AVG(HOUR_APPR_PROCESS_START) AS avg_hour_appr_start,
        AVG(SELLERPLACE_AREA) AS avg_sellerplace_area,
        AVG(CNT_PAYMENT) AS avg_cnt_payment,

        AVG(RATE_DOWN_PAYMENT) AS avg_rate_down_payment,
        AVG(RATE_INTEREST_PRIMARY) AS avg_rate_interest_primary,
        AVG(RATE_INTEREST_PRIVILEGED) AS avg_rate_interest_privileged,

        AVG(DAYS_DECISION) AS avg_days_decision,
        MIN(DAYS_FIRST_DRAWING) AS min_days_first_drawing,
        MAX(DAYS_FIRST_DUE) AS max_days_first_due,
        MAX(DAYS_LAST_DUE_1ST_VERSION) AS max_days_last_due_1st_version,
        MAX(DAYS_LAST_DUE) AS max_days_last_due,
        MAX(DAYS_TERMINATION) AS max_days_termination
    FROM previous_application
    GROUP BY SK_ID_CURR
),

binary_agg AS (
    SELECT
        SK_ID_CURR,
        AVG(CASE WHEN FLAG_LAST_APPL_PER_CONTRACT = 'Y' THEN 1 ELSE 0 END) AS ratio_flag_last_appl_per_contract,
        AVG(NFLAG_LAST_APPL_IN_DAY) AS avg_nflag_last_appl_in_day,
        AVG(NFLAG_INSURED_ON_APPROVAL) AS avg_nflag_insured_on_approval
    FROM previous_application
    GROUP BY SK_ID_CURR
),

categorical_agg AS (
    SELECT
        SK_ID_CURR,

        MODE() WITHIN GROUP (ORDER BY NAME_CONTRACT_TYPE) AS mode_contract_type,
        MODE() WITHIN GROUP (ORDER BY WEEKDAY_APPR_PROCESS_START) AS mode_weekday,
        MODE() WITHIN GROUP (ORDER BY NAME_CASH_LOAN_PURPOSE) AS mode_cash_loan_purpose,
        MODE() WITHIN GROUP (ORDER BY NAME_CONTRACT_STATUS) AS mode_contract_status,
        MODE() WITHIN GROUP (ORDER BY NAME_PAYMENT_TYPE) AS mode_payment_type,
        MODE() WITHIN GROUP (ORDER BY CODE_REJECT_REASON) AS mode_reject_reason,
        MODE() WITHIN GROUP (ORDER BY NAME_TYPE_SUITE) AS mode_type_suite,
        MODE() WITHIN GROUP (ORDER BY NAME_CLIENT_TYPE) AS mode_client_type,
        MODE() WITHIN GROUP (ORDER BY NAME_GOODS_CATEGORY) AS mode_goods_category,
        MODE() WITHIN GROUP (ORDER BY NAME_PORTFOLIO) AS mode_portfolio,
        MODE() WITHIN GROUP (ORDER BY NAME_PRODUCT_TYPE) AS mode_product_type,
        MODE() WITHIN GROUP (ORDER BY CHANNEL_TYPE) AS mode_channel_type,
        MODE() WITHIN GROUP (ORDER BY NAME_SELLER_INDUSTRY) AS mode_seller_industry,
        MODE() WITHIN GROUP (ORDER BY NAME_YIELD_GROUP) AS mode_yield_group,
        MODE() WITHIN GROUP (ORDER BY PRODUCT_COMBINATION) AS mode_product_combination

    FROM previous_application
    GROUP BY SK_ID_CURR
)

SELECT
    n.*,
    b.avg_nflag_last_appl_in_day,
    b.ratio_flag_last_appl_per_contract,
    b.avg_nflag_insured_on_approval,

    c.mode_contract_type,
    c.mode_weekday,
    c.mode_cash_loan_purpose,
    c.mode_contract_status,
    c.mode_payment_type,
    c.mode_reject_reason,
    c.mode_type_suite,
    c.mode_client_type,
    c.mode_goods_category,
    c.mode_portfolio,
    c.mode_product_type,
    c.mode_channel_type,
    c.mode_seller_industry,
    c.mode_yield_group,
    c.mode_product_combination

FROM numerical_agg n
LEFT JOIN binary_agg b USING (SK_ID_CURR)
LEFT JOIN categorical_agg c USING (SK_ID_CURR);


"""

app_train_query = """
SELECT *
FROM application_train
WHERE SK_ID_CURR NOT IN (
    SELECT SK_ID_CURR
    FROM application_test
)
"""

