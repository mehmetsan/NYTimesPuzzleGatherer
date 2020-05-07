from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime
import time
import os
import requests
import methods as m

#INITIALIZING A CHROME DRIVER
driver = webdriver.Chrome()
driver.maximize_window()
driver.get("https://www.nytimes.com/crosswords/game/mini")
time.sleep(7)


# INITIALIZING DRIVER FOR LOG
driver2     = webdriver.Chrome()
path        = os.getcwd() + "\\log.html"    #GET RELATIVE PATH
driver2.get(path)                           #OPEN RECONSTRUCT SITE
logs        =  driver2.find_element_by_id("log")

m.pushLog(driver2,logs,"Driver accessed the site")

#CLOSE THE INITIAL POP-UP
popUp = driver.find_element(By.XPATH, '//button[contains(.,\'OK\')]')
popUp.click()
time.sleep(1)
m.pushLog(driver2,logs,"Closed the initial pop-up")

#GET THE PAGE CONTENTS
html = driver.page_source
soup = BeautifulSoup(html,"html.parser")
m.pushLog(driver2,logs,"Got the site contents")

#FINDING THE DATACELLS (BOXES)
group = soup.find ('g', {'data-group' : 'cells'})
datas = group.findAll("g")

#GETTING THE SCHEMA OF THE GRID
blacks  = []
whites  = []
numbers = []

for each in datas:
    dataContent = each.find("text") #LOOKING FOR A TEXT IN EACH BOX
    if(dataContent is None):        #A BLACK SQUARE INDEX
        boxId = each.find ('rect')["id"].replace("cell-id-","")
        blacks.append(boxId)        #ADDING THE INDEX TO CORRECT LIST

    else:                           #A WHITE SQUARE INDEX
        boxId = each.find ('rect')["id"].replace("cell-id-","")
        whites.append(boxId)        #ADDING THE INDEX TO CORRECT LIST

        #LOCATING LITTLE NUMBERS
        if(each.find('text').get_text() == ""):
            pass
        else:
            littleNumber = each.find('text').get_text()
            numbers.append([littleNumber,boxId])    #ADD THE LITTLE NUMBER AND BOXID PAIR AS A LIST TO NUMBERS LIST
m.pushLog(driver2,logs,"Located indexes of blacks, letters and little numbers")
#GETTING THE CLUES
clues   = soup.find('section', {'class' : 'Layout-clueLists--10_Xl'}).findAll("div")
acr     = clues[0].find("ol").findAll("li") #LIST OF ACROSS CLUES SOUP OBJECT
dwn     = clues[1].find("ol").findAll("li") #LIST OF DOWN CLUES SOUP OBJECT

#GETTING THE CLUES IN LIST FORMAT
across  = []
down    = []

#CONVERTING THE SOUP ELEMENT INTO A LIST
for each in acr:
    clueNo  = each.findAll("span")[0].get_text()   #THE PART WHERE THE TEXT OF THE CLUE IS STORED
    clue    = each.findAll("span")[1].get_text()   #THE PART WHERE THE TEXT OF THE CLUE IS STORED
    across.append([clueNo,clue])                         #ADD THE CLUE TO LIST

#CONVERTING THE SOUP ELEMENT INTO A LIST
for each in dwn:
    clueNo  = each.findAll("span")[0].get_text()   #THE PART WHERE THE TEXT OF THE CLUE IS STORED
    clue    = each.findAll("span")[1].get_text()   #THE PART WHERE THE TEXT OF THE CLUE IS STORED
    down.append([clueNo,clue])                           #ADD THE CLUE TO LIST

m.pushLog(driver2,logs,"Stored across and down clues as lists")

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
m.pushLog(driver2,logs,"Approved to reveal the puzzle")

#CLOSE THE POP-UP BY SENDING ESC KEY
time.sleep(1)
chain = ActionChains(driver)
chain.send_keys(Keys.ESCAPE).perform()
m.pushLog(driver2,logs,"Closed the pop-up")

