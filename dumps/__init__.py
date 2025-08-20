from otree.api import *
from otree.models import Participant
import random

c = cu

doc = ("""

This App handel Stage 2, where 3 participants formed a team:
- Treatment A: Spider Graph
- Treatment B: Spider Graph + Mental Contrasting (MC)


- 7 min video meeting
- Questionnaire 1/3: See / hear each other
- Questionnaire 2/3: Nasa TLX, Zoom Fatigue & Exhaustion
- Intro Weakest Link Game (WLG)
- Comprehension WLG
- Decision WLG (One-Shot)
- Questionnaire 3/3: Mental Model (compare with initial answer) + decision reasoning (Spider Graph, MC, Video Meeting)


Players only arrive in this app, if it was possible to form a team. 
The initial wait page saves the player objects and calculates payoff_bonus_svo
    -> upd. payoff_total = payoff_fix + payoff_bonus_svo + payoff_compensation_wait

Dropout handling I:
    - Guarantee that the video meeting completes (only situation where the participants interact in realtime)
    - OnPage-Timer and WaitPages control the "experiment" that participants proceed in the same pase
    -  if timeout happens -> all players are tagged as "single_player" and forwarded to Stage 3
                          -> the participant who raised the timeout get no compensation for stage 2
                          -> the other two will be compensated with 150 ECU (3 pound)
                          
Dropout handling II:
    - Once participants completed the video meeting -> no live interaction anymore
    - no OnPage-Timer and no WaitPages -> pace is not controlled
    - On the very last page of Stage 3 player objects of group members will checked for WLG Decision
        -> if decision made by all players: calculate payoff_bonus_wlg
        -> else: payoff_bonus_wlg = 0; payoff_compensation_wlg_dropout = 150 ECU
        
""")


class C(BaseConstants):
    NAME_IN_URL = 'App02'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 1
    ENDOWMENT = 200


class Subsession(BaseSubsession):
    pass


# TODO -> Clarify: do I need this?
class Group(BaseGroup):
    groupMin = models.IntegerField(
        min=0, max=40, initial=40
    )
    randomNumber = models.IntegerField()


def make_field(label):
    return models.IntegerField(
        choices=[0, 10, 20, 30, 40],
        label=label,
        widget=widgets.RadioSelect,
    )


class Player(BasePlayer):
    # Hardcoding treatment-number for VVC page -> we use only the "control-Method" version
    treatmentNumber = models.IntegerField(initial=0, blank=True)

    # Anujas version of see-hear
    seeHear = models.IntegerField(blank=True, choices=[[0, '0'], [1, '1'], [2, '2']], label='',
                                  attrs={"invisible": True}, default=2)
    attentionCheck = models.IntegerField(blank=True, choices=[[0, '0'], [1, '1']], label='',
                                         attrs={"invisible": True}, default=0)

    # my version of see-hear - not used right now
    see_others = models.BooleanField(
        default=False,
        blank=True,
        label='I was able to see the others',
        widget=widgets.CheckboxInput,
    )
    hear_others = models.BooleanField(
        default=False,
        blank=True,
        label='I was able to hear the others',
        widget=widgets.CheckboxInput,
    )

    good_quality = models.BooleanField(
        default=False,
        blank=True,
        label='The video meeting quality was good enough to participate in the conversation',
        widget=widgets.CheckboxInput,
    )

    wlg_decision = make_field("Please choose one")
    payoff_hypo_subround1 = models.IntegerField()

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

class MyWaitPage(WaitPage):     # TODO -> clarify: do we need "dropout logic"?
    """
    Page grouping participants by arrival time. Because App01_waiting guarantees for exact 3 active participants,
    we can simply use "group_by_arrival_time"
    """

    group_by_arrival_time = True

    @staticmethod
    def after_all_players_arrive(group: Group):
        """
        - store code of team members in participant field
        - select one of the others for svo by random
        - calculate payoff_bonus_svo
        - update payoff_total
        """
        # for all players in the group
        for p in group.get_players():
            print('this is player: ', p)
            # store the id's (code) of the other group members in a participant field "other_players_ids"
            p.participant.other_players_ids = [pl.participant.code for pl in p.get_others_in_group()]
            # get randomly the code of one group member
            the_other_id = random.choice(p.participant.other_players_ids)
            p.participant.the_other_id = the_other_id

            # and search this participant in the session to get his svo
            for other in group.session.get_participants():
                if other.code == the_other_id:
                    svo_from_other = other.svo_to_other
                    break
            try:
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
        if timeout_happened:
            player.participant.single_player = True


