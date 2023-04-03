import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():
    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):
                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    totalProbability = 1
    for person in people.values():
        scenarioProb = 1
        if ((person["mother"] is None and person["father"] is not None) or
                (person["mother"] is not None and person["father"] is None)):
            raise RuntimeError("Unexpected value: one parent is filled and the other one is empty")
        # now i can avoid to check is father is none because, because wrong inputs are threated with RuntimeError
        num_gene = (1 if person["name"] in one_gene else
                    2 if person["name"] in two_genes else 0)
        if person["mother"] is None:
            scenarioProb *= PROBS["gene"][num_gene]
        else:
            mother_gene = (1 if person["mother"] in one_gene else
                           2 if person["mother"] in two_genes else 0)
            father_gene = (1 if person["father"] in one_gene else
                           2 if person["father"] in two_genes else 0)
            probGeneMother = parentGeneProb(mother_gene)
            probGeneFather = parentGeneProb(father_gene)
            if num_gene == 0:
                scenarioProb *= probGeneMother[0] * probGeneFather[0]
            elif num_gene == 2:
                scenarioProb *= probGeneMother[1] * probGeneFather[1]
            else:
                scenarioProb *= probGeneMother[0] * probGeneFather[1] + probGeneMother[1] * probGeneFather[0]
        trait = True if person["name"] in have_trait else False
        scenarioProb *= PROBS["trait"][num_gene][trait]
        totalProbability *= scenarioProb
    return totalProbability


def parentGeneProb(parent_gene):
    probGeneParent = {}
    if parent_gene == 0:
        probGeneParent[0] = 1 - PROBS["mutation"]
        probGeneParent[1] = PROBS["mutation"]
    elif parent_gene == 2:
        probGeneParent[0] = PROBS["mutation"]
        probGeneParent[1] = 1 - PROBS["mutation"]
    else:
        probGeneParent[0] = 0.5
        probGeneParent[1] = 0.5
    return probGeneParent


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        num_gene = (1 if person in one_gene else
                    2 if person in two_genes else 0)
        trait = True if person in have_trait else False
        probabilities[person]["gene"][num_gene] += p
        probabilities[person]["trait"][trait] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        probabilities[person]["gene"] = {num_gene: val / sum(probabilities[person]["gene"].values())
                                         for num_gene, val in probabilities[person]["gene"].items()}
        probabilities[person]["trait"] = {trait: val / sum(probabilities[person]["trait"].values())
                                          for trait, val in probabilities[person]["trait"].items()}


if __name__ == "__main__":
    main()
