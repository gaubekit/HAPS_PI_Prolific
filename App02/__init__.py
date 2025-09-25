from otree.api import *
import random
import time

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
The initial waitpage saves the player codes of the group members and update payoff_bonus_svo
    -> upd. payoff_total = payoff_fix + payoff_bonus_svo + payoff_compensation_wait

Dropout Handling I:
    - Guarantee that the video meeting completes (only situation where the participants interact in realtime)
    - OnPage-Timer and WaitPages control that participants proceed in the same pase
    - Additionally a heartbeat_detection functions monitors "active players" -> tab closed / disconnect
    
    - if timeout_happens or inactive player detected:
        -> all players are tagged as "single_player" and forwarded to Stage 3
        -> the participant who raised the timeout is tagged as "raised_timeout" and
         get no compensation for Stage 2
        -> the other two will be compensated with 150 ECU (3 pound)
                          
Dropout Handling II:
    - Once participants completed the video meeting without dropout -> no live interaction anymore
    - no dropout detection after WaitPage3
    - On the very last page of Stage 3 player.particpant.code of group members will checked for WLG Decision
        -> if decision made by all players: calculate payoff_bonus_wlg
        -> else: payoff_bonus_wlg, payoff_compensation_wlg_dropout = 0, 150 (ECU)
        
