from os import environ

SESSION_CONFIG_DEFAULTS = dict(real_world_currency_per_point=1, participation_fee=0)
SESSION_CONFIGS = [dict(name='HAPS_PI_Prolific', num_demo_participants=3,
                        app_sequence=[
                            'App00_1_consent',  # Browser check and study information
                            'App00_2_exit',  # check for consent
                            'App00_3_continued',  # Audio and Video-Check, Prolific ID
                            'App01',  # Study Information, SVO, -> Stage 1 (individual)
                            'App01_waiting',  # Wait for 3 active players, 5 x 5 minutes waiting time
                            'App02',  # SpiderGraph(+ WOOP) -> Stage 2 (group)
                            'App03',  # Questionnaires -> Stage 3 (individual)
                            'App04'  # Payout & ThankYou
                              ]),
                   # dict(
                   #     name='Testing',
                   #     display_name="Testing",
                   #     app_sequence=['VM'],
                   #     num_demo_participants=3,
                   # ),
                   ]
LANGUAGE_CODE = 'en'
REAL_WORLD_CURRENCY_CODE = ''
USE_POINTS = False
DEMO_PAGE_INTRO_HTML = ''
PARTICIPANT_FIELDS = [
    # control variables for consent
    'consent',
    'optInConsent',
    # control variables for experiment flow
    'wait_page_arrival',
    'additional_wait_time',
    'assigned_to_team',
    'single_player',
    'confirmed_meeting',
    # Social Value Orientation
    'svo_self',
    'svo_to_other',
    'svo_other',
    # goal variables for visualization
    'vm_pref_achievement',
    'vm_pref_dominance',
    'vm_pref_face',
    'vm_pref_rules',
    'vm_pref_concern',
    'vm_pref_tolerance',
    'others_vm_pref',
    # weakest link game control variables
    'wlg_own_choice',
    'wlg_min_choice',
    'wlg_payoff',
    # payoff control variables
    'attention_fail',
    'attention_fail_cost',
    'additional_payoff',
    'fixed_payoff',
    'total_payoff',
    'final_payoff'
]

SESSION_FIELDS = ['vm_goal_labels',
                  'vm_goal_description']
ROOMS = [
    dict(
        name='PersonalityBehavior',
        display_name='Personality and Behavior in virtual Collaboration'
    )]

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

SECRET_KEY = 'blahblah'
OTREE_REST_KEY = 'otreehapsserverrest3'

# if an app is included in SESSION_CONFIGS, you don't need to list it here
INSTALLED_APPS = ['otree']

OTREE_PRODUCTION=1

# deactivate debug info
DEBUG = False