#GET THE NEW CONTENTS, UPDATE THE SOUP WITH THE REVEALED STATE
html = driver.page_source
soup = BeautifulSoup(html,"html.parser")
m.pushLog(driver2,logs,"Updated the soup with the revealed state")

letters = []
group   = soup.find ('g', {'data-group' : 'cells'})
groups  = group.findAll("g")


for each in groups:
    #LOCATING LETTERS
    if(each.find('text') is None):  #IF A BLACK SQUARE IS ENCOUNTERED
        letters.append("BLACK")
    else:                           #IF A WHITE SQUARE IS ENCOUNTERED
        texts = each.findAll("text")

        lastTextIndex   = len(texts) - 1              #NEED TO FIND THE LAST TEXT TAG, IN WHERE THE LETTER IS STORED
        letter          = texts[lastTextIndex].get_text()    #SINCE LITTLE NUMBERS ARE IN THE FIRST TEXT TAG
        letters.append(letter)                      #STORE THE LETTER

m.pushLog(driver2,logs,"Stored the revealed state letters")

####################################
#-------NEW CLUE GENERATION--------#
####################################


###STORING ANSWERS IN (LITTLENO, INDEX, ANSWER) TRIPLETS
rowAnswers = []
for x in range(5):
    first = True
    litNo = -1
    co = 5
    answer = ""
    check = True
    index = -1
    for y in range(5):
        if(letters[co*x+y] != "BLACK"):
            if(first):
                first = False
                for i in range(len(numbers)):
                    if(numbers[i][1] == str(co*x+y) ):

                        litNo = numbers[i][0]
            if(check):
                index = co*x +y
                check = False
            answer += letters[co*x+y]
    rowAnswers.append((litNo,index,answer))

colAnswers = []
for x in range(5):
    first = True
    litNo = -1
    co = 5
    answer = ""
    check = True
    index = -1
    for y in range(5):
        if(letters[co*y+x] != "BLACK"):
            if(first):
                first = False
                for i in range(len(numbers)):
                    if(numbers[i][1] == str(co*y+x) ):
                        litNo = numbers[i][0]

            if(check):
                index = co*y+x
                check = False
            answer += letters[co*y+x]
    colAnswers.append((litNo,index,answer))
m.pushLog(driver2,logs,"Stored answer along with their start indexes")

#### GETTING DEFINITIONS PART ####

wnRowResults = []
mrRowResults = []
dcRowResults = []

# GET DEFINITIONS FOR ROW CLUES
for each in rowAnswers:
    currentAns      = m.findCorrectClue(across,each[0])
    wordnetResult   = m.tryWordnet(each[2])
    merriamResult   = m.tryMerriam(each[2])
    translation     = m.translate(each[2],currentAns)

    wnRowResults.append((each[0],each[2],wordnetResult))
    mrRowResults.append((each[0],each[2],merriamResult))
    dcRowResults.append((each[0],each[2],translation))

wnColResults = []
mrColResults = []
dcColResults = []
m.pushLog(driver2,logs,"Gathered alternatives for 'Across' answers")


# GET DEFINITIONS FOR COL CLUES
for each in colAnswers:
    currentAns      = m.findCorrectClue(down,each[0])
    print(currentAns)
    wordnetResult   = m.tryWordnet(each[2])
    merriamResult   = m.tryMerriam(each[2])
    translation     = m.translate(each[2],currentAns)

    wnColResults.append((each[0],each[2],wordnetResult))
    mrColResults.append((each[0],each[2],merriamResult))
    dcColResults.append((each[0],each[2],translation))

m.pushLog(driver2,logs,"Gathered alternatives for 'Down' answers")

# CHOOSE AND STORE THE GENERATED CLUES
accrossClues    = m.decideResult(driver2, logs, wnRowResults,mrRowResults,dcRowResults)
downClues       = m.decideResult(driver2, logs, wnColResults,mrColResults,dcColResults)
m.pushLog(driver2,logs,"Selected regenerated clues from various sources")
m.pushLog(driver2,logs,"based on source priorities")


