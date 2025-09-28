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
| Academic Search         |           668.25 |    99.09 |      202.74 |
| Arxiv                   |           213.87 |   255.35 |      158.37 |
| Data Exploration        |           136.60 |   140.56 |      178.68 |
| Duckduckgo              |           107.42 |   124.31 |      206.82 |
| Everything Search       |           160.35 |   126.38 |      106.24 |
| Financial Data          |           360.70 |   293.10 |      472.55 |
| Flights                 |           141.89 |   142.87 |      154.61 |
| Git                     |           462.40 |   396.37 |      411.10 |
| Huggingface             |          1076.94 |   349.01 |     1235.04 |
| Image Converter         |            91.52 |   102.22 |       96.15 |
| Image Search            |           136.01 |   166.09 |      156.33 |
| Markdown                |            79.92 |   113.65 |       91.17 |
| Mongodb                 |           241.06 |   196.67 |      206.96 |
| Mysql                   |           134.30 |   104.95 |      110.49 |
| Opencv                  |           751.11 |   323.89 |      306.53 |
| Outlook                 |           219.33 |   259.23 |      213.62 |
| Pdf Tools               |           234.06 |   241.40 |      246.76 |
| Screenshot              |           125.32 |   145.90 |      123.02 |
| Ssh                     |           350.43 |  1766.97 |      323.85 |
| Tavily                  |           170.75 |   173.65 |      185.32 |
| Text Editor             |           282.36 |   267.55 |      341.84 |
| Unsplash                |            85.09 |    80.51 |       80.42 |
| Word Automation (Doc)   |           592.36 |   257.21 |      572.92 |
| Word Processor (Office) |           488.92 |   374.22 |      607.16 |
| Zotero                  |           167.20 |   130.14 |      143.06 |
| **Total Duration**      |          7478.17 |  6631.32 |     6931.75 |

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
