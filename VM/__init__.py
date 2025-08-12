from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'VM'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    video_ready = models.BooleanField(default=False)



# PAGES
class VideoMeeting(Page):
    """
    This page gives instructions about the VideoMeeting,
    asks for consens (do not speal about personal goals or intended behavior)
    and enables the video meeting (jitsi) after all players has agreed
    """

    # https://github.com/gaubekit/hapshiddenprofile/blob/dev_new/MeetingC/MeetingC.html#L254
    @staticmethod
    def live_method(player, data):
        player.video_ready = data
        all_ready = all(p.video_ready for p in player.group.get_players())
        print(all_ready)
        return {0: all_ready}

class VMtest(Page):
    form_model = 'player'

class VVC(Page):
    form_model = 'player'
    timeout_seconds = 540
    form_fields = ['seeHear', 'treatmentNumber','attentionCheck'] # TODO: Frage Warum ist hier seeHear?

    @staticmethod
    def vars_for_template(player: Player):
        optInConsent = player.participant.vars['optInConsent']

        if 'is_dropout' in player.participant.vars:
            is_dropout = player.participant.vars['is_dropout']
        else:
            is_dropout = False
        return dict(optInConsent=optInConsent,  # TODO: Brauche ich den optInConsent? Habe ich den?
                    is_dropout=is_dropout)


page_sequence = [
    VMtest,
]
