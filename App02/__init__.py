from otree.api import *
import random

c = cu

doc = ("""

This App handel Stage 2, where 3 participants formed a team:
- Treatment A: Spider Graph
- Treatment B: Spider Graph + Mental Contrasting (MC)


- 7 min video meeting
    + 2min upload time
    + Questionnaire 1/3: SeeHear, Background, Human
- Questionnaire 2/3: Nasa TLX, Zoom Fatigue & Exhaustion
- Intro Weakest Link Game (WLG)
- Comprehension WLG
- Decision WLG (One-Shot)
- Questionnaire 3/3: Mental Model (compare with initial answer) + decision reasoning (Spider Graph, MC, Video Meeting)


Players only arrive in this app, if it was possible to form a team. (flag "assigned_to_team" = True)
The initial wait saves the player codes of the group members and calculates payoff_bonus_svo
    -> upd. payoff_total = payoff_fix + payoff_bonus_svo + payoff_compensation_wait

Dropout Handling I:
    - Guarantee that the video meeting completes (only situation where the participants interact in realtime)
    - OnPage-Timer and WaitPages control the "experiment" that participants proceed in the same pase
    -  if timeout happens -> all players are tagged as "single_player" and forwarded to Stage 3
                          -> the participant who raised the timeout is tagged as "raised_timeout" and
                             get no compensation for Stage 2 (calculated at the end of Stage 3)
                          -> the other two will be compensated with 150 ECU (3 pound) (at the end of Stage 3)
                          
Dropout Handling II:
    - Once participants completed the video meeting -> no live interaction anymore
    - no OnPage-Timer and no WaitPages -> pace is not controlled after WaitPage3
    - On the very last page of Stage 3 player code of group members will checked for WLG Decision
        -> if decision made by all players: calculate payoff_bonus_wlg
        -> else: payoff_bonus_wlg = 0; payoff_compensation_wlg_dropout = 150 ECU
        
""")


class C(BaseConstants):
    NAME_IN_URL = 'App02'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 1

    # Central configuration of duration Video Meeting and Upload Time Limit
    VM_DURATION = 3 * 60  # TODO 7 minutes
    VM_UPLOAD_DURATION = 2 * 60  # TODO 2 minutes


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
     pass


class Player(BasePlayer):
    # Var to control Video Meeting Behavior: 1 -> no modification, 2 -> no self-view, 3 -> additional message above
    # Note: not used in this study -> hardcoded '1' = no modification
    video_meeting_behavior = models.IntegerField(initial=1, blank=True)

    # Var for Treatment
    treatment_completed = models.StringField(initial='no')

    # Var to ensure that Video Meeting worked properly
    seeHear = models.IntegerField(blank=True, choices=[[0, '0'], [1, '1'], [2, '2']], label='',
                                  attrs={"invisible": True}, default=2)

    attentionCheck = models.IntegerField(blank=True, choices=[[0, '0'], [1, '1']], label='',
                                         attrs={"invisible": True}, default=0)

    correctBackground = models.IntegerField(blank=True, choices=[[0, '0'], [1, '1']], label='',
                                            attrs={"invisible": True}, default=0)

    # Decisions in Weakest Link game
    wlg_decision = models.IntegerField(
        choices=[0, 10, 20, 30, 40],
        label='',
        widget=widgets.RadioSelect,
    )

    # Decision Post Questionnaire -> what influenced the decision
    impact_goal = models.IntegerField(widget=widgets.RadioSelect, choices=[-3, -2, -1, 0, 1, 2, 3])
    impact_expectation = models.IntegerField(widget=widgets.RadioSelect, choices=[-3, -2, -1, 0, 1, 2, 3])
    impact_spider_graph = models.IntegerField(widget=widgets.RadioSelect, choices=[-3, -2, -1, 0, 1, 2, 3])
    impact_video_meeting = models.IntegerField(widget=widgets.RadioSelect, choices=[-3, -2, -1, 0, 1, 2, 3])
    impact_woop = models.IntegerField(widget=widgets.RadioSelect, choices=[-3, -2, -1, 0, 1, 2, 3])

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
        label='<b>You contribute 0 hours and the minimum contribution by any team member is 10 hours:</b>', min=0, max=400)
    comprehension2 = models.IntegerField(
        label='<b>You contribute 20 hours and the minimum contribution by any team member is 10 hours:</b>', min=0, max=400)
    comprehension3 = models.IntegerField(
        label='<b>You contribute 40 hours and the minimum contribution by any team member is 30 hours:</b>', min=0, max=400)
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

# HELP FUNCTIONS
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

