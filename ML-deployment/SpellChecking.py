import enchant


def Spell_Checking(sentence: str):
    en = enchant.Dict("en_US")
    words = sentence.split()
    fixed_sentence = []

    for word in words:
        if not en.check(word):
            suggestions = en.suggest(word)
            if suggestions:
                print(suggestions)
                fixed_word = suggestions[0]
            else:
                fixed_word = word
        else:
            fixed_word = word

        fixed_sentence.append(fixed_word)

    return " ".join(fixed_sentence)


result = Spell_Checking("Thise is a test sentence with misspellings.")
print(result)
