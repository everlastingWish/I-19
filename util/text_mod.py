from discord import Emoji, User
from difflib import SequenceMatcher
from typing import List
import re


# ==================================
#======================== eliza functions

def anti_spam(memory_entries, threshold=0.8):
    """
    Filters memory entries [(text, tokens)] to remove near-duplicate messages
    based on the text content, keeping the first occurrence.

    Args:
        memory_entries (list): List of (text: str, tokens: int) tuples.
        threshold (float): Similarity ratio above which messages are considered spam.

    Returns:
        tuple: (filtered_memory, tokens_removed)
    """
    if len(memory_entries) < 2:
        return memory_entries, 0

    indices_to_remove = set()
    total_tokens_removed = 0

    # Iterate through all entries and compare each unique message (i) to all subsequent messages (j)
    for i in range(len(memory_entries)):
        if i in indices_to_remove:
            continue

        text_i, _ = memory_entries[i]

        for j in range(i + 1, len(memory_entries)):
            if j in indices_to_remove:
                continue

            text_j, tokens_j = memory_entries[j]

            # Use SequenceMatcher to calculate similarity ratio
            if SequenceMatcher(None, text_i, text_j).ratio() > threshold:
                # Message j is a near-duplicate of message i, remove j
                indices_to_remove.add(j)
                total_tokens_removed += tokens_j

    # Build the filtered memory list
    filtered_memory = [memory_entries[i] for i in range(len(memory_entries)) if i not in indices_to_remove]

    return filtered_memory, total_tokens_removed

def replace_emojis_pings(text: str, users: List[User], emojis: List[Emoji]) -> str:
    # sort users from largest username to smallest
    users = sorted(users, key=lambda user: len(user.name), reverse=True)

    for user in users:
        text = text.replace(f'@{user.name}', f'<@{user.id}>')

    for emoji in emojis:
        text = text.replace(f':{emoji.name}:', f'<:{emoji.name}:{emoji.id}>')
    
    # remove any remaining text enclosed in colons
#    text = re.sub(r':\S+:', '', text)
    # remove any excess spaces
    text = re.sub(r'\s+', ' ', text)
    
    return text

def replace_emojis_pings_inverse(text: str, users: List[User], emojis: List[Emoji]) -> str:
    for user in users:
        text = text.replace(f'<@{user.id}>', f'@{user.name}')

    for emoji in emojis:
        text = text.replace(f'<:{emoji.name}:{emoji.id}>', f':{emoji.name}:')
    
    return text

def standardize_punctuation(text):
    text = text.replace("’", "'")
    text = text.replace("`", "'")
    text = text.replace("“", '"')
    text = text.replace("”", '"')
    return text

def fix_trailing_quotes(text):
    num_quotes = text.count('"')
    if num_quotes % 2 == 0:
        return text
    else:
        return text + '"'

def cut_trailing_sentence(text):
    text = standardize_punctuation(text)
    last_punc = max(text.rfind("."), text.rfind("!"), text.rfind("?"), text.rfind(".\""), text.rfind("!\""), text.rfind("?\""), text.rfind(".\'"), text.rfind("!\'"), text.rfind("?\'"))
    if last_punc <= 0:
        last_punc = len(text) - 1
    et_token = text.find("<")
    if et_token > 0:
        last_punc = min(last_punc, et_token - 1)
    text = text[: last_punc + 1]
    text = fix_trailing_quotes(text)
    return text
#==============================
# actual functions
#===============================

    #run once and forget abt it
def pattern_maker(templates: List[str]):
    iset = {'i','I','l','1','|'}
    iset1 = {'!'}
    pattern_list = []
    for t in templates:
        patternP = ""
        for char in t:
            if char in iset:
                patternP += r'[iIl1|]'
            elif char in iset1:
                patternP += r'[iIl|]'
            else:
                patternP += re.escape(char)
        pattern_list.append(patternP)
        combined_pattern = rf'({"|".join(pattern_list)})'
    return combined_pattern

def keyword_matcher(sets: list, txt_input: str) -> bool:
    input_norm = txt_input.lower()
    for phrase in sets:
        if phrase in input_norm:
            return True
    return False 

def splitUserMsg(prefix, messageContent, replacement=None):    
    if messageContent.startswith(prefix):
        modified = messageContent[len(prefix):].strip()
        if replacement:
            modified = replacement + modified
        return modified
    return messageContent #default case

def phrase_swap(response, black_list_dict=None):
    if black_list_dict is not None:
        for key in black_list_dict:
            response = response.replace(key, black_list_dict[key])
    return response