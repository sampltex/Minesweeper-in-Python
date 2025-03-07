import os
import sys
import pygame
from pygame.locals import *
from pygame.font import *
import numpy as np
import pygetwindow as gw
import random
import math

global boardWidth, boardLength, numberOfMines, sweeping, screenHeight, screenWidth

boardLength = 18
boardWidth = 32
numberOfMines = 0

tileScale = 0.25
cellSize = tileScale * 128
global gameBoard   
gameBoard = np.zeros((0, 0))
# global win
win = False
firstClick = True
minesAround = 0
# if islands, winning, or counting breaks check these because i removed global from them

screenHeight = boardLength*cellSize # 288 for 9x9
screenWidth = boardWidth*cellSize # 288 for 9x9

pygame.init()
textFont = pygame.font.SysFont("🎉🎉🎉", 60)
screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.time.wait(100)
window = gw.getWindowsWithTitle("pygame window")[0]
clock = pygame.time.Clock()
running = True
sweeping = False

def create_path(relative_path: str) -> str:
    """Create and return the path to the resource depending on whether this is
       a PyInstaller exe or being run in the development environment."""
    path: str
    if hasattr(sys, '_MEIPASS'):
        path = os.path.join(sys._MEIPASS, relative_path)
    else:
        path = os.path.join(os.path.abspath("."), relative_path)
    return path

def get_image(sheet, frame, row, width, height, scale, colorkey):
    image = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()
    image.blit(sheet, (0, 0), (frame * width, row * height, width, height))
    image = pygame.transform.scale(image, (width * scale, height * scale))
    image.set_colorkey(colorkey)
    return image
spritesheet = pygame.image.load(create_path("MinesweeperSheet.jpg")) # 512 x 384

hiddenTile = get_image(spritesheet, 0, 0, 128, 128, tileScale, (1, 1, 1))
flaggedTile = get_image(spritesheet, 1, 0, 128, 128, tileScale, (1, 1, 1))
mineTile = get_image(spritesheet, 2, 0, 128, 128, tileScale, (1, 1, 1))
blankTile = get_image(spritesheet, 3, 0, 128, 128, tileScale, (1, 1, 1))
oneTile = get_image(spritesheet, 0, 1, 128, 128, tileScale, (1, 1, 1))
twoTile = get_image(spritesheet, 1, 1, 128, 128, tileScale, (1, 1, 1))
threeTile = get_image(spritesheet, 2, 1, 128, 128, tileScale, (1, 1, 1))
fourTile = get_image(spritesheet, 3, 1, 128, 128, tileScale, (1, 1, 1))
fiveTile = get_image(spritesheet, 0, 2, 128, 128, tileScale, (1, 1, 1))
sixTile = get_image(spritesheet, 1, 2, 128, 128, tileScale, (1, 1, 1))
sevenTile = get_image(spritesheet, 2, 2, 128, 128, tileScale, (1, 1, 1))
eightTile = get_image(spritesheet, 3, 2, 128, 128, tileScale, (1, 1, 1))
# screen.blit(hiddenTile, (100, 100)) the tuple is the location

pygame.display.set_caption('Minesweeper')
pygame.display.set_icon(get_image(spritesheet, 2, 0, 128, 128, tileScale, (128, 128, 128)))

global hiddenCellTypes
hiddenCellTypes = { # tens position
    1: hiddenTile,
    2: flaggedTile,
    3: { # ones position also shownCellTypes
        0: blankTile,
        1: oneTile,
        2: twoTile,
        3: threeTile,
        4: fourTile,
        5: fiveTile,
        6: sixTile,
        7: sevenTile,
        8: eightTile,
        9: mineTile
    }
}

