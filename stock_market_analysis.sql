-- 1. BAJAJ AUTO

CREATE TABLE bajaj_auto (
    date DATE,
    open_price NUMERIC,
    high_price NUMERIC,
    low_price NUMERIC,
    close_price NUMERIC,
    wap NUMERIC,
    no_of_shares BIGINT,
    no_of_trades BIGINT,
    total_turnover NUMERIC,
    deliverable_quantity BIGINT,
    delivery_percentage NUMERIC,
    spread_high_low NUMERIC,
    spread_close_open NUMERIC
);


-- 2. EICHER MOTORS

CREATE TABLE eicher_motors (
    date DATE,
    open_price NUMERIC,
    high_price NUMERIC,
    low_price NUMERIC,
    close_price NUMERIC,
    wap NUMERIC,
    no_of_shares BIGINT,
    no_of_trades BIGINT,
    total_turnover NUMERIC,
    deliverable_quantity BIGINT,
    delivery_percentage NUMERIC,
    spread_high_low NUMERIC,
    spread_close_open NUMERIC
);


-- 3. HERO MOTOCORP

CREATE TABLE hero_motocorp (
    date DATE,
    open_price NUMERIC,
    high_price NUMERIC,
    low_price NUMERIC,
    close_price NUMERIC,
    wap NUMERIC,
    no_of_shares BIGINT,
    no_of_trades BIGINT,
    total_turnover NUMERIC,
    deliverable_quantity BIGINT,
    delivery_percentage NUMERIC,
    spread_high_low NUMERIC,
    spread_close_open NUMERIC
);


-- 4. INFOSYS

CREATE TABLE infosys (
    date DATE,
    open_price NUMERIC,
    high_price NUMERIC,
    low_price NUMERIC,
    close_price NUMERIC,
    wap NUMERIC,
    no_of_shares BIGINT,
    no_of_trades BIGINT,
    total_turnover NUMERIC,
    deliverable_quantity BIGINT,
    delivery_percentage NUMERIC,
    spread_high_low NUMERIC,
    spread_close_open NUMERIC
);


-- 5. TCS

CREATE TABLE tcs (
    date DATE,
    open_price NUMERIC,
    high_price NUMERIC,
    low_price NUMERIC,
    close_price NUMERIC,
    wap NUMERIC,
    no_of_shares BIGINT,
    no_of_trades BIGINT,
    total_turnover NUMERIC,
    deliverable_quantity BIGINT,
    delivery_percentage NUMERIC,
    spread_high_low NUMERIC,
    spread_close_open NUMERIC
);


-- 6. TVS MOTORS

CREATE TABLE tvs_motors (
    date DATE,
    open_price NUMERIC,
    high_price NUMERIC,
    low_price NUMERIC,
    close_price NUMERIC,
    wap NUMERIC,
    no_of_shares BIGINT,
    no_of_trades BIGINT,
    total_turnover NUMERIC,
    deliverable_quantity BIGINT,
    delivery_percentage NUMERIC,
    spread_high_low NUMERIC,
    spread_close_open NUMERIC
);

-- Data Check

SELECT COUNT(*) FROM bajaj_auto;
SELECT COUNT(*) FROM eicher_motors;
SELECT COUNT(*) FROM hero_motocorp;
SELECT COUNT(*) FROM infosys;
SELECT COUNT(*) FROM tcs;
SELECT COUNT(*) FROM tvs_motors;

-- Basic analysis

--Date range

SELECT MIN(date) AS start_date,
       MAX(date) AS end_date
FROM bajaj_auto;

SELECT MIN(date), MAX(date) FROM eicher_motors;
SELECT MIN(date), MAX(date) FROM hero_motocorp;
SELECT MIN(date), MAX(date) FROM infosys;
SELECT MIN(date), MAX(date) FROM tcs;
SELECT MIN(date), MAX(date) FROM tvs_motors;

-- Highest closing price

SELECT date, close_price
FROM bajaj_auto
ORDER BY close_price DESC
LIMIT 1;

-- Lowest closing price

SELECT date, close_price
FROM bajaj_auto
ORDER BY close_price ASC
LIMIT 1;

-- 01-Jan-2015 price

SELECT *
FROM bajaj_auto
WHERE date = '2015-01-01';

-- 31-Jul-2018 price

SELECT *
FROM bajaj_auto
WHERE date = '2018-07-31';

-- Percentage change

WITH prices AS (
    SELECT
        MAX(CASE WHEN date = '2015-01-01'
                 THEN close_price END) AS old_price,
        MAX(CASE WHEN date = '2018-07-31'
                 THEN close_price END) AS new_price
    FROM bajaj_auto
)
SELECT
    old_price,
    new_price,
    ROUND(
        ((new_price - old_price) / old_price) * 100,
        2
    ) AS percentage_change
FROM prices;

-- Positive / negative days

