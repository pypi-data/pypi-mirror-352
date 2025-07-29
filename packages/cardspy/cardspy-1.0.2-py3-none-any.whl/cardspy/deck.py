"""Deck"""
import random
from typing import List
from .rank import (
    RA,
    RK,
    RQ,
    RJ,
    RT,
    R9,
    R8,
    R7,
    R6,
    R5,
    R4,
    R3,
    R2,
)
from .card import Card, extract_cards, extract_cards_key


CLUBS = 0x1111111111111
DIAMONDS = 0x2222222222222
HEARTS = 0x4444444444444
SPADES = 0x8888888888888

SAME_RANKS = [
    0xF, 0xF0, 0xF00, 0xF000, 0xF0000, 0xF00000,
    0xF000000, 0xF0000000, 0xF00000000, 0xF000000000,
    0xF0000000000, 0xF00000000000, 0xF000000000000
]

RANKS_DESC = [RA, RK, RQ, RJ, RT, R9, R8, R7, R6, R5, R4, R3, R2]

FULL_DECK_MASK = (1 << 52) - 1


class Deck:
    """Deck"""
    def __init__(self) -> None:
        self.key = FULL_DECK_MASK
        self._cards: List[int] = [(1 << i) for i in range(52)]

    def clear(self) -> None:
        """Clear the deck"""
        self.key = 0
        self._cards = []

    def reset(self) -> None:
        """Reset the deck"""
        self.key = FULL_DECK_MASK
        self._cards = [(1 << i) for i in range(52)]

    def contains(self, cards_key: int) -> bool:
        """Check if the deck contains a list of cards

        Args:
            cards_key (int): List of cards to check

        Returns:
            bool: True if the deck contains all the cards, False otherwise
        """
        return cards_key & self.key == cards_key

    def get_cards(self) -> List[Card]:
        """Get all cards in the deck

        Returns:
            List[Card]: List of cards in the deck
        """
        return extract_cards(self.key)

    def shuffle(self) -> None:
        """
        Reset the deck to a full 52-card mask and generate
        a new random ordering of the 52 single-card masks.
        """
        # generate one mask per card (bits 0..51) and shuffle
        self._cards = [(1 << i) for i in range(52)]
        random.shuffle(self._cards)

    def count(self) -> int:
        """Returns the number of cards in the deck"""
        return self.key.bit_count()

    def add_card(self, card_key: int) -> None:
        """Add a card to the deck"""
        self.key |= card_key
        self._cards.append(card_key)

    def add_cards(self, cards_key: int) -> None:
        """Add a list of cards to the deck"""
        self.key |= cards_key
        self._cards.extend(extract_cards_key(cards_key))

    def remove_card(self, card_key: int) -> None:
        """Remove a card from the deck"""
        self.key &= ~card_key
        self._cards.remove(card_key)

    def remove_cards(self, cards_key: int) -> None:
        """Remove a list of cards from the deck"""
        self.key &= ~cards_key
        self._cards = [
            card for card in self._cards
            if card not in extract_cards_key(cards_key)
        ]

    def deal_cards(self, count: int = 1, shuffle: bool = True) -> int:
        """Deal cards from the deck

        Args:
            count (int, optional): Number of cards to deal. Defaults to 1.

        Returns:
            List[Card]: List of cards dealt
        """
        if count < 0:
            raise ValueError("Cannot draw a negative number of cards")
        if len(self._cards) < count:
            raise ValueError(
                f"Only {len(self._cards)} cards remaining; cannot draw {count}"
            )

        if shuffle:
            random.shuffle(self._cards)

        deal_masks = self._cards[:count]
        # remove them from the deck order
        self._cards = self._cards[count:]

        # combine all dealt bits into one mask
        result_mask = 0
        for m in deal_masks:
            result_mask |= m

        # clear these bits from the deck’s remaining key
        self.key &= ~result_mask
        return result_mask

    def deal_specific_card(self, card_key: int) -> int:
        """Deal a specific card from the deck"""
        if not self.contains(card_key):
            raise ValueError("Card not in deck")
        self.remove_card(card_key)
        return card_key

    def deal_specific_cards(self, cards_key: int) -> int:
        """Deal specific cards from the deck"""
        for card_key in extract_cards_key(cards_key):
            self.deal_specific_card(card_key)
        return cards_key
