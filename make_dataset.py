import copy
import json
import time

import numpy as np
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webdriver import By
import selenium.webdriver.support.expected_conditions as EC  # noqa
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys

import undetected_chromedriver as uc
import pandas as pd


class Enumerator:
    def __init__(self, start=0, step=1):
        self.parties = {}
        self.counter = start
        self.step = step

    def get_party(self, party):
        if party not in self.parties:
            self.parties[party] = self.counter
            self.counter += self.step
        return self.parties[party]

def collect_100_votes():
    # start with vote 38326 and go back 100 votes
    # we are not using open_voting_page because it is too slow to use driver.get() 100 times
    # instead we will iterate over votes and draw inspiration from open_voting_page. in the future we will
    # break this function into smaller functions
    print("collecting 100 votes")
    knesset_enumerator = Enumerator(start=25, step=-1)
    # make a dictionary for each of the 25 knesset sessions to hold the votes
    votes_per_knesset = {i: {} for i in range(1, 26)}
    politician_parties_per_knesset = {i: {} for i in range(1, 26)}
    # create a new Chrome session and gather voting data from the Knesset website
    driver = uc.Chrome()
    driver.get(f'https://main.knesset.gov.il/Activity/plenum/Votes/Pages/vote.aspx?voteid=38326')
    time.sleep(10)

    # now we will iterate over the votes, each time we will get the knesset session number and the vote number
    # we will create a dictionary for each knesset session and each politician.
    # for each politician we will create a dictionary with vote number as key and vote as value
    # we will also create a dictionary for each knesset session with the politician name as key and the politicians party as value

    for i in range(100):
        vote_id = 38326 - i
        knesset_names = driver.find_elements(By.CLASS_NAME, "knessetVoteInnerRowSecondItemSub")
        knesset_name = knesset_names[0].text
        knesset_number = knesset_enumerator.get_party(knesset_name)

        # find all elements with class name "votesListInnerResultCell votesListInnerResultCellMk"
        print("collecting all votes")
        start_time = time.time()
        all_votes = driver.find_elements(By.CLASS_NAME, "votesListInnerResultCell")
        for i, vote in enumerate(all_votes):
            if i < 9:  # the first 9 elements are not votes, they are headers
                continue
            column_index = (i + 9) % 6
            if column_index == 0:  # the first column is the politician name
                if vote.text == '':
                    break
                politician_name = vote.text
                if politician_name not in votes_per_knesset[knesset_number]:
                    votes_per_knesset[knesset_number][politician_name] = {}
            elif column_index == 1:  # the second column is the politician's party
                party = vote.text
                if politician_name not in politician_parties_per_knesset[knesset_number]:
                    politician_parties_per_knesset[knesset_number][politician_name] = party
            elif column_index == 2:
                if vote.text == 'x':
                    votes_per_knesset[knesset_number][politician_name][vote_id] = 1
            elif column_index == 3:
                if vote.text == 'x':
                    votes_per_knesset[knesset_number][politician_name][vote_id] = 0
            elif column_index == 4:
                if vote.text == 'x':
                    votes_per_knesset[knesset_number][politician_name][vote_id] = -1
            elif column_index == 5:
                if vote.text == 'x':
                    votes_per_knesset[knesset_number][politician_name][vote_id] = -2

        print(f'time to collect votes: {time.time() - start_time} seconds')
        # now we will go back to the previous vote
        # find the "previous vote" button and click it
        print("going to previous vote")
        previous_vote_button = driver.find_element(By.CLASS_NAME, 'page-link')
        previous_vote_button.click()
        time.sleep(3)

    result = {'votes_per_knesset': votes_per_knesset, 'politician_parties_per_knesset': politician_parties_per_knesset}
    print('saving votes to file')
    json.dump(result, open('votes.json', 'w'))
    print('done')


def main():
    # open_voting_page()
    collect_100_votes()

if __name__ == '__main__':
    main()
