# No-Profanity
**No-Profanity** is a simple library that uses regexes to detect and block profanity in strings. It's designed to detect even the most creative modifications of profanity.

## How to use?
The library contains 1 class. This class contains 5 functions.

```py
from no_profanity import ProfanityFilter

# ProfanityFilter(censor_symbol: str = "*")
filter = ProfanityFilter()

# 1. Add Custom Words
filter.add_custom_words(["happy", "hello"])

# 2. Set Censor Symbol
filter.set_censor_symbol("-")

# 3. is_profanity(txt: str) -> bool
filter.is_profanity("my name is Lime") # False
filter.is_profanity("shut the fuck up") # True

# 4. censor_text(txt: str, censor_symbol: str = None) -> str
filter.censor_text("what the fuck is this") # what the ---- is this

# Without set_censor_symbol(): what the **** is this

# 5. full_detection(txt: str) -> list
# [[match_in_string, start_index, end_index, found_word], ...]
filter.full_detection("you fuck1ng bitch") # [["fuck1ng", 4, 10, "fucking"], ["bitch", 12, 16, "bitch"]]
```

## Pros
The library can detect *modified* profanity. Examples:
```py
filter.is_profanity("fuckfuck") # True
filter.is_profanity("niggafuck") # True
filter.is_profanity("b i t c h") # True
filter.is_profanity("sexx") # True

filter.is_profanity("n1@@a") # True
filter.is_profanity("f u cckbitch es") # True

filter.is_profanity("@fuck@") # True
```

## Cons
The filter can be bypassed by putting an extra letter(s) that isn't part of profanity. This will be fixed in the future! :D
```py
filter.is_profanity("afuck") # False
```

This library has originally been made for my Discord bot **AutoProtection**, but now it's released for everyone to use!
If you have more questions, please contact me on my [Discord server](https://discord.com/invite/tr55DGHEwN).

Thank you for reading this! I hope you'll like my first library. I'm always opened to new ideas for improvements! ^^