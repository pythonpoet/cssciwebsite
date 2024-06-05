SELECT c.name AS country,
       bd.broadband_speed AS broadband,
       COALESCE(gini_2022, ..., gini_1963) AS gini,
       COALESCE(gdp_2020, ..., gdp_1960) AS gpd
FROM countries c
LEFT JOIN broadband_data bd ON c.name = bd.country
LEFT JOIN gini_index gi ON c.name = gi.country
LEFT JOIN gdp_table gt ON c.name = gt.country
WHERE bd.broadband_speed IS NOT NULL AND COALESCE(gini_2022, ... , gdp_1960) IS NOT NULL
