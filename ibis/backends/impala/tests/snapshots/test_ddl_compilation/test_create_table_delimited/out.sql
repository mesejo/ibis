CREATE EXTERNAL TABLE IF NOT EXISTS `foo`.`new_table`
(`a` string,
 `b` int,
 `c` double,
 `d` decimal(12, 2))
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '|'
ESCAPED BY '\'
LINES TERMINATED BY ' '
STORED AS TEXTFILE
LOCATION '/path/to/files/'