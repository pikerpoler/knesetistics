import numpy as np


def matrix_from_dictionary(data, party_per_politician):
    """
    This function creates a correlation matrix from a given dataset.
    :param data: a dictionary of politicians, each politician is a dictionary of votes.
    :param party_per_politician: a dictionary of politicians and their parties.
    :return: a correlation matrix of the votes.
    """
    # create a politician_per_party dictionary
    politician_per_party = {}
    for politician in party_per_politician:
        party = party_per_politician[politician]
        if party not in politician_per_party:
            politician_per_party[party] = []
        politician_per_party[party].append(politician)
    # create an index_per_politician dictionary. indexes of politicians are ordered by party.
    index_per_politician = {}
    index = 0
    for party in politician_per_party:
        for politician in politician_per_party[party]:
            index_per_politician[politician] = index
            index += 1

    # create matrix
    matrix = np.full((len(data), len(data)), -1, dtype=float)
    for politician1, i in index_per_politician.items():
        for politician2, j in index_per_politician.items():
            votes1 = data[politician1]
            votes2 = data[politician2]
            votes = set(votes1.keys()).intersection(set(votes2.keys()))
            if len(votes) > 0:
                sum = 0
                for vote in votes:
                    sum += 1 if votes1[vote] == votes2[vote] else 0
                matrix[i, j] = sum / len(votes)
                matrix[j, i] = sum / len(votes)
    return matrix

def create_from_random():
    """
    This function creates a correlation matrix from a random dataset.
    120 politicians, 1000 votes. each politician votes randomly, and has a 50% chance of participating in each vote.
    when a politician votes, he votes randomly, and has a 2% chance of abstaining.
    the party_per_politician is not random.
    :return: a correlation matrix.
    """
    mandates_per_party = {'licud': 32,
                          'atid': 24,
                          'mamlachti': 12,
                          'shas': 11,
                          'tora': 7,
                          'stionut': 7,
                          'might': 6,
                          'beitenu': 6,
                          'raam': 5,
                          'taal': 5,
                          'haavoda': 4,
                          'noam': 1,
                          }
    # create politicians and party_per_politician
    party_per_politician = {}
    for party in mandates_per_party:
        for i in range(mandates_per_party[party]):
            party_per_politician[f'{party}_{i}'] = party
    print(f'party_per_politician: {party_per_politician}')

    # create votes
    data = {}
    for vote_id in range(1000):
        for politician in party_per_politician:
            if np.random.rand() < 0.5:
                data.setdefault(politician, {})[vote_id] = np.random.randint(0, 2)
                if np.random.rand() < 0.02:
                    data[politician][vote_id] = -1
    print(f'data: {data.keys()}')
    # create matrix
    matrix = matrix_from_dictionary(data, party_per_politician)
    return matrix

def main():
    # matrix = matrix_from_dictionary(data, party_per_politician)
    matrix = create_from_random()
    print(matrix)
    np.save('test.npy', matrix)

if __name__ == '__main__':
    main()