class WaitPage1(WaitPage):
    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        for p in player.group.get_players():
            if p.participant.single_player:
                return 'App03'
        return None


class TreatmentA(Page):  # TODO: Update after Treatment B is i.o.
    pass
    # """
    # This page handles one of two treatments, and therefore includes:
    #     - visualize personal and team-averaged Playground goals
    #
    # The treatment is handled via control-variable and a is_displayed staticmethod# TODO
    #
    # """
    # form_model = 'player'
    #
    # @staticmethod
    # def js_vars(player):
    #     others = player.get_others_in_subsession()
    #     others_vm_pref = [
    #         (others[0].participant.vm_pref_achievement + others[1].participant.vm_pref_achievement) / 2,
    #         (others[0].participant.vm_pref_dominance + others[1].participant.vm_pref_dominance) / 2,
    #         (others[0].participant.vm_pref_face + others[1].participant.vm_pref_face) / 2,
    #         (others[0].participant.vm_pref_rules + others[1].participant.vm_pref_rules) / 2,
    #         (others[0].participant.vm_pref_concern + others[1].participant.vm_pref_concern) / 2,
    #         (others[0].participant.vm_pref_tolerance + others[1].participant.vm_pref_tolerance) / 2,
    #         ]
    #
    #     player.participant.others_vm_pref = others_vm_pref
    #
    #     return dict(
    #         own=[player.participant.vm_pref_achievement,
    #              player.participant.vm_pref_dominance,
    #              player.participant.vm_pref_face,
    #              player.participant.vm_pref_rules,
    #              player.participant.vm_pref_concern,
    #              player.participant.vm_pref_tolerance],
    #         other=others_vm_pref
    #     )
    #
    # @staticmethod
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


class TreatmentB(Page): # TODO add WOOP
    """
    This page handles one of two treatments, and therefore includes:
        - visualize personal and team-averaged Playground goals
        - Mental Contrasting

    The treatment is handled via control-variable and a is_displayed staticmethod# TODO

    """
    form_model = 'player'

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


# class VideoMeeting(Page):
#     """
#     This page gives instructions about the VideoMeeting,
#     asks for consent (do not speak about personal goals or intended behavior)
#     and enables the video meeting (jitsi) after all players has agreed
#     """
#     @staticmethod
#     def live_method(player, data):
#         player.video_ready = data
#         all_ready = all(p.video_ready for p in player.group.get_players())
#         print(all_ready)
#         return {0: all_ready}
#
#     # TODO: activate timeout code
#     # @staticmethod
#     # def get_timeout_seconds(player):
#     #     if player.participant.single_player:
#     #         return 1
#     #     else:
#     #         return 9 * 60 # 7min video meeting + 2 min puffer for joining (same as in mega-study)
#     #
#     # @staticmethod
#     # def before_next_page(player, timeout_happened):
#     #     if timeout_happened:
#     #         player.participant.single_player = True






class VVC(Page):
    # Note: I added global.css, Picture_Camera.jpg and Picture_Microphone.jpg to _static ..srsly, why coding this dirty? :(
    form_model = 'player'
    timeout_seconds = 540
    form_fields = ['seeHear', 'treatmentNumber', 'attentionCheck']

    @staticmethod
    def vars_for_template(player: Player):
        # TODO: Hardcoded for testing, because optInConsent is written in App01 and I have no "is_dropout" logic
        player.participant.optInConsent = 1

        return dict(optInConsent=player.participant.optInConsent, is_dropout=False)

    # TODO: Fragen ob alle anderen einen background aktiviert hatten












