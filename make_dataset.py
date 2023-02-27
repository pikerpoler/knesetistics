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

party_enumerator = Enumerator()
politician_enumerator = Enumerator()


def open_voting_page_df(id=3835):
    #create a new Chrome session and gather voting data from the Knesset website
    driver = uc.Chrome()
    # driver.get("https://main.knesset.gov.il/Activity/plenum/Votes/Pages/default.aspx")
    driver.get(f'https://main.knesset.gov.il/Activity/plenum/Votes/Pages/vote.aspx?voteid={id}')
    time.sleep(10)
    # find all elements with class name "votesListInnerResultCell votesListInnerResultCellMk"
    # and put into a dataframe
    # create a dataframe with the following columns:
    # name, party, vote_for, vote_against, vote_abstain, vote_absent
    df = pd.DataFrame(columns=['name', 'party', 'vote'])
    print("collecting all votes")
    all_votes = driver.find_elements(By.CLASS_NAME, "votesListInnerResultCell")
    print(all_votes)
    # row = {'name': '', 'party': '', 'vote_for': '', 'vote_against': '', 'vote_abstain': '', 'vote_absent': ''}
    row = {'name': '', 'party': '', 'vote': ''}
    for i, vote in enumerate(all_votes):
        if i < 9:
            continue # skipping the header
        column_index = (i + 9) % 6
        print(f"i: {i}, column_index: {column_index}, vote: {vote.text}")
        if column_index == 0:
            if i > 9:
                df = df.append(row, ignore_index=True)
            if vote.text == '':
                break
            row['name'] = politician_enumerator.get_party(vote.text)
        elif column_index == 1:
            row['party'] = party_enumerator.get_party(vote.text)
        elif column_index == 2:
            if vote.text == 'x':
                row['vote'] = True
        elif column_index == 3:
            if vote.text == 'x':
                row['vote'] = False
        elif column_index == 4:
            if vote.text == 'x':
                row['vote'] = 'abstain'
        elif column_index == 5:
            if vote.text == 'x':
                row['vote'] = 'absent'

    print("printing dataframe")
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    print(f'parties: {party_enumerator.parties}')
    print(f'politicians: {politician_enumerator.parties}')
    print(df)
    driver.close()

    time.sleep(60)

def open_voting_page(id=38326):
    # this is the same as open_voting_page_df, but without using pandas. we use dictionaries instead
    #create a new Chrome session and gather voting data from the Knesset website
    driver = uc.Chrome()
    # driver.get("https://main.knesset.gov.il/Activity/plenum/Votes/Pages/default.aspx")
    driver.get(f'https://main.knesset.gov.il/Activity/plenum/Votes/Pages/vote.aspx?voteid={id}')
    time.sleep(10)
    # find all elements with class name "votesListInnerResultCell votesListInnerResultCellMk"
    # and put into a dataframe
    votes = dict()
    print("collecting all votes")
    all_votes = driver.find_elements(By.CLASS_NAME, "votesListInnerResultCell")
    row = {'name': '', 'party': '', 'vote': ''}
    for i, vote in enumerate(all_votes):
        if i < 9:
            continue
        column_index = (i + 9) % 6
        print(f"i: {i}, column_index: {column_index}, vote: {vote.text}")
        if column_index == 0:
            if i > 9:
                votes[row['name']] = row
            if vote.text == '':
                break
            row['name'] = politician_enumerator.get_party(vote.text)


