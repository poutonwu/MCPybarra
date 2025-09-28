# Pipeline Model Performance Comparison Report

This report compares the performance of different AI models on the same server generation tasks.

## 1. Overall Score Comparison (Higher is Better)

| public_server_name      |   gemini-2.5-pro |   gpt-4o |   qwen-plus |
|:------------------------|-----------------:|---------:|------------:|
| Academic Search         |            81    |     39   |       91    |
| Arxiv                   |            94    |     88   |       91    |
| Data Exploration        |            86    |     83   |       70    |
| Duckduckgo              |            71    |     83   |       73    |
| Everything Search       |            86    |     52   |       91    |
| Financial Data          |            65    |     69   |       15    |
| Flights                 |            61    |     68   |       96    |
| Git                     |            91    |     92   |       93    |
| Huggingface             |            77    |     96   |       34    |
| Image Converter         |            72    |     92   |       77    |
| Image Search            |            86    |     67   |       91    |
| Markdown                |            63    |     64   |       66    |
| Mongodb                 |            87    |    100   |       97    |
| Mysql                   |            92    |     91   |       96    |
| Opencv                  |            86    |     87   |       91    |
| Outlook                 |            82    |     75   |       77    |
| Pdf Tools               |            92    |     77   |       76    |
| Screenshot              |            94    |     84   |       65    |
| Ssh                     |            90    |     59   |       88    |
| Tavily                  |            67    |     78   |       70    |
| Text Editor             |            91    |     86   |       47    |
| Unsplash                |            93    |     84   |       98    |
| Word Automation (Doc)   |            96    |     90   |       88    |
| Word Processor (Office) |            91    |     70   |       88    |
| Zotero                  |            89    |     96   |       93    |
| **Average Score**       |            83.32 |     78.8 |       78.48 |

## 2. Total Duration Comparison (in seconds, Lower is Better)

| public_server_name      |   gemini-2.5-pro |   gpt-4o |   qwen-plus |
|:------------------------|-----------------:|---------:|------------:|
| Academic Search         |           668.26 |    99.1  |      202.75 |
| Arxiv                   |           213.92 |   255.36 |      158.38 |
| Data Exploration        |           136.64 |   140.6  |      179.26 |
| Duckduckgo              |           107.43 |   124.32 |      206.89 |
| Everything Search       |           160.46 |   126.39 |      106.29 |
| Financial Data          |           360.72 |   293.11 |      472.56 |
| Flights                 |           141.89 |   142.92 |      154.68 |
| Git                     |           462.55 |   396.38 |      411.16 |
| Huggingface             |          1077.04 |   349.02 |     1235.04 |
| Image Converter         |            91.53 |   102.23 |       96.17 |
| Image Search            |           136.02 |   166.1  |      156.34 |
| Markdown                |            79.93 |   113.68 |       91.19 |
| Mongodb                 |           241.07 |   196.73 |      206.97 |
| Mysql                   |           134.31 |   104.96 |      110.5  |
| Opencv                  |           751.13 |   323.9  |      306.54 |
| Outlook                 |           219.34 |   259.24 |      213.64 |
| Pdf Tools               |           234.13 |   241.41 |      246.79 |
| Screenshot              |           125.39 |   145.91 |      123.07 |
| Ssh                     |           350.44 |  1766.98 |      323.86 |
| Tavily                  |           170.77 |   173.66 |      185.34 |
| Text Editor             |           282.38 |   267.56 |      341.85 |
| Unsplash                |            85.1  |    80.52 |       80.44 |
| Word Automation (Doc)   |           592.38 |   257.23 |      572.94 |
| Word Processor (Office) |           489    |   374.23 |      607.2  |
| Zotero                  |           167.21 |   130.15 |      143.07 |
| **Total Duration**      |          7479.04 |  6631.69 |     6932.92 |

## 3. Total Token Consumption (Lower is Better)

| public_server_name      |   gemini-2.5-pro |   gpt-4o |        qwen-plus |
|:------------------------|-----------------:|---------:|-----------------:|
| Academic Search         |  29015           |     6009 |  37449           |
| Arxiv                   |  34788           |    35670 |  36235           |
| Data Exploration        |  28149           |    17918 |  47714           |
| Duckduckgo              |  13443           |    12342 |  18658           |
| Everything Search       |  14692           |    13120 |  13945           |
| Financial Data          |  83658           |    40461 | 105962           |
| Flights                 |  23006           |    18317 |  34656           |
| Git                     | 131481           |    92425 | 163683           |
| Huggingface             |  83738           |    66906 |  65907           |
| Image Converter         |   8917           |     7381 |  11031           |
| Image Search            |  39025           |    19726 |  36899           |
| Markdown                |   8063           |     7922 |  11326           |
| Mongodb                 |  49651           |    39702 |  57292           |
| Mysql                   |  24608           |    21620 |  29788           |
| Opencv                  |  88325           |    74419 | 101573           |
| Outlook                 | 124478           |    37174 |  54849           |
| Pdf Tools               |  40482           |    42932 |  52407           |
| Screenshot              |  61431           |    39963 |  40702           |
| Ssh                     |  58939           |    39938 |  65460           |
| Tavily                  |  25368           |    20207 |  33511           |
| Text Editor             |  59051           |    47251 |  95792           |
| Unsplash                |  15187           |    55903 |  18906           |
| Word Automation (Doc)   | 127795           |    46671 | 189319           |
| Word Processor (Office) | 138673           |    69184 | 210703           |
| Zotero                  |  35045           |    23745 |  29897           |
| **Total Tokens**        |      1.34701e+06 |   896906 |      1.56366e+06 |