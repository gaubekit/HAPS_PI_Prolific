from otree.api import *
import time


doc = """
Your app description
"""

last_active = {}

class C(BaseConstants):
    NAME_IN_URL = 'Playground'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 1
    VM_DURATION = 420
    VM_UPLOAD_DURATION = 120


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # video_ready = models.BooleanField(default=False)

    # Var to control Video Meeting Behavior
    # 1 = no modification , 2 = no self-view, 3 = additional message on top
    video_meeting_behavior = models.IntegerField(initial=1, blank=True)

    # Var to ensure that Video Meeting worked properly
    seeHear = models.IntegerField(blank=True, choices=[[0, '0'], [1, '1'], [2, '2']], label='',
                                  attrs={"invisible": True}, default=2)
    attentionCheck = models.IntegerField(blank=True, choices=[[0, '0'], [1, '1']], label='',
                                         attrs={"invisible": True}, default=0)
    correctBackground = models.IntegerField(blank=True, choices=[[0, '0'], [1, '1']], label='',
                                         attrs={"invisible": True}, default=0)


# PAGES
class HeartBeat(Page):
    @staticmethod
    def live_method(player, data):
        now = time.time()
        p = player.participant
        page = p._current_page_name

        # update last active time for current player
        last_active[p.code] = now

        if page == "HeartBeat" and last_active.get(p.code, 0) > now - 0.8:
            print(f'player {p.code} was active: {last_active[p.code]}')
        else:
            print(f'!INACTIVE playe:r {p.code} {last_active[p.code]}')


class WaitPageGroup(WaitPage):
    group_by_arrival_time = True


class MyPage0(Page):
    """ Only a Dummy Page for testing """
    form_model = 'player'

    @staticmethod
    def before_next_page(player, timeout_happened):
        #player.participant.single_player = False
        #player.participant.raised_dropout = False
        if player.id_in_group == 1:
            print('\n\n\n')
            print(' New Round ')
            print('===========')


class MyPage(Page):
    """ Only a Dummy Page for testing """
    form_model = 'player'

    @staticmethod
    def get_timeout_seconds(player):
        if player.participant.single_player:
            return 1
        else:
            return 60

    @staticmethod
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            print(player, ' tagged as raised_dropout')
            player.participant.single_player = True
            player.participant.raised_dropout = True


class WaitPage3(WaitPage):  # TODO https://otree.readthedocs.io/en/latest/multiplayer/waitpages.html
    """
    This Wait Page has to ensure, that dropout during the video meeting is detected.
    """

    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        for p in player.group.get_players():
            if p.participant.raised_dropout:
                # if one of the others is a single player, all in the group are flagged as single player
                player.participant.single_player = True

        if player.participant.single_player:
            print('player tagged as single player')
        return None


class MyPage2(Page):
    """ Only a Dummy Page for testing """
    form_model = 'player'

# class VideoMeeting(Page):
#     """
#     This page gives instructions about the VideoMeeting,
#     asks for consens (do not speal about personal goals or intended behavior)
#     and enables the video meeting (jitsi) after all players has agreed
#     """
#
#     # https://github.com/gaubekit/hapshiddenprofile/blob/dev_new/MeetingC/MeetingC.html#L254
#     @staticmethod
#     def live_method(player, data):
#         player.video_ready = data
#         all_ready = all(p.video_ready for p in player.group.get_players())
#         print(all_ready)
#         return {0: all_ready}
#
# class VMtest(Page):
#     form_model = 'player'


class VideoMeetingTest(Page):
    # Note: I added global.css, Picture_Camera.jpg and Picture_Microphone.jpg to _static ..srsly, why coding this dirty? :(
    form_model = 'player'
    timeout_seconds = C.VM_DURATION + C.VM_UPLOAD_DURATION   # 540 7min Playground + 2min upload/Fragebögen
    form_fields = ['seeHear', 'video_meeting_behavior', 'attentionCheck', 'correctBackground']


    @staticmethod
    def vars_for_template(player: Player):
        # TODO: Hardcoded for testing, because optInConsent is written in App01 and I have no "is_dropout" logic
        player.participant.optInConsent = 1

        return dict(optInConsent=player.participant.optInConsent)

    @staticmethod
    def before_next_page(player, timeout_happened):
        print('seeHear ', player.seeHear)
        print('attentionCheck ', player.attentionCheck)
        print('correctBackground ', player.correctBackground)


# class VVC(Page):
#     form_model = 'player'
#     timeout_seconds = 540
#     form_fields = ['seeHear', 'treatmentNumber','attentionCheck'] # TODO: Frage Warum ist hier seeHear?
#
#     @staticmethod
#     def vars_for_template(player: Player):
#         optInConsent = player.participant.vars['optInConsent']
#
#         if 'is_dropout' in player.participant.vars:
#             is_dropout = player.participant.vars['is_dropout']
#         else:
#             is_dropout = False
#         return dict(optInConsent=optInConsent,  # TODO: Brauche ich den optInConsent? Habe ich den?
#                     is_dropout=is_dropout)


page_sequence = [
    WaitPageGroup,
    HeartBeat,
    # MyPage0,
    # MyPage,
    # WaitPage3,
    # MyPage2,

    #VideoMeetingTest,
]
