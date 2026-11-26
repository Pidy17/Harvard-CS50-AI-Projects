from logic import *

# There are two possibilities for each character:
# They are either a Knight or a Knave.

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")


# Puzzle 0
# A says: "I am both a knight and a knave."

knowledge0 = And(

    # A must be either a knight or a knave.
    Or(AKnight, AKnave),

    # A cannot be both.
    Not(And(AKnight, AKnave)),

    # If A is a knight, A's statement must be true.
    Implication(AKnight, And(AKnight, AKnave)),

    # If A is a knave, A's statement must be false.
    Implication(AKnave, Not(And(AKnight, AKnave)))
)


# Puzzle 1
# A says: "We are both knaves."
# B says nothing.

knowledge1 = And(

    # A must be either a knight or a knave.
    Or(AKnight, AKnave),

    # A cannot be both.
    Not(And(AKnight, AKnave)),

    # B must be either a knight or a knave.
    Or(BKnight, BKnave),

    # B cannot be both.
    Not(And(BKnight, BKnave)),

    # A says that both A and B are knaves.
    # A knight must tell the truth.
    Implication(AKnight, And(AKnave, BKnave)),

    # A knave must lie.
    Implication(AKnave, Not(And(AKnave, BKnave)))
)


# Puzzle 2
# A says: "We are the same kind."
# B says: "We are of different kinds."

knowledge2 = And(

    # A must be either a knight or a knave.
    Or(AKnight, AKnave),

    Not(And(AKnight, AKnave)),

    # B must be either a knight or a knave.
    Or(BKnight, BKnave),

    Not(And(BKnight, BKnave)),

    # A says that A and B are the same kind.
    Implication(
        AKnight,
        Or(
            And(AKnight, BKnight),
            And(AKnave, BKnave)
        )
    ),

    Implication(
        AKnave,
        Not(
            Or(
                And(AKnight, BKnight),
                And(AKnave, BKnave)
            )
        )
    ),

    # B says that A and B are different kinds.
    Implication(
        BKnight,
        Or(
            And(AKnight, BKnave),
            And(AKnave, BKnight)
        )
    ),

    Implication(
        BKnave,
        Not(
            Or(
                And(AKnight, BKnave),
                And(AKnave, BKnight)
            )
        )
    )
)

# Puzzle 3
# A says either "I am a knight" or "I am a knave."
# B says:
# 1. A said "I am a knave."
# 2. C is a knave.
# C says: "A is a knight."

ASaidKnave = Symbol("A said I am a knave")

knowledge3 = And(

    # A must be either a knight or a knave.
    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave)),

    # B must be either a knight or a knave.
    Or(BKnight, BKnave),
    Not(And(BKnight, BKnave)),

    # C must be either a knight or a knave.
    Or(CKnight, CKnave),
    Not(And(CKnight, CKnave)),

    # A cannot truthfully say "I am a knave"
    # because a knight saying this would be lying,
    # while a knave saying this would be telling the truth.
    Not(ASaidKnave),

    # B says A said "I am a knave."
    Biconditional(BKnight, ASaidKnave),

    # B also says C is a knave.
    Biconditional(BKnight, CKnave),

    # C says A is a knight.
    Biconditional(CKnight, AKnight)
)


def main():

    symbols = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]

    for puzzle, knowledge in symbols:

        print(puzzle)

        for symbol in [
            AKnight, AKnave,
            BKnight, BKnave,
            CKnight, CKnave
        ]:

            if model_check(knowledge, symbol):
                print(f"    {symbol}")

        print()



if __name__ == "__main__":
    main()