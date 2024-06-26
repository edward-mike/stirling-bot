from translator import detect_language, get_language_name, is_english


# Testing. Langdetect `failed` to detect i meant to start a conversion in english.
# Limitation with LangDetect, you need to use ip address and get country of origin.

lang = "hello"

if __name__ == "__main__":
    print(detect_language(lang))
    print(is_english(lang))
    print(get_language_name(lang))
