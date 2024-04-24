import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QSize
import random
import math

class MCTSNode:
    def __init__(self, board, parent=None):
        self.board = board
        self.parent = parent
        self.children = []
        self.visits = 0
        self.wins = 0

    def select_child(self):
        if self.visits == 0:
            # Si le nœud n'a pas encore été visité, sélectionnez un enfant aléatoire
            return random.choice(self.children)
        else:
            # Sélectionne l'enfant avec le meilleur score UCB1
            return max(self.children, key=lambda node: node.wins / (node.visits + 1) + math.sqrt(2 * math.log(self.visits) / (node.visits + 1) if node.visits > 0 else 1))

    def expand(self):
        # Étend les enfants en ajoutant tous les coups possibles
        empty_positions = self.board.get_empty_positions()
        for x, y in empty_positions:
            child_board = self.board.copy()  # Créer une copie du plateau pour chaque enfant
            child_board.place_stone(x, y)
            self.children.append(MCTSNode(child_board, parent=self))

    def backpropagate(self, result):
        # Met à jour les statistiques des nœuds visités pendant la simulation
        self.visits += 1
        self.wins += result
        if self.parent:
            self.parent.backpropagate(result)

class MonteCarloTreeSearch:
    def __init__(self, board):
        self.root = MCTSNode(board)

    def search(self, num_simulations):
        for _ in range(num_simulations):
            node = self.select_node()
            result = self.simulate(node)
            node.backpropagate(result)
        if self.root.children:
            best_move = self.select_best_move()
            return best_move
        else:
            return None


    def select_node(self):
        # Sélectionne le nœud à explorer en fonction de l'algorithme UCT (Upper Confidence Bound Applied to Trees)
        node = self.root
        while node.children:
            if random.random() < 0.1:  # Ajouter de l'exploration stochastique
                return node
            node = node.select_child()
        if not node.children:
            node.expand()  # Étendre les enfants si le nœud n'en a pas
            return node.select_child()

    def simulate(self, node):
        # Effectue une simulation à partir du nœud donné
        current_board = node.board.copy()
        while not current_board.is_game_over():
            empty_positions = current_board.get_empty_positions()
            if empty_positions:
                x, y = random.choice(empty_positions)
                current_board.place_stone(x, y)
            else:
                break
        result = current_board.calculate_winner()
        return result

    def select_best_move(self):
        # Sélectionne le meilleur coup en fonction des statistiques accumulées
        valid_moves = [(node.board.get_last_move(), node.visits) for node in self.root.children if node.visits > 0]
        if not valid_moves:
            return None
        return max(valid_moves, key=lambda move: move[1])[0]

