from otree.api import *
import re
import time


doc = """
- checking Browser
- Checking Audio and Video (question)
- Checking Audio and Video (test)
- Test call to adjust background
- Prolific ID
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
    colorVideo = models.IntegerField(blank=False, label="What color was mentioned in the video?",
                                     choices=[[0, 'Red'], [1, 'Blue'], [2, 'Green'], [3, 'Yellow']])
    numberVideo = models.IntegerField(blank=False, label="Which number was shown in the video?",
                                      choices=[[1, '1'], [2, '2'], [3, '3'], [4, '4'], [5, '5']])


def ProlificId_error_message(player: Player, value):
    if not re.fullmatch(r'^[A-Za-z0-9]{24}$', value):
        return "Prolific ID must be exactly 24 alphanumeric characters (letters and numbers only)."
    return None


# PAGES
class ConfirmAudioVideoInteract(Page):
    """ Get the confirmation for Audio/Video/Cam, Interaction in VM and Payout """
    form_model = 'player'
    form_fields = ['willingToInteract', 'willingToBePaid', 'camMicStatus']

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if not timeout_happened:
            player.participant.vars['wait_page_arrival'] = time.time()


class BrowserCheck(Page):
    """ Check Browser a second time and force to change browser if necessary"""
    form_model = 'player'


# class AudioVideoCheck(Page): # TODO: could be deleted
#     form_model = 'player'
#     form_fields = ['colorVideo', 'numberVideo']

    # @staticmethod
    # def before_next_page(player: Player, timeout_happened):
    #     if not timeout_happened:
    #         player.participant.vars['colorVideo'] = player.colorVideo
    #         player.participant.vars['numberVideo'] = player.numberVideo
    #         player.participant.vars['wait_page_arrival'] = time.time()
    #
    # @staticmethod
    # def app_after_this_page(player: Player, upcoming_apps):
    #     if player.numberVideo != 2 or player.colorVideo != 3:
    #         return 'App04'  # TODO: Handle Return differently "you cant take part without giving consent" doesnt fit the mater
    # TODO -> Note: Muss ich bei return App04 noch irgendwas beachten, wenn diese Seite raus ist?


class VVC0(Page):
    """ Testing Jitsi and selecting Background """
    form_model = 'player'


class EnterProlificId(Page):
    """ Getting Prolific ID """
    form_model = 'player'
    form_fields = ['ProlificId']


page_sequence = [
    ConfirmAudioVideoInteract,
    BrowserCheck,
    # AudioVideoCheck, # not needed with the VVCO check
    VVC0,
    EnterProlificId]
