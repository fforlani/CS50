import random
from collections import OrderedDict


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = cells
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    # The following methods were defined in the problem but I do not find them useful

    # def known_mines(self):
    #     """
    #     Returns the set of all cells in self.cells known to be mines.
    #     """
    #     count = 0
    #     for cell, status in self.cells:
    #         count += status
    #     return count
    #
    # def known_safes(self):
    #     """
    #     Returns the set of all cells in self.cells known to be safe.
    #     """
    #     count = 0
    #     for cell, status in self.cells:
    #         count += 1 - status
    #     return count

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)

depth = 0
class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = []

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        # I have to remove the sentences when empty otherwise i could enter an infinite loop when updating knowledge
        self.mines.add(cell)
        sentences = self.knowledge.copy()
        for sentence in sentences:
            sentence.mark_mine(cell)
            if len(sentence.cells) == 0:
                self.knowledge.remove(sentence)


    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        # I have to remove the sentences when empty otherwise i could enter an infinite loop when updating knowledge
        self.safes.add(cell)
        sentences = self.knowledge.copy()
        for sentence in sentences:
            sentence.mark_safe(cell)
            if len(sentence.cells) == 0:
                self.knowledge.remove(sentence)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        self.moves_made.append(cell)
        self.safes.add(cell)
        neighbours = self.getNeighbours(cell)
        sentence = Sentence(neighbours, count)
        self.knowledge.append(sentence)
        self.updateKnowledge(self.knowledge, sentence)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        safeMoves = self.safes.difference(self.moves_made)
        if len(safeMoves) > 0:
            move = next(iter(safeMoves))
            print(move)
            return move
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        # I set the first move as a standard one. I prefer to start in the corner so there are less chances to find a mine
        if len(self.moves_made) == 0:
            return (0,0)

        allMoves = set((i, j) for i in range(self.height) for j in range(self.width))
        allMoves = allMoves.difference(self.moves_made).difference(self.mines)
        if len(allMoves) > 0:
            move = next(iter(allMoves))
            print(move)
            return move
        return None

    def getNeighbours(self, cell):
        moves = [[0, 1],
                 [1, 1],
                 [1, 0],
                 [1, -1],
                 [0, -1],
                 [-1, -1],
                 [-1, 0],
                 [-1, 1]]
        neighbours = [(cell[0] + move[0], cell[1] + move[1]) for move in moves if
                      0 <= cell[0] + move[0] <= self.height - 1 and 0 <= cell[1] + move[1] <= self.width - 1]
        return [neighbour for neighbour in neighbours if neighbour not in self.moves_made]

    def updateSentence(self, sentence):
        # since mark_safe and mark_mine remove a cell from sentence i have to iterate over a copy
        if sentence.count == 0:
            nieghbours = sentence.cells.copy()
            for neighbour in nieghbours:
                self.safes.add(neighbour)
                self.mark_safe(neighbour)
        elif sentence.count == len(sentence.cells):
            nieghbours = sentence.cells.copy()
            for neighbour in nieghbours:
                self.mines.add(neighbour)
                self.mark_mine(neighbour)

    def updateKnowledge(self, knowledge, newSentence):
        # first of all i remove the known cells from the sentence to reduce the size of it
        for safe in self.safes:
            if safe in newSentence.cells:
                newSentence.cells.remove(safe)
        for mine in self.mines:
            if mine in newSentence.cells:
                newSentence.cells.remove(mine)
                newSentence.count -= 1
        self.updateSentence(newSentence)

        for sentence in knowledge:
            # managing the case when a sentence in a subset of another one
            if not sentence.__eq__(newSentence) and len(set(sentence.cells) - set(newSentence.cells)) == 0:
                newSentence.cells = [cell for cell in newSentence.cells if cell not in sentence.cells]
                newSentence.count -= sentence.count
                if len(sentence.cells) == 0:
                    return
                self.updateKnowledge(knowledge, newSentence)
            if not sentence.__eq__(newSentence) and len(set(newSentence.cells) - set(sentence.cells)) == 0:
                sentence.cells = [cell for cell in sentence.cells if cell not in newSentence.cells]
                sentence.count -= newSentence.count
                if len(sentence.cells) == 0:
                    return
                self.updateKnowledge(knowledge, sentence)