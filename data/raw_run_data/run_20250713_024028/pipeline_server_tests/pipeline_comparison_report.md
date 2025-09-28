# Pipeline Model Performance Comparison Report

This report compares the performance of different AI models on the same server generation tasks.

## 1. Overall Score Comparison (Higher is Better)

| public_server_name      |   gemini-2.5-pro |   gpt-4o |   qwen-plus |
|:------------------------|-----------------:|---------:|------------:|
| Academic Search         |            76    |    37    |       88    |
| Arxiv                   |            93    |    84    |       74    |
| Data Exploration        |            96    |    82    |       73    |
| Duckduckgo              |            94    |    56    |       83    |
| Everything Search       |            94    |    49    |       93    |
| Financial Data          |            66    |    63    |       12    |
| Flights                 |            49    |    88    |       66    |
| Git                     |            88    |    82    |       81    |
| Huggingface             |             0    |    74    |        0    |
| Image Converter         |            71    |    90    |       89    |
| Image Search            |            92    |    68    |       91    |
| Markdown                |            84    |    59    |       63    |
| Mongodb                 |            92    |    89    |       88    |
| Mysql                   |            89    |    90    |      100    |
| Opencv                  |            89    |    91    |       79    |
| Outlook                 |            83    |    69    |       79    |
| Pdf Tools               |            99    |    89    |       78    |
| Screenshot              |            93    |    82    |       60    |
| Ssh                     |            86    |    75    |       92    |
| Tavily                  |           100    |    74    |       94    |
| Text Editor             |            92    |    95    |       98    |
| Unsplash                |            94    |    86    |       97    |
| Word Automation (Doc)   |            97    |    87    |       92    |
| Word Processor (Office) |            85    |    92    |       88    |
| Zotero                  |            93    |    80    |       96    |
| **Average Score**       |            87.29 |    77.24 |       81.42 |

## 2. Total Duration Comparison (in seconds, Lower is Better)

| public_server_name      |   gemini-2.5-pro |   gpt-4o |   qwen-plus |
|:------------------------|-----------------:|---------:|------------:|
| Academic Search         |           554.28 |    87.57 |      192.95 |
| Arxiv                   |           242.17 |   247.14 |      154.05 |
| Data Exploration        |           112.93 |   149.52 |      164.52 |
| Duckduckgo              |            80.88 |   124.51 |      208.46 |
| Everything Search       |            78.97 |   122.35 |       93.46 |
| Financial Data          |           353.31 |   265.52 |      457.79 |
| Flights                 |           149.66 |   160.88 |      176.72 |
| Git                     |           428.31 |   429.13 |      549.07 |
| Huggingface             |          1639.99 |   357.97 |        0.00 |
| Image Converter         |            79.37 |    97.76 |      109.65 |
| Image Search            |           133.72 |   160.07 |      150.12 |
| Markdown                |            83.92 |   109.21 |       62.75 |
| Mongodb                 |           199.31 |   187.63 |      230.98 |
| Mysql                   |           118.07 |   108.11 |      113.02 |
| Opencv                  |           594.77 |   340.77 |      766.31 |
| Outlook                 |           282.02 |   215.32 |      203.96 |
| Pdf Tools               |           235.58 |   240.23 |      262.78 |
| Screenshot              |           124.55 |   127.72 |      125.71 |
| Ssh                     |           591.75 |  1772.00 |      401.27 |
| Tavily                  |           233.83 |   181.64 |      167.35 |
| Text Editor             |           288.18 |   230.57 |      259.90 |
| Unsplash                |            71.85 |    93.10 |       91.25 |
| Word Automation (Doc)   |           553.89 |   271.16 |      664.06 |
| Word Processor (Office) |           572.60 |   396.75 |      665.18 |
| Zotero                  |           161.50 |   144.37 |      170.47 |
| **Total Duration**      |          7965.42 |  6621.00 |     6441.77 |

## 3. Total Token Consumption (Lower is Better)

| public_server_name      |   gemini-2.5-pro |   gpt-4o |       qwen-plus |
|:------------------------|-----------------:|---------:|----------------:|
| Academic Search         |  24753           |     5825 |  40828          |
| Arxiv                   |  36900           |    32201 |  36903          |
| Data Exploration        |  23705           |    18034 |  38542          |
| Duckduckgo              |  12461           |     8749 |  16182          |
| Everything Search       |  14410           |    14405 |  13437          |
| Financial Data          |  80094           |    35411 |  70353          |
| Flights                 |  22490           |    17914 |  32691          |
| Git                     | 131582           |    88366 | 111708          |
| Huggingface             |  88155           |    84131 |      0          |
| Image Converter         |   8471           |     7476 |  10016          |
| Image Search            |  37760           |    19484 |  34253          |
| Markdown                |   7895           |    12609 |   9821          |
| Mongodb                 |  46798           |    39149 |  40368          |
| Mysql                   |  23236           |    21329 |  22294          |
| Opencv                  |  92724           |    96258 |  64766          |
| Outlook                 | 107152           |    35291 |  34134          |
| Pdf Tools               |  41418           |    32184 |  44257          |
| Screenshot              |  62459           |    39727 |  36855          |
| Ssh                     |  75477           |    49010 |  43329          |
| Tavily                  |  41464           |    29937 |  43609          |
| Text Editor             |  66400           |    41961 |  51105          |
| Unsplash                |  14899           |    63337 |  14912          |
| Word Automation (Doc)   | 118351           |    44684 | 172374          |
| Word Processor (Office) | 148277           |    69907 | 132678          |
| Zotero                  |  40124           |    23909 |  30687          |
| **Total Tokens**        |      1.36746e+06 |   931288 |      1.1461e+06 |
