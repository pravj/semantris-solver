import time


class Player(object):
    """Player class represents a semantris solver agent.

    It implements top-level features of a player and its behavior
    in different configurations.

    Attributes:
        mode: (str) Semantris game mode (default: arcade)
        initial_wait_time: (int) Initial wait time (seconds) before starting
        verbose: (bool) Verbose logging configuration
    """

    def __init__(self, mode='arcade', initial_wait_time=10, verbose=False):
        self.mode = mode
        self.verbose = verbose
        self.initial_wait_time = initial_wait_time

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

        if self.mode == 'arcade':
            from players import arcade
            arcade.run()
        else:
            # Unreachable code (as of now)
            self.__log('Only arcade mode is supported as of now')
            return

    def __log(self, message):
        """
        Print a given log message based on the verbose configuration
        :param message: (str) Log message
        :return: None
        """

        if self.verbose:
            print(message)
