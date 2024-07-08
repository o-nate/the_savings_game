"""Defines data collected and functions for the Savings Game"""

import csv
from decimal import *
import json
import random
from re import sub
import statistics

from otree.api import *

from settings import SESSION_CONFIG_DEFAULTS, LANGUAGE_CODE

author = "Nathaniel Archer Lawrence"
doc = """
The Savings Game: Inflation simulation to measure savings and consumption
decision making
"""

if LANGUAGE_CODE == "fr":
    from _static.lexicon_fr import Lexicon
else:
    from _static.lexicon_en import Lexicon


# this is the dict you should pass to each page in vars_for_template,
# enabling you to do if-statements like {{ if fr }} Oui {{ else }} Yes {{ endif }}
which_language = {"en": False, "fr": False}  # noqa
which_language[LANGUAGE_CODE[:2]] = True


def read_csv_catalog():
    """Convert csv with product catalog to dict"""
    with open(__name__ + "/catalog.csv", encoding="utf-8-sig") as file:
        f = file
        rows = [row for row in csv.DictReader(f)]
        for row in rows:
            # Convert values in CSV from string to float
            row["unit_price"] = float(row["unit_price"])
            # Translate name of good
            row["name"] = Lexicon.food
        return rows


def read_csv_inflation():
    """Convert csv with inflation to dict"""
    with open(__name__ + "/animal_spirits.csv", encoding="utf-8-sig") as file:
        f = file
        rows = [row for row in csv.DictReader(f)]
        for row in rows:
            # all values in CSV are string unless you convert them
            # / 12 # convert from the annualized rate
            row["430"] = float(row["430"])
            # / 12 # convert from the annualized rate
            row["1012"] = float(row["1012"])
            row["period"] = int(row["period"])
        return rows


class C(BaseConstants):
    """Experimenter-defined constants, see SESSION_CONFIG_DEFAULTS for
    additional experiment-wide constants that may be used here."""

    NAME_IN_URL = "task"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = SESSION_CONFIG_DEFAULTS["task_duration"]
    TIME_LIMIT = SESSION_CONFIG_DEFAULTS["time_limit"]

    # Consumption constants
    INITIAL_ENDOWMENT = SESSION_CONFIG_DEFAULTS["initial_endowment"]
    INCOME = SESSION_CONFIG_DEFAULTS["income"]
    INTEREST_RATE = SESSION_CONFIG_DEFAULTS["interest_rate"]
    CONSUMPTION_RATE = 1  # Amount of good consumed from stock balance each period
    MONETARY_POLICY = SESSION_CONFIG_DEFAULTS["monetary_policy"]

    # Inflation parameters from csv
    INFLATION = read_csv_inflation()
    # period = ID in dict
    INFLATION_DICT = {row["period"]: row for row in INFLATION}

    # List of products taken from csv file
    PRODUCTS = read_csv_catalog()
    # SKU = 'stock keeping unit' = product ID
    PRODUCTS_DICT = {row["sku"]: row for row in PRODUCTS}


class Subsession(BaseSubsession):
    """Subsession not required for the standard Savings Game"""

    pass


class Group(BaseGroup):
    """Group not required for the standard Savings Game"""

    pass


