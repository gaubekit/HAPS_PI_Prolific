from otree.api import *

c = cu

doc = ("""
 
    This App handles the ExitPage, including:
    
        - Thank You
        - Feedback Question
        - Payoff Information + Reasoning
        - storing control and payoff participant-vars in player fields
        - forwarding to App05 -> ReturnToProlific
    
    Participants can reach App04 by:
    
        (I)   giving no consent (App00_1 & App00_2) -> no payoff
        (II)  completing the study, raised dropout in stage 2 -> payoff Stage 1 & 3, no payoff wlg
        (III)  completing the study, excluding Stage 2 -> payoff Stage 1 & 3
        (IV) completing the study, dropout happened in Stage 2  -> payoff Stage 1 & 3, compensation wlg, svo_from_other
        (V)   completing the study, including Stage 2  -> payoff Stage 1, 2 & 3
    
""")


class C(BaseConstants):
    NAME_IN_URL = 'App04'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    feedback = models.LongStringField(label="If you have any feedback, you can state it here:")

    payoff_fix_pound = models.FloatField()
    payoff_bonus_svo_pound = models.FloatField()
    payoff_compensation_wait_pound = models.FloatField()
    payoff_bonus_wlg_pound = models.FloatField()
    payoff_compensation_wlg_dropout_pound = models.FloatField()
    payoff_total_pound = models.FloatField()

    svo_to_self = models.FloatField()
    svo_from_other = models.FloatField()
    svo_to_other = models.FloatField()
    wlg_own_choice = models.IntegerField()
    wlg_min_choice = models.FloatField()
    additional_wait_time = models.IntegerField()

    raised_dropout = models.BooleanField()
    single_player = models.BooleanField()
    assigned_to_team = models.BooleanField()


# HELPER FUNCTION
def process_data(player):
    """ Helper function, called in vars_for_template to set player fields and provide payout info in pound"""
    participant_fields = [
        "payoff_fix",
        "payoff_bonus_svo",
        "payoff_compensation_wait",
        "payoff_bonus_wlg",
        "payoff_compensation_wlg_dropout",
        "payoff_total",
        "svo_from_other",
        "svo_to_other",
        "wlg_own_choice",
        "wlg_min_choice",
        "raised_dropout",
        "additional_wait_time",
        "single_player",
        "assigned_to_team",
    ]

    for field in participant_fields:
        try:
            value = getattr(player.participant, field)
            if field.startswith("payoff_"):
                value = round(value * 0.2)
        except KeyError:
            value = 0
        setattr(player, f"{field}_pound" if field.startswith("payoff_") else field, value)


# PAGES
class ThankYouI(Page):
    """
    (I) Page for players who give no consent
    ========================================

        - no payoff
        - short info that they can't participate without giving consent


    """

    form_model = 'player'
    form_field = ['feedback',]

    @staticmethod
    def is_displayed(player):
        try:
            return not player.participant.consent
        # Players that not eligible (willing to use Chrome etc.) raise TypeError(None) and enter this page
        # these are also forwarded to App05 and not reach ThankYouII etc.
        except TypeError:
            return True

    @staticmethod
    def vars_for_template(player):

        process_data(player)

        return dict(
            payoff_fix_pound=player.payoff_total_pound)

    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        return 'App05'


class ThankYouII(Page):
    """
    (II) Page for players who raised a dropout in Stage II
    ========================================

        - no payoff

    """
    form_model = 'player'
    form_field = ['feedback',]

    @staticmethod
    def is_displayed(player):
        return player.participant.raised_dropout

    @staticmethod
    def vars_for_template(player):

        process_data(player)

        return dict(
            payoff_fix_pound=player.payoff_total_pound)

    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        return 'App05'


class ThankYouIII(Page):
    """
    (III) Page for players who formed no team for Stage 2
    ======================================================

        - payoff WLG

    """
    form_model = 'player'
    form_field = ['feedback', ]

    @staticmethod
    def is_displayed(player):
        return not player.participant.assigned_to_team

    @staticmethod
    def vars_for_template(player):
        process_data(player)

        return dict(
            payoff_fix_pound=player.payoff_total_pound)

    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        return 'App05'


class ThankYouIV(Page):
    """
    (IV) Page for players dropped out during Stage 2
    ======================================================

        - payoff WLG

    """
    form_model = 'player'
    form_field = ['feedback', ]

    @staticmethod
    def is_displayed(player):
        # Single player who raised_dropout or not assigned_to_team do not reach this page in the page sequence
        return player.participant.single_player

    @staticmethod
    def vars_for_template(player):
        process_data(player)

        return dict(
            payoff_fix_pound=player.payoff_total_pound)

    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        return 'App05'


class ThankYouV(Page):
    form_model = 'player'
    form_fields = ['feedback']

    @staticmethod
    def vars_for_template(player):
        process_data(player)

        return dict(
            payoff_fix_pound=player.payoff_total_pound)

    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        return 'App05'


page_sequence = [
    ThankYouI,
    ThankYouII,
    ThankYouIII,
    ThankYouIV,
    ThankYouV,
]
