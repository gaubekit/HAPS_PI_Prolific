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

    # Portrait Value Questionnaire
    # q1 = make_6_point_likert_skale('It is important to him/her to form his/her views independently.')
    # q2 = make_6_point_likert_skale('It is important to him/her that his/her country is secure and stable.')
    # q3 = make_6_point_likert_skale('It is important to him/her to have a good timeslots.')
    # q4 = make_6_point_likert_skale('It is important to him/her to avoid upsetting other people.')
    # q5 = make_6_point_likert_skale('It is important to him/her that the weak and vulnerable in society be protected.')
    # q6 = make_6_point_likert_skale('It is important to him/her that people do what he/she says they should.')
    # q7 = make_6_point_likert_skale('It is important to him/her never to think he/she deserves more than other people.')
    # q8 = make_6_point_likert_skale('It is important to him/her to care for nature.')
    # q9 = make_6_point_likert_skale('It is important to him/her that no one should ever shame him/her.')
    # q10 = make_6_point_likert_skale('It is important to him/her always to look for different things to do.')

    ## 13 It is important to him/her to form his/her views independently.
    pvq1 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])


    # Nasa TLX, Zoom Fatigue & Exhaustion Subscale Social and General
    ## How mentally demanding was this video conference task?
    nasatlx_1 = models.IntegerField(widget=widgets.RadioSelect, choices=list(range(-10, 11)))
    ## How hurried or rushed was the pace of this video conference?
    nasatlx_2 = models.IntegerField(widget=widgets.RadioSelect, choices=list(range(-10, 11)))
    ## How much do you tend to avoid social situations after this video conference?
    zfe_social_1 = models.IntegerField(widget=widgets.RadioSelect, choices=list(range(-10, 11)))
    ## How much do you want to be alone after this video conference?
    zfe_social_2 = models.IntegerField(widget=widgets.RadioSelect, choices=list(range(-10, 11)))
    ## How much do you need time by yourself after this video conference?
    zfe_social_3 = models.IntegerField(widget=widgets.RadioSelect, choices=list(range(-10, 11)))
    ## How much do you dread having to do things after this video conference?
    zfe_general_1 = models.IntegerField(widget=widgets.RadioSelect, choices=list(range(-10, 11)))
    ## How much do you feel like doing nothing after this video conference?
    zfe_general_2 = models.IntegerField(widget=widgets.RadioSelect, choices=list(range(-10, 11)))
    ## How much do you feel too tired to do other things after this video conference?
    zfe_general_3 = models.IntegerField(widget=widgets.RadioSelect, choices=list(range(-10, 11)))

    # Comprehension Weakest Link Game
    comp1_check = models.IntegerField(initial=0)
    comp2_check = models.IntegerField(initial=0)
    comp3_check = models.IntegerField(initial=0)
    comp4_check = models.IntegerField(initial=0)
    comprehension1 = models.IntegerField(
        label='<br><strong>What would be your compensation if you work 0 hours on the team project '
              'and the lowest contribution of a team member to the team project is 10 hours?</strong>', min=0, max=400)
    comprehension2 = models.IntegerField(
        label='<br><strong>What would be your compensation if you work 20 hours on the team project '
              'and the lowest contribution of a team member to the team project is 10 hours?</strong>', min=0, max=400)
    comprehension3 = models.IntegerField(
        label='<br><strong>What would be your compensation if you work 40 hours on the team project '
              'and the lowest contribution of a team member to the team project is 30 hours?</strong>', min=0, max=400)
    comprehension4a = models.BooleanField(
        default=False,
        label='',
        widget=widgets.CheckboxInput,
        blank=True
    )
    comprehension4b = models.BooleanField(
        default=False,
        label='',
        widget=widgets.CheckboxInput,
        blank=True
    )
    comprehension4c = models.BooleanField(
        default=False,
        label='',
        widget=widgets.CheckboxInput,
        blank=True)