####################################
#-------PUZZLE REGENERATION--------#
####################################
time.sleep(5)
path = os.getcwd() + "\\site.html"  #GET RELATIVE PATH
driver.get(path)                    #OPEN RECONSTRUCT SITE

#INITIAL COORDINATES FOR THE RECONSTRUCTED TABLE
X=70
Y=7
index=1 #CURRENT BOX INDEX

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
            inserted = "<g><rect x="+str(X)+" y="+str(Y)+" width=10 height=10 style=\"fill:white;opacity:0.5\" />\" /> <text x="+str(X+3)+" y="+str(Y+6)+" font-size = 5 >"+each+"</text> <text aria-live=\"polite\"" +"x="+str(X+1)+" y="+str(Y+2)+" font-size = 2 >"+number+"</text> </g>"
        else:                       #NORMAL SQUARES WITHOUT LITTLE NUMBERS
            inserted = "<g><rect x="+str(X)+" y="+str(Y)+" width=10 height=10 style=\"fill:white;opacity:0.5\" />\" /> <text x="+str(X+3)+" y="+str(Y+6)+" font-size = 5 >"+each+"</text> </g>"

    if(index % 5 == 0):             #CALCULATE NEXT SQUARE COORDINATES (VERTICAL)
            X = 70
            Y += 11
    else:                           #CALCULATE NEXT SQUARE COORDINATES (HORIZONTAL)
        X += 11

    index += 1

    #MAKE THE INSERTION TO THE HTML OF THE PAGE
    script = "arguments[0].insertAdjacentHTML('beforeend', arguments[1])"
    driver.execute_script(script, element, inserted)

m.pushLog(driver2,logs,"Reconstructed the puzzle on custom site")

####################################
#------RECONSTRUCTING CLUES--------#
####################################

#ADD EACH ONE OF THE ORIGINAL ACROSS CLUES
element =  driver.find_element_by_id("acrossClues")
inserted= "<div><text>"+"<b> ORIGINAL CLUES </b> "+"</text></div>"
script  = "arguments[0].insertAdjacentHTML('beforeend', arguments[1])"
driver.execute_script(script, element, inserted)

for i in range(len(across)):
    clueNo  = across[i][0]
    if(len(down[i][1]) > 60):
        index = across[:60].rindex(' ')
        part1   = "<div><text><b>"+clueNo + "</b> " +across[i][1][:index]+"</text></div>"
        part2   = "<div><text>"+ "  " +across[i][1][index:]+"</text></div>"
        script  = "arguments[0].insertAdjacentHTML('beforeend', arguments[1])"
        driver.execute_script(script, element, part1)
        driver.execute_script(script, element, part2)
    else:
        inserted= "<div><text><b>"+clueNo + "</b> " +across[i][1]+"</text></div>"
        script  = "arguments[0].insertAdjacentHTML('beforeend', arguments[1])"
        driver.execute_script(script, element, inserted)

#ADD EACH ONE OF THE GENERATED ACROSS CLUES
element =  driver.find_element_by_id("acrossClues")
inserted= "<div><text>"+"<b> GENERATED CLUES </b>"+"</text></div>"
script  = "arguments[0].insertAdjacentHTML('beforeend', arguments[1])"
driver.execute_script(script, element, inserted)
for i in range(len(across)):
    clueNo  = across[i][0]
    clue    = m.findCorrectClue(accrossClues, clueNo)
    clue    = clue[0].upper() + clue[1:]
    if(len(clue) > 60):
        index = clue[:60].rindex(' ')
        part1   = "<div><text><b>"+clueNo + "</b> " +clue[:index]+"</text></div>"
        part2   = "<div><text>"+"  " +clue[index:]+"</text></div>"
        script  = "arguments[0].insertAdjacentHTML('beforeend', arguments[1])"
        driver.execute_script(script, element, part1)
        driver.execute_script(script, element, part2)
    else:
        inserted= "<div><text><b>"+clueNo + "</b> " +clue+"</text></div>"
        script  = "arguments[0].insertAdjacentHTML('beforeend', arguments[1])"
        driver.execute_script(script, element, inserted)