class Player(BasePlayer):
    """Data collected on each subject's (i.e. Player's) performance.
    Each field represents a column in the data table."""

    total_price = models.CurrencyField(initial=0)
    initial_savings = models.CurrencyField(initial=0)
    cashOnHand = models.CurrencyField(initial=0)
    finalSavings = models.CurrencyField(initial=0)
    finalStock = models.IntegerField(initial=0)
    interestEarned = models.CurrencyField(initial=0)
    decision = models.LongStringField(initial="")
    newPrice = models.FloatField(initial=C.PRODUCTS_DICT["1"]["unit_price"])
    realInterest = models.FloatField()

    # Response time
    responseTime = models.FloatField(initial=0)

    # Inflation estimates
    qualitative_estimate = models.IntegerField(
        label=Lexicon.qualitative_estimate,
        choices=[
            [3, Lexicon.qualitative_est_rapid],
            [2, Lexicon.qualitative_est_moderate],
            [1, Lexicon.qualitative_est_slight],
            [0, Lexicon.qualitative_est_same],
            [-1, Lexicon.qualitative_est_decrease],
        ],
        widget=widgets.RadioSelect,
    )
    qualitative_expectation = models.IntegerField(
        label="",
        choices=[
            [3, Lexicon.qualitative_exp_rapid],
            [2, Lexicon.qualitative_exp_moderate],
            [1, Lexicon.qualitative_exp_slight],
            [0, Lexicon.qualitative_exp_same],
            [-1, Lexicon.qualitative_exp_decrease],
        ],
        widget=widgets.RadioSelect,
    )
    inf_estimate = models.FloatField(
        label=Lexicon.inf_estimate, blank=True, min=-100, max=100
    )
    inf_expectation = models.FloatField(
        label=Lexicon.inf_expectation, blank=True, min=-100, max=100
    )


class Item(ExtraModel):
    """Custom class to create product object and track its price and consumption"""

    player = models.Link(Player)
    sku = models.StringField()
    name = models.StringField()
    quantity = models.IntegerField()
    unit_price = models.CurrencyField()
    newPrice = models.FloatField()


def custom_export(players):
    """Export Item table"""

    yield [
        "session",
        "participant",
        "round_number",
        "sku",
        "name",
        "quantity",
        "unit_price",
        "new_price",
    ]

    # 'filter' without any args returns everything
    items = Item.filter()
    for item in items:
        player = item.player
        participant = player.participant
        sku = item.sku
        name = item.name
        quantity = item.quantity
        unit_price = item.unit_price
        new_price = item.newPrice
        session = player.session
        yield [
            session.code,
            participant.code,
            player.round_number,
            sku,
            name,
            quantity,
            unit_price,
            new_price,
        ]


def qualitative_expectation_choices(player):
    """Change answer options for Month 1 versus others"""
    if player.round_number == 1:
        choices = [
            [3, Lexicon.qualitative_exp_rapid_month_1],
            [2, Lexicon.qualitative_exp_moderate_month_1],
            [1, Lexicon.qualitative_exp_slight_month_1],
            [0, Lexicon.qualitative_exp_same_month_1],
            [-1, Lexicon.qualitative_exp_decrease_month_1],
        ]
    else:
        choices = [
            [3, Lexicon.qualitative_exp_rapid],
            [2, Lexicon.qualitative_exp_moderate],
            [1, Lexicon.qualitative_exp_slight],
            [0, Lexicon.qualitative_exp_same],
            [-1, Lexicon.qualitative_exp_decrease],
        ]
    return choices


def total_price(item: Item):
    """Calculate total price of item with quantity selected"""
    return item.quantity * item.unit_price


def to_dict(item: Item):
    """Convert information about items into a dictionary"""
    return dict(
        sku=item.sku,
        name=item.name,
        quantity=item.quantity,
        total_price=total_price(item),
    )


