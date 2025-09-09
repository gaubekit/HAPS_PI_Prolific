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


class C(BaseConstants):
    NAME_IN_URL = 'App02'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 1

    HEARTBEAT_THRESHOLD = 20  # 120

    # Central configuration of duration Video Meeting and Upload Time Limit
    VM_DURATION = 3 * 60  # TODO 7 minutes
    VM_UPLOAD_DURATION = 2 * 60  # TODO 2 minutes

    AUDIO_GUIDE_APPEAR = 1 * 60
    AUDIO_GUIDE_AUTO_SUBMIT = 2 * 60
    AUDIO_GUIDE_DURATION = 5 * 60  # the duration of the mp3-file
    AUDIO_GUIDE_TIME_AFTERWARDS = 2 * 60


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
     pass


# def make_field(label):
#     return models.IntegerField(
#         choices=[1, 2, 3, 4, 5, 6, 7],
#         label=label,
#         widget=widgets.RadioSelect,
#     )


class Player(BasePlayer):
    # Var to control Video Meeting Behavior: 1 -> no modification, 2 -> no self-view, 3 -> additional message above
    # Note: not used in this study -> hardcoded '1' = no modification
    video_meeting_behavior = models.IntegerField(initial=1, blank=True)

    # Var for Treatment
    treatment_completed = models.StringField(initial='no')

    # var storing notes in TreatmentB
    treatment_notes = models.LongStringField()

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
        label='To the team project, you contribute 0 hours and the minimum contribution by any team member is 10 hours:', min=0, max=400)
    comprehension2 = models.IntegerField(
        label='To the team project, you contribute 20 hours and the minimum contribution by any team member is 10 hours:', min=0, max=400)
    comprehension3 = models.IntegerField(
        label='To the team project, you contribute 40 hours and the minimum contribution by any team member is 30 hours:', min=0, max=400)
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

    holidays_1 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6, 7])#, label='Sun, sea, and beach vacation')
    holidays_2 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6, 7])#, label='Party vacation')
    holidays_3 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6, 7])#, label='Winter sports vacation')
    holidays_4 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6, 7])#, label='City trip')
    holidays_5 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6, 7])#, label='Backpacking vacation')
    holidays_6 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6, 7])#, label='Excursion')
    holidays_7 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6, 7])#, label='Camping vacation')
    holidays_8 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6, 7])#, label='Cruise vacation')


# HELP FUNCTIONS
# def heartbeat_dropout_detection(player, threshold):
#     """
#     Detect inactive players based on heartbeat pings.
#     If a player has been inactive longer than the given threshold,
#     they are flagged with participant fields `single_player=True` and `raised_dropout=True`.
#
#     Args:
#         player (Player): The current player object.
#         threshold (int): Timeout in seconds, typically set from `C.HEARTBEAT_THRESHOLD`.
#
#     Usage:
#         - Call inside `live_method()`.
#         - Requires global dictionary `last_active` to track last activity.
#         - Requires participant fields `single_player` and `raised_dropout`.
#
#     Backend requirements:
#         - `vars_for_template(player)` must pass `dropout_threshold=C.HEARTBEAT_THRESHOLD`
#           to make the threshold available in the frontend.
#
#     Frontend requirements:
#         - Include `heartbeat.js` in template:
#             <script src="{% static 'heartbeat.js' %}"></script>
#             <script>
#                 startHeartbeat(800, {{ dropout_threshold }});
#             </script>
#     """
#     last_active = {}  # participant.code -> timestamp
#     now = time.time()
#     code = player.participant.code
#
#     #player_on_page = player.participant._current_page_name
#     # arrival = player.participant._last_page_timestamp
#
#     if player_on_page == current_page_name:
#         last_active[code] = now
#
#     active_players = [
#         p for p in player.subsession.get_players()
#         if p.participant._current_page_name == page_name
#            and last_active.get(p.participant.code, 0) > now - threshold]

    #
    #
    # # Check all players in the group for inactivity
    # for p in player.group.get_players():
    #     last_active.get(p.participant.code, 0)
    #
    #     # If last activity exceeds threshold → flag as dropout
    #     if p.participant._current_page_name == page_name and last_active.get(p.participant.code, 0) > now - threshold:
    #             p.participant.raised_dropout = True
    #             p.participant.single_player = True
    #             print(f"Dropout detected after {threshold} seconds inactivity: {p.participant.code}")
    #
    #             # TODO -> clarify: sollte frontendseitig ein auto-submit erzwungen werden?


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
    Page grouping participants by arrival time. Theoretical App01_waiting guarantees for exact 3 active participants.
    As fallback-mechanism, group_by_arrival_time_method() guarantees that player can't get stuck on this wait page.

    The after_all_player_arrive methode is used to update the svo_bonus and to store group information.
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

    # @staticmethod
    # def vars_for_template(player):
    #     return dict(dropout_threshold=C.HEARTBEAT_THRESHOLD)
    #
    # @staticmethod
    # def live_method(player, data):
    #     # heartbeat_dropout_detection(player, C.HEARTBEAT_THRESHOLD)
    #     return {player.id_in_group: dict(ok=True)}

    @staticmethod
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            print("timeout_happened is true in InformOnScreenTimer. This player raised a dropout: ", player.participant.code)
            player.participant.raised_dropout = True
            player.participant.single_player = True


