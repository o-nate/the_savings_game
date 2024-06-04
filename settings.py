from os import environ, getenv

from dotenv import load_dotenv

# * Retrieve API credentials
load_dotenv()
SECRET = getenv("SECRET_KEY")

# * Define conversion between experimental currency and payment currency
CONVERSION_FACTOR = 750

SESSION_CONFIGS = [
    dict(
        name="init",
        display_name="init",
        app_sequence=["init"],
        num_demo_participants=1,
        day="0",
    ),
    dict(
        name="task_1",
        display_name="Task 1",
        app_sequence=[
            "task_instructions",
            "task",
            "task_int",
            "redirectapp",
        ],
        num_demo_participants=1,
    ),
    dict(
        name="task_2",
        display_name="Task 2",
        app_sequence=["task", "redirectapp"],
        num_demo_participants=1,
    ),
    dict(
        name="sessionResults",
        display_name="sessionResults",
        app_sequence=["sessionResults", "redirecttopayment"],
        num_demo_participants=1,
    ),
    dict(
        name="instructions",
        display_name="Instructions",
        app_sequence=[
            "filler",
            "task_instructions",
            "redirectapp",
        ],
        num_demo_participants=1,
    ),
    dict(
        name="intervention_feedback",
        display_name="Intervention avec feedback",
        app_sequence=["filler", "task", "task_int", "redirectapp"],
        num_demo_participants=1,
    ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    inflation=[
        # * Define potential inflation sequences
        [430, 430],
        # [1012, 1012],
        # [430, 1012],
        # [1012, 430],
    ],
    real_world_currency_per_point=1.00,
    conversion_factor=CONVERSION_FACTOR,
    participation_fee=(5 * CONVERSION_FACTOR),
    doc="",
    task_duration=120,  # ! Enter the number of months for the task
    initial_endowment=863.81,
    income=4.32,
    interest_rate=0.22773 / 12,
    monetary_policy=0,
    time_limit=60,
    test_mode=True,  # !!!!!! Set to false before running the experiment
)

PARTICIPANT_FIELDS = [
    "instructions",
    "reaction_times",
    "periods_survived",
    "task_results",
    "task_results_1",
    "errors_1",
    "task_results_2",
    "errors_2",
    "day_1",
    "inflation",
    "round",
    "day_room_number",
    "error",
    "last_room_day",
    "next_room",
    "err_msg",
    "vars_done",
]

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = "fr"

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = "₮"
USE_POINTS = False  # ! Set to False so that currency symbol appears
# ! (must convert back to actual currency before calculating final remuneration)

ADMIN_USERNAME = "admin"
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get("OTREE_ADMIN_PASSWORD")

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = SECRET
