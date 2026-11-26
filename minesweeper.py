
import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        self.height = height
        self.width = width
        self.mines = set()

        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

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

        count = 0

        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                if (i, j) == cell:
                    continue

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
    Logical statement about a Minesweeper game.
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
        Returns all cells known to be mines.
        """
        if len(self.cells) == self.count:
            return set(self.cells)

        return set()

    def known_safes(self):
        """
        Returns all cells known to be safe.
        """
        if self.count == 0:
            return set(self.cells)

        return set()

    def mark_mine(self, cell):
        """
        Updates the sentence when a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates the sentence when a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player.
    """

    def __init__(self, height=8, width=8):

        self.height = height
        self.width = width

        self.moves_made = set()

        self.mines = set()
        self.safes = set()

        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine and updates all sentences.
        """
        self.mines.add(cell)

        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe and updates all sentences.
        """
        self.safes.add(cell)

        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Updates the AI's knowledge after a safe cell is revealed.
        """

        # 1. Record the move.
        self.moves_made.add(cell)

        # 2. Mark the revealed cell as safe.
        self.mark_safe(cell)

        # 3. Identify neighboring cells that are still unknown.
        neighbors = set()

        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                neighbor = (i, j)

                if neighbor == cell:
                    continue

                if not (0 <= i < self.height and 0 <= j < self.width):
                    continue

                if neighbor in self.mines:
                    count -= 1

                elif neighbor not in self.safes:
                    neighbors.add(neighbor)

        # 4. Add the new sentence to the knowledge base.
        if neighbors:
            new_sentence = Sentence(neighbors, count)

            if new_sentence not in self.knowledge:
                self.knowledge.append(new_sentence)

        # 5. Continue making logical inferences until
        # no more new information can be discovered.
        changed = True

        while changed:

            changed = False

            # Find cells that are definitely mines or safe.
            new_mines = set()
            new_safes = set()

            for sentence in self.knowledge:
                new_mines.update(sentence.known_mines())
                new_safes.update(sentence.known_safes())

            # Remove cells already known to the AI.
            new_mines -= self.mines
            new_safes -= self.safes

            # Mark newly discovered mines.
            for mine in new_mines:
                self.mark_mine(mine)
                changed = True

            # Mark newly discovered safe cells.
            for safe in new_safes:
                self.mark_safe(safe)
                changed = True

            # Remove empty sentences.
            self.knowledge = [
                sentence for sentence in self.knowledge
                if sentence.cells
            ]

            # 6. Apply subset inference.
            new_sentences = []

            for sentence1 in self.knowledge:
                for sentence2 in self.knowledge:

                    if sentence1 == sentence2:
                        continue

                    # If sentence1 is a subset of sentence2,
                    # subtract the smaller sentence from the larger.
                    if sentence1.cells < sentence2.cells:

                        difference = sentence2.cells - sentence1.cells

                        new_count = sentence2.count - sentence1.count

                        inferred_sentence = Sentence(
                            difference,
                            new_count
                        )

                        # Only add valid, non-empty sentences.
                        if difference and 0 <= new_count <= len(difference):

                            if inferred_sentence not in self.knowledge:
                                if inferred_sentence not in new_sentences:
                                    new_sentences.append(inferred_sentence)

            # Add newly inferred sentences.
            if new_sentences:
                self.knowledge.extend(new_sentences)
                changed = True

    def make_safe_move(self):
        """
        Returns a known safe cell that has not been played.
        """

        available_moves = self.safes - self.moves_made

        if available_moves:
            return next(iter(available_moves))

        return None

    def make_random_move(self):
        """
        Returns a random cell that has not been played
        and is not known to be a mine.
        """

        available_moves = []

        for i in range(self.height):
            for j in range(self.width):

                cell = (i, j)

                if cell in self.moves_made:
                    continue

                if cell in self.mines:
                    continue

                available_moves.append(cell)

        if available_moves:
            return random.choice(available_moves)

        return None