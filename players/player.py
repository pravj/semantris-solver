import os
import time
import random
from collections import defaultdict
import pyautogui
from gensim.models.keyedvectors import KeyedVectors
from utils import utils


class Player(object):
    """Player class represents a semantris solver agent.

    It implements top-level features of a player and its behavior
    in different configurations.

    Attributes:
        mode: (str) Semantris game mode (default: arcade)
        initial_wait_time: (int) Initial wait time (seconds) before starting
        refresh_time: (int) Time (seconds) to refresh the session
        verbose: (bool) Verbose logging configuration
    """

    def __init__(self, mode='arcade', initial_wait_time=10, refresh_time=0.2, verbose=False):
        self.mode = mode
        self.initial_wait_time = initial_wait_time

        # relatively higher wait time for blocks mode
        self.refresh_time = refresh_time if mode == 'arcade' else 2

        self.verbose = verbose

        # List of words to find associated words for
        self.selected_words = []

        # Dictionary containing associated words attempted for a word so far
        self.associated_word_mapping = defaultdict(list)

        # Word2Vec model key vector instance
        self.model = None

    def run(self):
        """
        Run the solver agent based on the game mode
        :return: None
        """

        # initial wait before startup to give proper time
        # before setting up the screen for game
        self.__log('Waiting {} seconds before starting the game ...'.format(
            self.initial_wait_time))
        time.sleep(self.initial_wait_time)

        self.__load_model()

        if self.mode == 'arcade':
            from players import arcade as game
        elif self.mode == 'blocks':
            from players import blocks as game

        num = 0
        while True:
            self.__log('Taking screen shot')
            # suitable region for 1440x900 full screen mode
            screen_region = (200, 100, 1000, 700) if self.mode == 'blocks' else None
            screen = utils.get_screen_shot(region=screen_region, wait_time=0)

            self.__log('Collecting focus word from screen shot')
            selected_word_candidates = list(set(game.get_selected_words(screen, num)))
            self.__log(selected_word_candidates)
            self.__log('Collected {} focus word from screen shot'.format(len(selected_word_candidates)))
            for selected_word in selected_word_candidates:
                if selected_word is not '':
                    """
                    Enter the same word if there is no similar words available

                    It can happen because of the following known reasons:
                    - Error in focus word detection (OCR)
                    """
                    try:
                        associated_word = self.__get_associated_word(selected_word)
                    except KeyError:
                        self.__log('Entering same word {} as there is no similar word for it'.format(selected_word))
                        associated_word = selected_word

                    self.__enter_word(selected_word, associated_word)

                print('selected word', selected_word)

            self.__log('Waiting before next screen shot')
            time.sleep(self.refresh_time)

            num += 1

    def __log(self, message):
        """
        Print a given log message based on the verbose configuration
        :param message: (str) Log message
        :return: None
        """

        if self.verbose:
            print(message)

    def __load_model(self):
        """
        Load the word2vec key vector instance in memory
        :return: None
        """
        self.__log('Loading Word2Vec model ...')
        self.model = KeyedVectors.load_word2vec_format(
            os.getenv('SEMANTRIS_SOLVER_WORD2VEC_PATH'),
            binary=True
        )

    def __get_associated_word(self, word):
        """
        Return a word associated with the given word
        using a word embedding model
        :param word: Original word
        :return: (str) associated word
        """

        self.__log('Searching associated word for {}'.format(word))

        word = word.lower()

        # select a random section in space separated word
        # for example, 'debit card' might return 'debit' OR 'card'
        if len(word.split()) > 1:
            word = random.choice(word.split())

        candidate_word_tuples = self.model.most_similar(word, topn=20)
        for candidate_word, _ in candidate_word_tuples:
            candidate_word = candidate_word.lower()

            # Ignore a candidate word if
            # it shares prefix (4 character) with original word
            # it has more than 10 characters
            # it has been tried earlier for this word
            if word[:4] == candidate_word[:4] or \
                    len(candidate_word) > 10 or \
                    candidate_word in self.associated_word_mapping[word]:
                continue

            self.associated_word_mapping[word].append(candidate_word)
            return candidate_word.lower().replace('_', ' ')

    def __enter_word(self, word, associated_word):
        """
        Enter a given word at a 'pre-selected' input field
        :param word: Word to enter (type-in)
        :return: None
        """

        self.__log("Entering associated word '{}' for '{}'".format(
            associated_word,
            word
        ))

        pyautogui.typewrite(associated_word, interval=round(random.random() / 4, 2))
        pyautogui.press('enter')
