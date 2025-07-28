from otree.api import *
import time

c = cu

doc = ("""

This App handel Stage 2, where the participants form a group of three to:
- See the goal preferences of the others
- additionally perform WOOP in the treatment group
- have a 7 min video meeting
- answer whether they were able to see the others

( - getting a introduction to WLG)
(- Playing WLG one-shot)

Players arrive at this app with several flags. A group is only formed when three players waiting.
Due to the multiple rounds character player can rejoin the grouping or decide to be forwarded to Stage 3
Once players joined a group they are flagged as assigned_to_group
Once players decide to continue with Stage 3 after a waiting period (5 minutes) or are in round 5 (+ 4 times waiting) 
without forming a group, participants are flagged as single player and be forwarded to App03

How often participants agree to additional wait time will be counted and considered in the payout.
""")


class C(BaseConstants):
    NAME_IN_URL = 'App02'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 2
    ENDOWMENT = 200



class Subsession(BaseSubsession):
    pass
    # waitCount = models.IntegerField(initial=0)  # used for waitpage


# TODO -> Clarify: do I need this?
class Group(BaseGroup):
    groupMin = models.IntegerField(
        min=0, max=40, initial=40
    )
    randomNumber = models.IntegerField()


def make_field6(label):
    return models.IntegerField(
        choices=[1, 2, 3, 4, 5, 6],
        label=label,
        widget=widgets.RadioSelectHorizontal,
    )


def make_field(label):
    return models.IntegerField(
        choices=[0, 10, 20, 30, 40],
        label=label,
        widget=widgets.RadioSelect,
    )


def waiting_too_long(player):
    """ check whether the player already waits longer than the defined time"""
    wait_too_long_check = time.time() - player.participant.wait_page_arrival > 60  # * 10 # TODO ADD 10 for 10 Minutes!
    return wait_too_long_check


def group_by_arrival_time_method(subsession, waiting_players):
    """
    This function is called in MyWaitPage and controls for the players waiting
    - 3 players waiting? form group
    - calls waiting_too_long
    - if waiting_too_long and wait
    """

    print(waiting_players)
    if len(waiting_players) >= 3:
        return waiting_players[:3]
    for player in waiting_players:
        print('test: ', player)
        print(player.participant.waiting_too_long)
        if waiting_too_long(player):
            player.participant.waiting_too_long = True
            return [player]


class Player(BasePlayer):
    q_continue_waiting = models.StringField(
        choices=[
            ['Yes', 'Yes - I want to wait additional 5 minutes and be compensated for the extra waiting time'],
            ['No',
             'No - I don\'t want to wait any longer, continue with Stage 3 and, waive of the payout from Stage 2'],
        ],
        label='Do you like to wait additional 5 minutes for Stage 2?'
    )

    ownDecision_subround1 = make_field("Please choose one")
    payoff_hypo_subround1 = models.IntegerField()

    # my own goals VS the goals of others?
    team_goal = make_field6(
        'To what extent was it your goal to collaborate?') # TODO --> Siehe App01 -> MentalModel
    team_expectation = make_field6(
        'To what extent do you expect your team members have collaborated?') # TODO Siehe App01 -> MentalModel


class MyWaitPage(WaitPage):
    """
    This wait page ensures, that Stage 2 of the experiment will only be played if a group of 3 players ca be formed.
    The page is skipped if players already flagged as single player.
    The page set
    """

    group_by_arrival_time = True

    # TODO: Kann man round number auf 1 manuell setzen? Groupen wenn in verschiedenen Runden funktioniert nicht

    @staticmethod  # TODO: Wird nicht gecalled
    def before_next_page(player, timeout_happened):
        """ if players proceeding to the next page and are not flagged as waiting to long, they formed a team"""
        print('the before_next_page methode is called')
        if not player.participant.waiting_too_long:
            print('player assigned to team')
            player.participant.assigned_to_team = True

    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        """ Player are waiting to long after round 5, they will be flagged as single player and forwarded to Stage 3 """
        if player.round_number == C.NUM_ROUNDS and not player.participant.assigned_to_team:
            print('I was here')
            print('assigned to team?:', player.participant.assigned_to_team)
            player.participant.single_player = True
            return 'App03'
        else:
            # Test
            print('soll asigned werden?')
            if not player.participant.waiting_too_long:
                print('player assigned to team')
                player.participant.assigned_to_team = True



class WaitingTooLong(Page):
    """
    Landing Page is only displayed if player was not succesfull assigned to a team
    Players are asked whether they want to continue with waiting or be forwarded to Stage 3
    """

    form_model = 'player'
    form_fields = ['q_continue_waiting']

    @staticmethod
    def is_displayed(player):
        return not player.participant.assigned_to_team and player.round_number < C.NUM_ROUNDS

    @staticmethod
    def before_next_page(player, timeout_happened):
        """ update player and participant vars"""
        print('display answer', player.q_continue_waiting)
        if player.q_continue_waiting == 'Yes':
            # all other pages are skipped, hence reset arrival time
            player.participant.wait_page_arrival = time.time()
            # reset waiting_too_long flag
            player.participant.waiting_too_long = False
            # increase waiting count to keep track for payout
            player.participant.additional_wait_time += 1
        else:
            # If player don't like to continue, they are flagged as single player
            player.participant.single_player = True

    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        # if players are flagged as single player, they will be forwarded to Stage 3
        if player.participant.single_player:
            return 'App03'


