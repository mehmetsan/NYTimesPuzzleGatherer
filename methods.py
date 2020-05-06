from langdetect import detect
from PyDictionary import PyDictionary
from translate import Translator


def translate( myWord ):
    lan         = detect(myWord.lower()+" ")
    translator  = Translator(from_lang=lan, to_lang="en")
    translation = translator.translate(myWord.lower()+" ")

    return translation, lan