def collect_1000_votes():
    # start with vote 38326 and go back 1000 votes
    # we are not using open_voting_page because it is too slow to use driver.get() 1000 times
    # instead we will iterate over votes and draw inspiration from open_voting_page. in the future we will
    # break this function into smaller functions

    # make enumerators for each of the 25 knesset sessions
    enumerators = {i: {'party': Enumerator(), 'politician': Enumerator()} for i in range(1, 26)}
    knesset_enumerator = Enumerator(start=25, step=-1)
    # make a dictionary for each of the 25 knesset sessions to hold the votes
    votes_per_knesset = {i: [] for i in range(1, 26)}
    # create a new Chrome session and gather voting data from the Knesset website
    driver = uc.Chrome()
    # driver.get("https://main.knesset.gov.il/Activity/plenum/Votes/Pages/default.aspx")
    driver.get(f'https://main.knesset.gov.il/Activity/plenum/Votes/Pages/vote.aspx?voteid=38326')
    time.sleep(10)

    # now we will iterate over the votes, each time we will get the knesset session number and the vote number

    for i in range(1000):
        try:
            # we will use these numbers to get the correct enumerator and votes dictionary
            # find all elements of class "knessetVoteInnerRowSecondItemSub"
            knesset_names = driver.find_elements(By.CLASS_NAME, "knessetVoteInnerRowSecondItemSub")
            knesset_name = knesset_names[0].text
            knesset_number = knesset_enumerator.get_party(knesset_name)  # the numbers are reversed,but that is fine for now
            party_enumerator = enumerators[knesset_number]['party']
            politician_enumerator = enumerators[knesset_number]['politician']

            # find all elements with class name "votesListInnerResultCell votesListInnerResultCellMk"
            votes = []
            print("collecting all votes")
            start_time = time.time()
            all_votes = driver.find_elements(By.CLASS_NAME, "votesListInnerResultCell")
            row = {'name': '', 'party': '', 'vote': ''}
            for i, vote in enumerate(all_votes):
                if i < 9:
                    continue
                column_index = (i + 9) % 6
                if column_index == 0:
                    if i > 9:
                        votes.append(copy.deepcopy(row))
                        row = {'name': '', 'party': '', 'vote': ''}
                    if vote.text == '':
                        break
                    row['name'] = politician_enumerator.get_party(vote.text)
                elif column_index == 1:
                    row['party'] = party_enumerator.get_party(vote.text)
                elif column_index == 2:
                    if vote.text == 'x':
                        row['vote'] = True
                elif column_index == 3:
                    if vote.text == 'x':
                        row['vote'] = False
                elif column_index == 4:
                    if vote.text == 'x':
                        row['vote'] = 'abstain'
                elif column_index == 5:
                    if vote.text == 'x':
                        row['vote'] = 'absent'

            # now we have the votes for this knesset session. we will add them to the votes dictionary
            votes_per_knesset[knesset_number].append(votes)
            print(f'time to collect votes: {time.time() - start_time} seconds')
            # now we will go back to the previous vote
            # find the "previous vote" button and click it
            print("going to previous vote")
            previous_vote_button = driver.find_element(By.CLASS_NAME, 'page-link')
            previous_vote_button.click()
            time.sleep(2)
        except Exception as e:
            print(f"error: trying to wait 5 seconds")
            time.sleep(5)
            # we will use these numbers to get the correct enumerator and votes dictionary
            # find all elements of class "knessetVoteInnerRowSecondItemSub"
            knesset_names = driver.find_elements(By.CLASS_NAME, "knessetVoteInnerRowSecondItemSub")
            knesset_name = knesset_names[0].text
            knesset_number = knesset_enumerator.get_party(
                knesset_name)  # the numbers are reversed,but that is fine for now
            party_enumerator = enumerators[knesset_number]['party']
            politician_enumerator = enumerators[knesset_number]['politician']

            # find all elements with class name "votesListInnerResultCell votesListInnerResultCellMk"
            votes = []
            print("collecting all votes")
            all_votes = driver.find_elements(By.CLASS_NAME, "votesListInnerResultCell")
            row = {'name': '', 'party': '', 'vote': ''}
            for i, vote in enumerate(all_votes):
                if i < 9:
                    continue
                column_index = (i + 9) % 6
                if column_index == 0:
                    if i > 9:
                        votes.append(copy.deepcopy(row))
                        row = {'name': '', 'party': '', 'vote': ''}
                    if vote.text == '':
                        break
                    row['name'] = politician_enumerator.get_party(vote.text)
                elif column_index == 1:
                    row['party'] = party_enumerator.get_party(vote.text)
                elif column_index == 2:
                    if vote.text == 'x':
                        row['vote'] = True
                elif column_index == 3:
                    if vote.text == 'x':
                        row['vote'] = False
                elif column_index == 4:
                    if vote.text == 'x':
                        row['vote'] = 'abstain'
                elif column_index == 5:
                    if vote.text == 'x':
                        row['vote'] = 'absent'

            # now we have the votes for this knesset session. we will add them to the votes dictionary
            votes_per_knesset[knesset_number].append(votes)

            # now we will go back to the previous vote
            # find the "previous vote" button and click it
            print("going to previous vote")
            previous_vote_button = driver.find_element(By.CLASS_NAME, 'page-link')
            previous_vote_button.click()
            time.sleep(2)

    print('saving votes to file')
    # save the votes to a file
    with open('votes.json', 'w') as f:
        json.dump(votes_per_knesset, f)
    print('done')


def main():
    # open_voting_page()
    collect_1000_votes()

if __name__ == '__main__':
    main()
