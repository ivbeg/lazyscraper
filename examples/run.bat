lscraper.py extract --url "https://rosreestr.ru/wps/portal/p/cc_ib_portal_services/cc_ib_ais_fdgko/!ut/p/z1/lZDBDoIwDIafxSdopwa4AjEEOQgSlO1iFrOYJYORberrux3FEGJvTb-__VJg0AMb-Us-uJN65Mr3lEW3otkfSL4nVdFlEaZlfcwuZY6IMVxnQENiD6QV2ZEC8USA_Zf_AUIeFypFn2ezE98G-XYFCIprR6iXjBclE4Q27Ljr0RmtlDBAlbTuLCZtnA0jI6zTRrTCWv_X1nEngDrzFDANXY-yHobkvfkABwARKw!!/p0/IZ7_GQ4E1C41KGUB60AIPJBVIC0080=CZ6_GQ4E1C41KGUB60AIPJBVIC0007=MEcontroller!listReports==/?restoreSessionState=true" --xpath "//table[@id='mainTable']//th[@style='width:75px;']/../../../tbody/tr/td/a"  --fieldnames _text,href --absolutize True --post True --pagekey massReportListPaging.pageNumber --pagerange 1,72,1 --output rosreestr.txt