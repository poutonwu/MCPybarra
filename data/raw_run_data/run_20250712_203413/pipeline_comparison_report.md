# Pipeline Model Performance Comparison Report

This report compares the performance of different AI models on the same server generation tasks.

## 1. Overall Score Comparison (Higher is Better)

| public_server_name      |   gemini-2.5-pro |   gpt-4o |   qwen-plus |
|:------------------------|-----------------:|---------:|------------:|
| Academic Search         |            72    |    40    |        94   |
| Arxiv                   |            89    |    79    |         0   |
| Data Exploration        |            94    |    95    |       100   |
| Duckduckgo              |            77    |    76    |        78   |
| Everything Search       |            98    |    37    |        93   |
| Financial Data          |            61    |    69    |        21   |
| Flights                 |            75    |    66    |        85   |
| Git                     |            89    |    89    |        81   |
| Huggingface             |            65    |    83    |        21   |
| Image Converter         |            64    |    97    |        93   |
| Image Search            |            83    |    70    |        78   |
| Markdown                |            74    |    70    |        60   |
| Mongodb                 |            92    |    82    |        93   |
| Mysql                   |            96    |    94    |        91   |
| Opencv                  |            89    |    89    |        94   |
| Outlook                 |            77    |    73    |        83   |
| Pdf Tools               |            97    |    91    |        85   |
| Screenshot              |            92    |    72    |        69   |
| Ssh                     |            66    |    31    |        71   |
| Tavily                  |            93    |    81    |        92   |
| Text Editor             |            63    |    94    |        72   |
| Unsplash                |            93    |    97    |        97   |
| Word Automation (Doc)   |            92    |    87    |        94   |
| Word Processor (Office) |            95    |    78    |        95   |
| Zotero                  |            81    |    82    |        95   |
| **Average Score**       |            82.68 |    76.88 |        77.4 |

## 2. Total Duration Comparison (in seconds, Lower is Better)

| public_server_name      |   gemini-2.5-pro |   gpt-4o |   qwen-plus |
|:------------------------|-----------------:|---------:|------------:|
| Academic Search         |           575.78 |    95.52 |      330.71 |
| Arxiv                   |           685.92 |   287.99 |        0.00 |
| Data Exploration        |           165.14 |   156.89 |      145.20 |
| Duckduckgo              |           112.90 |   130.29 |      261.73 |
| Everything Search       |            72.86 |   113.92 |       72.33 |
| Financial Data          |           420.14 |   323.95 |      662.07 |
| Flights                 |           153.34 |   133.09 |      187.61 |
| Git                     |           407.72 |   377.43 |      490.37 |
| Huggingface             |          1076.01 |   382.12 |     1748.34 |
| Image Converter         |           111.42 |    87.43 |       89.34 |
| Image Search            |           156.63 |   150.55 |      146.19 |
| Markdown                |            80.25 |   101.06 |      151.31 |
| Mongodb                 |           211.39 |   229.27 |      210.64 |
| Mysql                   |           110.20 |   117.08 |      103.84 |
| Opencv                  |           368.84 |   308.27 |      679.24 |
| Outlook                 |           246.88 |   233.60 |      224.81 |
| Pdf Tools               |           237.37 |   237.35 |      243.44 |
| Screenshot              |           114.67 |   155.97 |      103.88 |
| Ssh                     |           364.09 |   272.80 |      281.95 |
| Tavily                  |           212.98 |   244.75 |      235.61 |
| Text Editor             |           269.67 |   269.66 |      210.36 |
| Unsplash                |            74.97 |   239.81 |       92.72 |
| Word Automation (Doc)   |           509.82 |   222.58 |      536.60 |
| Word Processor (Office) |           570.80 |   370.31 |      777.14 |
| Zotero                  |           248.86 |   134.71 |      180.00 |
| **Total Duration**      |          7558.65 |  5376.40 |     8165.42 |

## 3. Total Token Consumption (Lower is Better)

| public_server_name      |   gemini-2.5-pro |   gpt-4o |        qwen-plus |
|:------------------------|-----------------:|---------:|-----------------:|
| Academic Search         |  26735           |     5913 |  36653           |
| Arxiv                   |  32620           |    35122 |      0           |
| Data Exploration        |  21841           |    17254 |  42317           |
| Duckduckgo              |  14177           |    10258 |  17146           |
| Everything Search       |  12998           |    12847 |  12555           |
| Financial Data          |  78934           |    35628 | 109186           |
| Flights                 |  21237           |    18496 |  32912           |
| Git                     | 113184           |    88580 | 162337           |
| Huggingface             |  96349           |    81044 |  68551           |
| Image Converter         |   7889           |     7213 |  10045           |
| Image Search            |  35863           |    18071 |  33666           |
| Markdown                |   7285           |    11816 |  12240           |
| Mongodb                 |  44166           |    37393 |  55115           |
| Mysql                   |  22513           |    19390 |  26215           |
| Opencv                  |  84074           |    74267 |  94578           |
| Outlook                 |  98561           |    29579 |  45639           |
| Pdf Tools               |  37978           |    36126 |  49444           |
| Screenshot              |  58694           |    38159 |  36185           |
| Ssh                     |  54525           |    36753 |  49058           |
| Tavily                  |  32936           |    31172 |  55315           |
| Text Editor             |  55855           |    40356 |  59363           |
| Unsplash                |  15671           |    78206 |  13253           |
| Word Automation (Doc)   | 121283           |    37874 | 169353           |
| Word Processor (Office) | 142418           |    65204 | 219096           |
| Zotero                  |  32468           |    23916 |  30644           |
| **Total Tokens**        |      1.27025e+06 |   890637 |      1.44087e+06 |