#ADD EACH ONE OF THE ORIGINAL DOWN CLUES
element =  driver.find_element_by_id("downClues")
inserted= "<div><text>"+"<b> ORIGINAL CLUES </b> "+"</text></div>"
script  = "arguments[0].insertAdjacentHTML('beforeend', arguments[1])"
driver.execute_script(script, element, inserted)
for i in range(len(down)):
    clueNo  = down[i][0]
    if(len(down[i][1]) > 60):
        index = down[:60].rindex(' ')
        part1   = "<div><text><b>"+clueNo + "</b> " +down[i][1][:index]+"</text></div>"
        part2   = "<div><text>"+ "  " +down[i][1][index:]+"</text></div>"
        script  = "arguments[0].insertAdjacentHTML('beforeend', arguments[1])"
        driver.execute_script(script, element, part1)
        driver.execute_script(script, element, part2)
    else:
        inserted= "<div><text><b>"+clueNo + "</b> " +down[i][1]+"</text></div>"
        script  = "arguments[0].insertAdjacentHTML('beforeend', arguments[1])"
        driver.execute_script(script, element, inserted)

#ADD EACH ONE OF THE GENERATED DOWN CLUES
element =  driver.find_element_by_id("downClues")
inserted= "<div><text>"+"<b> GENERATED CLUES </b>"+"</text></div>"
script  = "arguments[0].insertAdjacentHTML('beforeend', arguments[1])"
driver.execute_script(script, element, inserted)
for i in range(len(down)):
    clueNo  = down[i][0]
    clue    = m.findCorrectClue(downClues, clueNo)
    clue    = clue[0].upper() + clue[1:]
    if(len(clue) > 60):
        index = clue[:60].rindex(' ')
        part1   = "<div><text><b>"+clueNo + "</b> " +clue[:index]+"</text></div>"
        part2   = "<div><text>"+ "  " +clue[index:]+"</text></div>"
        script  = "arguments[0].insertAdjacentHTML('beforeend', arguments[1])"
        driver.execute_script(script, element, part1)
        driver.execute_script(script, element, part2)
    else:
        inserted= "<div><text><b>"+clueNo + "</b> " +clue+"</text></div>"
        script  = "arguments[0].insertAdjacentHTML('beforeend', arguments[1])"
        driver.execute_script(script, element, inserted)

m.pushLog(driver2,logs,"Inserted new clues to the custom site")
#GET THE CURRENT TIME
now     = datetime.now()
time    = now.strftime("%d/%m/%Y %H:%M:%S")
info    = "Date is : <b>" + time + "</b> Prepared by Group : <b>POWERPUFFGIRLS</b>"

#INSERT GROUP INFO INTO CORRECT PLACE
element     =  driver.find_element_by_id("board")
inserted    = "<div id=\"group_name\"><h6>"+info+"</h6></div>"
script      = "arguments[0].insertAdjacentHTML('afterend', arguments[1])"
driver.execute_script(script, element, inserted)
m.pushLog(driver2,logs,"Inserted group info to the custom site")

#CHANGE THE TITLE AS THE CURRENT DATE
title   = driver.find_element(By.XPATH, '//title')
date    = now.strftime("%d/%m/%Y")
script  = "arguments[0].insertAdjacentHTML('beforeend', arguments[1])"
driver.execute_script(script, title, date)

#SAVE THE RESULT
fileName  = date.replace('/',"-")
path      = os.getcwd()+"\\storedPuzzles\\"
f   = open(path+fileName+".html","w+")
f.write(driver.page_source)
f.close()
m.pushLog(driver2,logs,"Saved the custom site")
