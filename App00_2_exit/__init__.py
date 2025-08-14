import time

from otree.api import *

c = cu

doc = 'Check Consent a second Time'


class C(BaseConstants):
    NAME_IN_URL = 'App00_2_exit'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    confirmConsent = models.IntegerField(blank=False, choices=[[0, '0'], [1, '1']], label='Do you want to participate?',
                                  attrs={"invisible": True})


class ConsentFormB2(Page):
    form_model = 'player'
    form_fields = ['confirmConsent']

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        if player.confirmConsent == 0:
            player.participant.consent = player.confirmConsent
            return 'App04'
        else:
            return 'App00_3_continued'


page_sequence = [ConsentFormB2]