""")


# GLOBAL VAR for App02
last_active = {}        # Tracks last "ping" timestamp per player


class C(BaseConstants):
    NAME_IN_URL = 'App02'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 1

    # Central configuration of duration Video Meeting and Upload Time Limit
    # VM_DURATION = 7 * 60
    VM_DURATION = 1 * 60  # 1 minute for testing
    VM_UPLOAD_DURATION = 2 * 60

    # Central configuration of timings on TreatmentB Page
    AUDIO_GUIDE_APPEAR = 1 * 60
    AUDIO_GUIDE_AUTO_SUBMIT = 2 * 60
    AUDIO_GUIDE_DURATION = 5 #* 60  # the duration of the mp3-file # TODO
    AUDIO_GUIDE_TIME_AFTERWARDS = 2 * 60


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
     dropout_happened = models.BooleanField(initial=False)
     treatment = models.StringField(initial='WOOP')


class Player(BasePlayer):
    # Var to control Video Meeting Behavior: 1 -> no modification, 2 -> no self-view, 3 -> additional message above
    # Note: not used in this study -> hardcoded '1' = no modification
    video_meeting_behavior = models.IntegerField(initial=1, blank=True)

    # Var for Treatment
    treatment_completed = models.StringField(initial='no')

    # var storing notes in TreatmentB
    treatment_notes = models.LongStringField(initial='', blank=True)

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
    #  <How mentally demanding was this video conference task?>
    nasatlx_1 = models.IntegerField(widget=widgets.RadioSelect, choices=list(range(-10, 11)))
    # <How hurried or rushed was the pace of this video conference?>
    nasatlx_2 = models.IntegerField(widget=widgets.RadioSelect, choices=list(range(-10, 11)))
    # <How much do you tend to avoid social situations after this video conference?>
    zfe_social_1 = models.IntegerField(widget=widgets.RadioSelect, choices=list(range(-10, 11)))
    # <How much do you want to be alone after this video conference?>
    zfe_social_2 = models.IntegerField(widget=widgets.RadioSelect, choices=list(range(-10, 11)))
    # <How much do you need time by yourself after this video conference?>
    zfe_social_3 = models.IntegerField(widget=widgets.RadioSelect, choices=list(range(-10, 11)))
    # <How much do you dread having to do things after this video conference?>
    zfe_general_1 = models.IntegerField(widget=widgets.RadioSelect, choices=list(range(-10, 11)))
    # <How much do you feel like doing nothing after this video conference?>
    zfe_general_2 = models.IntegerField(widget=widgets.RadioSelect, choices=list(range(-10, 11)))
    # <How much do you feel too tired to do other things after this video conference?>
    zfe_general_3 = models.IntegerField(widget=widgets.RadioSelect, choices=list(range(-10, 11)))

    # Comprehension Weakest Link Game
    comp1_check = models.IntegerField(initial=0)
    comp2_check = models.IntegerField(initial=0)
    comp3_check = models.IntegerField(initial=0)
    comp4_check = models.IntegerField(initial=0)
    comprehension1 = models.IntegerField(
        label='To the team project, you contribute 0 hours and the minimum contribution '
              'by any team member is 10 hours:', min=0, max=400)
    comprehension2 = models.IntegerField(
        label='To the team project, you contribute 20 hours and the minimum contribution '
              'by any team member is 10 hours:', min=0, max=400)
    comprehension3 = models.IntegerField(
        label='To the team project, you contribute 40 hours and the minimum contribution '
              'by any team member is 30 hours:', min=0, max=400)
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

    # Holiday Preferences for priming Video Meeting (Same as in Joint Study)
    holidays_1 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6, 7])
    holidays_2 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6, 7])
    holidays_3 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6, 7])
    holidays_4 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6, 7])
    holidays_5 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6, 7])
    holidays_6 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6, 7])
    holidays_7 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6, 7])
    holidays_8 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6, 7])


# HELP FUNCTIONS

# Functions to handle grouping and waiting_too_long on waitpages
def waiting_too_long(player):
    """
    Returns boolean, indicating whether the players waiting to long (after 60 seconds),
    guaranteeing that player can't get stuck
    """
    return time.time() - player.participant.arrival_time_for_grouping > 60


def group_by_arrival_time_method(subsession, waiting_players):
    """ methode is called implicitly when group_by_arrival_time = True """
    if len(waiting_players) >= 3:
        return waiting_players[:3]
    for player in waiting_players:
        if waiting_too_long(player):
            player.participant.single_player = True
            # make a single-player group.
            return [player]


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
            return ("Unfortunately, that's incorrect. Your compensation depends on the <strong>"
                    "number of hours you work on the team project</strong> and the <strong>fewest "
                    "number of hours worked by a member of your team on the team project</strong>.")
    return None


def comprehension4b_error_message(player: Player, value):
    if value:
        player.comp4_check += 1
        if player.comp4_check == 1:
            return "Unfortunately, that's incorrect. Please try again."
        elif player.comp4_check >= 2:
            return ("Unfortunately, that's incorrect. Your compensation depends on the <strong>"
                    "number of hours you work on the team project</strong> and the <strong>"
                    "fewest number of hours worked by a member of your team on the team project</strong>.")
    return None


def comprehension4c_error_message(player: Player, value):
    if not value:
        player.comp4_check += 1
        if player.comp4_check == 1:
            return "Unfortunately, that's incorrect. Please try again."
        elif player.comp4_check >= 2:
            return ("Unfortunately, that's incorrect. Your compensation depends on the <strong>"
                    "number of hours you work on the team project</strong> and the <strong>"
                    "fewest number of hours worked by a member of your team on the team project</strong>.")
    return None


# PAGES
class MyWaitPage(WaitPage):
    """
    Page grouping participants by arrival time. Theoretical App01_waiting guarantees for exact 3 active participants.
    As fallback-mechanism, group_by_arrival_time_method() guarantees that player can't get stuck on this wait page.

    The after_all_player_arrive methode is used to:
        - update the svo_bonus
        - store group information
        - initialize entry's for participants of the group in last_active
        - select group treatment randomly
    """

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

            if p.id_in_group == 1:
                p.group.treatment = random.choice(['WOOP', 'Control'])
                print(f'group was assigned to treatment {p.group.treatment}')

            # initialize dict with time, page and activity status for each participant
            last_active[p.participant.code] = {
                'last_time': time.time(),
                'current_page': p.participant._current_page_name,
                'activity_status': True,
            }

            p.session.last_active_session_wide[p.participant.code] = last_active[p.participant.code]
            p.participant.last_sync = time.time()

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
                print('Error in App02 WaitPage, there was no other in the group')
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
                        + p.participant.payoff_compensation_svo_other
                )
                p.participant.payoff_total = round(p.participant.payoff_total, 2)

                print('payoff svo: ', p.participant.payoff_bonus_svo)
                print('payoff svo compensation: ', p.participant.payoff_compensation_svo_other)
                print('payoff waiting: ', p.participant.payoff_compensation_wait)
                print('payoff total: ', p.participant.payoff_total)
            except NameError:
                print('Error in App02 WaitPage: The Other had no svo_to_other ->payoff_bonus_svo not updated')
                p.participant.payoff_compensation_svo_other = 50
                print(f'payoff_compensation_svo_other for {p.participant.code} was updated: ', p.participant.payoff_compensation_svo_other)
                p.participant.payoff_total = (
                        p.participant.payoff_fix
                        + p.participant.payoff_bonus_svo
                        + p.participant.payoff_compensation_wait
                        + p.participant.payoff_compensation_svo_other
                )
                p.participant.payoff_total = round( p.participant.payoff_total, 2)

    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        if player.participant.single_player:
            return 'App03'


class InformOnScreenTimer(Page):
    """
        This page is thought to inform players about the on_screen timer, which raise drop_out if players
        do not proceed in time.
    """

    form_model = 'player'
    timeout_seconds = 5 * 60

    @staticmethod
    def live_method(player, data):
        try:
            """ checks every 800ms whether all players are alive (browser not closed)"""
            now = time.time()
            code = player.participant.code
            page = player.participant._current_page_name

            last_active[code]['last_time'] = now
            last_active[code]['current_page'] = page

            # Check whether one of the players is inactive fore more than 2 minutes
            for p in player.group.get_players():
                if last_active[p.participant.code]['last_time'] < now - 60 * 2:
                    last_active[p.participant.code]['activity_status'] = False
                    print('set set activity_status in last_active to False for: ', p.participant.code)
                    p.participant.raised_dropout = True
                    p.participant.single_player = True
                    p.group.dropout_happened = True

            # Save last_active every 90 seconds in participant var as backup
            if time.time() - player.participant.last_sync < 90:
                player.session.last_active_session_wide[player.participant.code] = last_active[player.participant.code]
                player.participant.last_sync = time.time()

            return None

        except KeyError as e:
            # Restore participant key in last_active
            missing_key = e.args[0]
            last_active[missing_key] = player.session.last_active_session_wide[missing_key]
            print(f'Restored {e.args[0]} in last_active on InformOnScreenTimer')

            return None

    @staticmethod
    def before_next_page(player, timeout_happened):
        """ Checks whether a player was alive but did not proceed within the given time """
        if timeout_happened:
            print("timeout_happened is true in InformOnScreenTimer. This player raised a dropout: ", player.participant.code)
            player.participant.raised_dropout = True
            player.participant.single_player = True
            player.group.dropout_happened = True


class WaitPage1(Page):
    """
        This Page simulates a WaitPage, but controlling for players "alive"-status (browser not closed longer than 2min)
        Page has a Timeout of 5 minutes, guaranteeing that active players are forwarded in any case.
    """
    form_model = 'player'
    timeout_seconds = 5 * 60

    @staticmethod
    def vars_for_template(player: Player):
        """ passing timeout seconds to frontend --> ensuring players forwarded automatically after xx seconds"""
        print('wait page timeout seconds', WaitPage1.timeout_seconds)
        return dict(timeout_seconds=WaitPage1.timeout_seconds)

    @staticmethod
    def live_method(player, data):
        """ checks every 800ms whether all players are alive (browser not closed)"""
        try:
            now = time.time()
            page = player.participant._current_page_name
            code = player.participant.code

            last_active[code]['last_time'] = now
            last_active[code]['current_page'] = page

            # check whether a player is not "alive" for longer than 2 minutes
            for p in player.group.get_players():
                if last_active[p.participant.code]['last_time'] < now - 60 * 2:
                    last_active[p.participant.code]['activity_status'] = False
                    p.participant.raised_dropout = True
                    p.participant.single_player = True
                    p.group.dropout_happened = True

            # Save last_active every 90 seconds in participant var as backup
            if time.time() - player.participant.last_sync < 90:
                player.session.last_active_session_wide[player.participant.code] = last_active[player.participant.code]
                player.participant.last_sync = time.time()

            # create a list of all players waiting on this page
            alive_players_waiting = [
                p for p in player.group.get_players()
                if last_active.get(p.participant.code, {}).get('activity_status', False)
                   and last_active.get(p.participant.code, {}).get('current_page', False) == page
            ]
            return {
                p.id_in_group: dict(
                    count=len(alive_players_waiting),
                    ready=len(alive_players_waiting) == 3 or p.group.dropout_happened
                )
                for p in player.group.get_players()
            }
        except KeyError as e:
            # Restore participant key in last_active
            missing_key = e.args[0]
            last_active[missing_key] = player.session.last_active_session_wide[missing_key]
            print(f'Restored {e.args[0]} in last_active on WaitPage1')

    @staticmethod
    def before_next_page(player, timeout_happened):
        """if timeout_happened = player alive but do not proceed in time -> flag player"""
        if timeout_happened:
            # flag player who raised the timeout
            player.participant.raised_dropout = True

            # flag all players as single player
            for p in player.group.get_players():
                p.participant.single_player = True

        # Setting the treatment manually to "WOOP" for testing reasons
        # player.group.treatment = 'WOOP'
        player.group.treatment = 'Control'

    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        """if player flagged -> direct  to App03"""

        if any(p.participant.single_player for p in player.group.get_players()):
            for p in player.group.get_players():
                p.participant.single_player = True
                p.group.dropout_happened = True

        if player.participant.single_player:
            return 'App03'
        else:
            print(f' Player {player.participant.code}: InformOnPageScreener i.o.')


class TreatmentA(Page):
    """
    This page handles one of two treatments, and therefore includes:
        - visualize personal and team-averaged Playground goals

    The treatment is handled via control-variable and an is_displayed staticmethod

    """
    form_model = 'player'
    form_fields = ['treatment_notes']

    timeout_seconds = (C.AUDIO_GUIDE_DURATION + C.AUDIO_GUIDE_TIME_AFTERWARDS)

    @staticmethod
    def is_displayed(player):
        print(f'treatment is {player.group.treatment}')
        return player.group.treatment == 'Control'

    @staticmethod
    def js_vars(player):
        others = player.get_others_in_group()
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

    @staticmethod
    def live_method(player, data):
        try:
            """ checks every 800ms whether all players are alive (browser not closed)"""
            now = time.time()
            code = player.participant.code
            page = player.participant._current_page_name

            last_active[code]['last_time'] = now
            last_active[code]['current_page'] = page

            # Check whether one of the players is inactive fore more than 2 minutes
            for p in player.group.get_players():
                if last_active[p.participant.code]['last_time'] < now - 60 * 2:
                    last_active[p.participant.code]['activity_status'] = False
                    print('set set activity_status in last_active to False for: ', p.participant.code)
                    p.participant.raised_dropout = True
                    p.participant.single_player = True
                    p.group.dropout_happened = True

            # Save last_active every 90 seconds in participant var as backup
            if time.time() - player.participant.last_sync < 90:
                player.session.last_active_session_wide[player.participant.code] = last_active[player.participant.code]
                player.participant.last_sync = time.time()

            return None

        except KeyError as e:
            # Restore participant key in last_active
            missing_key = e.args[0]
            last_active[missing_key] = player.session.last_active_session_wide[missing_key]
            print(f'Restored {e.args[0]} in last_active on TreatmentA')

            return None

    @staticmethod
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            print("timeout_happened is true in TreatmentA. This player raised a dropout: ", player.participant.code)
            player.participant.raised_dropout = True
            player.participant.single_player = True
            player.group.dropout_happened = True


class TreatmentB(Page):
    """
        This page handles one of two treatments, and therefore includes:
            - visualize personal and team-averaged Playground goals
                ° same graph as in

            - Mental Contrasting

        The treatment is handled via control-variable and an is_displayed staticmethod.

        Dropout detection is ensured via timeout_seconds:

        timeout_seconds = (a) time for audio button  +  (b) audio button auto submit + (c) audio instruction
                          + (d) time to click next-button

            (a) 1 min in AUDIO_GUIDE_APPEAR
            (b) 2 min in AUDIO_GUIDE_AUTO_SUBMIT
            (c) 5 min in AUDIO_GUIDE_DURATION
            (d) 2 min in AUDIO_GUIDE_TIME_AFTERWARDSF

        --> timeout_seconds = 10 * 60 min
    """
    form_model = 'player'
    form_fields = ['treatment_notes']

    timeout_seconds = (C.AUDIO_GUIDE_APPEAR + C.AUDIO_GUIDE_AUTO_SUBMIT
                       + C.AUDIO_GUIDE_DURATION + C.AUDIO_GUIDE_TIME_AFTERWARDS)

    @staticmethod
    def is_displayed(player):
        print(f'treatment is {player.group.treatment}')
        return player.group.treatment == 'WOOP'

    @staticmethod
    def js_vars(player):
        others = player.get_others_in_group()
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

    @staticmethod
    def live_method(player, data):
        try:
            """ checks every 800ms whether all players are alive (browser not closed)"""
            now = time.time()
            code = player.participant.code
            page = player.participant._current_page_name

            last_active[code]['last_time'] = now
            last_active[code]['current_page'] = page

            # Check whether one of the players is inactive fore more than 2 minutes
            for p in player.group.get_players():
                if last_active[p.participant.code]['last_time'] < now - 60 * 2:
                    last_active[p.participant.code]['activity_status'] = False
                    print('set set activity_status in last_active to False for: ', p.participant.code)
                    p.participant.raised_dropout = True
                    p.participant.single_player = True
                    p.group.dropout_happened = True

            # Save last_active every 90 seconds in participant var as backup
            if time.time() - player.participant.last_sync < 90:
                player.session.last_active_session_wide[player.participant.code] = last_active[player.participant.code]
                player.participant.last_sync = time.time()

            return None

        except KeyError as e:
            # Restore participant key in last_active
            missing_key = e.args[0]
            last_active[missing_key] = player.session.last_active_session_wide[missing_key]
            print(f'Restored {e.args[0]} in last_active on TreatmentB')

            return None

    @staticmethod
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            print("timeout_happened is true in TreatmentB. This player raised a dropout: ", player.participant.code)
            player.participant.raised_dropout = True
            player.participant.single_player = True
            player.group.dropout_happened = True


class WaitPage2(Page):
    """
        This Page simulates a WaitPage, but controlling for players "alive"-status (browser not closed longer than 2min)
        Page has a Timeout of 5 minutes, guaranteeing that active players are forwarded in any case.
    """
    form_model = 'player'
    timeout_seconds = 8 * 60

    @staticmethod
    def vars_for_template(player: Player):
        """ passing timeout seconds to frontend --> ensuring players forwarded automatically after xx seconds"""
        return dict(timeout_seconds=WaitPage2.timeout_seconds)

    @staticmethod
    def live_method(player, data):
        """ checks every 800ms whether all players are alive (browser not closed)"""
        try:
            now = time.time()
            page = player.participant._current_page_name
            code = player.participant.code

            last_active[code]['last_time'] = now
            last_active[code]['current_page'] = page

            # check whether a player is not "alive" for longer than 2 minutes
            for p in player.group.get_players():
                if last_active[p.participant.code]['last_time'] < now - 60 * 2:
                    last_active[p.participant.code]['activity_status'] = False
                    p.participant.raised_dropout = True
                    p.participant.single_player = True
                    p.group.dropout_happened = True

            # Save last_active every 90 seconds in participant var as backup
            if time.time() - player.participant.last_sync < 90:
                player.session.last_active_session_wide[player.participant.code] = last_active[player.participant.code]
                player.participant.last_sync = time.time()

            # create a list of all players waiting on this page
            alive_players_waiting = [
                p for p in player.group.get_players()
                if last_active.get(p.participant.code, {}).get('activity_status', False)
                and last_active.get(p.participant.code, {}).get('current_page', False) == page
            ]
            return {
                    p.id_in_group: dict(
                        count=len(alive_players_waiting),
                        ready=len(alive_players_waiting) == 3 or p.group.dropout_happened
                    )
                    for p in player.group.get_players()
                }
        except KeyError as e:
            # Restore participant key in last_active
            missing_key = e.args[0]
            last_active[missing_key] = player.session.last_active_session_wide[missing_key]
            print(f'Restored {e.args[0]} in last_active on WaitPage2')

    @staticmethod
    def before_next_page(player, timeout_happened):
        """if timeout_happened = player alive but do not proceed in time -> flag player"""
        if timeout_happened:
            # flag player who raised the timeout
            player.participant.raised_dropout = True

            # flag all players as single player
            for p in player.group.get_players():
                p.participant.single_player = True

    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        """if player flagged -> direct  to App03"""

        if any(p.participant.single_player for p in player.group.get_players()):
            for p in player.group.get_players():
                p.participant.single_player = True
                p.group.dropout_happened = True

        if player.participant.single_player:
            return 'App03'
        else:
            print(f' Player {player.participant.code}: Treatment i.o.')


class HolidayPreferences(Page):
    """
        This asks about holiday-preferences, with the goal to actively prime the discussion topic.

        Note: The methods get_form_fields and vars_for_template shuffle the formfields (types of vataion) in an
              random order. The usage of participant.vars['some_var'] allows for usage of participant fields
              without defining in settings.py. Because vars_for_template reloads get_form_fields, the non-existing
              participant variable is used to set the field only once (in the shuffled order).
    """
    form_model = 'player'
    timeout_seconds = 60 * 3

    @staticmethod
    def get_form_fields(player):
        try:
            return [f for f, _ in player.participant.vars['holiday_list']]
        except KeyError:
            return None

    @staticmethod
    def vars_for_template(player):
        if 'holiday_list' not in player.participant.vars:
            holidays = [
                ('holidays_1', 'Sun, sea, and beach vacation'),
                ('holidays_2', 'Party vacation'),
                ('holidays_3', 'Winter sports vacation'),
                ('holidays_4', 'City trip'),
                ('holidays_5', 'Backpacking vacation'),
                ('holidays_6', 'Excursion'),
                ('holidays_7', 'Camping vacation'),
                ('holidays_8', 'Cruise vacation'),
            ]
            random.shuffle(holidays)
            player.participant.vars['holiday_list'] = holidays
            print("Shuffle created:", player.participant.code, holidays)
        else:
            print("Using existing shuffle:", player.participant.code, player.participant.vars['holiday_list'])

        return dict(holidays=player.participant.vars['holiday_list'])

    @staticmethod
    def live_method(player, data):
        try:
            """ checks every 800ms whether all players are alive (browser not closed)"""
            now = time.time()
            code = player.participant.code
            page = player.participant._current_page_name

            last_active[code]['last_time'] = now
            last_active[code]['current_page'] = page

            # Check whether one of the players is inactive fore more than 2 minutes
            for p in player.group.get_players():
                if last_active[p.participant.code]['last_time'] < now - 60 * 2:
                    last_active[p.participant.code]['activity_status'] = False
                    print('set set activity_status in last_active to False for: ', p.participant.code)
                    p.participant.raised_dropout = True
                    p.participant.single_player = True
                    p.group.dropout_happened = True

            # Save last_active every 90 seconds in participant var as backup
            if time.time() - player.participant.last_sync < 90:
                player.session.last_active_session_wide[player.participant.code] = last_active[player.participant.code]
                player.participant.last_sync = time.time()

            return None

        except KeyError as e:
            # Restore participant key in last_active
            missing_key = e.args[0]
            last_active[missing_key] = player.session.last_active_session_wide[missing_key]
            print(f'Restored {e.args[0]} in last_active on HolidayPreferences')

            return None

    @staticmethod
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            print("timeout_happened is true in HolidayPreferences. This player raised a dropout: ", player.participant.code)
            player.participant.raised_dropout = True
            player.participant.single_player = True
            player.group.dropout_happened = True


class WaitPage3(Page):
    """
        Waitpage Simulation - Same as previously
    """
    form_model = 'player'
    timeout_seconds = 3 * 60

    @staticmethod
    def vars_for_template(player: Player):
        """ passing timeout seconds to frontend --> ensuring players forwarded automatically after xx seconds"""
        return dict(timeout_seconds=WaitPage3.timeout_seconds)

    @staticmethod
    def live_method(player, data):
        """ checks every 800ms whether all players are alive (browser not closed)"""
        try:
            now = time.time()
            page = player.participant._current_page_name
            code = player.participant.code

            last_active[code]['last_time'] = now
            last_active[code]['current_page'] = page

            # check whether a player is not "alive" for longer than 2 minutes
            for p in player.group.get_players():
                if last_active[p.participant.code]['last_time'] < now - 60 * 2:
                    last_active[p.participant.code]['activity_status'] = False
                    p.participant.raised_dropout = True
                    p.participant.single_player = True
                    p.group.dropout_happened = True

            # Save last_active every 90 seconds in participant var as backup
            if time.time() - player.participant.last_sync < 90:
                player.session.last_active_session_wide[player.participant.code] = last_active[player.participant.code]
                player.participant.last_sync = time.time()

            # create a list of all players waiting on this page
            alive_players_waiting = [
                p for p in player.group.get_players()
                if last_active.get(p.participant.code, {}).get('activity_status', False)
                   and last_active.get(p.participant.code, {}).get('current_page', False) == page
            ]
            return {
                p.id_in_group: dict(
                    count=len(alive_players_waiting),
                    ready=len(alive_players_waiting) == 3 or p.group.dropout_happened
                )
                for p in player.group.get_players()
            }
        except KeyError as e:
            # Restore participant key in last_active
            missing_key = e.args[0]
            last_active[missing_key] = player.session.last_active_session_wide[missing_key]
            print(f'Restored {e.args[0]} in last_active on WaitPage3')

    @staticmethod
    def before_next_page(player, timeout_happened):
        """if timeout_happened = player alive but do not proceed in time -> flag player"""
        if timeout_happened:
            # flag player who raised the timeout
            player.participant.raised_dropout = True

            # flag all players as single player
            for p in player.group.get_players():
                p.participant.single_player = True

    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        """if player flagged -> direct  to App03"""

        if any(p.participant.single_player for p in player.group.get_players()):
            for p in player.group.get_players():
                p.participant.single_player = True
                p.group.dropout_happened = True

        if player.participant.single_player:
            return 'App03'
        else:
            print(f' Player {player.participant.code}: HolidayPreferences i.o.')


class VideoMeeting(Page):
    # Note: I added global.css, Picture_Camera.jpg and Picture_Microphone.jpg to _static from joint-study
    form_model = 'player'
    timeout_seconds = C.VM_DURATION + C.VM_UPLOAD_DURATION   # 540 7min VM + 2min upload/Questionnaire
    form_fields = ['seeHear', 'correctBackground', 'attentionCheck', 'video_meeting_behavior']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(optInConsent=player.participant.optInConsent,
                    timeout_seconds=VideoMeeting.timeout_seconds)

    @staticmethod
    def live_method(player, data):
        try:
            """ checks every 800ms whether all players are alive (browser not closed)"""
            now = time.time()
            code = player.participant.code
            page = player.participant._current_page_name

            last_active[code]['last_time'] = now
            last_active[code]['current_page'] = page

            # Check whether one of the players is inactive fore more than 2 minutes
            for p in player.group.get_players():
                if last_active[p.participant.code]['last_time'] < now - 60 * 2:
                    last_active[p.participant.code]['activity_status'] = False
                    print('set set activity_status in last_active to False for: ', p.participant.code)
                    p.participant.raised_dropout = True
                    p.participant.single_player = True
                    p.group.dropout_happened = True

            # Save last_active every 90 seconds in participant var as backup
            if time.time() - player.participant.last_sync < 90:
                player.session.last_active_session_wide[player.participant.code] = last_active[player.participant.code]
                player.participant.last_sync = time.time()

            return None

        except KeyError as e:
            # Restore participant key in last_active
            missing_key = e.args[0]
            last_active[missing_key] = player.session.last_active_session_wide[missing_key]
            print(f'Restored {e.args[0]} in last_active on VideoMeeting')

            return None

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
    form_model = 'player'
    timeout_seconds = C.VM_UPLOAD_DURATION
    form_fields = ['seeHear', 'correctBackground', 'attentionCheck', 'video_meeting_behavior']

    @staticmethod
    def vars_for_template(player: Player):
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


class WaitPage4(Page):
    """
        Waitpage Simulation

        Three active players joining the Video Meeting at the same time (WaitPage2). They are automatically
        forwarded after C.VM_DURATION + C.VM_UPLOAD_DURATION, landing on this Page.
        If a player do not confirm that he is "human", this players will be labeled as "raised_dropout"
        and as "single_player" in the before_next_page methode. Also, players date do not seeHear all the others are
        labeled as "single_player"
    """
    form_model = 'player'
    timeout_seconds = 3 * 60

    @staticmethod
    def vars_for_template(player: Player):
        """ passing timeout seconds to frontend --> ensuring players forwarded automatically after xx seconds"""
        return dict(timeout_seconds=WaitPage2.timeout_seconds)

    @staticmethod
    def live_method(player, data):
        """ checks every 800ms whether all players are alive (browser not closed)"""
        try:
            now = time.time()
            page = player.participant._current_page_name
            code = player.participant.code

            last_active[code]['last_time'] = now
            last_active[code]['current_page'] = page

            # check whether a player is not "alive" for longer than 2 minutes
            for p in player.group.get_players():
                if last_active[p.participant.code]['last_time'] < now - 60 * 2:
                    last_active[p.participant.code]['activity_status'] = False
                    p.participant.raised_dropout = True
                    p.participant.single_player = True
                    p.group.dropout_happened = True

            # Save last_active every 90 seconds in participant var as backup
            if time.time() - player.participant.last_sync < 90:
                player.session.last_active_session_wide[player.participant.code] = last_active[player.participant.code]
                player.participant.last_sync = time.time()

            # create a list of all players waiting on this page
            alive_players_waiting = [
                p for p in player.group.get_players()
                if last_active.get(p.participant.code, {}).get('activity_status', False)
                   and last_active.get(p.participant.code, {}).get('current_page', False) == page
            ]
            return {
                p.id_in_group: dict(
                    count=len(alive_players_waiting),
                    ready=len(alive_players_waiting) == 3 or p.group.dropout_happened
                )
                for p in player.group.get_players()
            }
        except KeyError as e:
            # Restore participant key in last_active
            missing_key = e.args[0]
            last_active[missing_key] = player.session.last_active_session_wide[missing_key]
            print(f'Restored {e.args[0]} in last_active on WaitPage4')

    @staticmethod
    def before_next_page(player, timeout_happened):
        """if timeout_happened = player alive but do not proceed in time -> flag player"""
        if timeout_happened:
            # flag player who raised the timeout
            player.participant.raised_dropout = True

            # flag all players as single player
            for p in player.group.get_players():
                p.participant.single_player = True

    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        """if player flagged -> direct  to App03"""

        if any(p.participant.single_player for p in player.group.get_players()):
            for p in player.group.get_players():
                p.participant.single_player = True
                p.group.dropout_happened = True

        if player.participant.single_player:
            return 'App03'
        else:
            print(f' Player {player.participant.code}: VideoMeeting i.o.')
            player.treatment_completed = player.group.treatment


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

    @staticmethod
    def get_form_fields(player):
        fields = ['impact_goal', 'impact_expectation', 'impact_spider_graph', 'impact_video_meeting']
        if player.group.treatment == "WOOP":
            fields.append('impact_woop')
        return fields


page_sequence = [
    # --- Dropout Handling I --- #
    MyWaitPage,
    InformOnScreenTimer,
    WaitPage1,
    TreatmentA,
    TreatmentB,
    WaitPage2,
    HolidayPreferences,
    WaitPage3,
    # VideoMeeting_dummy,  # TODO -> activate or deactivate
    VideoMeeting,  # TODO -> activate or deactivate
    WaitPage4,
    # --- Dropout Handling II --- #
    PostVideoMeetingQuestionnaireII,
    IntroWLG,
    ComprehensionWLG,
    DecisionWLG,
    PostCoordinationQuestionnaire,
]
