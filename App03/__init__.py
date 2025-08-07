import random
from otree.api import *


doc = """
    This App handles Stage 3 of the Experiment, where the individuals continue on their own.
    If any particpants where labeled as dropout (because of unsufficant video quality or dropout in the team) they will
    arrive on the Singleplayer Landingpage and continue afterwards as everyone else with..
    
        - Demographics
        - Video Meeting Goals Part II
        - Portrait Value Questionnaire (PVQ)
"""


class C(BaseConstants):
    NAME_IN_URL = 'App03'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    FIX_PAYOFF = 400


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    # Demographics
    age = models.IntegerField(label='How old are you? <br/>(Please enter a valid age between 18 and 65.)', min=18,
                              max=66, error_messages={
            'min_value': 'Please enter an age of at least 18.',
            'max_value': 'Please enter an age of 65 or less.',
            'invalid': 'Please enter a valid age between 18 and 65.',
        }
                              )
    gender = models.IntegerField(label='<br>How do you identify?', blank=False,
                                 choices=[[1, 'male'], [2, 'female'], [3, 'other']])
    ethnicity = models.IntegerField(
        label="<br>What ethnic group do you belong to?", blank=False,
        choices=[[1, 'White'], [2, 'Black'], [3, 'Asian'],
                 [4, 'Mixed'], [5, 'Other'], [6, 'Prefer not to say']])

    education = models.IntegerField(
        label="<br>What is the highest level of <b>education</b> you have completed?</br>",
        choices=[[1, 'less than High School'], [2, 'High School/GED'], [3, 'Some College'],
                 [4, '2-year College degree'], [5, '4-year College degree'],
                 [6, 'Master’s degree'], [7, 'Doctoral degree or Professional Degree (JD, MD)']])

    prolificdays_month = models.IntegerField(
        label="<br>How many days per month do you typically use Prolific?</br> (Please enter a valid number between 0 and 31.)",
        min=0, max=31)
    prolifichours_day = models.IntegerField(
        label="<br>On the days when you use Prolific, how many hours do you typically spend on it?</br> (Please enter a valid number between 1 and 24.)",
        min=1, max=24)
    prolificprimary_income = models.IntegerField(label="Is Prolific your primary source of income?", blank=False,
                                                 choices=[[1, 'Yes'], [2, 'No'], [3, 'Other, please specify']])
    other_income_specify = models.StringField(
        blank=True,
        label=""
    )
    us_state = models.StringField(
        choices=[
            [1, 'Alabama'], [2, 'Alaska'], [3, 'Arizona'], [4, 'Arkansas'],
            [5, 'California'], [6, 'Colorado'], [7, 'Connecticut'], [8, 'Delaware'],
            [9, 'Florida'], [10, 'Georgia'], [11, 'Hawaii'], [12, 'Idaho'],
            [13, 'Illinois'], [14, 'Indiana'], [15, 'Iowa'], [16, 'Kansas'],
            [17, 'Kentucky'], [18, 'Louisiana'], [19, 'Maine'], [20, 'Maryland'],
            [21, 'Massachusetts'], [22, 'Michigan'], [23, 'Minnesota'], [24, 'Mississippi'],
            [25, 'Missouri'], [26, 'Montana'], [27, 'Nebraska'], [28, 'Nevada'],
            [29, 'New Hampshire'], [30, 'New Jersey'], [31, 'New Mexico'], [32, 'New York'],
            [33, 'North Carolina'], [34, 'North Dakota'], [35, 'Ohio'], [36, 'Oklahoma'],
            [37, 'Oregon'], [38, 'Pennsylvania'], [39, 'Rhode Island'], [40, 'South Carolina'],
            [41, 'South Dakota'], [42, 'Tennessee'], [43, 'Texas'], [44, 'Utah'],
            [45, 'Vermont'], [46, 'Virginia'], [47, 'Washington'], [48, 'West Virginia'],
            [49, 'Wisconsin'], [50, 'Wyoming']
        ],
        label="<br>Which U.S state do you currently live in? <br/>"
    )
    other_gender_specify = models.StringField(
        blank=True,
        label=""
    )
    other_ethnicity_specify = models.StringField(
        blank=True,
        label=""
    )

    # Video Meeting Goals - In vide meetings, it is important for me...
    ## 1 ..to add also environmental and sustainability concerns to the discussion.
    vm_universalism_nature = models.IntegerField(widget=widgets.RadioSelect, choices=[-3, -2, -1, 0, 1, 2, 3])  # Environmental Awareness
    ## 2 ..to notice and respond to my teammembers' needs
    vm_benevolence_caring = models.IntegerField(widget=widgets.RadioSelect, choices=[-3, -2, -1, 0, 1, 2, 3])  # Care and Support
    ## 3 ..to be someone my team can fully rely on (e.g., being punctual, prepared, and following through on commitments).
    vm_benevolence_dependability = models.IntegerField(widget=widgets.RadioSelect, choices=[-3, -2, -1, 0, 1, 2, 3])  # Reliable and Trustworthy
    ## 4 ..to feel free, express my own ideas and perspectives, even if they differ from the group.
    vm_selfdirection_thought = models.IntegerField(widget=widgets.RadioSelect, choices=[-3, -2, -1, 0, 1, 2, 3])  # Independent Thinking
    ## 5 ..to make my own decisions and take responsibility for my actions.
    vm_selfdirection_action = models.IntegerField(widget=widgets.RadioSelect, choices=[-3, -2, -1, 0, 1, 2, 3])  # Act Autonomously
    ## 6 ..to have fun, feel good, and enjoy positive interactions.
    vm_hedonism = models.IntegerField(widget=widgets.RadioSelect, choices=[-3, -2, -1, 0, 1, 2, 3])  # Enjoyment
    ## 7 ..to control key tools or have privileges (e.g., screen sharing, hosting rights, decision-making authority).
    vm_power_resources = models.IntegerField(widget=widgets.RadioSelect, choices=[-3, -2, -1, 0, 1, 2, 3])  # Control and Privileges
    ## 8 ..to feel personally and emotionally safe and secure.
    vm_security_personal = models.IntegerField(widget=widgets.RadioSelect, choices=[-3, -2, -1, 0, 1, 2, 3])  # Personal Safety
    ## 9 ..to be part of a resilient and reliable team.
    vm_security_societal = models.IntegerField(widget=widgets.RadioSelect, choices=[-3, -2, -1, 0, 1, 2, 3])  # Group Safety
    ##  ..to signal attenition to the questions by moving the slider to one (positive)
    vm_attention = models.IntegerField(widget=widgets.RadioSelect, choices=[-3, -2, -1, 0, 1, 2, 3])
    ## 10 ..to maintain traditional values and ways of thinking.
    vm_tradition = models.IntegerField(widget=widgets.RadioSelect, choices=[-3, -2, -1, 0, 1, 2, 3])  # Traditions and Norms
    ## 11 ..to avoid doing anything that might upset or annoy others (e.g., speaking out of turn, causing technical issues).
    vm_conformity_interpersonal = models.IntegerField(widget=widgets.RadioSelect, choices=[-3, -2, -1, 0, 1, 2, 3])  # Avoiding Conflicts
    ## 12 ..to be humble and not put myself above others.
    vm_humility = models.IntegerField(widget=widgets.RadioSelect, choices=[-3, -2, -1, 0, 1, 2, 3])  # Stay Modest
    ## 13 ..to be engaged by new topics, fresh perspectives, unexpected ideas, and dynamic discussions
    vm_stimulation = models.IntegerField(widget=widgets.RadioSelect, choices=[-3, -2, -1, 0, 1, 2, 3])  # Novelty and Excitement


    # Portrait Value Questionnaire (PVQ) - It is important to him/her ...
    ## PVQ Page 1
    pvq1 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..to form his/her views independently.
    pvq2 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..that his/her country is secure and stable.
    pvq3 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..to have a good timeslots.
    pvq4 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..to avoid upsetting other people.
    pvq5 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..that the weak and vulnerable in society be protected.
    pvq6 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..that people do what he/she says they should.
    pvq7 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..never to think he/she deserves more than other people.
    pvq8 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..to care for nature.
    pvq9 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..that no one should ever shame him/her.
    pvq10 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..always to look for different things to do.
    ## PVQ Page 2
    pvq11 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..to take care of people he/she is close to.
    pvq12 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..to have the power that money can bring.
    pvq13 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..to avoid disease and protect his/her health.
    pvq14 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..to be tolerant toward all kinds of people and groups.
    pvq15 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..never to violate rules or regulations.
    pvq16 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..to make his/her own decisions about his/her life.
    pvq17 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..to have ambitions in life.
    pvq18 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..to maintain traditional values and ways of thinking.
    pvq_attention_1 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..to indicate that the person is "Not like me at all" to show that he/she is answering the questions attentively..
    pvq19 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..that people he/she knows have full confidence in him/her.
    ## PVQ Page 3
    pvq20 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..to be wealthy.
    pvq21 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..to take part in activities to defend nature.
    pvq22 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..never to annoy anyone.
    pvq23 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..to develop his/her own opinions.
    pvq24 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..to protect his/her public image.
    pvq25 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..to help the people dear to him/her.
    pvq26 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..to be personally safe and secure.
    pvq27 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..to be a dependable and trustworthy friend.
    pvq28 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..to take risks that make life exciting.
    pvq29 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..to have the power to make people do what he/she wants.
    ## PVQ Page 4
    pvq30 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..to plan his/her activities independently.
    pvq31 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..to follow rules even when no one is watching.
    pvq32 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..to be very successful.
    pvq_attention_2 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..to indicate that the person is "Not like me " to show that he/she is answering the questions attentively.
    pvq33 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..to follow his/her family’s customs or the customs of a religion.
    pvq34 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..to listen to and understand people who are different from him/her.
    pvq35 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..to have a strong state that can defend its citizens.
    pvq36 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..to enjoy life’s pleasures.
    pvq37 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..that every person in the world have equal opportunities in life.
    pvq38 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..to be humble.
    ## PVQ Page 5
    pvq39 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..to figure things out himself/herself.
    pvq40 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..to honor the traditional practices of his/her culture.
    pvq41 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..to be the one who tells others what to do.
    pvq42 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..to obey all the laws.
    pvq43 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..to have all sorts of new experiences.
    pvq44 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..to own expensive things that show his/her wealth.
    pvq45 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..to protect the natural environment from destruction or pollution.
    pvq46 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..to take advantage of every opportunity to have fun.
    pvq47 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..to concern himself/herself with every need of his/her dear ones.
    pvq48 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..that people recognize what he/she achieves.
    ## PVQ Page 6
    pvq49 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..never to be humiliated.
    pvq50 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..that his/her country protect itself against all threats.
    pvq51 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..never to make other people angry.
    pvq52 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..that everyone be treated justly, even people he/she doesn’t know.
    pvq53 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..to avoid anything dangerous.
    pvq_attention_3 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..to indicate that the person is "A little like me" to show that he/she is answering the questions attentively.
    pvq54 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..to be satisfied with what he/she has and not ask for more.
    pvq55 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..that all his/her friends and family can rely on him/her completely.
    pvq56 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..to be free to choose what he/she does by himself/herself.
    pvq57 = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2, 3, 4, 5, 6])  # ..to accept people even when he/she disagrees with them.

    # attention checks
    attention_check = models.IntegerField(initial=0)  # used to count attention checks

    # Computed subscale scores
    universalism_nature = models.FloatField()  # Universalism-Nature: Preservation of the natural environment
    universalism_concern = models.FloatField()  # Universalism-Concern: Commitment to equality, justice, and protection for all people
    universalism_tolerance = models.FloatField()  # Universalism-Tolerance: Acceptance and understanding of those who are different from oneself
    benevolence_caring = models.FloatField()  # Benevolence-Caring: Devotion to the welfare of in-group members
    benevolence_dependability = models.FloatField()  # Benevolence-Dependability: Being a reliable and trustworthy member of the in-group
    selfdirection_thought = models.FloatField()  # Self-Direction-Thought: The freedom to cultivate one’s own ideas and abilities
    selfdirection_action = models.FloatField()  # Self-Direction-Action: The freedom to determine one’s own actions
    hedonism = models.FloatField()  # Hedonism: Definition unchanged
    achievement = models.FloatField()  # Achievement: Definition unchanged
    power_dominance = models.FloatField()  # Power-Dominance: Power through exercising control over people
    power_resources = models.FloatField()  # Power-Resources: Power through control of material and social resources
    face = models.FloatField()  # Face: Security and power through maintaining one’s public image and avoiding humiliation
    security_personal = models.FloatField()  # Security-Personal: Safety in one’s immediate environment
    security_societal = models.FloatField()  # Security-Societal: Safety and stability in the wider society
    tradition = models.FloatField()  # Tradition: Maintaining and preserving cultural, family, or religious traditions
    conformity_rules = models.FloatField()  # Conformity-Rules: Compliance with rules, laws, and formal obligations
    conformity_interpersonal = models.FloatField()  # Conformity-Interpersonal: Avoidance of upsetting or harming other people
    humility = models.FloatField()  # Humility: Recognizing one’s insignificance in the larger scheme of things
    stimulation = models.FloatField()  # Stimulation: Excitement, novelty, and change

    # payoff # TODO
    total_payoff = models.FloatField()
    additional_payoff = models.FloatField()
    svo_payoff = models.FloatField()
    wlg_payoff = models.FloatField()
    attention_fail_cost = models.FloatField()
    final_payoff = models.FloatField()


