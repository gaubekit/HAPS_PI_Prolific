from otree.api import *
import math
import time

c = cu
doc = ('''

This App contains
- social value orientation and general mental model
- main video meeting preferences
- Introduction to Spider Graph and WOOP

''')


class C(BaseConstants):
    NAME_IN_URL = 'App01'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    # Social Value Orientation
    svo_values = dict(
        # Primary I
        C11=[85, 85, 85, 85, 85, 85, 85, 85, 85],  # you
        C21=[85, 76, 68, 59, 50, 41, 33, 24, 15],  # other

        # Primary II
        C12=[85, 87, 89, 91, 93, 94, 96, 98, 100],  # you
        C22=[15, 19, 24, 28, 33, 37, 41, 46, 50],  # other

        # Primary III
        C13=[50, 54, 59, 63, 68, 72, 76, 81, 85],  # you
        C23=[100, 98, 96, 94, 93, 91, 89, 87, 85],  # other

        #  Primary IV
        C14=[50, 54, 59, 63, 68, 72, 76, 81, 85],  # you
        C24=[100, 89, 79, 68, 58, 47, 36, 26, 15],  # other

        # Primary V
        C15=[100, 94, 88, 81, 75, 69, 63, 56, 50],  # you
        C25=[50, 56, 63, 69, 75, 81, 88, 94, 100],  # other

        # Primary IV
        C16=[100, 98, 96, 94, 93, 91, 89, 87, 85],  # you
        C26=[50, 54, 59, 63, 68, 72, 76, 81, 85],  # other


        # # Example used for picture (screenshot) in SVO Introduction
        # C17=[30, 35, 40, 45, 50, 55, 60, 65, 70],  # you
        # C27=[80, 70, 60, 50, 40, 30, 20, 10, 0],  # other

    )


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    # Social Value Orientation
    q1_svo = models.IntegerField()
    q2_svo = models.IntegerField()
    q3_svo = models.IntegerField()
    q4_svo = models.IntegerField()
    q5_svo = models.IntegerField()
    q6_svo = models.IntegerField()
    svo_to_self = models.FloatField()
    svo_to_other = models.FloatField()
    svo_ratio = models.FloatField()
    svo = models.FloatField()
    svo_angle = models.FloatField()
    svo_type = models.StringField()

    # General Mental Model
    collaborative_goal = models.IntegerField(
        widget=widgets.RadioSelect,
        choices=[-3, -2, -1, 0, 1, 2, 3]
    )
    collaboration_expectations = models.IntegerField(
        widget=widgets.RadioSelect,
        choices=[-3, -2, -1, 0, 1, 2, 3]
    )

    # Video Meeting Behavior Preferences
    ## In vide meetings, it is imortant for me...

    ## ..to perform well, make valuable contributions, and be recognized for my efforts.
    vm_achievement = models.IntegerField(widget=widgets.RadioSelect, choices=[-3, -2, -1, 0, 1, 2, 3]) # Success and Recognition

    ## ..to take a leading role, direct the meetings agenda and shape decision
    vm_power_dominance = models.IntegerField(widget=widgets.RadioSelect, choices=[-3, -2, -1, 0, 1, 2, 3]) # Leading the Meeting

    ## ..to appear competent and avoid embarrassment or loss of status.
    vm_face = models.IntegerField(widget=widgets.RadioSelect, choices=[-3, -2, -1, 0, 1, 2, 3]) # Positive Public Image

    ## ..to respect formal rules, roles, and formal obligations.
    vm_conformity_rules = models.IntegerField(widget=widgets.RadioSelect, choices=[-3, -2, -1, 0, 1, 2, 3]) # Rules and Obligations

    ## ..to treat all participants equally, regardless of their role or seniority offer the same opportunities to contribute.
    vm_universalism_concern = models.IntegerField(widget=widgets.RadioSelect, choices=[-3, -2, -1, 0, 1, 2, 3]) # Fairness and Justice

    ## ..to actively listen to all participants and respect their viewpoints, regardless of different perspectives, values, and backgrounds
    vm_universalism_tolerance = models.IntegerField(widget=widgets.RadioSelect, choices=[-3, -2, -1, 0, 1, 2, 3]) # Diversity and Inclusion


# PAGES


class IntroSVO(Page):
    """ This page introduces the Social Value Orientation"""
    pass  # no additional logic needed


