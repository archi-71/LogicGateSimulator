import pygame, sys, os
from pygame.locals import *

if sys.platform == "win32":
    import ctypes
    cytypes.windll.user32.SetProcessDPIAware()

pygame.init()

PATH_SEP = os.path.sep
WINDOW_WIDTH = 1510
WINDOW_HEIGHT = 830
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1010
PANEL_WIDTH = SCREEN_WIDTH / 5
MIN_INPUTS = 1
MAX_INPUTS = 8

BLACK = (0,0,0)
DARKGREY = (50,50,50)
GREY = (150,150,150)
MIDLIGHTGREY = (180, 180, 180)
LIGHTGREY = (200,200,200)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 128)
DARKYELLOW = (205, 205, 78)

clock = pygame.time.Clock()
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), DOUBLEBUF)
screen = pygame.surface.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Logic Gates")

gateImages = {"NOT": pygame.image.load(f"resources{PATH_SEP}NOTGate.png").convert_alpha(),
              "AND": pygame.image.load(f"resources{PATH_SEP}ANDGate.png").convert_alpha(),
              "OR": pygame.image.load(f"resources{PATH_SEP}ORGate.png").convert_alpha(),
              "XOR": pygame.image.load(f"resources{PATH_SEP}XORGate.png").convert_alpha(),
              "NAND": pygame.image.load(f"resources{PATH_SEP}NANDGate.png").convert_alpha(),
              "NOR": pygame.image.load(f"resources{PATH_SEP}NORGate.png").convert_alpha(),
              "XNOR": pygame.image.load(f"resources{PATH_SEP}XNORGate.png").convert_alpha()}


class Circuit():
    def __init__(self):
        self.gates = []
        self.inputNum = 3
        self.inputs = [IODisplay(pygame.Vector2(PANEL_WIDTH+11, i * SCREEN_HEIGHT/(self.inputNum+1)), True) for i in range(1, self.inputNum+1)]
        self.output = IODisplay(pygame.Vector2(SCREEN_WIDTH - 60, SCREEN_HEIGHT/2), False)
        self.expression = None
        
    def updateInputNumber(self, inputNum):
        if MIN_INPUTS <= inputNum <= MAX_INPUTS:
            self.inputNum = inputNum
            for connector in connectors:
                for i in self.inputs:
                    if i.connector == connector.connection:
                        connector.connection = None
            self.inputs = [IODisplay(pygame.Vector2(PANEL_WIDTH+11, i * SCREEN_HEIGHT/(self.inputNum+1)), True) for i in range(1, self.inputNum+1)]
    
    def evaluate(self):
        for connector in connectors:
            if connector not in [i.connector for i in self.inputs]:
                connector.value = None
        for connector in connectors:
            if connector.value == None:
                connector.evaluate()
        if self.output.value != None:
            self.expression = "X = " + self.output.connector.calculateBooleanExpression()
        else:
            self.expression = None
    
    def draw(self, mousePos):
            
        for gate in self.gates:
            gate.checkConnectors(mousePos)
            gate.draw()
        
        for IO in self.inputs + [self.output]:
            IO.draw(mousePos, self.inputs)

class IODisplay():
    def __init__(self, pos, togglable):
        self.rect = pygame.Rect((pos.x, pos.y-30), (60, 60))
        self.clickRect = pygame.Rect(self.rect.x+5, self.rect.y+5, self.rect.width-10, self.rect.height-10)
        self.togglable = togglable
        if self.togglable:
            self.value = 0
        else:
            self.value = None
        if togglable:
            self.connector = Connector(pygame.Vector2(pos.x + 80, pos.y), "output")
        else:
            self.connector = Connector(pygame.Vector2(pos.x - 20, pos.y), "input")
        self.connector.value = self.value
        self.selected = False
    
    def toggle(self):
        if self.value == 0:
            self.value = 1
        else:
            self.value = 0
        self.connector.value = self.value
    
    def draw(self, mousePos, inputs):
        self.value = self.connector.value
        pygame.draw.line(screen, MIDLIGHTGREY, (self.rect.x, self.rect.y + self.rect.height/2), self.connector.pos, 10)
        pygame.draw.rect(screen, DARKGREY, self.rect)
        if self.togglable and self.clickRect.collidepoint(mousePos):
            self.selected = True
            if self.value:
                pygame.draw.rect(screen, DARKYELLOW, self.clickRect)
            else:
                pygame.draw.rect(screen, GREY, self.clickRect)
        else:
            self.selected = False
            if self.value:
                pygame.draw.rect(screen, YELLOW, self.clickRect)
            else:
                pygame.draw.rect(screen, LIGHTGREY, self.clickRect)
        if self.value != None:
            renderText(f"{self.value}", 50, BLACK, pygame.Rect(self.clickRect.x, self.clickRect.y + 2, self.clickRect.width, self.clickRect.height))
        self.connector.checkSelected(mousePos)
        self.connector.draw()
        if self.togglable:
            pass
            renderText(f"{chr(inputs.index(self)+65)}", 40, WHITE, pygame.Rect(self.clickRect.x, self.clickRect.y - self.clickRect.height + 5, self.clickRect.width, self.clickRect.height))
        else:
            renderText("X", 40, WHITE, pygame.Rect(self.clickRect.x, self.clickRect.y - self.clickRect.height + 5, self.clickRect.width, self.clickRect.height))
        