def pvq_scale_calc(pvq1, pvq2, pvq3):
    return pvq1 + pvq2 + pvq3

def age_error_message(player: Player, value):
    if value < 18 or value > 66:
            return "You need to be between 18 years and 66 years to participate."
    return None

# ====================================================== PAGES ====================================================== #
class LandingPageSinglePlayer(Page):
    @staticmethod
    def is_displayed(player):
        return player.participant.single_player


class QuestDemographics(Page):
    form_model = 'player'
    form_fields = ['prolificdays_month', 'prolifichours_day', 'prolificprimary_income',
                   'other_income_specify', 'us_state',  'gender', 'age', 'education', 'ethnicity',
                   'other_ethnicity_specify', 'other_gender_specify']


class VideoMeetingBehaviorII(Page):
    """
        This page asks about the video meeting goals (as in App2). The goal is to correlate these items
        with the low level constructs of the PVQ which are asked in SurveyPVQ1 to SurveyPVQ6
    """
    form_model = 'player'
    form_fields = ['vm_universalism_nature', 'vm_benevolence_caring', 'vm_benevolence_dependability',
                   'vm_selfdirection_thought', 'vm_selfdirection_action', 'vm_attention', 'vm_hedonism',
                   'vm_power_resources', 'vm_security_personal', 'vm_security_societal', 'vm_tradition',
                   'vm_conformity_interpersonal', 'vm_humility', 'vm_stimulation']

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.vm_attention != 1:
            player.attention_check += 1


