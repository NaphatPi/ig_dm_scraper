import pandas as pd
import spacy
nlp = spacy.load("en_core_web_sm")

from nltk.tokenize import wordpunct_tokenize


ENDING = ['sent an attachment.', 
            'missed an audio call', 
            'started an audio call',
            'shared a story.']



def _get_names_from_sender(sender_name:pd.Series) -> set:
    """Get a set of all possible names from sender names"""
    name_list = sender_name.str.lower().unique()
    name_set = set()
    for name in name_list:
        if len(name) > 2:
            name_set.add(name.lower())
            if len(name.split()) > 1:
                for sub_name in name.split():
                    if len(sub_name) > 2:
                        name_set.add(sub_name.lower())

    return name_set


def _anonymize_person_name(text: str, sender_name_set: set):
    """Anonymize person names in text"""

    # First, remove from some clear patterns
    pattern_found = False
    for ending in ENDING:
        if text.endswith(ending):
            anon_text = '[person] ' + ending
            pattern_found = True
            break
    
    if not pattern_found:
        # Second, find names using Name Entity Recognition appraoch
        doc = nlp(text)
        named_entities = [ent.text for ent in doc.ents if ent.label_ == 'PERSON']
        anon_text = text
        for entity in named_entities:
            anon_text = anon_text.replace(entity, "[person]")

        # Third, find names using names from sender names appraoch
        named_entities = [word for word in wordpunct_tokenize(anon_text) if word.lower() in sender_name_set]
        for entity in named_entities:
            anon_text = anon_text.replace(entity, "[person]")

    return anon_text


def anonymize(df: pd.DataFrame):
    """Anonymize data by replacing name entities in sender_name and text column with placeholders.
    
        Args:
            df (pd.DataFrame): get this dataframe from calling clean_format function with as_dataframe=True

        Return:
            Anonymized dataframe
    """
    print('Anonymizing the data ... ', end="")
    anom_df = df.copy()
    # Anonymize sender_name column
    sender_name = list(df.sender_name.unique())
    if 'participant' in sender_name:
        sender_name.remove('participant')
    else:
        raise Exception('[participant] not found in sender_name. Failed to anonymize.')

    name_map = {v:f"person_{i}" for i, v in enumerate(sender_name, 1)}
    name_map['participant'] = 'participant'
    anom_df['sender_name'] = df.sender_name.map(name_map)

    # Anonymize text column
    sender_name_set = _get_names_from_sender(df.sender_name)
    anom_df['text'] = df.text.apply(
                            func=_anonymize_person_name,
                            sender_name_set=sender_name_set
                      )

    print('done')
    
    return anom_df