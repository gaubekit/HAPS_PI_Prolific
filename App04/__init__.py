from otree.api import *

c = cu

doc = ' Thank You + payoff, depending on Consent und Team forming yes/no'


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


# class ThankYouExit(Page):
#     form_model = 'player'
#     form_field = ['feedback',]
#
#     @staticmethod
#     def is_displayed(player):
#         return player.participant.consent == 0



class ThankYou(Page):
    form_model = 'player'
    form_fields = ['feedback']

    # @staticmethod
    # def is_displayed(player):
    #     return player.participant.consent == 1 and not player.participant.single_player

    # TODO: get payoff information from participants field and display it on page
    # @staticmethod
    # def vars_for_template(player):
    #     return dict(
    #         svo_to_self=player.participant.svo_to_self,
    #         svo_to_other=player.participant.svo_to_other,
    #         fixed_payoff=player.participant.fixed_payoff,
    #         additional_payoff=player.participant.additional_payoff,
    #         attention_fail_cost=player.participant.attention_fail_cost,
    #         wlg_own_choice=player.participant.wlg_own_choice,
    #         wlg_min_choice=player.participant.wlg_min_choice,
    #         wlg_payoff=player.participant.wlg_payoff,
    #         total_payoff=player.participant.total_payoff,
    #         final_payoff=player.participant.final_payoff,
    #         attention_fail=player.participant.attention_fail
    #     )


# class ThankYouByPass(Page):
#     form_model = 'player'
#
#     @staticmethod
#     def is_displayed(player):
#         return player.participant.consent == 1 and player.participant.single_player
#
#     # # TODO: get payoff information from participants field and display it on page
#     # @staticmethod
#     # def vars_for_template(player):
#     #     return dict(
#     #         svo_to_self=player.participant.svo_to_self,
#     #         fixed_payoff=player.participant.fixed_payoff,
#     #         additional_payoff=player.participant.additional_payoff,
#     #         attention_fail_cost=player.participant.attention_fail_cost,
#     #         total_payoff=player.participant.total_payoff,
#     #         final_payoff=player.participant.final_payoff,
#     #         attention_fail=player.participant.attention_fail
#     #     )

page_sequence = [ThankYou, ]
# page_sequence = [ThankYou, ThankYouByPass, ThankYouExit]