class SurveyPVQ1(Page):
    form_model = 'player'
    form_fields = ['pvq1', 'pvq2', 'pvq3', 'pvq4', 'pvq5', 'pvq6', 'pvq7', 'pvq8', 'pvq9', 'pvq10']


class SurveyPVQ2(Page):
    form_model = 'player'
    form_fields = ['pvq11', 'pvq12', 'pvq13', 'pvq14', 'pvq_attention_1', 'pvq15', 'pvq16', 'pvq17', 'pvq18', 'pvq19']

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.pvq_attention_1 != 1:
            player.attention_check += 1


class SurveyPVQ3(Page):
    form_model = 'player'
    form_fields = ['pvq20', 'pvq21', 'pvq22', 'pvq23', 'pvq24', 'pvq25', 'pvq26', 'pvq27', 'pvq28', 'pvq29', ]


class SurveyPVQ4(Page):
    form_model = 'player'
    form_fields = ['pvq30', 'pvq31', 'pvq32', 'pvq33', 'pvq34', 'pvq_attention_2', 'pvq35', 'pvq36', 'pvq37', 'pvq38', ]

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.pvq_attention_2 != 2:
            player.attention_check += 1


class SurveyPVQ5(Page):
    form_model = 'player'
    form_fields = ['pvq39', 'pvq40', 'pvq41', 'pvq42', 'pvq43', 'pvq44', 'pvq45', 'pvq46', 'pvq47', 'pvq48']



