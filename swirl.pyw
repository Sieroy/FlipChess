import random
import math
import pygame
from pprint import pprint
from pygame.locals import *

screenSize = (1080, 720)
tickFPS = 60

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode(screenSize, 0, 32)
pygame.display.set_caption('Swirl')


class SwirlStage:
    def handle(self):
        pass

    def draw(self, surf):
        pass


class SwirlGame:
    waitingActionFlame = 25
    player0ScoreColor = pygame.Color(230,100,100)
    player1ScoreColor = pygame.Color(80,170,230)
    player0ScoreRect = pygame.Rect(screenSize[0]-350,60,150,50)
    player1ScoreRect = pygame.Rect(screenSize[0]-200,60,150,50)
    playersScoreBarRTWH = (50, 120, 300, 10)
    exitButtonRect = pygame.Rect(screenSize[0]-350,screenSize[1]-100,300,50)
    exitButtonColors = (
        pygame.Color(200,200,200),
        pygame.Color(200,150,200),
        pygame.Color(100,200,200)
    )

    class Piece:
        sizeWH = 48
        targetPos = (
            ((50-sizeWH//2, 50-sizeWH//2),),
            ((50-sizeWH//2, 70-sizeWH//2), (50-sizeWH//2, 30-sizeWH//2)),
            ((30-sizeWH//2, 68-sizeWH//2), (70-sizeWH//2, 68-sizeWH//2), (50-sizeWH//2, 32-sizeWH//2)),
            ((30-sizeWH//2, 70-sizeWH//2), (70-sizeWH//2, 70-sizeWH//2), (70-sizeWH//2, 30-sizeWH//2), (30-sizeWH//2, 30-sizeWH//2))
        )
        movingtimes = 20

        movingscale = tuple(range(1,1+math.ceil(movingtimes/2)))+tuple(range(1,1+math.floor(movingtimes/2)))[::-1]
        movingsteps_list = []
        for i in range(movingtimes):
            movingsteps_list.append(movingscale[i]/sum(movingscale[i:]))
        movingsteps = tuple(movingsteps_list)
        del movingscale
        del movingsteps_list

        imagenum = 18
        imageseq = []

        def __init__(self, pos=(-1,-1), chequer=None, player=None, game=None):
            self.player = player
            player.pieces.append(self)
            self.chequer = chequer
            self.game = game
            self.x, self.y = pos
            self.alpha = 255
            self.moving = -1
            self.turning = player.id*self.imagenum
            self.id = -1

        def setPlayer(self, player):
            if self.player != player:
                self.player.pieces.remove(self)
                player.pieces.append(self)
            self.player = player

        def setChequer(self, chequer, id):
            self.chequer = chequer
            self.id = id
            self.moving = 0

        def discard(self):
            self.player.pieces.remove(self)
            self.setChequer(None, -1)
            self.game.dustPieces.append(self)

        def update(self):
            if not self.chequer:
                if self.moving >=0:
                    self.alpha -= int(-self.alpha*self.movingsteps[self.moving])
                    if self.moving >= self.movingtimes:
                        self.moving = -1
            elif self.moving >= 0:
                targetX, targetY = self.targetPos[len(self.chequer.pieces)-1][self.id]
                targetX+= self.chequer.getOffset()[0]
                targetY+= self.chequer.getOffset()[1]
                self.x += int((targetX-self.x)*self.movingsteps[self.moving])
                self.y += int((targetY-self.y)*self.movingsteps[self.moving])
                self.moving += 1
                if self.moving >= self.movingtimes:
                    self.moving = -1

            if self.turning < self.player.id*self.imagenum:
                self.turning += 1
            elif self.turning > self.player.id*self.imagenum:
                self.turning -= 1

        def draw(self, surf):
            if self.alpha!=255:
                tmpalpha = self.imageseq[self.turning].get_alpha()
                self.imageseq[self.turning].set_alpha(alpha)
                surf.blit(self.imageseq[self.turning], (self.x, self.y))
                self.imageseq[self.turning].set_alpha(tmpalpha)
            else:
                surf.blit(self.imageseq[self.turning], (self.x, self.y))

    class Chequer:
        offsetX = 45
        offsetY = 45
        w = 100
        h = 100
        marginX = 6
        marginY = 6
        borderColor = (160, 160, 160)
        borderWeight = 1
        borderRadius = 4
        backgroundColor = (120, 120, 120, 100)
        backgrounds = tuple()

        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.pieces = []
            self.neighbors = []
            self.rect = pygame.Rect(self.getOffset(),(self.w,self.h))
            self.hovered = 0

        def addPiece(self, piece):
            for p in self.pieces:
                p.setPlayer(piece.player)
                p.moving = 0
            if len(self.pieces) >= len(self.neighbors):
                piece.discard()
            else:
                self.pieces.append(piece)
                piece.setChequer(self, self.pieces.index(piece))

        def getPlayer(self):
            if not self.pieces:
                return None
            else:
                return self.pieces[0].player

        def diffuse(self):
            for ne in self.neighbors:
                ne.addPiece(self.pieces.pop())

        def diffusable(self):
            return len(self.pieces) >= len(self.neighbors)

        def draw(self, surf):
            surf.blit(self.backgrounds[self.hovered], self.rect)
            pygame.draw.rect(   surf,
                                self.borderColor,
                                self.rect,
                                self.borderWeight,
                                self.borderRadius)
            for p in self.pieces:
                p.update()
                p.draw(surf)

        def getOffset(self):
            return (self.x*(self.w+self.marginX)+self.offsetX,
                    self.y*(self.h+self.marginY)+self.offsetY)

    class Player:
        def __init__(self, id):
            self.pieces = []
            self.id = id


    def __init__(self, celist=None):
        self.backgroundImg = pygame.image.load('image/bg.png')
        self.textFont = pygame.font.Font('font/FZYTK.ttf', 30)

        if not self.Piece.imageseq:
            oriimg = pygame.image.load('image/turning.png')
            for i in range(19):
                tmpsurf = oriimg.subsurface(pygame.Rect(i*640,0,640,640))
                self.Piece.imageseq.append(pygame.transform.scale(tmpsurf, (self.Piece.sizeWH, self.Piece.sizeWH)))

        if not self.Chequer.backgrounds:
            self.Chequer.backgrounds = (
                pygame.Surface((self.Chequer.w,self.Chequer.h)),
                pygame.Surface((self.Chequer.w,self.Chequer.h))
            )
            pygame.draw.rect(   self.Chequer.backgrounds[0],
                                self.Chequer.backgroundColor,
                                pygame.Rect(0, 0, self.Chequer.w, self.Chequer.h),
                                0,
                                self.Chequer.borderRadius)
            pygame.draw.rect(   self.Chequer.backgrounds[1],
                                self.Chequer.backgroundColor,
                                pygame.Rect(0, 0, self.Chequer.w, self.Chequer.h),
                                0,
                                self.Chequer.borderRadius)
            self.Chequer.backgrounds[0].set_alpha(50)
            self.Chequer.backgrounds[1].set_alpha(100)

        self.board = {}
        line = row = 6
        for i in range(line):
            for j in range(row):
                self.board[(j,i)] = self.Chequer(j, i)

        for i in range(line):
            for j in range(row):
                cn = self.board.get((j-1, i))
                if cn:
                    self.board[(j,i)].neighbors.append(cn)
                cn = self.board.get((j+1, i))
                if cn:
                    self.board[(j,i)].neighbors.append(cn)
                cn = self.board.get((j, i-1))
                if cn:
                    self.board[(j,i)].neighbors.append(cn)
                cn = self.board.get((j, i+1))
                if cn:
                    self.board[(j,i)].neighbors.append(cn)

        self.players = [self.Player(0), self.Player(1)]
        self.nowPlayer = self.players[random.randint(0,1)]
        if celist:
            for i in range(6):
                for j in range(6):
                    if celist[i][j] > 0:
                        for _ in range(celist[i][j]):
                            self.board[(j, i)].pieces.append(self.Piece(player=self.players[0], chequer=self.board[(j, i)], game=self))
                    elif celist[i][j] < 0:
                        for _ in range(-celist[i][j]):
                            self.board[(j, i)].pieces.append(self.Piece(player=self.players[1], chequer=self.board[(j, i)], game=self))
        self.waitingAction = 1
        self.dustPieces = []
        self.piecesNum0 = 0
        self.piecesNum1 = 0
        self.player0ScoreSurf = self.textFont.render(str(self.piecesNum0), True, self.player0ScoreColor)
        self.player1ScoreSurf = self.textFont.render(str(self.piecesNum1), True, self.player1ScoreColor)
        self.player0ScoreBarRect = pygame.Rect(
            screenSize[0]-self.playersScoreBarRTWH[0]-self.playersScoreBarRTWH[2],
            self.playersScoreBarRTWH[1],
            int((self.piecesNum0*2+1)/((self.piecesNum0+self.piecesNum1)*2+2)*self.playersScoreBarRTWH[2]),
            self.playersScoreBarRTWH[3]
        )
        self.player1ScoreBarRect = pygame.Rect(
            self.player0ScoreBarRect.x+self.player0ScoreBarRect.w,
            self.playersScoreBarRTWH[1],
            self.playersScoreBarRTWH[2]-self.player0ScoreBarRect.w,
            self.playersScoreBarRTWH[3]
        )
        self.winner = None
        self.winnerSurf = None
        self.exitButtonState = 0
        self.exitButtonText = self.textFont.render('离开', True, self.exitButtonColors[0])

    def trigger(self):
        diffusing_list = []
        for ce in self.board.values():
            if ce.diffusable():
                diffusing_list.append(ce)
        for ce in diffusing_list:
            ce.diffuse()
        self.piecesNum0, self.piecesNum1 = len(self.players[0].pieces), len(self.players[1].pieces)
        self.player0ScoreSurf = self.textFont.render(str(self.piecesNum0), True, self.player0ScoreColor)
        self.player1ScoreSurf = self.textFont.render(str(self.piecesNum1), True, self.player1ScoreColor)
        self.player0ScoreBarRect.w = int((self.piecesNum0*2+1)/((self.piecesNum0+self.piecesNum1)*2+2)*self.playersScoreBarRTWH[2])
        self.player1ScoreBarRect.x = self.player0ScoreBarRect.x+self.player0ScoreBarRect.w
        self.player1ScoreBarRect.w = self.playersScoreBarRTWH[2]-self.player0ScoreBarRect.w
        if self.piecesNum0+self.piecesNum1 > 2 and (not self.piecesNum0 or not self.piecesNum1):
            self.winner = self.nowPlayer
            self.winnerSurf = self.textFont.render('胜利', True, self.player1ScoreColor if self.winner.id else self.player0ScoreColor)
            return self.winner

        return not diffusing_list

    def draw(self, surf):
        surf.blit(self.backgroundImg, (0,0))
        for cel in self.board.values():
            cel.draw(surf)
        if self.nowPlayer is self.players[0]:
            pygame.draw.rect(surf, self.player0ScoreColor, self.player0ScoreRect, 2)
        else:
            pygame.draw.rect(surf, self.player1ScoreColor, self.player1ScoreRect, 2)
        surf.blit(self.player0ScoreSurf, (self.player0ScoreRect.x+5, self.player0ScoreRect.y+5))
        surf.blit(self.player1ScoreSurf, (self.player1ScoreRect.x+self.player1ScoreRect.w-self.player1ScoreSurf.get_width()-5, self.player1ScoreRect.y+5))
        pygame.draw.rect(surf, self.player0ScoreColor, self.player0ScoreBarRect)
        pygame.draw.rect(surf, self.player1ScoreColor, self.player1ScoreBarRect)
        pygame.draw.rect(surf, self.exitButtonColors[self.exitButtonState], self.exitButtonRect, 2)
        surf.blit(self.exitButtonText, (self.exitButtonRect.x+(self.exitButtonRect.w-self.exitButtonText.get_width())//2,self.exitButtonRect.y+5))
        if self.winner:
            if self.winner.id == 0:
                surf.blit(self.winnerSurf, (self.player0ScoreBarRect.x+5,self.player0ScoreBarRect.y+10))
            else:
                surf.blit(self.winnerSurf, (self.player1ScoreBarRect.x+self.player1ScoreBarRect.w-self.winnerSurf.get_width()-5,self.player1ScoreBarRect.y+10))


class SwirlStage_Menu(SwirlStage):
    logoRect = pygame.Rect(400,100,200,60)
    item1Text = '人机对弈'
    item1Rect = pygame.Rect(480,360,200,50)
    item1BorderRect = pygame.Rect(300,350,480,60)
    item2Text = '双人互啄'
    item2Rect = pygame.Rect(480,460,200,50)
    item2BorderRect = pygame.Rect(300,450,480,60)
    item3Text = '退出'
    item3Rect = pygame.Rect(480,560,200,50)
    item3BorderRect = pygame.Rect(300,550,480,60)
    itemsBorderColors = (
        pygame.Color(200,200,200),
        pygame.Color(200,150,200),
        pygame.Color(100,200,200)
    )

    def __init__(self):
        itemsTextFont = pygame.font.Font('font/FZYTK.ttf', 30)
        self.backgroundImg = pygame.transform.scale(pygame.image.load('image/bg.png'),screenSize)
        self.logoImg = pygame.image.load('image/logo.png')
        self.logoRect.left = (screenSize[0]-self.logoImg.get_width())//2

        self.item1State = 0
        self.item2State = 0
        self.item3State = 0
        # 0 - Nothing
        # 1 - Hovered
        # 2 - Clicked
        self.item1TextSurf = (  itemsTextFont.render(self.item1Text, True, self.itemsBorderColors[0]),
                                itemsTextFont.render(self.item1Text, True, self.itemsBorderColors[1]),
                                itemsTextFont.render(self.item1Text, True, self.itemsBorderColors[2]))
        self.item2TextSurf = (  itemsTextFont.render(self.item2Text, True, self.itemsBorderColors[0]),
                                itemsTextFont.render(self.item2Text, True, self.itemsBorderColors[1]),
                                itemsTextFont.render(self.item2Text, True, self.itemsBorderColors[2]))
        self.item3TextSurf = (  itemsTextFont.render(self.item3Text, True, self.itemsBorderColors[0]),
                                itemsTextFont.render(self.item3Text, True, self.itemsBorderColors[1]),
                                itemsTextFont.render(self.item3Text, True, self.itemsBorderColors[2]))
        self.item1Rect.left = (screenSize[0]-self.item1TextSurf[0].get_width())//2
        self.item2Rect.left = (screenSize[0]-self.item2TextSurf[0].get_width())//2
        self.item3Rect.left = (screenSize[0]-self.item3TextSurf[0].get_width())//2
        self.itemBackgrounds = (pygame.Surface((self.item1BorderRect.w, self.item1BorderRect.h)),
                                pygame.Surface((self.item2BorderRect.w, self.item2BorderRect.h)),
                                pygame.Surface((self.item3BorderRect.w, self.item3BorderRect.h)))
        self.itemBackgrounds[0].fill(self.itemsBorderColors[0])
        self.itemBackgrounds[1].fill(self.itemsBorderColors[1])
        self.itemBackgrounds[2].fill(self.itemsBorderColors[2])
        self.itemBackgrounds[0].set_alpha(50)
        self.itemBackgrounds[1].set_alpha(50)
        self.itemBackgrounds[2].set_alpha(50)

    def handle(self):
        while True:
            clock.tick(tickFPS)
            for e in pygame.event.get():
                if e.type == pygame.MOUSEMOTION:
                    if self.item1BorderRect.collidepoint(e.pos):
                        if self.item1State == 0:
                            self.item1State = 1
                        continue
                    else:
                        self.item1State = 0
                    if self.item2BorderRect.collidepoint(e.pos):
                        if self.item2State == 0:
                            self.item2State = 1
                        continue
                    else:
                        self.item2State = 0
                    if self.item3BorderRect.collidepoint(e.pos):
                        if self.item3State == 0:
                            self.item3State = 1
                        continue
                    else:
                        self.item3State = 0
                elif e.type == pygame.MOUSEBUTTONDOWN:
                    if self.item1BorderRect.collidepoint(e.pos):
                        self.item1State = 2
                    elif self.item2BorderRect.collidepoint(e.pos):
                        self.item2State = 2
                    elif self.item3BorderRect.collidepoint(e.pos):
                        self.item3State = 2
                elif e.type == pygame.MOUSEBUTTONUP:
                    if self.item1BorderRect.collidepoint(e.pos):
                        if self.item1State == 2:
                            return SwirlStage_Play1()
                    elif self.item2BorderRect.collidepoint(e.pos):
                        if self.item2State == 2:
                            return SwirlStage_Play2()
                    elif self.item3BorderRect.collidepoint(e.pos):
                        if self.item3State == 2:
                            return None
                    else:
                        self.item1State = self.item2State = self.item3State = 0
                elif e.type == pygame.QUIT:
                    return None

            self.draw(screen)
            pygame.display.update()

    def draw(self, surf):
        surf.blit(self.backgroundImg, (0,0))
        surf.blit(self.logoImg, self.logoRect)
        surf.blit(self.itemBackgrounds[self.item1State], self.item1BorderRect)
        surf.blit(self.itemBackgrounds[self.item2State], self.item2BorderRect)
        surf.blit(self.itemBackgrounds[self.item3State], self.item3BorderRect)
        pygame.draw.rect(   surf,
                            self.itemsBorderColors[self.item1State],
                            self.item1BorderRect,
                            2)
        pygame.draw.rect(   surf,
                            self.itemsBorderColors[self.item2State],
                            self.item2BorderRect,
                            2)
        pygame.draw.rect(   surf,
                            self.itemsBorderColors[self.item3State],
                            self.item3BorderRect,
                            2)
        surf.blit(self.item1TextSurf[self.item1State], self.item1Rect)
        surf.blit(self.item2TextSurf[self.item2State], self.item2Rect)
        surf.blit(self.item3TextSurf[self.item3State], self.item3Rect)


class SwirlStage_Play1(SwirlStage, SwirlGame):
    class Evaluator:
        ev_chain = 5   # 每拥有一条链子，便拥有的分
        ev_chknot = 1  # 链子节点得分
        ev_boom = 1    # 作为炸弹格子而附加的评估分
        ev_cell = 2    # 占领某格子所拥有的基础分
        ev_wave = 1    # 扩散范围分

        class EvalChain:
            def __init__(self,player=0,score=0,chainlist=[]):
                self.score = score
                self.chainlist = chainlist
                self.player = player

            def __repr__(self):
                return '\n{"player": %d, "score": %d, "list": '%(self.player, self.score) + str([list(bp) for bp in self.chainlist]) + '}\n'

            def __str__(self):
                return '\n{"player": %d, "score": %d, "list": '%(self.player, self.score) + str([list(bp) for bp in self.chainlist]) + '}\n'

        class Piece(object):
            def __init__(self, player):
                self.player = player

            def conquered(self, player):
                self.player = player

        class Cell(object):
            def __init__(self, pos):
                self.pos = pos
                self.pieces = []
                self.player = 0
                self.neighbors = []

            def play(self, player):
                if player != self.player and bool(self.player) :
                    return False
                self.player = player
                self.pieces.append(SwirlStage_Play1.Evaluator.Piece(player))
                return True

            def diffuse(self):
                for cn in self.neighbors:
                    cn.diffused(self.pieces.pop())
                self.player = 0

            def diffused(self, piece):
                if len(self.pieces) >= len(self.neighbors):
                    return
                if self.player == 0 :
                    self.player = piece.player
                elif self.player != piece.player :
                    self.player = piece.player
                    for pie in self.pieces :
                        pie.conquered(piece.player)

                self.pieces.append(piece)

            def diffusable(self):
                return len(self.pieces)>=len(self.neighbors)


        def initiate(self, line, row):
            cells = {}

            for i in range(line):
                for j in range(row):
                    cells[(j,i)] = self.Cell((j, i))

            for i in range(line):
                for j in range(row):
                    cn = cells.get((j-1, i))
                    if cn:
                        cells[(j,i)].neighbors.append(cn)
                    cn = cells.get((j+1, i))
                    if cn:
                        cells[(j,i)].neighbors.append(cn)
                    cn = cells.get((j, i-1))
                    if cn:
                        cells[(j,i)].neighbors.append(cn)
                    cn = cells.get((j, i+1))
                    if cn:
                        cells[(j,i)].neighbors.append(cn)

            return cells

        def judge(self, cells):
            piece1 = 0
            piece2 = 0
            boom = []

            for cell in list(cells.values()) :
                if cell.player == 0 :
                    continue
                elif cell.player == 1 :
                    piece1 += len(cell.pieces)
                else :
                    piece2 += len(cell.pieces)

                if len(cell.pieces) >= len(cell.neighbors) :
                    boom.append(cell)

            if ( piece1 == 0 or piece2 == 0 ) and piece1 + piece2 >1 :
                return 1 if piece1 > 0 else 2

            if len(boom) == 0 :
                return 0

            for cell in boom :
                cell.diffuse(cells = cells)

            return -1

        def __init__(self, board=None):
            self.board = {}
            if board:
                self.board = board

        def parse(self, celist):
            board = self.initiate(6,6)
            for i in range(6):
                for j in range(6):
                    if celist[i][j] > 0:
                        for _ in range(celist[i][j]):
                            board[(j, i)].pieces.append(self.Piece(1))
                        board[(j, i)].player = 1
                    elif celist[i][j] < 0:
                        for _ in range(-celist[i][j]):
                            board[(j, i)].pieces.append(self.Piece(2))
                        board[(j, i)].player = 2
            return board

        def deduce(self, board):
            diffusing_list = [1]
            count = 36
            while diffusing_list:
                diffusing_list = []
                for ce in board.values():
                    if ce.diffusable():
                        diffusing_list.append(ce)
                for ce in diffusing_list:
                    ce.diffuse()
                if count<=0:
                    break
                count -= 1

        def evaluate(self, cells):
            booms = []  # 炸弹
            chains = []  # 炸弹链子

            cellnum = [0,0,0]

            # 先揪出炸弹
            for cl in cells.values():
                cellnum[cl.player] += 1
                if len(cl.pieces) == len(cl.neighbors)-1:
                    booms.append(cl)

            # 对于已分出胜负的情况，直接给出评估结果
            if cellnum[1]+cellnum[2] >= 2:
                if not cellnum[1]:
                    return [self.EvalChain(player=2,score=29999)]
                elif not cellnum[2]:
                    return [self.EvalChain(player=1,score=29999)]

            # 初步组链
            boom_copy = booms.copy()
            for bo in booms:
                if bo not in boom_copy:
                    # 如果炸弹已经被组链了，就跳过
                    continue
                boom_copy.remove(bo)
                chain = [bo]
                for ck in chain:
                    for cn in ck.neighbors:
                        if cn in chain:
                            continue
                        if cn in booms:
                            chain.append(cn)
                            if cn in boom_copy:
                                boom_copy.remove(cn)
                chains.append(chain)

            # 分玩家讨论各自链情况
            # 比如下面这种情况，对于不同方，链是不一样的
            # +---+---+---+
            # |+3 |+3 |   |
            # +---+---+---+
            # |+3 |+2 |-3 |
            # +---+---+---+
            chains1 = []
            chains2 = []

            for ch in chains:
                if [1 for b in ch if b.player==1]:
                    chains1.append(ch.copy())
                if [2 for b in ch if b.player==2]:
                    chains2.append(ch.copy())

            for ch in chains1.copy():
                # 这里使用浅复制，以避免影响遍历
                if ch not in chains1:
                    # 如果属于已经被剔除或合并的链，则跳过
                    continue
                for bo in ch:
                    for bn in bo.neighbors:
                        if bn in ch:
                            # 如果已经在链内，跳过
                            continue
                        if len([1 for bnn in bn.neighbors if bnn in ch])+len(bn.pieces) >= len(bn.neighbors):
                            # 如果属于假炸弹，也排进链内
                            ch.append(bn)
                            # 如果周围有其他真炸弹且属于其他链
                            for bnn in bn.neighbors:
                                if bnn in booms:
                                    if bnn in ch:
                                        continue
                                    for chai in chains:
                                        if chai is ch:
                                            continue
                                        if bnn in chai:
                                            for boo in chai:
                                                if boo not in ch:
                                                    ch.append(boo)
            for ch in chains2.copy():
                # 这里使用浅复制，以避免影响遍历
                if ch not in chains2:
                    # 如果属于已经被剔除或合并的链，则跳过
                    continue
                for bo in ch:
                    for bn in bo.neighbors:
                        if bn in ch:
                            # 如果已经在链内，跳过
                            continue
                        if len([1 for bnn in bn.neighbors if bnn in ch])+len(bn.pieces) >= len(bn.neighbors):
                            # 如果属于假炸弹，也排进链内
                            ch.append(bn)
                            # 如果周围有其他真炸弹且属于其他链
                            for bnn in bn.neighbors:
                                if bnn in booms:
                                    if bnn in ch:
                                        continue
                                    for chai in chains:
                                        if chai is ch:
                                            continue
                                        if bnn in chai:
                                            for boo in chai:
                                                if boo not in ch:
                                                    ch.append(boo)

            # 针对链们评分
            point1 = sum([self.ev_cell for c in cells.values() if c.player==1])
            point2 = sum([self.ev_cell for c in cells.values() if c.player==2])

            chainpoints1 = []
            chainpoints2 = []

            for ch in chains1:
                chainpoint = self.ev_chain + self.ev_chknot*len(ch)
                wavecell = []
                for i in range(6):
                    for j in range(6):
                        if cells[(j, i)] in ch:
                            wavecell.append(cells[(j, i)])
                            continue
                        for cn in cells[(j, i)].neighbors:
                            if cn in ch:
                                wavecell.append(cells[(j, i)])
                                break
                othercell = [c for c in cells.values() if c not in wavecell]
                fl = 1
                for c in othercell:
                    if c.player == 2:
                        fl = 0
                        break
                if cellnum[1] + cellnum[2] >= 2 and fl:
                    chainpoint =29999
                    chainpoints1.append(chainpoint)
                    break
                chainpoint += len(wavecell) * self.ev_wave
                chainpoints1.append(chainpoint)

            for ch in chains2:
                chainpoint = self.ev_chain +self.ev_chknot*len(ch)
                wavecell = []
                for i in range(6):
                    for j in range(6):
                        if cells[(j, i)] in ch:
                            wavecell.append(cells[(j, i)])
                            continue
                        for cn in cells[(j, i)].neighbors:
                            if cn in ch:
                                wavecell.append(cells[(j, i)])
                                break
                othercell = [c for c in cells.values() if c not in wavecell]
                fl = 1
                for c in othercell:
                    if c.player == 1:
                        fl = 0
                        break
                if cellnum[1] + cellnum[2] >= 2 and fl:
                    chainpoint =29999
                    chainpoints2.append(chainpoint)
                    break
                chainpoint += len(wavecell) * self.ev_wave
                chainpoints2.append(chainpoint)

            result = []
            for ch, poi in zip(chains1, chainpoints1):
                cho = self.EvalChain()
                cho.chainlist = [ck.pos for ck in ch]
                cho.player = 1
                cho.score = poi
                result.append(cho)
            for ch, poi in zip(chains2, chainpoints2):
                cho = self.EvalChain()
                cho.chainlist = [ck.pos for ck in ch]
                cho.player = 2
                cho.score = poi
                result.append(cho)
            return result

        def decide(self, board):
            celist = [[len(board[(j,i)].pieces)*((1 if board[(j,i)].getPlayer().id==1 else -1) if board[(j,i)].getPlayer() else 0) for j in range(6)] for i in range(6)]
            choices = {}
            for i in range(6):
                for j in range(6):
                    if board[(i,j)].getPlayer() and board[(i,j)].getPlayer().id!=1:
                        continue
                    boardInBrain = self.parse(celist)
                    boardInBrain[(i,j)].play(1)
                    self.deduce(boardInBrain)
                    result = self.evaluate(boardInBrain)
                    mychains, enemychains = [chm for chm in result if chm.player==1], [che for che in result if che.player==2]
                    mychains.sort(key=lambda a:a.score,reverse=True)
                    enemychains.sort(key=lambda a:a.score,reverse=True)
                    if enemychains and enemychains[0].score==29999:
                        choices[(i,j)] = -29999
                        continue
                    myh, enh = 0, 0
                    if mychains:
                        myh = mychains[0].score
                    if enemychains:
                        enh = enemychains[0].score
                    choices[(i,j)] = myh-5*enh

            choi = [(chk, choices[chk]) for chk in choices]
            choi.sort(key=lambda a:a[1], reverse=True)
            #return random.choice([c for c in choi if c[1]==choi[0][1]])[0]
            return choi[0][0]



    def __init__(self):
        super(SwirlStage_Play1, self).__init__()

    def handle(self):
        while True:
            clock.tick(tickFPS)
            if self.waitingAction>0:
                self.waitingAction -= 1
                if self.waitingAction <=0:
                    result = self.trigger()
                    if not result:
                        self.waitingAction = self.waitingActionFlame
                    elif type(result) == self.Player:
                        pass
                    else:
                        self.nowPlayer = self.players[0] if self.nowPlayer==self.players[1] else self.players[1]
                        if self.nowPlayer.id == 1:
                            result = self.board[self.Evaluator().decide(self.board)]
                            result.addPiece(self.Piece((960,80), result, self.nowPlayer, self))
                            self.waitingAction = self.waitingActionFlame
            for e in pygame.event.get():
                if e.type == pygame.MOUSEMOTION:
                    if self.exitButtonRect.collidepoint(e.pos):
                        if self.exitButtonState == 0:
                            self.exitButtonState = 1
                    else:
                        self.exitButtonState = 0
                    for ce in self.board.values():
                        if ce.rect.collidepoint(e.pos):
                            ce.hovered = 1
                        else:
                            ce.hovered = 0
                elif e.type == pygame.MOUSEBUTTONDOWN:
                    if self.exitButtonRect.collidepoint(e.pos):
                        self.exitButtonState = 2
                    if self.waitingAction <=0 and not self.winner and self.nowPlayer is not self.players[1]:
                        for ce in self.board.values():
                            if ce.rect.collidepoint(e.pos):
                                targetPlayer = ce.getPlayer()
                                if targetPlayer == self.nowPlayer or not targetPlayer:
                                    ce.addPiece(self.Piece(e.pos, ce, self.nowPlayer, self))
                                    self.waitingAction = self.waitingActionFlame
                                break
                elif e.type == pygame.MOUSEBUTTONUP:
                    if self.exitButtonRect.collidepoint(e.pos):
                        return SwirlStage_Menu()
                elif e.type == pygame.QUIT:
                    return None

            self.draw(screen)
            pygame.display.update()

    def draw(self, surf):
        SwirlGame.draw(self, surf)


class SwirlStage_Play2(SwirlStage, SwirlGame):
    def __init__(self):
        super(SwirlStage_Play2, self).__init__()

    def handle(self):
        while True:
            clock.tick(tickFPS)
            if self.waitingAction>0:
                self.waitingAction -= 1
                if self.waitingAction <=0:
                    result = self.trigger()
                    if not result:
                        self.waitingAction = self.waitingActionFlame
                    elif type(result) == self.Player:
                        pass
                    else:
                        self.nowPlayer = self.players[0] if self.nowPlayer==self.players[1] else self.players[1]
            for e in pygame.event.get():
                if e.type == pygame.MOUSEMOTION:
                    if self.exitButtonRect.collidepoint(e.pos):
                        if self.exitButtonState == 0:
                            self.exitButtonState = 1
                    else:
                        self.exitButtonState = 0
                    for ce in self.board.values():
                        if ce.rect.collidepoint(e.pos):
                            ce.hovered = 1
                        else:
                            ce.hovered = 0
                elif e.type == pygame.MOUSEBUTTONDOWN:
                    if self.exitButtonRect.collidepoint(e.pos):
                        self.exitButtonState = 2
                    if self.waitingAction <=0 and not self.winner:
                        for ce in self.board.values():
                            if ce.rect.collidepoint(e.pos):
                                targetPlayer = ce.getPlayer()
                                if targetPlayer == self.nowPlayer or not targetPlayer:
                                    ce.addPiece(self.Piece(e.pos, ce, self.nowPlayer, self))
                                    self.waitingAction = self.waitingActionFlame
                                break
                elif e.type == pygame.MOUSEBUTTONUP:
                    if self.exitButtonRect.collidepoint(e.pos):
                        return SwirlStage_Menu()
                elif e.type == pygame.QUIT:
                    return None

            self.draw(screen)
            pygame.display.update()

    def draw(self, surf):
        SwirlGame.draw(self, surf)


if __name__ == '__main__':
    nextStage = SwirlStage_Menu()

    while nextStage:
        nowStage = nextStage
        nextStage = nowStage.handle()