class PostVideoMeetingQuestionnaireI(Page):  # TODO This was replaced by the functionality in VVC -> How to Control for dropout?
    form_model = 'player'
    form_fields = ['see_others', 'hear_others', 'good_quality']

    @staticmethod
    def get_timeout_seconds(player):
        if player.participant.single_player:
            return 1
        else:
            return 5 * 60

    @staticmethod
    def before_next_page(player, timeout_happened):
        if timeout_happened or not player.see_others or not player.hear_others or not player.good_quality:
            player.participant.single_player = True


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

            # Emotional Fatigue domain from ZEF-Scale - Note: not incorporated
            ## How emotionally drained do you feel after this video conference?
            ## How irritable do you feel after this video conference?
            ## How moody do you feel after this video conference?
        """
        form_model = 'player'
        form_fields = ['nasatlx_1', 'nasatlx_2', 'zfe_social_1', 'zfe_social_2',
                       'zfe_social_3', 'zfe_general_1', 'zfe_general_2', 'zfe_general_3']


class WaitPage3(WaitPage):
    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        for p in player.group.get_players():
            if p.participant.single_player:
                # if one of the others is a single player, all in the group are flagged as single player
                player.participant.single_player = True

        if player.participant.single_player:
            return 'App03'
        return None


class IntroWLG(Page):
    form_model = 'player'


class ComprehensionWLG(Page):
    form_model = 'player'
    form_fields = ['comprehension1', 'comprehension2',
                   'comprehension3', 'comprehension4a',
                   'comprehension4b', 'comprehension4c']


class DecisionWLG(Page):  # TODO: Adjust instructions etc
    form_model = 'player'
    form_fields = ['wlg_decision']

    @staticmethod
    def is_displayed(player):
        return player.participant.assigned_to_team

    @staticmethod
    def live_method(player: Player, data):
        if "wlg_decision" in data:
            player.wlg_decision = data["wlg_decision"]

    @staticmethod
    def vars_for_template(player: Player):
        return dict(round_num=player.round_number)

    # TODO add logic for payoff structure and droput
    # @staticmethode
    # def before_next_page(player, timeout_happened
    #    pass


class PostCoordinationQuestionnaire(Page):
    form_model = 'player'
    form_fields = ['impact_goal', 'impact_expectation','impact_spider_graph','impact_video_meeting','impact_woop']

########### old pages #############
#
# class Description1(Page):
#     @staticmethod
#     def is_displayed(player):
#         return player.participant.assigned_to_team
#
#

#
#
# class CalculatePayoff1(WaitPage):
#     body_text = "Please wait until your team members have made their decision."
#
#     @staticmethod
#     def is_displayed(player):
#         return not player.participant.assigned_to_team
#
#     def vars_for_template(self): # TODO staticmethodes?
#         # Get the number of players who have arrived (decided) in the group
#         arrived_players = [p for p in self.group.get_players() if p.field_maybe_none('wlg_decision') is not None]
#         waiting_count = len(arrived_players)
#
#         return {
#             'reload_interval': 5000,  # 5000 milliseconds = 5 seconds
#             'waiting_count': waiting_count
#         }
#
#     def get_template_name(self):
#         return 'global/MyWaitPage.html'
#
#     def js_vars(self):
#         return {
#             'reload_interval': 5000  # 5000 milliseconds = 5 seconds
#         }
#
#     @staticmethod
#     def after_all_players_arrive(group: Group):
#         # Calculate group minimum and individual payoffs
#         group.groupMin = min(p.wlg_decision for p in group.get_players())
#
#         for p in group.get_players():
#             p.payoff_hypo_subround1 = C.ENDOWMENT + (10 * group.groupMin) - (5 * p.wlg_decision)
#
#             # participant variables for payoff info
#             p.participant.wlg_payoff = p.payoff_hypo_subround1
#             p.participant.wlg_min_choice = group.groupMin
#             p.participant.wlg_own_choice = p.wlg_decision
#
#
# class IntroQuestionnaire(Page):
#     form_model = 'player'
#     form_fields = ['team_goal', 'team_expectation']
#
#     @staticmethod
#     def is_displayed(player):
#         return not player.participant.assigned_to_team
#
#
# class EndApp02(Page):
#     form_model = 'player'
#
#     @staticmethod
#     def is_displayed(player):
#         return not player.participant.assigned_to_team


page_sequence = [
    MyWaitPage,
    InformOnScreenTimer,
    WaitPage1,
    TreatmentB,  # TODO: add TreatmentA and control structure
    WaitPage2,
    VVC,
    # VideoMeeting, # TODO the version I created,
    # WaitPage3,
    # PostVideoMeetingQuestionnaireI,  # TODO -> Note: my control for hear-see, but we use the multi-design-shit now
    # TODO: Allow for "soft dropout" afterwards -> only flag the drop out person -> what to do with WLG payoff?
    # WaitPage4,
    PostVideoMeetingQuestionnaireII,  # TODO: NASA-TLX 1 item and ZEF Subscale social/general
    WaitPage3, # --> brauche ich eigentlich nicht, oder? wobei ich irgendwann halt schon wissen muss, was die anderen ausgewählt haben?
    IntroWLG,
    ComprehensionWLG,
    DecisionWLG,
    PostCoordinationQuestionnaire,
]
