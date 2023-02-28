import numpy as np
import time


class StatisticMaker:
    """
    This class creates statistics for a given correlation matrix, parties and coalition.
    """
    def __init__(self, matrix, mandates_per_party, coalition):
        self.matrix = matrix
        self.mandates_per_party = mandates_per_party
        self.coalition = coalition
        self.opposition = [party for party in mandates_per_party.keys() if party not in coalition]
        self.indexes_per_party = {}
        self.start = 0
        for party, mandates in mandates_per_party.items():
            self.indexes_per_party[party] = set(range(self.start, self.start + mandates))
            self.start += mandates

    def party_agreement(self, party_name):
        """
        Calculates the agreement between the politicians in the party.
        :param matrix: the correlation matrix
        :param indexes: the indexes of the politicians in the party
        :return: the average correlation between the politicians in the party.
            not including the diagonal and only the upper triangle of the matrix
        """
        indexes = self.indexes_per_party[party_name]
        return self._calc_party_agreement(indexes)

    def two_party_agreement(self, party_name1, party_name_2):
        """
        Calculates the agreement between two parties.
        :param matrix: the correlation matrix
        :param indexes1: the indexes of the politicians in the first party
        :param indexes2: the indexes of the politicians in the second party
        :return: the average correlation between the politicians in the two parties.
        not including the diagonal and only the upper triangle of the matrix
        """

        indexes1 = self.indexes_per_party[party_name1]
        indexes2 = self.indexes_per_party[party_name_2]
        return self._calc_two_party_agreement(indexes1, indexes2)

    def coalition_agreement(self):
        """
        Calculates the agreement between the coalition.
        this metric is the party agreement of the coalition as one party, divided by the two party agreement between the coalition and the opposition.
        :param matrix:
        :param coalition:
        :return:
        """

        coalition_indexes = set()
        for party in self.coalition:
            coalition_indexes = coalition_indexes.union(self.indexes_per_party[party])
        opposition_indexes = set()
        for party in self.opposition:
            opposition_indexes = opposition_indexes.union(self.indexes_per_party[party])
        all_indexes = coalition_indexes.union(opposition_indexes)

        coalition_party_agreement = self._calc_party_agreement(coalition_indexes)
        coalition_opposition_agreement = self._calc_two_party_agreement(coalition_indexes, opposition_indexes)
        all_agreement = self._calc_party_agreement(all_indexes)
        print(f'coalition_party_agreement: {coalition_party_agreement}')
        print(f'coalition_opposition_agreement: {coalition_opposition_agreement}')
        print(f'all_agreement: {all_agreement}')

        return coalition_party_agreement / coalition_opposition_agreement

    def _calc_party_agreement(self, indexes):
        sum_of_correlations = 0
        num_of_correlations = 0
        if len(indexes) == 1:
            return 1.0
        for i in indexes:
            for j in indexes:
                if i < j:
                    sum_of_correlations += self.matrix[i, j]
                    num_of_correlations += 1
        return sum_of_correlations / num_of_correlations

    def _calc_two_party_agreement(self, indexes1, indexes2):
        sum_of_correlations = 0
        num_of_correlations = 0
        for i in indexes1:
            for j in indexes2:
                sum_of_correlations += self.matrix[i, j]
                num_of_correlations += 1
        return sum_of_correlations / num_of_correlations


def random_correlation_matrix(n=120):
    """
    Creates a random correlation matrix of size n x n
    the diagonal is always 1 and the matrix is symmetric.
    :param n: size of matrix
    :return: a correlation matrix
    """
    matrix = np.random.rand(n, n)
    matrix = (matrix + matrix.T) / 2
    np.fill_diagonal(matrix, 1)
    return matrix



def analyze_random():
    """
    Analyze the random correlation matrix
    the matrix represents the correlation between votes of politicians (we have 120).
    we will use a case where we have parties of different sizes.
    :return:
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
    coalition = ['licud', 'shas', 'tora', 'stionut', 'might', 'noam']
    opposition = ['atid', 'mamlachti', 'beitenu', 'raam', 'taal', 'haavoda']
    print(f'check if amount of mandates is equal to 120: {sum(mandates_per_party.values()) == 120}')
    print(f'check how many mandates are in coalition: {sum([mandates_per_party[party] for party in coalition])}')
    print(f'check how many mandates are in opposition: {sum([mandates_per_party[party] for party in opposition])}')

    model = StatisticMaker(random_correlation_matrix(), mandates_per_party, coalition)
    for party in mandates_per_party.keys():
        print(f'{party} agreement is {model.party_agreement(party)}')

    print(f'two party (licud,atid) agreement is {model.two_party_agreement("licud", "atid")}')
    print(f'coalition agreement is {model.coalition_agreement()}')



def main():
    print('Creating statistics...')
    analyze_random()


if __name__ == '__main__':
    main()
