
"""
V-alpha
"""


def FrostCrypt(text, etext):
    encryptionkey = 0
    for i in etext:
        encryptionkey += ord(i)
    ltext = list(text)
    for i in range(len(ltext)):
        if ltext[i].islower():
            ltext[i] = chr((ord(ltext[i]) + encryptionkey - 97) % 26 + 97)
        elif ltext[i].isupper():
            ltext[i] = chr((ord(ltext[i]) + encryptionkey - 65) % 26 + 65)
        else:
            ltext[i] = ltext[i]
    return f'/FC${"".join(ltext)}/V-A$'


def FrostDCrypt(text, etext):
    encryptionkey = 0
    for i in etext:
        encryptionkey += ord(i)
    ltext = list(text)
    text = []
    for i in range(4, len(ltext)-5):
        if ltext[i].islower():
            text.append(chr((ord(ltext[i]) - encryptionkey - 97) % 26 + 97))
        elif ltext[i].isupper():
            text.append(chr((ord(ltext[i]) - encryptionkey - 65) % 26 + 65))
        else:
            text.append(ltext[i])
    return "".join(text)