SELECT
    COUNT(*) FILTER (WHERE close_price > open_price) AS positive_days,
    COUNT(*) FILTER (WHERE close_price < open_price) AS negative_days,
    COUNT(*) FILTER (WHERE close_price = open_price) AS unchanged_days
FROM bajaj_auto;

Buy / Sell signal

-- Simple logic:

Close > Open → BUY
Close < Open → SELL
Close = Open → HOLD

SELECT
    date,
    open_price,
    close_price,
    CASE
        WHEN close_price > open_price THEN 'BUY'
        WHEN close_price < open_price THEN 'SELL'
        ELSE 'HOLD'
    END AS signal
FROM bajaj_auto
ORDER BY date;

-- Buy / Sell count

SELECT
    COUNT(*) FILTER (WHERE close_price > open_price) AS buy_count,
    COUNT(*) FILTER (WHERE close_price < open_price) AS sell_count,
    COUNT(*) FILTER (WHERE close_price = open_price) AS hold_count
FROM bajaj_auto;

-- Latest trend

SELECT
    date,
    close_price,
    LAG(close_price) OVER (ORDER BY date) AS previous_close,
    CASE
        WHEN close_price > LAG(close_price) OVER (ORDER BY date)
            THEN 'UP'
        WHEN close_price < LAG(close_price) OVER (ORDER BY date)
            THEN 'DOWN'
        ELSE 'UNCHANGED'
    END AS trend
FROM bajaj_auto
ORDER BY date DESC
LIMIT 10;

-- Average closing price

SELECT ROUND(AVG(close_price), 2) AS average_close_price
FROM bajaj_auto;

-- Maximum and minimum closing price

SELECT
    MAX(close_price) AS highest_close,
    MIN(close_price) AS lowest_close
FROM bajaj_auto;

-- All six companies comparison

SELECT 'Bajaj Auto' AS company,
       MIN(date) AS start_date,
       MAX(date) AS end_date,
       ROUND(AVG(close_price),2) AS avg_close,
       MAX(close_price) AS highest_close,
       MIN(close_price) AS lowest_close
FROM bajaj_auto

UNION ALL

SELECT 'Eicher Motors',
       MIN(date),
       MAX(date),
       ROUND(AVG(close_price),2),
       MAX(close_price),
       MIN(close_price)
FROM eicher_motors

UNION ALL

SELECT 'Hero Motocorp',
       MIN(date),
       MAX(date),
       ROUND(AVG(close_price),2),
       MAX(close_price),
       MIN(close_price)
FROM hero_motocorp

UNION ALL

SELECT 'Infosys',
       MIN(date),
       MAX(date),
       ROUND(AVG(close_price),2),
       MAX(close_price),
       MIN(close_price)
FROM infosys

UNION ALL

SELECT 'TCS',
       MIN(date),
       MAX(date),
       ROUND(AVG(close_price),2),
       MAX(close_price),
       MIN(close_price)
FROM tcs

UNION ALL

SELECT 'TVS Motors',
       MIN(date),
       MAX(date),
       ROUND(AVG(close_price),2),
       MAX(close_price),
       MIN(close_price)
FROM tvs_motors;

-- Data Count Verify

SELECT 'Bajaj Auto' AS company, COUNT(*) AS rows FROM bajaj_auto
UNION ALL
SELECT 'Eicher Motors', COUNT(*) FROM eicher_motors
UNION ALL
SELECT 'Hero Motocorp', COUNT(*) FROM hero_motocorp
UNION ALL
SELECT 'Infosys', COUNT(*) FROM infosys
UNION ALL
SELECT 'TCS', COUNT(*) FROM tcs
UNION ALL
SELECT 'TVS Motors', COUNT(*) FROM tvs_motors;

-- Duplicate dates check

SELECT date, COUNT(*) AS duplicate_count
FROM bajaj_auto
GROUP BY date
HAVING COUNT(*) > 1;

-- NULL values check

SELECT
    COUNT(*) AS total_rows,
    COUNT(date) AS date_values,
    COUNT(open_price) AS open_values,
    COUNT(close_price) AS close_values
FROM bajaj_auto;

-- Year-wise average closing price

SELECT
    EXTRACT(YEAR FROM date) AS year,
    ROUND(AVG(close_price), 2) AS average_close
FROM bajaj_auto
GROUP BY EXTRACT(YEAR FROM date)
ORDER BY year;

-- Highest trading volume day

SELECT
    date,
    no_of_shares,
    close_price
FROM bajaj_auto
ORDER BY no_of_shares DESC
LIMIT 1;

-- Volatility / price movement

SELECT
    ROUND(AVG(spread_high_low), 2) AS average_daily_range,
    MAX(spread_high_low) AS maximum_daily_range,
    MIN(spread_high_low) AS minimum_daily_range
FROM bajaj_auto;