class LogicGate():
    def __init__(self, pos, gateType):
        self.rect = pygame.Rect(pos, (80, 80))
        self.type = gateType
        if self.type == "NOT":
            self.inputs = [Connector(pos + pygame.Vector2(-16, 40), "input")]
        else:
            self.inputs = [Connector(pos + pygame.Vector2(-16, 20), "input"), Connector(pos + pygame.Vector2(-16, 60), "input")]
        self.output = Connector(pos + pygame.Vector2(96, 40), "output")
        self.output.connection = self
     
    def evaluate(self):
        inp1 = self.inputs[0].evaluate()
        if self.type == "NOT":
            if inp1 == None:
                return None
        else:
            inp2 = self.inputs[1].evaluate()
            if inp1 == None or inp2 == None:
                return None
            
        if self.type == "NOT":
            return self.getValue(not inp1)
        elif self.type == "AND":
            return self.getValue(inp1 and inp2)
        elif self.type == "OR":
            return self.getValue(inp1 or inp2)
        elif self.type == "XOR":
            return self.getValue(inp1 != inp2)
        elif self.type == "NAND":
            return self.getValue(not(inp1 and inp2))
        elif self.type == "NOR":
            return self.getValue(not(inp1 or inp2))
        elif self.type == "XNOR":
            return self.getValue(inp1 == inp2)
                
    def getValue(self, boolean):
        if boolean:
            return 1
        else:
            return 0
            
    def updatePosition(self, newPos):
        moveVector = newPos -  pygame.Vector2(self.rect.x, self.rect.y)
        self.rect.x, self.rect.y = newPos.x, newPos.y
        for connector in self.inputs + [self.output]:
            connector.pos += moveVector
    
    def checkConnectors(self, mousePos):
        for connector in self.inputs + [self.output]:
            connector.checkSelected(mousePos)
    
    def delete(self, circuit, connectors):
        for connector in connectors:
            for selfConnector in self.inputs + [self.output]:
                if connector.connection == selfConnector:
                    connector.connection = None
        circuit.gates.remove(self)
    
    def draw(self):
        for gate in gateImages:
           if self.type == gate:
               screen.blit(gateImages[gate], (self.rect.x - 10, self.rect.y - 10))
               break
        for connector in self.inputs + [self.output]:
            connector.draw()


class Connector():
    def __init__(self, pos, connectorType):
         self.pos = pos
         self.type = connectorType
         self.selected = False
         self.connection = None
         self.value = None
    
    def checkSelected(self, mousePos):
        if pygame.Rect(self.pos.x - 8, self.pos.y - 8, 16, 16).collidepoint(mousePos):
            self.selected = True
        else:
            self.selected = False
    
    def evaluate(self):
        if self.connection:
            self.value = self.connection.evaluate()
        return self.value
    
    def calculateBooleanExpression(self):
        if not self.connection:
            inputs = [i.connector for i in circuit.inputs]
            if self in inputs:
                return f"{chr(inputs.index(self)+65)}"
        else:
            if type(self.connection).__name__ == "Connector":
                return self.connection.calculateBooleanExpression()
            else:
                if self.connection.type == "NOT":
                    return f"(NOT {self.connection.inputs[0].calculateBooleanExpression()})"
                else:
                    return f"({self.connection.inputs[0].calculateBooleanExpression()} {self.connection.type} {self.connection.inputs[1].calculateBooleanExpression()})"
        return ""
    
    def draw(self):
        if type(self.connection).__name__ == "Connector":
            if self.value or self.connection.value:
                pygame.draw.line(screen, YELLOW, self.pos, self.connection.pos, 10)
            else:
                pygame.draw.line(screen, MIDLIGHTGREY, self.pos, self.connection.pos, 10)
        if self.selected:
            if self.value:
                pygame.draw.circle(screen, DARKYELLOW, self.pos, 8)
            else:
                pygame.draw.circle(screen, GREY, self.pos, 8)
        else:
            if self.value:
                pygame.draw.circle(screen, YELLOW, self.pos, 8)
            else:
                pygame.draw.circle(screen, MIDLIGHTGREY, self.pos, 8)