class cell:

    def revealCell(XPos, YPos):
        global gameBoard
        if int(int(gameBoard[int(YPos-1)][int(XPos-1)])/10) == 1:
            gameBoard[int(YPos-1)][int(XPos-1)] += 20
    
    def placeFlag(XPos, YPos):
        global gameBoard
        try:
            if int(int(gameBoard[int(YPos-1)][int(XPos-1)])/10) == 1:
                gameBoard[int(YPos-1)][int(XPos-1)] += 10
            elif int(int(gameBoard[int(YPos-1)][int(XPos-1)])/10) == 2:
                gameBoard[int(YPos-1)][int(XPos-1)] -= 10
        except:
            IndexError

    def revealAroundBlankTile(XPos, YPos):
        global gameBoard
        rows, cols = gameBoard.shape
        if gameBoard[int(YPos)][int(XPos)] != 30:
            return
        queue = [(YPos, XPos)]
        while queue:
            cy, cx = queue.pop(0)
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    ny = cy + dy
                    nx = cx + dx
                    if 0 <= ny < rows and 0 <= nx < cols:
                        if gameBoard[int(ny)][int(nx)] // 10 == 1:
                            gameBoard[int(ny)][int(nx)] += 20
                            if gameBoard[int(ny)][int(nx)] % 10 == 0:
                                queue.append((ny, nx))

    def revealAroundRevealedTile(XPos, YPos):
        global gameBoard
        rows, cols = gameBoard.shape
        flag_count = 0
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                ny = YPos + dy
                nx = XPos + dx
                if 0 <= ny < rows and 0 <= nx < cols:
                    if int(gameBoard[int(ny)][int(nx)]/10) == 2:
                        flag_count += 1
        if flag_count == gameBoard[int(YPos)][int(XPos)] % 10:
            pass
        else:
            return

        if int(gameBoard[int(YPos)][int(XPos)]/10) != 3:
            return
        cy, cx = YPos, XPos
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                ny = cy + dy
                nx = cx + dx
                if 0 <= ny < rows and 0 <= nx < cols:
                    if int(gameBoard[int(ny)][int(nx)]/10) == 1:
                        gameBoard[int(ny)][int(nx)] += 20

    def makeIsland(x, y):
        global gameBoard, minesAround
        original = gameBoard.copy()
        rows, cols = original.shape
        minesAround = 0
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                ny = y + dy-1
                nx = x + dx-1
                if 0 <= ny < rows and 0 <= nx < cols:
                    if original[int(ny)][int(nx)] == 29 or original[int(ny)][int(nx)] == 19 or original[int(ny)][int(nx)] == 39:
                        gameBoard[int(ny)][int(nx)] = 10
                        minesAround += 1
        board.assignCorrectBoardValues()

class board:

    def createBoard(width, length, minecount):
        global gameBoard
        gameBoard = np.ones(length*width)
        for i in range(length*width):
            gameBoard[i] = 10
        for i in range(minecount):
            gameBoard[i] = 19
        random.shuffle(gameBoard)
        gameBoard = gameBoard.reshape(length,width)
        # print(gameBoard)

    def renderBoard():
        global gameBoard
        county = 0
        for y in gameBoard:
            countx = 0
            for x in y:
                if int(x/10) == 1:
                    screen.blit(hiddenTile, (countx*cellSize, county*cellSize))
                elif int(x/10) == 2:
                    screen.blit(flaggedTile, (countx*cellSize, county*cellSize))
                else:
                    x -= 30
                    screen.blit(hiddenCellTypes[3][x], (countx*cellSize, county*cellSize))
                countx += 1
            county += 1

    def assignCorrectBoardValues():
        global gameBoard
        original = gameBoard.copy()
        rows, cols = original.shape
        for y in range(rows):
            for x in range(cols):
                if original[y][x] == 29 or original[y][x] == 19 or original[y][x] == 39:
                    continue
                mine_count = 0
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        if dx == 0 and dy == 0:
                            continue
                        ny = y + dy
                        nx = x + dx
                        if 0 <= ny < rows and 0 <= nx < cols:
                            if original[ny][nx] == 29 or original[ny][nx] == 19 or original[ny][nx] == 39:
                                mine_count += 1
                gameBoard[y][x] = 10 + mine_count

    def showMines():
        global gameBoard
        rows, cols = gameBoard.shape
        for y in range(rows):
            for x in range(cols):
                if gameBoard[y][x] == 19:
                    gameBoard[y][x] += 20

    def checkForLoss():
        global gameBoard, firstClick
        rows, cols = gameBoard.shape
        for y in range(rows):
            for x in range(cols):
                if gameBoard[y][x] == 39:
                    pygame.time.wait(1000)
                    firstClick = True
                    board.createBoard(boardWidth, boardLength, numberOfMines)
                    board.assignCorrectBoardValues()
                    break

    def checkForWin():
        global gameBoard
        rows, cols = gameBoard.shape
        shownTiles = 0
        for y in range(rows):
            for x in range(cols):
                if gameBoard[y][x] // 10 == 3 and gameBoard[y][x] != 39:
                    shownTiles += 1
        if shownTiles == (boardLength * boardWidth) - (numberOfMines): #- minesAround):
            global win
            win = True
    
    def showBoard():
        global gameBoard
        rows, cols = gameBoard.shape
        for y in range(rows):
            for x in range(cols):
                if gameBoard[y][x] == 19:
                    gameBoard[y][x] = 29
                elif int(gameBoard[y][x]/10) == 1:
                    gameBoard[y][x] += 20
                elif int(gameBoard[y][x]/10) == 2 and gameBoard[y][x] != 29:
                    gameBoard[y][x] += 10

    def fixMinesAfterClick():
        global gameBoard, minesAround
        rows, cols = gameBoard.shape
        while minesAround > 0:
            randomY = random.randint(0,rows-1)
            randomX = random.randint(0,cols-1)
            if gameBoard[randomY][randomX] % 10 != 9 and gameBoard[randomY][randomX]//10 != 3:
                gameBoard[randomY][randomX] = 19
            else:
                minesAround += 1
            minesAround -= 1
        board.assignCorrectBoardValues()
        cell.revealCell(calcMouseCellPos()[0]/cellSize,calcMouseCellPos()[1]/cellSize)
        cell.revealAroundBlankTile((calcMouseCellPos()[0]/cellSize)-1,(calcMouseCellPos()[1]/cellSize)-1)

