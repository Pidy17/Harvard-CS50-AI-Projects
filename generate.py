import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generator.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]

        for variable, word in assignment.items():
            direction = variable.direction

            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]

        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")

            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont

        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border

        letters = self.letter_grid(assignment)

        img = Image.new(
            "RGBA",
            (
                self.crossword.width * cell_size,
                self.crossword.height * cell_size
            ),
            "black"
        )

        font = ImageFont.truetype(
            "assets/fonts/OpenSans-Regular.ttf", 80
        )

        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (
                        j * cell_size + cell_border,
                        i * cell_size + cell_border
                    ),
                    (
                        (j + 1) * cell_size - cell_border,
                        (i + 1) * cell_size - cell_border
                    )
                ]

                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")

                    if letters[i][j]:
                        _, _, w, h = draw.textbbox(
                            (0, 0), letters[i][j], font=font
                        )

                        draw.text(
                            (
                                rect[0][0] + ((interior_size - w) / 2),
                                rect[0][1] + ((interior_size - h) / 2) - 10
                            ),
                            letters[i][j],
                            fill="black",
                            font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()

        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Remove words that do not match the length of each variable.
        """
        for variable in self.domains:
            invalid_words = {
                word for word in self.domains[variable]
                if len(word) != variable.length
            }

            self.domains[variable] -= invalid_words

    def revise(self, x, y):
        """
        Make variable x arc consistent with variable y.
        """
        overlap = self.crossword.overlaps[x, y]

        if overlap is None:
            return False

        i, j = overlap
        revised = False

        invalid_words = set()

        for word_x in self.domains[x]:

            if not any(
                word_x[i] == word_y[j]
                for word_y in self.domains[y]
            ):
                invalid_words.add(word_x)

        if invalid_words:
            self.domains[x] -= invalid_words
            revised = True

        return revised

    def ac3(self, arcs=None):
        """
        Enforce arc consistency using the AC-3 algorithm.
        """
        if arcs is None:
            queue = [
                (x, y)
                for x in self.crossword.variables
                for y in self.crossword.neighbors(x)
            ]
        else:
            queue = list(arcs)

        while queue:

            x, y = queue.pop(0)

            if self.revise(x, y):

                if len(self.domains[x]) == 0:
                    return False

                for neighbor in self.crossword.neighbors(x):

                    if neighbor != y:
                        queue.append((neighbor, x))

        return True

    def assignment_complete(self, assignment):
        """
        Check whether every variable has been assigned a word.
        """
        return all(
            variable in assignment
            for variable in self.crossword.variables
        )

    def consistent(self, assignment):
        """
        Check whether an assignment satisfies all constraints.
        """

        # All assigned words must be different.
        words = list(assignment.values())

        if len(words) != len(set(words)):
            return False

        # Every assigned word must have the correct length.
        for variable, word in assignment.items():

            if len(word) != variable.length:
                return False

        # Overlapping variables must have matching letters.
        for variable in assignment:

            for neighbor in self.crossword.neighbors(variable):

                if neighbor in assignment:

                    overlap = self.crossword.overlaps[
                        variable, neighbor
                    ]

                    i, j = overlap

                    if assignment[variable][i] != assignment[neighbor][j]:
                        return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Order values using the least-constraining values heuristic.
        """

        def count_conflicts(value):

            conflicts = 0

            for neighbor in self.crossword.neighbors(var):

                if neighbor in assignment:
                    continue

                overlap = self.crossword.overlaps[var, neighbor]

                if overlap is None:
                    continue

                i, j = overlap

                for neighbor_word in self.domains[neighbor]:

                    if (
                        value[i] != neighbor_word[j]
                        or value == neighbor_word
                    ):
                        conflicts += 1

            return conflicts

        return sorted(
            self.domains[var],
            key=count_conflicts
        )

    def select_unassigned_variable(self, assignment):
        """
        Select a variable using MRV and the degree heuristic.
        """

        unassigned = [
            variable
            for variable in self.crossword.variables
            if variable not in assignment
        ]

        return min(
            unassigned,
            key=lambda variable: (
                len(self.domains[variable]),
                -len(self.crossword.neighbors(variable))
            )
        )

    def backtrack(self, assignment):
        """
        Solve the crossword using recursive backtracking search.
        """

        if self.assignment_complete(assignment):
            return assignment

        variable = self.select_unassigned_variable(assignment)

        for value in self.order_domain_values(variable, assignment):

            new_assignment = assignment.copy()
            new_assignment[variable] = value

            if self.consistent(new_assignment):

                result = self.backtrack(new_assignment)

                if result is not None:
                    return result

        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)

        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()