class TreatmentA(Page):
    """
        This page handles one of two treatments, and therefore includes:
            - visualize personal and team-averaged VM goals

        The treatment is handled via control-variable and a is_displayed staticmethod# TODO

        """
    pass


class TreatmentB(Page):
    """
    This page handles one of two treatments, and therefore includes:
        - visualize personal and team-averaged VM goals
        - WOOP

    The treatment is handled via control-variable and a is_displayed staticmethod# TODO

    """
    form_model = 'player'

    @staticmethod
    def is_displayed(player):
        return player.participant.assigned_to_team

    # @staticmethod
    # def is_displayed(player):
    #     print(player.participant.single_player)
    #     return not player.participant.single_player
    #
    # @staticmethod
    # def js_vars(player):
    #     others = player.get_others_in_group()
    #     return dict(
    #         own=[player.participant.vm_pref_achievement,
    #              player.participant.vm_pref_dominance,
    #              player.participant.vm_pref_face,
    #              player.participant.vm_pref_rules,
    #              player.participant.vm_pref_concern,
    #              player.participant.vm_pref_tolerance],
    #         other1=[others[0].participant.vm_pref_achievement,
    #                 others[0].participant.vm_pref_dominance,
    #                 others[0].participant.vm_pref_face,
    #                 others[0].participant.vm_pref_rules,
    #                 others[0].participant.vm_pref_concern,
    #                 others[0].participant.vm_pref_tolerance],
    #         other2=[others[1].participant.vm_pref_achievement,
    #                 others[1].participant.vm_pref_dominance,
    #                 others[1].participant.vm_pref_face,
    #                 others[1].participant.vm_pref_rules,
    #                 others[1].participant.vm_pref_concern,
    #                 others[1].participant.vm_pref_tolerance]
    #     )
    #
    # @staticmethod
    # def before_next_page(player, timeout_happened):
    #     #players = player.group.get_player_by_id()
    #
    #     if not player.participant.single_player:
    #         players = player.group.get_players()
    #
    #         players[0].participant.svo_other = players[2].participant.svo_to_other
    #         players[2].participant.svo_other = players[1].participant.svo_to_other
    #         players[1].participant.svo_other = players[0].participant.svo_to_other


class Description1(Page):
    """ Page informs the participants about the number of sub-round"""
    form_model = 'player'

    @staticmethod
    def is_displayed(player):
        return player.participant.assigned_to_team


class Decision1(Page):
    form_model = 'player'
    form_fields = ['ownDecision_subround1']

    @staticmethod
    def is_displayed(player):
        return player.participant.assigned_to_team

    @staticmethod
    def live_method(player: Player, data):
        if "ownDecision_subround1" in data:
            player.ownDecision_subround1 = data["ownDecision_subround1"]

    @staticmethod
    def vars_for_template(player: Player):
        return dict(round_num=player.round_number)


class CalculatePayoff1(WaitPage):
    body_text = "Please wait until your team members have made their decision."

    @staticmethod
    def is_displayed(player):
        return not player.participant.assigned_to_team

    def vars_for_template(self): # TODO staticmethodes?
        # Get the number of players who have arrived (decided) in the group
        arrived_players = [p for p in self.group.get_players() if p.field_maybe_none('ownDecision_subround1') is not None]
        waiting_count = len(arrived_players)

        return {
            'reload_interval': 5000,  # 5000 milliseconds = 5 seconds
            'waiting_count': waiting_count
        }

    def get_template_name(self):
        return 'global/MyWaitPage.html'

    def js_vars(self):
        return {
            'reload_interval': 5000  # 5000 milliseconds = 5 seconds
        }

    @staticmethod
    def after_all_players_arrive(group: Group):
        # Calculate group minimum and individual payoffs
        group.groupMin = min(p.ownDecision_subround1 for p in group.get_players())

        for p in group.get_players():
            p.payoff_hypo_subround1 = C.ENDOWMENT + (10 * group.groupMin) - (5 * p.ownDecision_subround1)

            # participant variables for payout info
            p.participant.wlg_payoff = p.payoff_hypo_subround1
            p.participant.wlg_min_choice = group.groupMin
            p.participant.wlg_own_choice = p.ownDecision_subround1


class IntroQuestionnaire(Page):
    form_model = 'player'
    form_fields = ['team_goal', 'team_expectation']

    @staticmethod
    def is_displayed(player):
        return not player.participant.assigned_to_team


class EndApp02(Page):
    form_model = 'player'

    @staticmethod
    def is_displayed(player):
        return not player.participant.assigned_to_team




page_sequence = [
    MyWaitPage,
    WaitingTooLong,
    TreatmentB,
    # Description1,
    # Decision1,
    # CalculatePayoff1,
    # IntroQuestionnaire,
    # EndApp02,
    # EndApp02ByPass
]
