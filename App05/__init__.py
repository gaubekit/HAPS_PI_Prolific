from otree.api import *


doc = """
    This App contains only one page with the return to prolific
"""


class C(BaseConstants):
    NAME_IN_URL = 'App05'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


# PAGES
class ReturnToProlific(Page):
    """ Contains return-link """
    pass


page_sequence = [ReturnToProlific]
