from otree.api import *
import time


doc = """
- 5 rounds
- timer WAIT_SECONDS (e.g waiting 5minutes per round)
- timeout -> next page -> asking: extend waiting time or skip to Stage II
    - next round or next page
- if 3 participants ACTIVE (for the last 800ms) on live page -> forward exactly THIS 3 players to the next app
"""

# Global variables to track matching
last_active = {}        # Tracks last "ping" timestamp per player
matched_codes = set()   # Tracks participant codes already matched


class C(BaseConstants):
    NAME_IN_URL = 'App01_waiting'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 5
    WAIT_SECONDS = 20  # 5 * 60


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    q_continue_waiting = models.StringField(
        choices=[
            ['Yes', 'Yes - I want to wait an additional 5 minutes and be compensated for the extra waiting time.'],
            ['No',
             'No - I don\'t want to wait any longer, continue with Stage 3, and waive the bonus payoff from Stage 2.'],
        ],
        label='<b>Do you like to wait an additional 5 minutes for stage 2?</b>'
    )
    single_player = models.BooleanField(initial=False)


class RollingMatching(Page):
    @staticmethod
    def vars_for_template(player):
        # Pass the countdown time to the frontend template
        return dict(wait_seconds=C.WAIT_SECONDS)

    @staticmethod
    def live_method(player, data):
        now = time.time()
        code = player.participant.code
        page = player.participant._current_page_name

        # Update last activity time only if player is not already matched
        if page == "RollingMatching" and code not in matched_codes:
            last_active[code] = now

        # Build list of active (not-yet-matched) players from current session
        active_players = [
            p for p in player.subsession.get_players()
            if p.participant._current_page_name == "RollingMatching"
            and last_active.get(p.participant.code, 0) > now - 0.8
            and p.participant.code not in matched_codes
        ]

        # Group players in batches of 3 (or more, multiple groups possible)
        while len(active_players) >= 3:
            matched_group = active_players[:3]  # select first 3 players

            for p in matched_group:
                p.participant.assigned_to_team = True
                matched_codes.add(p.participant.code)

            # Remove matched players from current pool
            active_players = [p for p in active_players if p not in matched_group]

        # Return status to each participant
        return {
            player.id_in_group: dict(
                ready=player.participant.assigned_to_team,
                count=len(active_players)
            )
        }

    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        # Proceed to next app if the participant has been matched
        if player.participant.assigned_to_team:
            return 'App02'
        return None


class NoMatch(Page):
    """
    This page informs in the last round(=C.NUM_ROUND) players,
    that we were not able to group them in C.NUM_ROUNDS * C.WAIT_SECONDS.

    Therefore, the player is forwarded to Stage 3 (App03)

    """
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        if player.round_number == C.NUM_ROUNDS:
            player.participant.additional_wait_time = player.round_number - 1
            player.participant.single_player = True
            player.single_player = True
            return 'App03'
        return None


class ContinueWaiting(Page):
    """
    Page is called after the Waiting Time and asking whether participants would like to continue waiting
    """
    form_model = 'player'
    form_fields = ['q_continue_waiting']

    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        if player.q_continue_waiting == 'No':
            player.participant.single_player = True
            player.single_player = True
            player.participant.additional_wait_time = player.round_number - 1
            return 'App03'
        return None


page_sequence = [
    RollingMatching,
    NoMatch,
    ContinueWaiting
]
