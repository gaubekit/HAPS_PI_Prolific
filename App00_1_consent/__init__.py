from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'App00_1_consent'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    consent = models.IntegerField(blank=False, choices=[[0, '0'], [1, '1']], label='Consent',
                                  attrs={"invisible": True})
    eligibility = models.IntegerField(blank=False, choices=[[0, '0'], [1, '1']], label='Eligibility',
                                      attrs={"invisible": True})
    optInConsent = models.IntegerField(blank=True, initial=0, choices=[[0, '0'], [1, '1']], label='Opt-In Consent',
                                       attrs={"invisible": True})


# PAGES
class EligibilityCheck(Page):  # TODO: no -> ask if you really dont like to participate - maybe reuse app00_2_exit
    form_model = 'player'
    form_fields = ['eligibility']

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        if player.eligibility == 0:
            player.participant.consent = 0  # set consent = 0 -> no consent to control exit pages
            return 'App04'


class ConsentFormA(Page):
    """ Welcome, Coal, payoff Information, Approximated Time """
    form_model = 'player'

    @staticmethod
    def before_next_page(player, timeout_happened):
        """ set single player var for waite page - will be changed to True, if no group forms"""
        player.participant.single_player = False


class ConsentFormA2(Page):
    """ PI, Eligibility. Risk&Benifits, Confidentiality, Participants Rights, IRB, optional opt-in """
    form_model = 'player'
    form_fields = ['optInConsent']

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.participant.optInConsent = player.optInConsent


class ConsentFormB(Page):
    """ if not consent:  ask second time in App00_2_exit (if not exit) else App00_3_continued """
    form_model = 'player'
    form_fields = ['consent']

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if not timeout_happened:
            player.participant.consent = player.consent

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        if player.consent == 0:
            return 'App00_2_exit'  # Check a second time for consent before going to exit (App04)
        else:
            return 'App00_3_continued'  # continue with Audio/Video Check and Prolific ID


page_sequence = [
    EligibilityCheck,
    ConsentFormA,
    ConsentFormA2,
    ConsentFormB,]