class GameBoard(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.current_player = 1  # Initialise le joueur actuel (1 pour les pierres noires, -1 pour les pierres blanches)
        self.occupied = [[0 for _ in range(9)] for _ in range(9)]  # Initialisation du plateau
        self.ko = None  # Attribut pour suivre la situation de ko
        self.ko_position = None  # Position du ko
        self.mcts = MonteCarloTreeSearch(self)
        self.last_move = (0, 0)

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

    def get_last_move(self):
        # Retourne les coordonnées du dernier coup joué
        return self.last_move

    def copy(self):
        # Créer une copie de l'objet GameBoard
        new_board = GameBoard()
        # Copier les attributs du plateau de jeu
        new_board.occupied = [row[:] for row in self.occupied]
        new_board.current_player = self.current_player
        # Copier d'autres attributs si nécessaire
        return new_board

    def get_empty_positions(self):
        # Renvoie une liste de tuples représentant les positions vides sur le plateau
        empty_positions = []
        for i in range(9):
            for j in range(9):
                if self.occupied[i][j] == 0:
                    empty_positions.append((i, j))
        return empty_positions

    def calculate_winner(self):
        black_score = 0
        white_score = 0
        for i in range(9):
            for j in range(9):
                if self.occupied[i][j] == 1:
                    black_score += 1
                elif self.occupied[i][j] == -1:
                    white_score += 1
        if black_score > white_score:
            return 1  # Le joueur noir gagne
        elif white_score > black_score:
            return -1  # Le joueur blanc gagne
        else:
            return 0  # Match nul

    def buttonClicked(self, x, y):
        if not self.occupied[x][y] and self.current_player == 1:
            self.place_stone(x, y)
            self.current_player *= -1  # Assurez-vous que le joueur actuel est correctement mis à jour
            self.place_white_stone()  # Appel à place_white_stone() pour que l'IA joue

    def place_white_stone(self):
        # Place une pierre blanche si c'est le tour de l'IA
        if self.current_player == -1:
            self.make_ai_move()
            self.current_player *= -1

    def place_stone(self, x, y):
        # Place une pierre sur le pldef select_node(self):
        self.occupied[x][y] = self.current_player
        self.last_move = (x, y)
        if self.current_player == 1:
            self.buttons[x][y].setIcon(QIcon("black_stone.png"))
        else:
            self.buttons[x][y].setIcon(QIcon("white_stone.png"))  # Mettre l'icône de la pierre blanche si c'est le tour de l'IA
        self.buttons[x][y].setIconSize(QSize(80, 80))
        # Vérifie et gère la capture des pierres
        captured_stones = self.check_capture(x, y)
        if captured_stones:
            self.remove_captured_stones(captured_stones)
        # Vérifie la règle du ko
        if self.check_ko():
            self.ko_position = (x, y)
        else:
            self.ko_position = None

    def is_game_over(self):
        # Vérifie si la partie est terminée
        # Ici, nous considérons la partie terminée si le plateau est entièrement rempli
        for row in self.occupied:
            for cell in row:
                if cell == 0:
                    return False  # S'il reste une case vide, la partie n'est pas terminée
        return True  # Si le plateau est entièrement rempli, la partie est terminée

    def check_capture(self, x, y):
        # Vérifie si des pierres sont capturées par le coup à la position (x, y)
        captured_stones = []
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 9 and 0 <= ny < 9 and self.occupied[nx][ny] == -self.current_player:
                group, liberties = self.find_group_and_liberties(nx, ny)
                if liberties == 0:
                    captured_stones.extend(group)
        return captured_stones

    def check_ko(self):
        # Vérifiez si une situation de ko est présente sur le plateau de jeu
        if self.ko is not None:
            x, y = self.ko
            if self.occupied[x][y] == 0:
                self.ko = None  # Réinitialiser la situation de ko si la pierre n'est plus là
            else:
                return True  # La situation de ko persiste
        return False

    def find_group_and_liberties(self, x, y):
        # Trouve le groupe de pierres à la position (x, y) et le nombre de libertés du groupe
        visited = set()
        group = []
        liberties = 0
        self.dfs(x, y, visited, group)
        for x, y in group:
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < 9 and 0 <= ny < 9 and self.occupied[nx][ny] == 0:
                    liberties += 1
        return group, liberties

    def dfs(self, x, y, visited, group):
        # Parcours en profondeur pour trouver le groupe de pierres
        if (x, y) in visited or self.occupied[x][y] != -self.current_player:
            return
        visited.add((x, y))
        group.append((x, y))
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 9 and 0 <= ny < 9:
                self.dfs(nx, ny, visited, group)

    def remove_captured_stones(self, captured_stones):
        # Retire les pierres capturées du plateau
        for x, y in captured_stones:
            self.occupied[x][y] = 0
            self.buttons[x][y].setIcon(QIcon(""))

    def make_ai_move(self):
        # Faire jouer l'IA en utilisant la recherche MCTS
        best_move = self.mcts.search(num_simulations=5)  # Augmentez le nombre de simulations pour une meilleure performance
        print("Best move:", best_move)
        if best_move is not None:
            x, y = best_move
            # Effectuer le coup retourné par MCTS
            if self.occupied[x][y] == 0:
                print("Moving to:", x, y)
                self.place_stone(x, y)
                self.occupied[x][y] = self.current_player
            else:
                print("Already occupied:", x, y)
                # self.make_ai_move()
        else:
            print("L'IA n'a pas trouvé de meilleur coup. La partie est terminée.")

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