import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
import random

class GameBoard(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.current_player = 1  # Initialise le joueur actuel (1 pour les pierres noires, -1 pour les pierres blanches)
        self.occupied = [[False for _ in range(9)] for _ in range(9)]  # Initialisation de la liste des cases occupées
    
    def initUI(self):
        layout = QGridLayout()  # Utilisation de QGridLayout pour une disposition en grille
        self.setLayout(layout)
        
        # Création de boutons pour représenter les intersections du plateau
        self.buttons = []
        for i in range(9):
            row = []
            for j in range(9):
                button = QPushButton("", self)
                button.setFixedSize(80, 80)
                button.clicked.connect(lambda state, x=i, y=j: self.buttonClicked(x, y))
                row.append(button)
                layout.addWidget(button, i, j)  # Ajout du bouton à la grille
            self.buttons.append(row)
    
    def buttonClicked(self, x, y):
        if not self.occupied[x][y] and self.current_player == 1:
            self.buttons[x][y].setIcon(QIcon("black_stone.png"))  # Affiche une pierre noire
            self.buttons[x][y].setIconSize(QSize(80, 80))  # Taille de l'icône pour correspondre à la taille du bouton
            self.occupied[x][y] = True  # Marque la case comme occupée
            self.current_player *= -1  # Passe au tour du joueur suivant
            self.place_white_stone()  # Place une pierre blanche si c'est le tour de l'IA
    
    def place_white_stone(self):
        # Place une pierre blanche si c'est le tour de l'IA
        if self.current_player == -1:
            x, y = self.choose_move()
            self.buttons[x][y].setIcon(QIcon("white_stone.png"))  # Affiche une pierre blanche
            self.buttons[x][y].setIconSize(QSize(80, 80))  # Taille de l'icône pour correspondre à la taille du bouton
            self.occupied[x][y] = True  # Marque la case comme occupée
            self.current_player *= -1  # Passe au tour du joueur suivant
    
    def choose_move(self):
        # Choix du meilleur coup en fonction de l'évaluation de la position des pierres
        empty_positions = [(i, j) for i in range(9) for j in range(9) if not self.occupied[i][j]]
        best_score = float('-inf')
        best_move = None
        for x, y in empty_positions:
            score = self.evaluate_move(x, y)
            if score > best_score:
                best_score = score
                best_move = (x, y)
        return best_move
    
    def evaluate_move(self, x, y):
        # Evaluation de la qualité d'un coup en fonction de la position sur le plateau
        # Pour simplifier, nous attribuons une valeur plus élevée aux coups près du centre du plateau
        distance_from_center = abs(4 - x) + abs(4 - y)
        return -distance_from_center  # Plus la distance est faible, meilleure est l'évaluation

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Jeu de Go")
        self.setGeometry(100, 100, 800, 600) # Taille de la fenêtre
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        
        self.gameBoard = GameBoard()
        
        layout = QVBoxLayout(self.centralWidget)
        layout.addWidget(self.gameBoard)

if __name__ == "__main__":
    app = QApplication([])
    mainWindow = MainWindow()
    mainWindow.show()
    app.exec_()