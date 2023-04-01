from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")
print(type(globals()['AKnight']))
print(exec('AKnight'))
print(type(exec('A' + 'Knight')))

# for each element in the puzzle i should add che condition that cannot be both knight and knave
def initializeElement(element):
    return Or(And(globals()[element + 'Knight'], Not(globals()[element + 'Knave'])),
              And(Not(globals()[element + 'Knight']), globals()[element + 'Knave']))


# for each statement i should define that it has to be true for knight and false for knave
def initializeStatement(speaker, statement):
    return And(Or(Not(globals()[speaker + 'Knight']), statement), Or(Not(globals()[speaker + 'Knave']), Not(statement)))


# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(initializeElement('A'))
knowledge0.add(initializeStatement('A', And(AKnight, AKnave)))

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(initializeElement('A'), initializeElement('B'))
knowledge1.add(initializeStatement('A', And(AKnave, BKnave)))

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(initializeElement('A'), initializeElement('B'))
knowledge2.add(initializeStatement('A', Or(And(AKnight, BKnight), And(AKnave, BKnave))))
knowledge2.add(initializeStatement('B', Or(And(AKnight, BKnave), And(AKnave, BKnight))))

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(initializeElement('A'), initializeElement('B'), initializeElement('C'))
knowledge3.add(initializeStatement('A', Or(initializeStatement('A', AKnave), initializeStatement('A', AKnight))))
knowledge3.add(initializeStatement('B', initializeStatement('A', AKnave)))
knowledge3.add(initializeStatement('B', CKnave))
knowledge3.add(initializeStatement('C', AKnight))


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
