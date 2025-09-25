from otree.api import *


doc = """
This app informs roughly about the study and checks for consent. No consent -> no participation.
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
    consent = models.IntegerField(
        label='<b>Do you want to participate?</b>',
        blank=False,
        choices=[(1, "Yes, I want to participate."), (0, "No, I do not want to participate.")],
        widget=widgets.RadioSelect
    )

    eligibility = models.IntegerField(
        label='<b>Are you able and willing to use a Chrome, Edge or Opera browser in this study?</b>',
        blank=False,
        choices=[(1, "Yes"), (0, "No")],
        widget=widgets.RadioSelectHorizontal
    )

    optInConsent = models.IntegerField(blank=True, initial=0, choices=[[0, '0'], [1, '1']], label='Opt-In Consent',
                                       attrs={"invisible": True})


# PAGES
class EligibilityCheck(Page):
    form_model = 'player'
    form_fields = ['eligibility']

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        if player.eligibility == 0:
            player.participant.consent = 0
            return 'App04'


class ConsentFormA(Page):
    """ Welcome, Coal, payoff Information, Approximated Time """
    form_model = 'player'


class ConsentFormA2(Page):
    """ PI, Eligibility. Risk&Benifits, Confidentiality, Participants Rights, IRB, optional opt-in """
    form_model = 'player'
    form_fields = ['optInConsent']

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.participant.optInConsent = player.optInConsent
        print('player label: ', player.participant.label)
        print('player code: ', player.participant.code)


class ConsentFormB(Page):
    """ if not consent:  ask second time in App00_2_exit (if not exit) else App00_3_continued """
    form_model = 'player'
    form_fields = ['consent']

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if not timeout_happened:
            player.participant.consent = player.consent

        try:
            # initialize dict for participant
            player.session.last_active_session_wide[player.participant.code] = {}
            print(player.session.last_active_session_wide)
        except KeyError as e:
            # initialize session var if not existing
            player.session.last_active_session_wide = {}
            player.session.last_active_session_wide[player.participant.code] = {}
            print('initialized session var last_active_session_wide')
            print(player.session.last_active_session_wide)




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
