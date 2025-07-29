import json
import re

from loguru import logger
from reportlab.lib.units import cm


class CardType(object):
    @staticmethod
    def decode_json(obj):
        return CardType(**obj)

    def __init__(
        self,
        card_type,
        card_type_image,
        group_global_type=None,
        group_cost=None,
        defaultCardCount=10,
        tabTextHeightOffset=0,
        tabCostHeightOffset=-1,
    ):
        self.typeNames = tuple(card_type)
        self.tabImageFile = card_type_image
        self.group_global_type = group_global_type
        self.group_cost = group_cost
        self.defaultCardCount = defaultCardCount
        self.tabTextHeightOffset = tabTextHeightOffset
        self.tabCostHeightOffset = tabCostHeightOffset

    def getTypeDefaultCardCount(self):
        return self.defaultCardCount

    def getTypeNames(self):
        return self.typeNames

    def getTabImageFile(self):
        if not self.tabImageFile:
            return None
        return self.tabImageFile

    def getGroupGlobalType(self):
        return self.group_global_type

    def getGroupCost(self):
        return self.group_cost

    def getTabTextHeightOffset(self):
        return self.tabTextHeightOffset

    def getTabCostHeightOffset(self):
        return self.tabCostHeightOffset


class Card(object):
    sets = None
    types = None
    type_names = None
    bonus_regex = None

    class CardJSONEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, Card):
                return obj.__dict__
            return json.JSONEncoder.default(self, obj)

    @staticmethod
    def decode_json(obj):
        return Card(**obj)

    def __init__(
        self,
        name=None,
        cardset="",
        types=None,
        cost="",
        description="",
        potcost=0,
        debtcost=0,
        extra="",
        count=None,
        card_tag="missing card_tag",
        cardset_tags=None,
        group_tag="",
        group_top=False,
        image=None,
        text_icon=None,
        randomizer=True,
        cardset_tag="",
    ):
        if types is None:
            types = []  # make sure types is a list
        if cardset_tags is None:
            cardset_tags = []  # make sure cardset_tags is a list
        if name is None:
            name = card_tag  # make sure there is a meaningful default name

        self.name = name.strip()
        self.cardset = cardset.strip()
        self.types = types
        self.types_name = ""
        self.cost = cost
        self.description = description
        self.potcost = potcost
        self.debtcost = debtcost
        self.extra = extra
        self.card_tag = card_tag
        self.cardset_tags = cardset_tags
        self.group_tag = group_tag
        self.group_top = group_top
        self.image = image  # used for promo cards with unique "set" images
        self.text_icon = text_icon
        self.cardset_tag = cardset_tag
        self.randomizer = randomizer

        if count is not None:
            if isinstance(count, int):
                self._counts = [count]
            elif isinstance(count, str) and count.isdigit():
                self._counts = [int(count)]
            else:
                raise TypeError(
                    f"{name or card_tag}: Count must be int or str: {count} has type {type(count)}"
                )
        else:
            self._counts = None

    def getCardCount(self) -> int:
        return sum(self.getCardCounts())

    def getCardCounts(self) -> list[int]:
        if self._counts is None:
            return [self.getType().getTypeDefaultCardCount()]
        return self._counts

    def setCardCount(self, value):
        if value == 0:
            self._counts = []
        else:
            self._counts = [int(value)]

    def mergeCardCount(self, value: list):
        if self._counts is None:
            self._counts = value
        else:
            self._counts.extend(value)

    def getStackHeight(self, thickness):
        # return height of the stacked cards in cm.  Using height in cm of a stack of 60 Copper cards as thickness.
        return self.getCardCount() * cm * (thickness / 60.0) + 2

    def getType(self) -> CardType:
        return Card.types[tuple(self.types)]

    def getBonusBoldText(self, text):
        for regex in Card.bonus_regex:
            text = re.sub(regex, "<b>\\1</b>", text)
        return text

    @staticmethod
    def addBonusRegex(bonus):
        # Each bonus_regex matches the bonus keywords to be highlighted
        # This only needs to be done once per language
        if Card.bonus_regex is None:
            # initialize the information holder
            Card.bonus_regex = []

        # Make sure have minimum to to anything
        if not isinstance(bonus, dict):
            return
        if "include" not in bonus:
            return
        if not bonus["include"]:
            return
        if "exclude" not in bonus:
            bonus["exclude"] = []

        # Start processing of lists into a single regex statement
        # (?i) makes this case insensitive
        # (?!\<b\>) and (?!\<\/b\>) prevents matching already bolded items
        # (?!\w) prevents smaller word matches.  Prevents matching "Action" in "Actions"
        if bonus["exclude"]:
            bonus["exclude"].sort(reverse=True)
            exclude_regex = r"(?!\w)(?!\s*(" + "|".join(bonus["exclude"]) + "))"
        else:
            exclude_regex = ""

        bonus["include"].sort(reverse=True)
        include_regex = r"(\+\s*\d+\s*(" + "|".join(bonus["include"]) + "))"
        regex = r"(?i)((?!\<b\>)" + include_regex + exclude_regex + r"(?!\<\/b\>))"
        Card.bonus_regex.append(regex)

    def __repr__(self):
        return '"' + self.name + '"'

    def toString(self):
        return (
            self.name
            + " "
            + self.cardset
            + " "
            + "-".join(self.types)
            + " "
            + self.cost
            + " "
            + self.description
            + " "
            + self.extra
        )

    def isType(self, what):
        return what in self.getType().getTypeNames()

    def isExpansion(self):
        return self.isType("Expansion")

    def isEvent(self):
        return self.isType("Event")

    def isLandmark(self):
        return self.isType("Landmark")

    def isPrize(self):
        return self.isType("Prize")

    def isLandscape(self):
        return self.getType().getGroupGlobalType() is not None

    def get_GroupGlobalType(self):
        return self.getType().getGroupGlobalType()

    def get_GroupCost(self):
        return self.getType().getGroupCost()

    def cost_sort_key(self):
        """Return a tuple that represents the total cost of this card in (coins, potions, debt)
        used for sorting cards by cost.
        Highest cost cards are in order:
        - Types with group cost of "" sort at the very end
        - cards with * since that can mean anything
        - cards with numeric errors
        convert cost (a string) into a number
        """
        if self.get_GroupCost() == "":
            c_cost = 999
        elif not self.cost:
            c_cost = 0  # if no cost, treat as 0
        elif "*" in self.cost:
            c_cost = 998  # make it a really big number
        else:
            try:
                c_cost = int(self.cost)
            except ValueError:
                c_cost = 997  # can't, so make it a really big number

        return c_cost, self.potcost, self.debtcost

    def setImage(self, use_set_icon=False):
        setImage = None
        if not use_set_icon and self.image is not None:
            setImage = self.image
        else:
            if self.cardset_tag in Card.sets:
                if "image" in Card.sets[self.cardset_tag]:
                    setImage = Card.sets[self.cardset_tag]["image"]

        if setImage is None and self.cardset_tag != "base":
            logger.warning(f'no set image for set "{self.cardset}", card "{self.name}"')
        return setImage

    def setTextIcon(self):
        setTextIcon = None
        if self.text_icon:
            setTextIcon = self.text_icon
        else:
            if self.cardset_tag in Card.sets:
                if "text_icon" in Card.sets[self.cardset_tag]:
                    setTextIcon = Card.sets[self.cardset_tag]["text_icon"]

        if setTextIcon is None and self.cardset != "base":
            logger.warning(f'no set text for set "{self.cardset}", card "{self.name}"')
        return setTextIcon

    def isBlank(self):
        return self.isType("Blank")


class BlankCard(Card):
    def __init__(self, num):
        Card.__init__(self, str(num), "extra", ("Blank",), 0)

    def isBlank(self):
        return True
