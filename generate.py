from crossword import Variable
import sys

from crossword import *


class CrosswordCreator():

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

        for var in self.crossword.variables:
            largo = var.length
            for frase in  self.crossword.words.copy():
                if len(frase) != largo:
                    self.domains[var].remove(frase)

        
        #raise NotImplementedError

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.

        """

        overlap = self.crossword.overlaps[x,y]

        if overlap == None:
            return False
        else:
            i = overlap[0]
            j = overlap[1]

        remover = []
        revisado = False

        for frase_x in self.domains[x]:
            for frase_y in self.domains[y]:
                if frase_x[i] == frase_y[j]:
                    break
            else:
                    if frase_x in remover:
                        continue
                    else:
                        remover.append(frase_x)
                        revisado = True

        return revisado

        #raise NotImplementedError

    def decola(self, arcos):
        """
        extrae arco desde cola

        """
        for (i,j) in arcos:
            arcos.remove((i,j))
            return i,j

        #raise NotImplementedError


    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.

        """
        
        if arcs == None:
            arcos = []

            for i in self.domains.keys():
                for j in self.domains.keys():
                    if i != j:
                        arco = (i,j)
                        arcos.append(arco)
        else:
            arcos = arcs[::]

        while arcos != None:
            (X,Y) = self.decola(arcos)
            if self.revise(X,Y):
                if len(self.domains[X]) == 0:
                    return False
            for Z in self.crossword.neighbors(X):
                if Z != Y:
                    arcos.append((Z,X))
            return True

    
        #raise NotImplementedError

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.

        """

        for i in self.domains.keys():
            if i not in assignment.keys():
                return False
            else:
                if assignment[i] == None:
                    return False
        return True                    

        #raise NotImplementedError

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.

        """

        valor = []

        for i,j in assignment.items():
            if j in valor:
                return False
            else:
                valor.append(j)
            if i.length != len(j):
                return False

            vecinos = self.crossword.neighbors(i)
            for vecino in vecinos:
                overlaps = self.crossword.overlaps[i, vecino]
                i_lap = list(overlaps)[0]
                vecino_lap = list(overlaps)[1]
                if vecino in assignment:
                    if assignment[vecino][vecino_lap] != j[i_lap]:
                        return False
        return True

        #raise NotImplementedError

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.

        """

        dict = {}
        valor = self.domains[var]
        vecino = self.crossword.neighbors(var)
        for i in valor:
            if i in assignment:
                continue
            else:
                contador = 0
            for j in vecino:
                if i in self.domains[j]:
                    contador += 1
            dict[i] = contador
        return sorted(dict, key = lambda k:dict[k])

        #raise NotImplementedError

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.

        """

        grado = 0
        valor = 1000
        for i in self.domains.keys():
            if i in assignment:
                continue
            else:
                if valor > len(self.domains[i]):
                    variable = i
                    valor = len(self.domains[i])
                    if self.crossword.neighbors(i) == None:
                        grado = 0
                elif valor == len(self.domains[i]):
                    if grado < len(self.crossword.neighbors(i)):
                        variable = i
                        valor = len(self.domains[i])
                        grado = len(self.crossword.neighbors(i))
                    else:
                        variable = i
                        valor = len(self.domains[i])
                        grado = 0
                else:
                    grado = len(self.crossword.neighbors(i))
        return variable

        #raise NotImplementedError

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.

        """

        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        for valor in self.order_domain_values(var,assignment):
            assignment[var] = valor
            if self.consistent(assignment):
                resultado = self.backtrack(assignment)
                if resultado != False:
                    return resultado
            assignment.pop(var)
        return False

        #raise NotImplementedError


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