def live_method(player: Player, data):
    """Send info to HTML components related to savings and consumption decisions"""
    if player.round_number == 1:
        player.newPrice = float(
            C.PRODUCTS_DICT["1"]["unit_price"]
            * (
                1
                + C.INFLATION_DICT[player.round_number][
                    str(player.participant.inflation[(player.participant.round - 1)])
                ]
            )
        )
    else:
        player.newPrice = player.in_round(player.round_number - 1).newPrice * (
            1
            + C.INFLATION_DICT[player.round_number][
                str(player.participant.inflation[(player.participant.round - 1)])
            ]
        )

    # Add and remove from shopping cart
    if "sku" in data:
        sku = data["sku"]
        delta = data["delta"]
        product = C.PRODUCTS_DICT[sku]
        matches = Item.filter(player=player, sku=sku)
        if matches:
            [item] = matches
            item.quantity += delta
            if item.quantity <= 0:
                item.delete()
        else:
            if delta > 0:
                Item.create(
                    player=player,
                    quantity=delta,
                    sku=sku,
                    name=product["name"],
                    unit_price=player.newPrice,
                )

    items = Item.filter(player=player)
    item_dicts = [to_dict(item) for item in items]
    player.total_price = sum([total_price(item) for item in items])
    if player.round_number == 1:
        # fetch previous period's final savings
        player.initial_savings = C.INITIAL_ENDOWMENT
        # fetch previous period's final stock
        player.finalStock = sum([item.quantity for item in items])
        player.interestEarned = 0
        player.realInterest = round(
            100
            * (
                C.INTEREST_RATE
                - C.INFLATION_DICT[player.round_number][
                    str(player.participant.inflation[(player.participant.round - 1)])
                ]
            ),
            2,
        )
    else:
        player.initial_savings = player.in_round(
            player.round_number - 1
        ).finalSavings * (
            1
            + (
                C.INTEREST_RATE
                + (
                    C.MONETARY_POLICY
                    * C.INFLATION_DICT[player.round_number - 1][
                        str(
                            player.participant.inflation[(player.participant.round - 1)]
                        )
                    ]
                )
            )
        )
        player.finalStock = player.in_round(player.round_number - 1).finalStock + sum(
            [item.quantity for item in items]
        )
        player.interestEarned = player.in_round(
            player.round_number - 1
        ).finalSavings * (
            C.INTEREST_RATE
            + (
                C.MONETARY_POLICY
                * C.INFLATION_DICT[player.round_number - 1][
                    str(player.participant.inflation[(player.participant.round - 1)])
                ]
            )
        )
        player.realInterest = round(
            100
            * (
                (
                    C.INTEREST_RATE
                    + (
                        C.MONETARY_POLICY
                        * C.INFLATION_DICT[player.round_number - 1][
                            str(
                                player.participant.inflation[
                                    (player.participant.round - 1)
                                ]
                            )
                        ]
                    )
                )
                - C.INFLATION_DICT[player.round_number][
                    str(player.participant.inflation[(player.participant.round - 1)])
                ]
            ),
            2,
        )
    player.cashOnHand = player.initial_savings + C.INCOME
    player.finalSavings = player.cashOnHand - player.total_price
    player.newPrice = player.newPrice
    player.decision = json.dumps(
        {
            "item": [item.sku for item in items],
            "quantity": [item.quantity for item in items],
            "price": [float(item.unit_price) for item in items],
        }
    )

    return {
        player.id_in_group: dict(
            items=item_dicts,
            total_price=player.total_price,
            initial_savings=player.initial_savings,
            interestEarned=player.interestEarned,
            cashOnHand=player.cashOnHand,
            finalSavings=player.finalSavings,
            finalStock=player.finalStock,
            decision=player.decision,
            newPrice=player.newPrice,
            realInterest=player.realInterest,
        )
    }


def average_early_stock(player):
    """Calculate average stock before first high inflation phase"""
    participant = player.participant
    current_round = participant.round
    inflation = participant.inflation[current_round - 1]
    before = 12 if inflation == 1012 else 30
    stock_values = [v.finalStock for v in player.in_rounds(1, before)]
    print(player.in_round(1).finalStock)
    print("stock values", stock_values)
    if -1 in stock_values:
        b_index = stock_values.index(-1)
        stock_values = stock_values[:b_index]
        print("adjusted stock values", stock_values)
    average_stock = statistics.mean(stock_values)
    return average_stock