class UI():
    def __init__(self):
        self.buttons = [[list(gateImages)[i], pygame.Rect(20, 20 + 120 * i, PANEL_WIDTH-40, 100), False] for i in range(len(list(gateImages)))]
        self.buttons.append(["-", pygame.Rect(PANEL_WIDTH-160, SCREEN_HEIGHT-80, 50, 50), False])
        self.buttons.append(["+", pygame.Rect(PANEL_WIDTH-90, SCREEN_HEIGHT-80, 50, 50), False])
    
    def checkButtons(self, mousePos):
        for i in range(len(self.buttons)):
            if self.buttons[i][1].collidepoint(mousePos):
                self.buttons[i][2] = True
            else:
                self.buttons[i][2] = False
    
    def draw(self):
        pygame.draw.rect(screen, DARKGREY, pygame.Rect(0, 0, PANEL_WIDTH, SCREEN_HEIGHT))
        pygame.draw.line(screen, LIGHTGREY, (PANEL_WIDTH+5, 0), (PANEL_WIDTH+5, SCREEN_HEIGHT), 10)
        renderText("Inputs:", 50, BLACK, pygame.Rect(PANEL_WIDTH-290, SCREEN_HEIGHT-80, 50, 50))
        for i in range(len(self.buttons)):
            if self.buttons[i][2]:
                pygame.draw.rect(screen, GREY, self.buttons[i][1])
            else:
                pygame.draw.rect(screen, LIGHTGREY, self.buttons[i][1])
            if i < len(gateImages):
                renderText(list(gateImages)[i], 50, BLACK, pygame.Rect(20, 20 + 120 * i, (PANEL_WIDTH-40)/2, 100))
                screen.blit(gateImages[list(gateImages)[i]], ((PANEL_WIDTH-40)*2/3, 20 + 120 * i))
            else:
                renderText(self.buttons[i][0], 50, BLACK, self.buttons[i][1])
                
        if circuit.expression:
            renderText(circuit.expression, 40, WHITE, pygame.Rect(PANEL_WIDTH, 0, SCREEN_WIDTH-PANEL_WIDTH, 100))
            
    def drawConnectingLine(self, mousePos, drawing):
        if drawing:
            if drawing.value and drawing.type == "output":
                pygame.draw.line(screen, YELLOW, drawing.pos, mousePos, 10)
            else:
                pygame.draw.line(screen, MIDLIGHTGREY, drawing.pos, mousePos, 10)


def renderText(text, size, colour, rect):
    font = pygame.font.SysFont("Consolas", size)
    textSize = font.size(text)
    screen.blit(font.render(text, False, colour), (rect.centerx - textSize[0]/2, rect.centery - textSize[1]/2))


connectors = []
circuit = Circuit()
ui = UI()
dragging = None
drawing = None

while True:
    screen.fill(BLACK)
    pressedKeys = pygame.key.get_pressed()
    mousePos = pygame.Vector2(int(pygame.mouse.get_pos()[0] * (SCREEN_WIDTH / WINDOW_WIDTH)), int(pygame.mouse.get_pos()[1] * (SCREEN_HEIGHT / WINDOW_HEIGHT)))
    
    connectors = [circuit.output.connector] + [inputDisplay.connector for inputDisplay in circuit.inputs]
    for gate in circuit.gates:
        connectors += gate.inputs + [gate.output]
    
    for event in pygame.event.get():
        if event.type == QUIT:
            sys.exit()
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0]:
                for i in range(len(ui.buttons)):
                    if ui.buttons[i][2]:
                        if i < len(gateImages):
                                dragging = LogicGate(mousePos, ui.buttons[i][0])
                                circuit.gates.append(dragging)
                        else:
                            if ui.buttons[i][0] == "-":
                                circuit.updateInputNumber(circuit.inputNum - 1)
                            elif ui.buttons[i][0] == "+":
                                circuit.updateInputNumber(circuit.inputNum + 1)
                            
                for gate in circuit.gates:
                    if gate.rect.collidepoint(mousePos):
                        dragging = gate
                        
                for inputDisplay in circuit.inputs:
                    if inputDisplay.selected:
                        inputDisplay.toggle()
                        
                for connector in connectors:
                    if connector.selected:
                        if connector.connection and connector.type == "input":
                            connector.connection = None
                        drawing = connector
                    
            elif pygame.mouse.get_pressed()[2]:
                for gate in circuit.gates:
                    if gate.rect.collidepoint(mousePos):
                        gate.delete(circuit, connectors)
                    
        if event.type == pygame.MOUSEBUTTONUP:
            if dragging:
                if mousePos.x < PANEL_WIDTH + 60:
                    dragging.delete(circuit, connectors)
                dragging = None
            if drawing:
                for connector in connectors:
                    if connector.selected and connector.type != drawing.type:
                        if connector.type == "input":
                            connector.connection = drawing
                        else:
                            drawing.connection = connector
                drawing = None
    
    if dragging:
        dragging.updatePosition(mousePos - pygame.Vector2(40, 40))
    
    circuit.evaluate()
    
    ui.checkButtons(mousePos)
    ui.draw()
    circuit.draw(mousePos)
    ui.drawConnectingLine(mousePos, drawing)

    window.blit(pygame.transform.scale(screen, window.get_rect().size), (0,0))    
    pygame.display.update()