class WaitPage1(WaitPage):
    @staticmethod
    def after_all_players_arrive(group):
        """ Check whether one of the players was labeled as single player. If so, all are labeled as single player """
        if any(p.participant.single_player for p in group.get_players()):
            for p in group.get_players():
                p.participant.single_player = True

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
                ° same graph as in

            - Mental Contrasting

        The treatment is handled via control-variable and a is_displayed staticmethod. # TODO

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
    # TODO deactivated for testing
    # timeout_seconds = (C.AUDIO_GUIDE_APPEAR + C.AUDIO_GUIDE_AUTO_SUBMIT
    #                    + C.AUDIO_GUIDE_DURATION + C.AUDIO_GUIDE_TIME_AFTERWARDS)

    # TODO deactivated for testing
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

    # TODO deactivated for testing
    # @staticmethod
    # def before_next_page(player, timeout_happened):
    #     if timeout_happened:
    #         print("timeout_happened is true in TreatmentB. This player raised a dropout: ", player.participant.code)
    #         player.participant.raised_dropout = True
    #         player.participant.single_player = True


class WaitPage2(WaitPage):
    """
        This Page ensures that all participants arrive to the same time on the video meeting page and the dropout time
        starts simultaneously. If a dropout happens, all group-members will be forwarded to Stage 3
    """
    @staticmethod
    def after_all_players_arrive(group):
        """ Check whether one of the players was labeled as single player. If so, all are labeled as single player """
        if any(p.participant.single_player for p in group.get_players()):
            print('dropout in TreatmentB detected')
            for p in group.get_players():
                p.participant.single_player = True
        else:
            print('TreatmentB i.o.')

    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        for p in player.group.get_players():
            if p.participant.single_player:
                # if one of the others is a single player, all in the group are flagged as single player
                p.participant.single_player = True

        if player.participant.single_player:
            return 'App03'
        return None


class HolidayPreferences(Page):
    """
        This asks about holiday-preferences, with the goal to actively prime the discussion topic.

        Note: The methods get_form_fields and vars_for_template shuffle the formfields (types of vataion) in an
              random order. The usage of participant.vars['some_var'] allows for usage of participant fields
              without defining in settings.py. Because vars_for_template reloads get_form_fields, the non-existing
              participant variable is used to set the field only once (in the shuffled order).
    """
    form_model = 'player'

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
            import random
            random.shuffle(holidays)
            player.participant.vars['holiday_list'] = holidays
            print(">>> Shuffle created:", player.participant.code, holidays)
        else:
            print(">>> Using existing shuffle:", player.participant.code, player.participant.vars['holiday_list'])

        return dict(holidays=player.participant.vars['holiday_list'])


class VideoMeeting(Page):
    # Note: I added global.css, Picture_Camera.jpg and Picture_Microphone.jpg to _static from joint-study
    form_model = 'player'
    timeout_seconds = C.VM_DURATION + C.VM_UPLOAD_DURATION   # 540 7min VM + 2min upload/Questionnaire
    form_fields = ['seeHear', 'correctBackground', 'attentionCheck', 'video_meeting_behavior']

    @staticmethod
    def vars_for_template(player: Player):
        # TODO: Hardcoded for testing, because optInConsent is written in App01 and I have no "is_dropout" logic
        player.participant.optInConsent = 1

        return dict(optInConsent=player.participant.optInConsent,
                    timeout_seconds=VideoMeeting.timeout_seconds)

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


page_sequence = [
    MyWaitPage,
    InformOnScreenTimer,
    WaitPage1,
    # Treatment A, # TODO
    TreatmentB,
    HolidayPreferences,
    WaitPage2,
    VideoMeeting_dummy,  # TODO
    # VideoMeeting,  # TODO
    WaitPage3,
    PostVideoMeetingQuestionnaireII,
    IntroWLG,
    ComprehensionWLG,
    DecisionWLG,
    PostCoordinationQuestionnaire,
]