class SurveyPVQ6(Page):
    form_model = 'player'
    form_fields = ['pvq49', 'pvq50', 'pvq51', 'pvq52', 'pvq53', 'pvq_attention_3', 'pvq54', 'pvq55', 'pvq56', 'pvq57']

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.pvq_attention_3 != 3:
            player.attention_check += 1

        # pvq construct calculation
        player.universalism_nature = pvq_scale_calc(player.pvq8, player.pvq21, player.pvq45)
        player.universalism_concern = pvq_scale_calc(player.pvq5, player.pvq37, player.pvq52)
        player.universalism_tolerance = pvq_scale_calc(player.pvq14, player.pvq34, player.pvq57)
        player.benevolence_caring = pvq_scale_calc(player.pvq11, player.pvq25, player.pvq47)
        player.benevolence_dependability = pvq_scale_calc(player.pvq19, player.pvq27, player.pvq55)
        player.selfdirection_thought = pvq_scale_calc(player.pvq1, player.pvq23, player.pvq39)
        player.selfdirection_action = pvq_scale_calc(player.pvq16, player.pvq30, player.pvq56)
        player.hedonism = pvq_scale_calc(player.pvq3, player.pvq36, player.pvq46)
        player.achievement = pvq_scale_calc(player.pvq17, player.pvq32, player.pvq48)
        player.power_dominance = pvq_scale_calc(player.pvq6, player.pvq29, player.pvq41)
        player.power_resources = pvq_scale_calc(player.pvq12, player.pvq20, player.pvq44)
        player.face = pvq_scale_calc(player.pvq9, player.pvq24, player.pvq49)
        player.security_personal = pvq_scale_calc(player.pvq13, player.pvq26, player.pvq53)
        player.security_societal = pvq_scale_calc(player.pvq2, player.pvq35, player.pvq50)
        player.tradition = pvq_scale_calc(player.pvq18, player.pvq33, player.pvq40)
        player.conformity_rules = pvq_scale_calc(player.pvq15, player.pvq31, player.pvq42)
        player.conformity_interpersonal = pvq_scale_calc(player.pvq4, player.pvq22, player.pvq51)
        player.humility = pvq_scale_calc(player.pvq7, player.pvq38, player.pvq54)
        player.stimulation = pvq_scale_calc(player.pvq10, player.pvq28, player.pvq43)


        # TODO: payoff Logic anpassen!!!!

        # # payoff calculation
        # if player.participant.svo_other:
        #     # if a team could form, take the svo self, svo other and WLG payoff
        #     player.additional_payoff = (player.participant.svo_self
        #                                       + player.participant.svo_other
        #                                       + player.participant.wlg_payoff)
        #
        # else:
        #     # if no team could form, compensate by 2 times svo self and 200 ECU
        #     player.additional_payoff = (player.participant.svo_self * 2) + 200
        #
        # player.participant.additional_payoff = round(player.additional_payoff, 2)
        # player.participant.fixed_payoff = C.FIX_PAYOFF
        # player.total_payoff = C.FIX_PAYOFF + player.additional_payoff
        # player.participant.total_payoff = player.total_payoff
        # print(player.total_payoff)
        # player.participant.attention_fail = player.attention_check
        # player.attention_fail_cost = round(1 - (player.attention_check / 5), 2)  # reduce payoff up 80 % (20 % per failed attention check)
        # player.participant.attention_fail_cost = player.attention_fail_cost
        # player.final_payoff = player.total_payoff * player.attention_fail_cost
        # player.participant.final_payoff = round(player.final_payoff, 2)


page_sequence = [
    LandingPageSinglePlayer,
    QuestDemographics,
    VideoMeetingBehaviorII,
    SurveyPVQ1,
    SurveyPVQ2,
    SurveyPVQ3,
    SurveyPVQ4,
    SurveyPVQ5,
    SurveyPVQ6,
]