def calculate_late_stock(player):
    """Determine how many units were purchase late"""
    participant = player.participant
    current_round = participant.round
    inflation = participant.inflation[current_round - 1]
    before = 12 if inflation == 1012 else 30
    after = before + 3
    end = C.NUM_ROUNDS
    if player.round_number >= before:
        stock_up = end - before - player.in_round(before).finalStock
    else:
        stock_up = 0
    if stock_up > 0:
        late = stock_up - player.in_round(after).finalStock
    else:
        late = 0
    return late


def determine_errors(player):
    """Identify which errors the subject committed"""
    end = C.NUM_ROUNDS
    errors = ["early", "late", "excess"]
    early = average_early_stock(player)
    print("first error", early)
    late = calculate_late_stock(player)
    print("second error", late)
    excess = player.in_round(end).finalStock
    error_dict = {error: amount for error, amount in zip(errors, [early, late, excess])}
    return error_dict


def determine_task_round_text(player):
    """Determine which round the subject is currently on"""
    task_round = player.participant.round
    if task_round == SESSION_CONFIG_DEFAULTS["exp_length_rounds"]:
        return Lexicon.last_round
    elif task_round == 1:
        return Lexicon.first_round
    elif task_round == 2:
        suffix = Lexicon.second
        return Lexicon.round.format(task_round, suffix)
    elif task_round == 3:
        suffix = Lexicon.third
        return Lexicon.round.format(task_round, suffix)
    else:
        suffix = Lexicon.nth
        return Lexicon.round.format(task_round, suffix)


# PAGES
class MyPage(Page):
    """Main screen for player to buy goods and see their savings balance,
    inflation rate, salary, stock of goods and interests recieved"""

    live_method = live_method
    form_model = "player"
    form_fields = ["responseTime"]

    @staticmethod
    def error_message(player, value):
        "Message saying insufficient cash"
        if player.finalSavings < 0:
            return Lexicon.error_task_insufficient_cash.format(Lexicon.total_cash)

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        """Moves to next round after timeout happened"""
        participant = player.participant
        participant.periods_survived = player.round_number
        player.finalStock -= 1

    @staticmethod
    def vars_for_template(player: Player):
        """Send values from this __init__ script to Django components in the HTML"""
        interest_rate = {"real": False, "nominal": True}
        task_int = {"int": False}
        if player.round_number > 1 and player.finalStock == 0:
            player.finalStock = player.in_round(player.round_number - 1).finalStock
        return dict(
            income=cu(C.INCOME),
            **interest_rate,
            nominal_interest_rate=round((C.INTEREST_RATE * 100), 2),
            **task_int,
            Lexicon=Lexicon,
            **which_language,
        )


class Survey1(Page):
    """Asks player their qualitative perception of how much prices changed"""

    form_model = "player"
    form_fields = ["qualitative_estimate"]
    timeout_seconds = C.TIME_LIMIT

    @staticmethod
    def is_displayed(player):
        """Page only displays every 12 months"""
        return player.round_number % 12 == 0

    @staticmethod
    def vars_for_template(player: Player):
        """Send values from this __init__ script to Django components in the HTML"""
        return dict(
            rounds12Before=player.round_number - 11, Lexicon=Lexicon, **which_language
        )


class Survey2(Page):
    """Asks subject their quantitative perception of inflation in %"""

    form_model = "player"
    form_fields = ["inf_estimate"]
    timeout_seconds = C.TIME_LIMIT

    @staticmethod
    def is_displayed(player):
        """Page only displays every 12 months if the participants responds to
        qualitative estimate that they believe prices changed"""
        return player.round_number % 12 == 0 and player.qualitative_estimate != 0

    @staticmethod
    def vars_for_template(player: Player):
        """Send values from this __init__ script to Django components in the HTML"""
        return dict(
            rounds12Before=player.round_number - 11, Lexicon=Lexicon, **which_language
        )


