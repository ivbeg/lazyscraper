lscraper extract --url "https://www.znanierussia.ru/about/Pages/kordiocionnii_sovet.aspx"  --xpath "//div[@class='sovet-page__item-name']" --fieldnames _text --output znanie_sov.csv
lscraper extract --url "https://www.znanierussia.ru/about/Pages/nabludatelnii_sovet.aspx"  --xpath "//div[@class='sovet-page__item-name']" --fieldnames _text --output znanie_nab.csv
lscraper extract --url "https://www.znanierussia.ru/about/Pages/reginalnie-otdelenia.aspx"  --xpath "//div[@class='regions__name']" --fieldnames _text --output znanie_reg.csv

