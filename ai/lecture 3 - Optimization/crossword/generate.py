import sys

from crossword import *
import copy
import timeit


class CrosswordCreator:

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
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

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
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
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var, domains in self.domains.items():
            self.domains[var] = [word for word in domains if len(word) == var.length]

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        (i, j) = self.crossword.overlaps[(x, y)]
        initLen = len(self.domains[x])
        self.domains[x] = [wordX for wordX in self.domains[x]
                           if any(wordX[i] == wordY[j] for wordY in self.domains[y])]
        return len(self.domains[x]) != initLen

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        arcs = arcs if arcs is not None \
            else [arc for arc in self.crossword.overlaps.keys() if self.crossword.overlaps[arc] is not None]
        updated = True
        while updated:
            updated = False
            for v1, v2 in arcs:
                updated = self.revise(v1, v2) or self.revise(v2, v1)
                if len(self.domains[v1]) == 0 or len(self.domains[v2]) == 0:
                    return False
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        return len(assignment.keys()) == len(self.crossword.variables)

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        if len(set(assignment.values())) != len(assignment.values()):
            return False
        for var1, word1 in assignment.items():
            for var2, word2 in assignment.items():
                if var1 == var2 or self.crossword.overlaps[(var1, var2)] is None:
                    continue
                (i, j) = self.crossword.overlaps[(var1, var2)]
                if word1[i] != word2[j]:
                    return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        neighbours = [variable for variable in self.crossword.variables
                      if variable not in assignment and var != variable and self.crossword.overlaps[(var, variable)] is not None]
        eliminated = {word: 0 for word in self.domains[var]}
        for varWord in eliminated.keys():
            counter = 0
            for neighbour in neighbours:
                (i, j) = self.crossword.overlaps[(var, neighbour)]
                for neighbourWord in self.domains[neighbour]:
                    if varWord[i] != neighbourWord[j]:
                        counter += 1
        return [k for k, _ in sorted(eliminated.items(), key=lambda item: item[1])]

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        numWords = sys.maxsize
        returnVar = None
        for var in self.crossword.variables:
            if var not in assignment.keys() and \
                    (len(self.domains[var]) < numWords or
                     (len(self.domains[var]) == numWords and len(self.domains[var]) > len(self.domains[returnVar]))):
                returnVar = var
                numWords = len(self.domains[var])
        return returnVar

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if not self.consistent(assignment):
            return None
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        # In order to apply arc consistency after assigning a value to a variable i need to copy the domains:
        # if the solution is not found i can restore the domain to its original value
        originalDomain = copy.deepcopy(self.domains)
        for word in self.order_domain_values(var, assignment):
            assignment[var] = word
            self.domains[var] = [word]
            self.ac3()
            sol = self.backtrack(assignment)
            if sol is not None:
                return sol
            self.domains = copy.deepcopy(originalDomain)
        assignment.pop(var)


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
    print(timeit.timeit(lambda : creator.solve(), number=5))
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
