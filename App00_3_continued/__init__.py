from otree.api import *
import re


doc = """
    - confirm audio and video interaction 
    - checking browser
    - Test call to adjust background
    - Prolific ID -> initialize participant variables for payoff
    - Study Information about Stage1, Stage2 and Stage3
    - Payoff Information
"""


class C(BaseConstants):
    NAME_IN_URL = 'App00_3_continued'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    ProlificId = models.StringField(label='Please enter your Prolific ID so that we can pay you.')
    willingToInteract = models.IntegerField(blank=False, choices=[[0, '0'], [1, '1']], label='',
                                            attrs={"invisible": True})
    willingToBePaid = models.IntegerField(blank=False, choices=[[0, '0'], [1, '1']], label='',
                                          attrs={"invisible": True})
    camMicStatus = models.IntegerField(blank=False, choices=[[0, '0'], [1, '1']], label='',
                                       attrs={"invisible": True})


def ProlificId_error_message(player: Player, value):
    if not re.fullmatch(r'^[A-Za-z0-9]{24}$', value):
        return "Prolific ID must be exactly 24 alphanumeric characters (letters and numbers only)."
    return None


# PAGES

class ConfirmAudioVideoInteract(Page):
    """ Get the confirmation for Audio/Video/Cam, Interaction in Playground and payoff """
    form_model = 'player'
    form_fields = ['willingToInteract', 'willingToBePaid', 'camMicStatus']


class BrowserCheck(Page):
    """ Check Browser a second time and force to change browser if necessary"""
    form_model = 'player'


class VVC0(Page):
    """ Testing Jitsi, Selecting Background and Confirming setup"""
    form_model = 'player'


class VVC0_dummy(Page):  # TODO: use after 15:30 for testing (joint study conflict)
    form_model = 'player'


class EnterProlificId(Page):
    """ Getting Prolific ID """
    form_model = 'player'
    form_fields = ['ProlificId']

    @staticmethod
    def before_next_page(player, timeout_happened):
        """
            Participant variables for payoff are initialized to avoid key errors
            and guarantee for 1.5 (75 ECU) in case of dropout.
        """
        player.participant.prolific_id = player.ProlificId
        player.participant.payoff_fix = 75
        player.participant.payoff_bonus_svo = 0
        player.participant.payoff_compensation_wait = 0
        player.participant.payoff_bonus_wlg = 0
        player.participant.payoff_compensation_wlg_dropout = 0
        player.participant.payoff_total = player.participant.payoff_fix


class GeneralInformation(Page):
    """ Giving general information about Stage1, Stage2 and Stage3"""
    form_model = 'player'


class PayoffInformation(Page):
    """ Giving general information about Stage1, Stage2 and Stage3"""
    form_model = 'player'


page_sequence = [
    ConfirmAudioVideoInteract,
    BrowserCheck,
    # VVC0_dummy,  # TODO: use after 15:30 for testing (joint study conflict)
    VVC0,  # TODO: use only until 15:00 for testing (joint study conflict)
    EnterProlificId,
    GeneralInformation,
    PayoffInformation
   ]
