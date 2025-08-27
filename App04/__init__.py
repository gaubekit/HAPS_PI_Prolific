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

    # TODO: add return-Link
    PROLIFIC_RETURN_LINK = r'<span style="color: orange;"> !!!! OPEN TODO RETURN LINK !!!!</span>"'


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    feedback = models.LongStringField(label="If you have any feedback, you can state it here: ")

    payoff_fix_pound = models.FloatField()
    payoff_bonus_svo_pound = models.FloatField()
    payoff_compensation_wait_pound = models.FloatField()
    payoff_bonus_wlg_pound = models.FloatField()
    payoff_compensation_wlg_dropout_pound = models.FloatField()
    payoff_compensation_svo_other_pound = models.FloatField()
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
        "payoff_compensation_svo_other",
        "payoff_total",
        "svo_to_self",
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
                value = round(value * 0.02, 2)

        except KeyError:
            value = 0
        setattr(player, f"{field}_pound" if field.startswith("payoff_") else field, value)
        print('set field: ', field)


# PAGES
class ThankYouI(Page):
    """
    (I) Page for players who give no consent
    ========================================

        - !NO payoff at all
        - short info that they can't participate without giving consent


    """

    form_model = 'player'
    form_fields = ['feedback']

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


class ThankYouII(Page):
    """
    (II) Page for players who raised a dropout in Stage II
    ========================================

        - payoff_fix
        - payoff_compensation_wait
        - payoff_svo_bonus = svo_to_self + svo_from_other
        - !NO payoff_bonus_wlg !
        - !NO payoff_compensation_wlg !

    """
    form_model = 'player'
    form_fields = ['feedback',]

    @staticmethod
    def is_displayed(player):
        return player.participant.raised_dropout

    @staticmethod
    def vars_for_template(player):
        process_data(player)

        return dict(
            payoff_total_pound=player.payoff_total_pound,
            payoff_fix_pound=player.payoff_fix_pound,
            payoff_bonus_svo_pound=player.payoff_bonus_svo_pound,
            svo_to_self=player.svo_to_self,
            svo_from_other=player.svo_from_other,
            payoff_compensation_wait_pound=player.payoff_compensation_wait_pound,
            payoff_compensation_wlg_dropout_pound=player.payoff_compensation_wlg_dropout_pound,
        )


class ThankYouIII(Page):
    """
    (III) Page for players who formed no team for Stage 2
    ======================================================

        - payoff_fix
        - payoff_compensation_wait
        - payoff_svo_bonus = svo_to_self !NO svo_from_other!
        - payoff_compensation_svo_other
        - !NO bonus_wlg!
        - !NO compensation_wlg!
    """
    form_model = 'player'
    form_fields = ['feedback']

    @staticmethod
    def is_displayed(player):
        return not player.participant.assigned_to_team

    @staticmethod
    def vars_for_template(player):
        process_data(player)

        return dict(
            payoff_total_pound=player.payoff_total_pound,
            payoff_fix_pound=player.payoff_fix_pound,
            payoff_bonus_svo_pound=player.payoff_bonus_svo_pound,
            svo_to_self=player.svo_to_self,
            payoff_compensation_svo_other_pound=player.payoff_compensation_svo_other_pound,
            payoff_compensation_wait_pound=player.payoff_compensation_wait_pound,
            payoff_compensation_wlg_dropout_pound=player.payoff_compensation_wlg_dropout_pound,
        )


class ThankYouIV(Page):
    """
    (IV) Page for players who dropped out during Stage 2
    ======================================================

        - payoff_fix
        - payoff_compensation_wait
        - payoff_svo_bonus = svo_to_self + svo_from_other
        - !NO payoff_bonus_wlg!
        - payoff_compensation_wlg

    """
    form_model = 'player'
    form_fields = ['feedback']

    @staticmethod
    def is_displayed(player):
        # Single player who raised_dropout or not assigned_to_team do not reach this page in the page sequence
        return player.participant.single_player

    @staticmethod
    def vars_for_template(player):
        process_data(player)

        return dict(
            payoff_total_pound=player.payoff_total_pound,
            payoff_fix_pound=player.payoff_fix_pound,
            payoff_bonus_svo_pound=player.payoff_bonus_svo_pound,
            svo_to_self=player.svo_to_self,
            svo_from_other=player.svo_from_other,
            payoff_compensation_wait_pound=player.payoff_compensation_wait_pound,
            payoff_compensation_wlg_dropout_pound=player.payoff_compensation_wlg_dropout_pound,
        )


class ThankYouV(Page):
    """
    (V) Page for players who completed the complete experiment
    ======================================================

        - payoff_fix
        - payoff_compensation_wait
        - payoff_svo_bonus = svo_to_self + svo_from_other
        - payoff_bonus_wlg
        - payoff_compensation_wlg

    """
    form_model = 'player'
    form_fields = ['feedback']

    @staticmethod
    def vars_for_template(player):
        process_data(player)

        return dict(
            payoff_total_pound=player.payoff_total_pound,
            payoff_fix_pound=player.payoff_fix_pound,
            payoff_bonus_svo_pound=player.payoff_bonus_svo_pound,
            svo_to_self=player.svo_to_self,
            svo_from_other=player.svo_from_other,
            payoff_bonus_wlg_pound=player.payoff_bonus_wlg_pound,
            payoff_compensation_wait_pound=player.payoff_compensation_wait_pound,
        )


# Note: Players who not completed  Stage3, never arrive here and have to live with whatever was allocated to their
#       total payoff at the stage where they stopped the experiment

page_sequence = [
    ThankYouI,
    ThankYouII,
    ThankYouIII,
    ThankYouIV,
    ThankYouV,
]
