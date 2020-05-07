from langdetect import detect
from PyDictionary import PyDictionary
from translate import Translator
from wordster import wordster
import requests
from bs4 import BeautifulSoup
import pycountry
from datetime import datetime
import time
import re

def tryWordnet( myWord ):
    wordnetURL      = "http://wordnetweb.princeton.edu/perl/webwn?s=" + myWord
    html_content    = requests.get(wordnetURL).text
    soup            = BeautifulSoup(html_content,"html.parser")
    defComponents   = soup.find_all("li")

    defs = []
    for definition in defComponents:
        temp    = definition.text[6:]
        index1  = temp.find('(') + 1
        index2  = temp.rindex(')')
        ans     = temp[index1:index2]
        if(';' in ans):
            index2 = ans.find(';')
        ans     = ans[:index2]
        while re.search(r"[(].*[)]", ans) != None:
            ans = ans.replace(re.search(r"[(].*[)]", ans).group(), "")
        defs.append(ans)

    if(len(defs) == 0): #IF NO RESULTS ARE RETURNED
        return "NODEF"
    return defs[0]      #RETURN FIRST MEANING


def tryMerriam( myWord ):
    merriamURL      = "https://www.merriam-webster.com/dictionary/" + myWord
    html_content    = requests.get(merriamURL).text
    soup            = BeautifulSoup(html_content,"html.parser")
    defComponents   = soup.findAll("span", {"class": "dtText"})

    defs = []
    for each in defComponents:
        whiteIndex = each.text.find("   ")
        if(whiteIndex == -1):
            ans = each.text[2:]
            while re.search(r"[(].*[)]", ans) != None:
                ans = ans.replace(re.search(r"[(].*[)]", ans).group(), "")
            defs.append(ans)
        else:
            ans = each.text[2:whiteIndex]
            while re.search(r"[(].*[)]", ans) != None:
                ans = ans.replace(re.search(r"[(].*[)]", ans).group(), "")
            defs.append(ans)

    if(len(defs) == 0): #IF NO RESULTS ARE RETURNED
        return "NODEF"
    return defs[0]      #RETURN FIRST MEANING

def translate( myWord, currentAns ):
    lan         = detect(myWord.lower()+" ")
    translator  = Translator(from_lang=lan, to_lang="en")
    translation = translator.translate(myWord.lower()+" ")
    lanName     = pycountry.languages.get(alpha_2=lan).name

    if(lan == 'en'):    #IF THE WORD IS NOT A FOREIGN ONE, LEAVE IT AS IT IS
        return currentAns
    return translation.lower() + " in " + lanName.upper()

def decideResult( wnResult, mrResult, dcResult):
    resList = []
    for i in range(len(wnResult)):
        if(wnResult[i][2]   != "NODEF"):
            resList.append(wnResult[i])
        elif(mrResult[i][2] != "NODEF"):
            resList.append(mrResult[i])
        else:
            resList.append(dcResult[i])

    return resList
def findCorrectClue( list, littleNumber ):

    for i in range(len(list)):
        if(list[i][0] == littleNumber):
            return list[i][-1]

def pushLog( driver,logs, message ):
    #GET THE CURRENT TIME
    now     = datetime.now()
    time    = now.strftime("%H:%M:%S.%f")

    inserted     = "<div><h3>"+message+ "\t\t\t\t\t///"+time+"</h3></div>"
    script       = "arguments[0].insertAdjacentHTML('beforeend', arguments[1])"
    driver.execute_script(script, logs, inserted)
