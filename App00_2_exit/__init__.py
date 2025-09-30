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
    consent_ = models.IntegerField(
        label='<b>Do you want to participate?</b>',
        blank=False,
        choices=[(1, "Yes, I want to participate."), (0, "No, I do not want to participate.")],
        widget=widgets.RadioSelect
    )

    consent_form_ = models.IntegerField(
        label='<b>Do you want to participate?</b>',
        blank=False,
        choices=[(1, "Yes, I want to participate."), (0, "No, I do not want to participate.")],
        widget=widgets.RadioSelect
    )


class ConsentFormB2(Page):
    form_model = 'player'
    form_fields = ['consent_form_']

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.participant.consent_form = player.consent_form_
        player.consent_ = player.participant.consent_form and player.participant.consent_eligibility
        player.participant.consent = player.consent_

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        if player.consent_ == 0:
            return 'App04'
        else:
            return 'App00_3_continued'


page_sequence = [ConsentFormB2]