# Functions for error messages in comprehension questions
def comprehension1_error_message(player: Player, value):
    if value != 200:
        player.comp1_check += 1
        if player.comp1_check == 1:
            return "Unfortunately, that's incorrect. Please try again."
        if player.comp1_check >= 2:
            return "Unfortunately, that's incorrect. The correct answer is <strong>200</strong>."
    return None  # Allow the participant to try again if they haven't clicked incorrectly twice


def comprehension2_error_message(player: Player, value):
    if value != 200:
        player.comp2_check += 1
        if player.comp2_check == 1:
            return "Unfortunately, that's incorrect. Please try again."
        elif player.comp2_check >= 2:
            return "Unfortunately, that's incorrect. The correct answer is <strong>200</strong>."
    return None


def comprehension3_error_message(player: Player, value):
    if value != 300:
        player.comp3_check += 1
        if player.comp3_check == 1:
            return "Unfortunately, that's incorrect. Please try again."
        elif player.comp3_check >= 2:
            return "Unfortunately, that's incorrect. The correct answer is <strong>300</strong>."
    return None


def comprehension4a_error_message(player: Player, value):
    if not value:
        player.comp4_check += 1
        if player.comp4_check == 1:
            return "Unfortunately, that's incorrect. Please try again."
        elif player.comp4_check >= 2:
            return "Unfortunately, that's incorrect. Your compensation depends on the <strong>number of hours you work on the team project</strong> and the <strong>fewest number of hours worked by a member of your team on the team project</strong>."
    return None


def comprehension4b_error_message(player: Player, value):
    if value:
        player.comp4_check += 1
        if player.comp4_check == 1:
            return "Unfortunately, that's incorrect. Please try again."
        elif player.comp4_check >= 2:
            return "Unfortunately, that's incorrect. Your compensation depends on the <strong>number of hours you work on the team project</strong> and the <strong>fewest number of hours worked by a member of your team on the team project</strong>."
    return None


def comprehension4c_error_message(player: Player, value):
    if not value:
        player.comp4_check += 1
        if player.comp4_check == 1:
            return "Unfortunately, that's incorrect. Please try again."
        elif player.comp4_check >= 2:
            return "Unfortunately, that's incorrect. Your compensation depends on the <strong>number of hours you work on the team project</strong> and the <strong>fewest number of hours worked by a member of your team on the team project</strong>."
    return None


# PAGES
class VideoMeeting(Page):  # TODO: The Next Button should be only available, after completing the 7min video call
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


class SurveyPVQ1(Page):
    form_model = 'player'
    form_fields = ['pvq1',]


class VideoBlurr(Page):
    """ Just a test-page to handle the blurr in the frontend"""
    pass


class PostVideoMeetingQuestionnaireII(Page):
    """
        # Social Fatigue domain from ZEF-Scale | not at all - slightly - moderately - very - extremely (5)
        ## How much do you tend to avoid social situations after this video conference?
        ## How much do you want to be alone after this video conference?
        ## How much do you need time by yourself after this video conference?

        # Mental Fatigue domain from ZEF-Scale
        ## How much do you dread having to do things after this video conference?
        ## How much do you feel like doing nothing after this video conference?
        ## How much do you feel too tired to do other things after this video conference?

        # Emotional Fatigue domain from ZEF-Scale
        ## How emotionally drained do you feel after this video conference?
        ## How irritable do you feel after this video conference?
        ## How moody do you feel after this video conference?
    """
    form_model = 'player'
    form_fields = ['nasatlx_1', 'nasatlx_2', 'zfe_social_1', 'zfe_social_2',
                   'zfe_social_3', 'zfe_general_1', 'zfe_general_2', 'zfe_general_3']


class IntroWLG(Page):
    form_model = 'player'
    form_fields = ['comprehension1', 'comprehension2',
                   'comprehension3', 'comprehension4a',
                   'comprehension4b', 'comprehension4c']


page_sequence = [
    IntroWLG,
    # PostVideoMeetingQuestionnaireII,
    # SurveyPVQ1,
    # VideoMeeting,
    # VideoBlurr
]