class MyWaitPage(WaitPage):
    """
    Page grouping participants by arrival time. Because App01_waiting guarantees for exact 3 active participants,
    we can simply use "group_by_arrival_time"
    """

    # Note: players can't get stuck on a wait page, if the previous page has a time_out functionallity
    # This case is special, theoretically 3 player should be automatically forwarded - but is there a chance to
    # set a timeout on this page?: https://otree.readthedocs.io/en/latest/multiplayer/waitpages.html#use-group-by-arrival-time
    # TODO def wait_too_long -> 30 secondes and def group_by_arrival_time_method(subsession, waiting_players)

    group_by_arrival_time = True

    @staticmethod
    def after_all_players_arrive(group: Group):
        """
            - store code of team members in participant field
            - select one of the others for svo by random
            - update payoff_bonus_svo
            - update payoff_total
        """
        # for all players in the group
        for p in group.get_players():
            print('this is player: ', p)
            # store the id's (code) of the other group members in a participant field "other_players_ids"
            p.participant.other_players_ids = [pl.participant.code for pl in p.get_others_in_group()]

            try:
                # get randomly the code of one group member
                the_other_id = random.choice(p.participant.other_players_ids)

                # and search this participant in the session to get his svo
                for other in group.session.get_participants():
                    if other.code == the_other_id:
                        svo_from_other = other.svo_to_other
                        break

            except IndexError:
                # no other -> no var "svo_from_other" --> NameError in next block
                pass

            try:
                p.participant.svo_from_other = svo_from_other
                # update payoff_bonus_svo
                p.participant.payoff_bonus_svo = round(svo_from_other + p.participant.svo_to_self, 2)
                print('SVO from other', svo_from_other, '\nSVO to self', p.participant.svo_to_self,
                      '\nSVO to other', p.participant.svo_to_other,)

                # updated payoff_total
                p.participant.payoff_total = (
                        p.participant.payoff_fix
                        + p.participant.payoff_bonus_svo
                        + p.participant.payoff_compensation_wait
                )
                print('payoff svo: ', p.participant.payoff_bonus_svo)
                print('payoff waiting: ', p.participant.payoff_compensation_wait)
                print('payoff total: ', p.participant.payoff_total)
            except NameError:
                svo_from_other = 0
                print('Error: The Other had no svo_to_other')


class InformOnScreenTimer(Page):
    @staticmethod
    def get_timeout_seconds(player):
        if player.participant.single_player:
            return 1
        else:
            return 5*60

    @staticmethod
    def before_next_page(player, timeout_happened):
        print("timeout_happened is true: ", player.participant.code)
        if timeout_happened:
            player.participant.single_player = True


class WaitPage1(WaitPage):
    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        for p in player.group.get_players():
            if p.participant.single_player:
                return 'App03'
        return None


class TreatmentA(Page):
    """
    This page handles one of two treatments, and therefore includes:
        - visualize personal and team-averaged Playground goals

    The treatment is handled via control-variable and an is_displayed staticmethod

    """
    pass  # TODO: Update after Treatment B is i.o.


class TreatmentB(Page):  # TODO add WOOP
    """
        This page handles one of two treatments, and therefore includes:
            - visualize personal and team-averaged Playground goals
            - Mental Contrasting

        The treatment is handled via control-variable and a is_displayed staticmethod# TODO

    """
    form_model = 'player'

    # @staticmethod
    # def is_displayed(player):
    #     return player.participant.treatment == 'WOOP'

    @staticmethod
    def js_vars(player):
        others = player.get_others_in_subsession()
        others_vm_pref = [
            (others[0].participant.vm_pref_achievement + others[1].participant.vm_pref_achievement) / 2,
            (others[0].participant.vm_pref_dominance + others[1].participant.vm_pref_dominance) / 2,
            (others[0].participant.vm_pref_face + others[1].participant.vm_pref_face) / 2,
            (others[0].participant.vm_pref_rules + others[1].participant.vm_pref_rules) / 2,
            (others[0].participant.vm_pref_concern + others[1].participant.vm_pref_concern) / 2,
            (others[0].participant.vm_pref_tolerance + others[1].participant.vm_pref_tolerance) / 2,
            ]

        player.participant.others_vm_pref = others_vm_pref

        return dict(
            own=[player.participant.vm_pref_achievement,
                 player.participant.vm_pref_dominance,
                 player.participant.vm_pref_face,
                 player.participant.vm_pref_rules,
                 player.participant.vm_pref_concern,
                 player.participant.vm_pref_tolerance],
            other=others_vm_pref
        )


    # @staticmethod # TODO ACTIVATE, is deactivated for testing reasons
    # def get_timeout_seconds(player):
    #     if player.participant.single_player:
    #         return 1
    #     else:
    #         return 5*60
    #
    # @staticmethod
    # def before_next_page(player, timeout_happened):
    #     if timeout_happened:
    #         player.participant.single_player = True


class WaitPage2(WaitPage):
    """
        This Page ensures that all participants arrive to the same time on the video meeting page and the dropout time
        starts simultaneously. If a dropout happens, all group-members will be forwarded to Stage 3
    """
    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        for p in player.group.get_players():
            if p.participant.single_player:
                # if one of the others is a single player, all in the group are flagged as single player
                player.participant.single_player = True

        if player.participant.single_player:
            return 'App03'
        return None