class SurveySVO(Page):
    """ This Page Measures the Social Value Orientation and Calculates all Values"""
    form_model = 'player'
    form_fields = ['q1_svo', 'q2_svo', 'q3_svo', 'q4_svo', 'q5_svo', 'q6_svo']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            **C.svo_values
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        """ calculating svo ratio, angle and type """
        svo_values = C.svo_values

        # calculating SVO angle
        player.svo_to_self = (svo_values['C11'][player.q1_svo - 1] +
                           svo_values['C12'][player.q2_svo - 1] +
                           svo_values['C13'][player.q3_svo - 1] +
                           svo_values['C14'][player.q4_svo - 1] +
                           svo_values['C15'][player.q5_svo - 1] +
                           svo_values['C16'][player.q6_svo - 1]) / 6

        player.svo_to_other = (svo_values['C21'][player.q1_svo - 1] +
                            svo_values['C22'][player.q2_svo - 1] +
                            svo_values['C23'][player.q3_svo - 1] +
                            svo_values['C24'][player.q4_svo - 1] +
                            svo_values['C25'][player.q5_svo - 1] +
                            svo_values['C26'][player.q6_svo - 1]) / 6

        player.svo_ratio = (player.svo_to_other - 50) / (player.svo_to_self - 50)
        player.svo_angle = math.degrees(math.atan(player.svo_ratio))

        # SVO-angle to svo-category (altruism, prosocial, individualistic, competitive)
        if player.svo_ratio >= 1.5488:
            player.svo = 1
            player.svo_type = 'Altruism'
        elif 0.441 < player.svo_ratio < 1.5488:
            player.svo = 2
            player.svo_type = 'Prosocial'
        elif -0.213 <= player.svo_ratio <= 0.441:
            player.svo = 3
            player.svo_type = 'Individualistic'
        elif player.svo_ratio < -0.213:
            player.svo = 4
            player.svo_type = 'Competitive'

        player.participant.svo_to_self = round(player.svo_to_self, 2)
        player.participant.svo_to_other = round(player.svo_to_other, 2)


class MentalModel(Page):
    """ This Page assesses the mental model -> Expectations VS Goal"""
    form_model = 'player'
    form_fields = ['collaborative_goal', 'collaboration_expectations']


class VideoMeetingBehaviorI(Page):
    """ This is the first part of rating video meeting preferences"""

    form_model = 'player'
    form_fields = ['vm_achievement', 'vm_power_dominance', 'vm_face',
                   'vm_conformity_rules', 'vm_universalism_concern', 'vm_universalism_tolerance']

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.participant.vm_pref_achievement = player.vm_achievement
        player.participant.vm_pref_dominance = player.vm_power_dominance
        player.participant.vm_pref_face = player.vm_face
        player.participant.vm_pref_rules = player.vm_conformity_rules
        player.participant.vm_pref_concern = player.vm_universalism_concern
        player.participant.vm_pref_tolerance = player.vm_universalism_tolerance

        # initialize predefined goal labels as session variable for use in Spider Graph
        player.session.vm_goal_labels = [
            ['Success and Recognition', ' '],
            ['   Leading', '       the', '   Meeting'],
            ['      Positive', '   Public Image'],
            [' ', 'Rules and Obligations'],
            ['Fairness   ', 'and       ', 'Justice    '],
            ['Diversity   ', 'and       ', 'Inclusion   ']
        ]  # Note: White spaces and lists are used as workaround for text-"centering"

        # initialize predefined goal descriptions as session variable for use in Spider Graph
        player.session.vm_goal_description = [
            # Success and Recognition
            # 'In video meetings, it is important to perform well, make valuable contributions, and be recognized for efforts',
            'perform well, make valuable contributions, and be recognized for efforts',

            # Leading the Meeting
            # 'In video meetings, it is important to take a leading role, direct the meetings agenda and shape decisions',
            'take a leading role, direct the meetings agenda and shape decisions',

            # Positive Public Image
            # 'In video meetings, it is important to appear competent and avoid embarrassment or loss of status',
            'appear competent and avoid embarrassment or loss of status',

            # Rules and Obligations
            # 'In video meetings, it is important to respect formal rules, roles, and formal obligations',
            'respect formal rules, roles, and formal obligations',

            # Fairness and Justice
            # 'In video meetings, it is important to treat all participants equally, regardless of their role or seniority',
            'treat all participants equally, regardless of their role or seniority',

            # Diversity and Inclusion
            # 'In video meetings, it is important to actively listen and respect all viewpoints, regardless of background',
            'actively listen and respect all viewpoints, regardless of background',
        ]


class IntroductionSpiderGraph(Page):
    """ This Page introduces the Spider Graph with the own Video Meeting Goals"""
    form_model = 'player'

    @staticmethod
    def js_vars(player):
        return dict(
            own=[player.participant.vm_pref_achievement,
                 player.participant.vm_pref_dominance,
                 player.participant.vm_pref_face,
                 player.participant.vm_pref_rules,
                 player.participant.vm_pref_concern,
                 player.participant.vm_pref_tolerance],
        )

    @staticmethod
    def before_next_page(player, timeout_happened):
        """
        This methode provides participant-var for the next app

            - store arrival time at the waite page (first page in next app) # TODO weg
        - define a flag for single player = False, used to flag players that form no group or can't continue
        - define a flag indicating whether the participant formed a team
        - define var to track additional wait time in rolling matching
            - confirmed meeting? # todo weg
        - define flag indicating whether this particular player raised the dropout
        - define flag indicating whether video_meeting_successful
        """

        # player.participant.wait_page_arrival = time.time() # TODO vermutlich outdated
        player.participant.single_player = False
        player.participant.assigned_to_team = False
        player.participant.additional_wait_time = 0
        # player.participant.confirmed_meeting = False # TODO: kann glaube ich weg
        player.participant.raised_dropout = False
        player.participant.vm_success = False


page_sequence = [
    IntroSVO,
    SurveySVO,
    MentalModel,
    VideoMeetingBehaviorI,
    IntroductionSpiderGraph,
]
