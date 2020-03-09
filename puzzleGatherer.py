'''
    Written by: Mehmet Sanisoğlu
'''

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime
import time
import os

#INITIALIZING A CHROME DRIVER
driver = webdriver.Chrome()
driver.get("https://www.nytimes.com/crosswords/game/mini")
time.sleep(7)

#CLOSE THE INITIAL POP-UP
popUp = driver.find_element(By.XPATH, '//button[contains(.,\'OK\')]')
popUp.click()
time.sleep(1)

#GET THE PAGE CONTENTS
html = driver.page_source
soup = BeautifulSoup(html,"html.parser")

group = soup.find ('g', {'data-group' : 'cells'})
datas = group.findAll("g")

#GETTING THE SCHEMA OF THE GRID
blacks = []
whites = []
numbers = []

for each in datas:
    dataContent = each.find("text")
    if(dataContent is None):   #A BLACK SQUARE INDEX
        boxId = each.find ('rect')["id"].replace("cell-id-","")
        blacks.append(boxId)
    else:               #A WHITE SQUARE INDEX
        boxId = each.find ('rect')["id"].replace("cell-id-","")
        whites.append(boxId)

        #LOCATING LITTLE NUMBERS
        if(each.find('text').get_text() == ""):
            pass
        else:
            numbers.append([each.find('text').get_text(),boxId])

#GETTING THE CLUES
clues = soup.find('section', {'class' : 'Layout-clueLists--10_Xl'}).findAll("div")
acr = clues[0].find("ol").findAll("li") #LIST OF ACROSS CLUES SOUP OBJECT
dwn = clues[1].find("ol").findAll("li") #LIST OF DOWN CLUES SOUP OBJECT

#GETTING THE CLUES IN LIST FORMAT
across = []
down = []

#CONVERTING THE SOUP ELEMENT INTO A LIST
for each in acr:
    clue = each.findAll("span")[1].get_text()
    across.append(clue)

#CONVERTING THE SOUP ELEMENT INTO A LIST
for each in dwn:
    clue = each.findAll("span")[1].get_text()
    down.append(clue)


#LOCATING REVEAL BUTTON
reveal = driver.find_element(By.XPATH, '//button[contains(.,\'reveal\')]')
reveal.click()
time.sleep(1)

#REVEAL WHOLE PUZZLE
puzzle = driver.find_element_by_link_text('Puzzle')
puzzle.click()

#APPROVE REVEAL
reveal2 = driver.find_element(By.XPATH, '//span[contains(.,\'Reveal\')]')
reveal2.click()

#CLOSE THE POP-UP BY SENDING ESC KEY
time.sleep(1)
chain = ActionChains(driver)
chain.send_keys(Keys.ESCAPE).perform()

#GET THE NEW CONTENTS, UPDATE THE SOUP WITH THE REVEALED STATE
html = driver.page_source
soup = BeautifulSoup(html,"html.parser")

letters = []
group = soup.find ('g', {'data-group' : 'cells'})
groups = group.findAll("g")


for each in groups:
    #LOCATING LETTERS
    if(each.find('text') is None):  #IF A BLACK SQUARE IS ENCOUNTERED
        letters.append("BLACK")
    else:                           #IF A WHITE SQUARE IS ENCOUNTERED
        texts = each.findAll("text")

        lastTextIndex = len(texts) - 1              #NEED TO FIND THE LAST TEXT TAG, IN WHERE THE LETTER IS STORED
        letter = texts[lastTextIndex].get_text()    #DUE TO LITTLE NUMBERS COMING BEFORE THE ACTUAL LETTERS
        letters.append(letter)                      #STORE THE LETTER


#------------------------------------------------------------------------
#RECONSTRUCTING PUZZLE
#------------------------------------------------------------------------

path = os.getcwd() + "\\site.html"  #GET RELATIVE PATH
driver.get(path)                    #OPEN RECONSTRUCT SITE

html = driver.page_source
soup = BeautifulSoup(html,"html.parser")

X=50
Y=0
index=1
for each in letters:                #FOR EACH COLLECTED LETTER, PLACE THEM IN CORRECT POSITIONS
    number = -1

    for pair in numbers:            #CHECK WHETHER THIS SQUARE MUST HAVE A LITTLE NUMBER
        if(int(pair[1]) == index-1):
            number = pair[0]

    inserted = ""                   #LINE TO BE INSERTED
    element =  driver.find_element_by_id("puzzleData")

    if(each == "BLACK"):            #FOR BLACK SQUARE
        inserted = "<g><rect x="+str(X)+" y="+str(Y)+" width=10 height=10 style=\"fill:black\"/>\" /></g>"
    else:                           #FOR NORMAL SQUARE

        if(number != -1):           #FLAG FOR SQUARES WITH LITTLE NUMBERS
            inserted = "<g><rect x="+str(X)+" y="+str(Y)+" width=10 height=10 style=\"fill:white;opacity:0.5\" />\" /> <text x="+str(X+3)+" y="+str(Y+6)+" font-size = 5 >"+each+"</text> <text x="+str(X+1)+" y="+str(Y+2)+" font-size = 2 >"+number+"</text> </g>"
        else:                       #NORMAL SQUARES WITHOUT LITTLE NUMBERS
            inserted = "<g><rect x="+str(X)+" y="+str(Y)+" width=10 height=10 style=\"fill:white;opacity:0.5\" />\" /> <text x="+str(X+3)+" y="+str(Y+6)+" font-size = 5 >"+each+"</text> </g>"

    if(index % 5 == 0):             #CALCULATE NEXT SQUARE COORDINATES (VERTICAL)
            X = 50
            Y += 11
    else:                           #CALCULATE NEXT SQUARE COORDINATES (HORIZONTAL)
        X += 11

    index += 1

    #MAKE THE INSERTION TO THE HTML OF THE PAGE
    script = "arguments[0].insertAdjacentHTML('beforeend', arguments[1])"
    driver.execute_script(script, element, inserted)


#RECONSTRUCTING CLUES

#ADD EACH ONE OF THE COLLECTED ACROSS CLUES
element =  driver.find_element_by_id("acrossClues")
for each in across:
    inserted = "<li><span>"+each+"</span></li>"
    script = "arguments[0].insertAdjacentHTML('beforeend', arguments[1])"
    driver.execute_script(script, element, inserted)


#ADD EACH ONE OF THE COLLECTED DOWN CLUES
element =  driver.find_element_by_id("downClues")
for each in down:
    inserted = "<li><span>"+each+"</span></li>"
    script = "arguments[0].insertAdjacentHTML('beforeend', arguments[1])"
    driver.execute_script(script, element, inserted)
    index += 1

#GET THE CURRENT TIME
now = datetime.now()
time = now.strftime("%d/%m/%Y %H:%M:%S")
info = "Date is : <b>" + time + "</b> Prepared by Group : <b>POWERPUFFGIRLS</b>"

#INSERT GROUP INFO INTO CORRECT PLACE
element =  driver.find_element_by_id("board")
inserted = "<div><p align=\"right\">" + info + "</p></div>"
script = "arguments[0].insertAdjacentHTML('beforeend', arguments[1])"
driver.execute_script(script, element, inserted)
