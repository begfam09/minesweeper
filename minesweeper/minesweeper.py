import itertools
import random
import copy


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
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
            Returns the set of all cells in self.cells known to be mines.
            """
        if self.count == len(self.cells):
            return self.cells

    def known_safes(self):
        """
            Returns the set of all cells in self.cells known to be safe.
            """
        if self.count == 0:
            return self.cells

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


class MinesweeperAI():
    """
      Minesweeper game player
      """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

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
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
            Marks a cell as safe, and updates all knowledge
            to mark that cell as safe as well.
            """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
            Called when the Minesweeper board tells us, for a given
            safe cell, how many neighboring cells have mines in them.

            This function should:
                1) DONE mark the cell as a move that has been made
                2) DONE mark the cell as safe
                3) DONE add a new sentence to the AI's knowledge base
                   based on the value of `cell` and `count`
                4) DONE mark any additional cells as safe or as mines
                   if it can be concluded based on the AI's knowledge base
                5) DONE add any new sentences to the AI's knowledge base
                   if they can be inferred from existing knowledge
            """

        # Add move to the moves_made list and mark it safe (removing cell from knowledge also)
        self.moves_made.add(cell)
        self.mark_safe(cell)

        # Get list of unexplored neighbors & process according to count
        unexplored_neighbors = self.find_unexplored_neighbors(cell)
        if count == 0:
            for cell in unexplored_neighbors:
                self.mark_safe(cell)
        elif len(unexplored_neighbors) <= count:
            for cell in unexplored_neighbors:
                self.mark_mine(cell)
        else:
            self.knowledge.append(Sentence(unexplored_neighbors, count))

        loop_again = True
        while loop_again:
            loop_again = False

            # Loop through knowledge, acquiring a list of mines to be marked. After knowledge is looped
            # through, update the knowledge with the list.
            mines_to_be_marked = set()
            for sentence in self.knowledge:
                if len(sentence.cells) == sentence.count:
                    for cell in sentence.cells:
                        if cell not in (self.mines | mines_to_be_marked):
                            mines_to_be_marked.add(cell)

            for cell in mines_to_be_marked:
                loop_again = True
                self.mark_mine(cell)

            # Loop through knowledge, acquiring a list of safes to be marked. After knowledge is looped
            # through, remove all sentences with count = 0, and update knowledge with safe list.
            safes_to_be_marked = set()
            temp_knowledge = copy.deepcopy(self.knowledge)
            for sentence in temp_knowledge:
                if sentence.count == 0:
                    for cell in sentence.cells:
                        if cell not in (self.safes | safes_to_be_marked):
                            safes_to_be_marked.add(cell)
                    self.knowledge.remove(sentence)

            for cell in safes_to_be_marked:
                loop_again = True
                self.mark_safe(cell)

            # Check to see if any sentences are subset of other sentences, and add resulting new knowledge,
            # if any.
            new_knowledge = []
            for sentence_a in self.knowledge:
                for sentence_b in self.knowledge:
                    if (sentence_a.cells != sentence_b.cells) and (sentence_a.cells.issubset(sentence_b.cells)):
                        new_sentence = Sentence(sentence_b.cells - sentence_a.cells, sentence_b.count - sentence_a.count)
                        if (new_sentence not in self.knowledge) and (new_sentence not in new_knowledge):
                            new_knowledge.append(new_sentence)

            for sentence in new_knowledge:
                loop_again = True
                self.knowledge.append(sentence)

    def make_safe_move(self):
        """
            Returns a safe cell to choose on the Minesweeper board.
            The move must be known to be safe, and not already a move
            that has been made.

            This function may use the knowledge in self.mines, self.safes
            and self.moves_made, but should not modify any of those values.
            """
        unmade_safes = self.safes - self.moves_made
        print(unmade_safes)
        while True:
            if len(unmade_safes) == 0:
                return None

            safe_cell = unmade_safes.pop()
            return safe_cell

    def make_random_move(self):
        """
            Returns a move to make on the Minesweeper board.
            Should choose randomly among cells that:
                1) have not already been chosen, and
                2) are not known to be mines
            """
        while True:

            random_cell = (random.randrange(self.height), random.randrange(self.width))

            if random_cell not in itertools.chain(self.moves_made, self.mines):
                return random_cell

    def find_unexplored_neighbors(self, cell):
        """
            Returns a cell's unexplored neighbors
            """
        neighbors = set()
        y = cell[0]
        x = cell[1]

        # Define the possible directions
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]

        for dy, dx in directions:
            neighbor_y = y + dy
            neighbor_x = x + dx
            neighbor_cell = (neighbor_y, neighbor_x)

            # Check if the neighbor is within the grid boundaries
            if (0 <= neighbor_y < self.height and 0 <= neighbor_x < self.width) and neighbor_cell not in (
                    self.moves_made | self.safes | self.mines):
                neighbors.add(neighbor_cell)

        return neighbors