class Survey3(Page):
    "Qualitative inflation expectation question"
    form_model = "player"
    form_fields = ["qualitative_expectation"]
    timeout_seconds = C.TIME_LIMIT

    @staticmethod
    def is_displayed(player):
        """Page only displays every 12 months as well as after month 1"""
        return (
            player.round_number == 1
            or player.round_number % 12 == 0
            and player.round_number != C.NUM_ROUNDS
        )

    @staticmethod
    def vars_for_template(player: Player):
        """Send values from this __init__ script to Django components in the HTML"""
        return dict(
            rounds12Before=player.round_number - 11, Lexicon=Lexicon, **which_language
        )


class Survey4(Page):
    "Asks subject their quantitative expectation of inflation in %"
    form_model = "player"
    form_fields = ["inf_expectation"]
    timeout_seconds = C.TIME_LIMIT

    @staticmethod
    def is_displayed(player):
        """Page only displays every 12 months as well as after month 1 if the
        participants responds to qualitative estimate that they believe prices
        changed"""
        return (player.round_number == 1 and player.qualitative_expectation != 0) or (
            player.round_number % 12 == 0
            and player.round_number != C.NUM_ROUNDS
            and player.qualitative_expectation != 0
        )

    @staticmethod
    def vars_for_template(player: Player):
        """Send values from this __init__ script to Django components in the HTML"""
        return dict(
            rounds12Before=player.round_number - 11, Lexicon=Lexicon, **which_language
        )


class Failed(Page):
    "Page displayed when subject fails to survive until the end of the Saving Game"

    @staticmethod
    def is_displayed(player: Player):
        "Displayed if subject advances with a stock or savings balance less than 0"
        return (
            player.in_round(player.round_number).finalStock < 0
            or player.in_round(player.round_number).finalSavings < 0
        )

    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        "Directs subject to the results app, `session_results`"
        return "session_results"

    @staticmethod
    def vars_for_template(player: Player):
        """Send values from this __init__ script to Django components in the HTML"""
        return dict(Lexicon=Lexicon, **which_language)

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        "Store data to PARTICIPANT_FIELDS to access in other apps, like `session_resulst`"
        participant = player.participant
        participant.periods_survived = player.round_number
        print(
            "participant.periods_survived=player.round_number: ",
            participant.periods_survived,
        )
        # Record payoff
        participant.task_results = 0
        print("results recorded: ", participant.task_results)
        setattr(participant, f"task_results_{participant.round}", float(0))
        print(
            "final recorded result (failed): ",
            getattr(participant, f"task_results_{participant.round}"),
        )
        ## Save number of erroneous units in stock at each benchmark month
        error_dict = determine_errors(player)
        current_round = participant.round
        setattr(participant, f"errors_{current_round}", error_dict)
        print(getattr(participant, f"errors_{current_round}"))
        print("this is the error", error_dict)


class Results(Page):
    """Dsplay game results"""

    @staticmethod
    def is_displayed(player):
        """Dislays page if game finished"""
        return player.round_number == C.NUM_ROUNDS

    # display final results
    @staticmethod
    def vars_for_template(player: Player):
        """Send values from this __init__ script to Django components in the HTML"""
        round_text = determine_task_round_text(player)
        print(f"task_round: {round_text}")

        return dict(
            round_text=round_text,
            final_results=player.finalSavings,
            Lexicon=Lexicon,
            **which_language,
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        """Store data to PARTICIPANT_FIELDS to access in other apps, like `session_resulst`"""
        participant = player.participant

        participant.task_results = float(player.finalSavings)
        setattr(
            participant, f"task_results_{participant.round}", float(player.finalSavings)
        )
        print(
            "Current recorded result: ",
            getattr(participant, f"task_results_{participant.round}"),
        )
        ## Save number of erroneous units in stock at each benchmark month
        error_dict = determine_errors(player)
        current_round = participant.round
        setattr(participant, f"errors_{current_round}", error_dict)
        print(getattr(participant, f"errors_{current_round}"))


page_sequence = [
    MyPage,
    Failed,
    Survey1,
    Survey2,
    Survey3,
    Survey4,
    Results,
]