base1 = Rect((133,228), (130,70))
base2 = Rect((361,228), (285,70))
base3 = Rect((734,228), (167,70))
outline11 = Rect((125, 220), (138, 78))
outline12 = Rect((125, 220), (146, 86))
outline21 = Rect((353, 220), (293, 78))
outline22 = Rect((353, 220), (301, 86))
outline31 = Rect((726, 220), (175, 78))
outline32 = Rect((726, 220), (183, 86))
buttonCorner = get_image(spritesheet, 7, 0, 16, 16, 0.5, (0, 0, 0))
textButton1 = textFont.render('Easy', False, (0, 200, 0))
textButton2 = textFont.render('Intermediate', False, (255, 255, 0))
textButton3 = textFont.render('Expert', False, (255, 0, 0))
altTextFont = pygame.font.SysFont("🎉🎉🎉", 20)
textButton4 = altTextFont.render('Challenge?', False, (10, 10, 10))

class menu:

    def renderMenu():
        # Easy button
        pygame.draw.rect(screen, (128, 128, 128), outline12)
        pygame.draw.rect(screen, (255, 255, 255), outline11)
        screen.blit(buttonCorner, (263,220))
        screen.blit(buttonCorner, (125, 298))
        pygame.draw.rect(screen, (192, 192, 192), base1)
        screen.blit(textButton1, (150, screenHeight/2-45))
        # Intermediate button
        pygame.draw.rect(screen, (128, 128, 128), outline22)
        pygame.draw.rect(screen, (255, 255, 255), outline21)
        screen.blit(buttonCorner, (646, 220))
        screen.blit(buttonCorner, (353, 298))
        pygame.draw.rect(screen, (192, 192, 192), base2)
        screen.blit(textButton2, (screenWidth/2-135, screenHeight/2-45))
        # Expert button
        pygame.draw.rect(screen, (128, 128, 128), outline32)
        pygame.draw.rect(screen, (255, 255, 255), outline31)
        screen.blit(buttonCorner, (901, 220))
        screen.blit(buttonCorner, (726, 298))
        pygame.draw.rect(screen, (192, 192, 192), base3)
        screen.blit(textButton3, (750, screenHeight/2-45))

        screen.blit(textButton4, (949, 560))
        
    def centerWindow():
        window.moveTo(int(1920//2-screenWidth//2), int(1080//2-screenHeight//2))

    def preLoadBoardSettings(boardWidthF, boardLengthF, numberOfMinesF):
        global boardWidth, boardLength, numberOfMines, sweeping, screenHeight, screenWidth, firstClick
        boardWidth = boardWidthF
        boardLength = boardLengthF
        numberOfMines = numberOfMinesF
        screenHeight = boardLengthF*cellSize
        screenWidth = boardWidthF*cellSize
        screen = pygame.display.set_mode((screenWidth, screenHeight))
        board.createBoard(boardWidthF, boardLengthF, numberOfMinesF)
        board.assignCorrectBoardValues()
        firstClick = True
        sweeping = True
        menu.centerWindow()
        print(gameBoard)

    def checkPressedButtons(XPos, YPos):
        if (XPos >= 125 and XPos <= 270) and (YPos >= 220 and YPos <= 305):
            menu.preLoadBoardSettings(9, 9, 10)
        elif (XPos >= 353 and XPos <= 654) and (YPos >= 220 and YPos <= 305):
            menu.preLoadBoardSettings(16, 16, 40)
        elif (XPos >= 726 and XPos <= 909) and (YPos >= 220 and YPos <= 305):
            menu.preLoadBoardSettings(30, 16, 99)
        elif XPos >= 950  and YPos >= 558:
            menu.preLoadBoardSettings(50, 30, 333)

def calcMouseCellPos():
    mouseXPos,mouseYPos = pygame.mouse.get_pos()
    mouseXPos = math.ceil(mouseXPos / cellSize) * cellSize
    mouseYPos = math.ceil(mouseYPos / cellSize) * cellSize
    return (mouseXPos,mouseYPos)

while running:
    screen.fill("black")
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if sweeping:
            if pygame.mouse.get_pressed(num_buttons=3)[0]:
                try:
                    if pygame.mouse.get_pressed(num_buttons=3)[2]:
                        cell.revealAroundRevealedTile((calcMouseCellPos()[0]/cellSize)-1,(calcMouseCellPos()[1]/cellSize)-1)
                        pygame.time.wait(1)
                        for dy in (-1, 0, 1):
                            for dx in (-1, 0, 1):
                                if dx == 0 and dy == 0:
                                    continue
                                cell.revealAroundBlankTile(((calcMouseCellPos()[0]/cellSize)-1)+dx,((calcMouseCellPos()[1]/cellSize)-1)+dy)
                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # replace elif for else if you want to hold down m1 to reveal tiles
                        if firstClick:
                            cell.makeIsland(calcMouseCellPos()[0]/cellSize,calcMouseCellPos()[1]/cellSize)
                            firstClick = False
                            cell.revealCell(calcMouseCellPos()[0]/cellSize,calcMouseCellPos()[1]/cellSize)
                            cell.revealAroundBlankTile((calcMouseCellPos()[0]/cellSize)-1,(calcMouseCellPos()[1]/cellSize)-1)
                            board.fixMinesAfterClick()
                            print(gameBoard)
                        else:
                            cell.revealCell(calcMouseCellPos()[0]/cellSize,calcMouseCellPos()[1]/cellSize)
                            cell.revealAroundBlankTile((calcMouseCellPos()[0]/cellSize)-1,(calcMouseCellPos()[1]/cellSize)-1)
                except:
                        IndexError
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                cell.placeFlag(calcMouseCellPos()[0]/cellSize,calcMouseCellPos()[1]/cellSize)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not win:
                        board.showBoard()
                        win = True
                    else:
                        board.createBoard(boardWidth, boardLength, numberOfMines)
                        board.assignCorrectBoardValues()
                        firstClick = True
                        win = False
                if event.key == pygame.K_ESCAPE:
                    boardLength = 18
                    boardWidth = 32
                    numberOfMines = 0
                    screenHeight = boardLength*cellSize
                    screenWidth = boardWidth*cellSize
                    screen = pygame.display.set_mode((screenWidth, screenHeight))
                    menu.centerWindow()
                    sweeping = False

            board.renderBoard()
            pygame.display.update()
            board.checkForLoss()
            board.checkForWin()

        else:
            menu.renderMenu()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                menu.checkPressedButtons(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1])
            pygame.display.update()

    clock.tick(60)

pygame.quit()
