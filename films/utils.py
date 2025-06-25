import re


MENTION_PATTERN = re.compile(r"@(\w+)")

def extract_tagged_users(text) -> list[str]:
    usernames = MENTION_PATTERN.findall(text)
    return usernames