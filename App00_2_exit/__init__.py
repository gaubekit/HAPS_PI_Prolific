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
    consent = models.IntegerField(
        label='<b>Do you want to participate?</b>',
        blank=False,
        choices=[(1, "Yes, I want to participate."), (0, "No, I do not want to participate.")],
        widget=widgets.RadioSelect
    )


class ConsentFormB2(Page):
    form_model = 'player'
    form_fields = ['consent']

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        if player.consent == 0:
            player.participant.consent = player.consent
            return 'App04'
        else:
            return 'App00_3_continued'


page_sequence = [ConsentFormB2]