class VideoMeeting(Page):
    # Note: I added global.css, Picture_Camera.jpg and Picture_Microphone.jpg to _static
    form_model = 'player'
    timeout_seconds = C.VM_DURATION + C.VM_UPLOAD_DURATION   # 540 7min VM + 2min upload/Questionnaire
    form_fields = ['seeHear', 'correctBackground', 'attentionCheck', 'video_meeting_behavior']

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

        if not player.attentionCheck:
            print('player raised dropout by not indicating that he is human')
            player.participant.single_player = True
            player.participant.raised_dropout = True

        elif not player.seeHear:
            print('could not seeHear others')
            player.participant.single_player = True


class VideoMeeting_dummy(Page):
    # Note: I added global.css, Picture_Camera.jpg and Picture_Microphone.jpg to _static
    form_model = 'player'
    timeout_seconds = C.VM_UPLOAD_DURATION
    form_fields = ['seeHear', 'correctBackground', 'attentionCheck', 'video_meeting_behavior']

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

        if not player.attentionCheck:
            print('player raised dropout by not indicating that he is human')
            player.participant.single_player = True
            player.participant.raised_dropout = True

        elif not player.seeHear:
            print('could not seeHear others')
            player.participant.single_player = True


class WaitPage3(WaitPage):
    """
        Three active players joining the Video Meeting at the same time (WaitPage2). They are automatically
        forwarded after C.VM_DURATION + C.VM_UPLOAD_DURATION, landing on this Page.
        If a player do not confirm that he is "human", this players will be labeled as "raised_dropout"
        and as "single_player" in the before_next_page methode. Also, players date do not seeHear  all others are
        labeled as "single_player"

        Therefore, this WaitPage have only to check whether someone in the group was labeled as single player.
        In this case, all players of the group are labeled as single player and forwarded to Stage 3.
    """

    @staticmethod
    def after_all_players_arrive(group):
        """ Check whether one of the players was labeled as single player. If so, all are labeled as single player """
        if any(p.participant.single_player for p in group.get_players()):
            for p in group.get_players():
                p.participant.single_player = True
        # else: # TODO
        #     # if the group number is equal, the treatment "woop" was completed
        #     if group.id_in_session % 2:  # TODO: is this working?
        #         for p in group.get_players():
        #             p.player.treatment_completed = 'woop'
        #     else:
        #         for p in group.get_players():
        #             p.player.treatment_completed = 'no_woop'

    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        """ In case of dropout, all players skip the Weakest Link game and continue with Stage 3 """
        if player.participant.single_player:
            return 'App03'
        return None


class PostVideoMeetingQuestionnaireII(Page):
        """
            2 Items of Nasa-TLX (as in joint study) and 6 items Zoom Fatigue & Exhaustion (ZFE) Questionnaire

            # Social Fatigue domain from ZFE-Scale | not at all - slightly - moderately - very - extremely (5)
            ## How much do you tend to avoid social situations after this video conference?
            ## How much do you want to be alone after this video conference?
            ## How much do you need time by yourself after this video conference?

            # Mental Fatigue domain from ZFE-Scale
            ## How much do you dread having to do things after this video conference?
            ## How much do you feel like doing nothing after this video conference?
            ## How much do you feel too tired to do other things after this video conference?
        """
        form_model = 'player'
        form_fields = ['nasatlx_1', 'nasatlx_2', 'zfe_social_1', 'zfe_social_2',
                       'zfe_social_3', 'zfe_general_1', 'zfe_general_2', 'zfe_general_3']


class IntroWLG(Page):
    form_model = 'player'


class ComprehensionWLG(Page):
    form_model = 'player'
    form_fields = ['comprehension1', 'comprehension2',
                   'comprehension3', 'comprehension4a',
                   'comprehension4b', 'comprehension4c']


class DecisionWLG(Page):
    form_model = 'player'
    form_fields = ['wlg_decision']

    @staticmethod
    def before_next_page(player, timeout_happened):
        """ Save decision in participant field. Calculation is done in App03/SurveyPVQ6 before_next_page() """
        print('WLG own decision: ', player.wlg_decision)
        player.participant.wlg_own_choice = player.wlg_decision


class PostCoordinationQuestionnaire(Page):
    form_model = 'player'
    form_fields = ['impact_goal', 'impact_expectation', 'impact_spider_graph', 'impact_video_meeting', 'impact_woop']


class MyPage(Page):  # TODO: only for testing reasons
    form_model = 'player'


page_sequence = [
    MyWaitPage,
    InformOnScreenTimer,
    WaitPage1,
    # Treatment A, # TODO
    TreatmentB,
    # MyPage,  # TODO: only a page for test reasons -> skip TreatmentB
    WaitPage2,
    VideoMeeting_dummy,  # TODO
    # VideoMeeting,  # TODO
    # WaitPage3,
    PostVideoMeetingQuestionnaireII,
    IntroWLG,
    ComprehensionWLG,
    DecisionWLG,
    PostCoordinationQuestionnaire,
]
