## Instagram Direct Message Scraper
This Python package helps scraping direct message information from an Instagram official dump zipfile (in JSON format) with functions to reformat and anonymize personal data such as names.

Tips for how to get IG official dump information in JSON format https://help.instagram.com/181231772500920 

#### Example

```python
# Put the IG official dump zip file (JSON format) in the current working directory before running this cell
# Note: how to get IG official dump information: 

from ig_dm_scraper.scraper import get_dm_from_zip
from ig_dm_scraper.formatter import reformat
from ig_dm_scraper.anonymizer import anonymize

raw = get_dm_from_zip('2023-05-01')  # Get data that is newer the specific date
df = reformat(raw, as_dataframe=True)  # reformat to Pandas dataframe 
anom_df = anonymize(df)  # Anonymize the data
anom_df.head()
```
|    |   thread_id | sender_name   | timestamp           | message_type     | text                                                                          | reaction   |
|---:|------------:|:--------------|:--------------------|:-----------------|:------------------------------------------------------------------------------|:-----------|
|  0 |           0 | participant   | 2023-08-27 02:46:45 | text             | No, I think [person] is on vacation. He probably won't be back til next week. | 👍         |
|  1 |           0 | person_1      | 2023-08-27 02:44:24 | text             | He hasn’t replied to me for a week already                                    |            |
|  2 |           0 | person_1      | 2023-08-27 02:43:46 | text             | Have you heard back from [person] yet?                                        |            |
|  3 |           0 | person_1      | 2023-08-20 06:08:28 | audio/video call | [person] missed an audio call                                                 |            |
|  4 |           0 | person_1      | 2023-08-20 06:08:20 | audio/video call | [person] started an audio call                                                |            |