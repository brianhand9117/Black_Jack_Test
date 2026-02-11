import random
from enum import Enum


class Suit(Enum):
    """Card suits"""
    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"
    SPADES = "♠"


class Rank(Enum):
    """Card ranks"""
    ACE = ("A", 11)
    TWO = ("2", 2)
    THREE = ("3", 3)
    FOUR = ("4", 4)
    FIVE = ("5", 5)
    SIX = ("6", 6)
    SEVEN = ("7", 7)
    EIGHT = ("8", 8)
    NINE = ("9", 9)
    TEN = ("10", 10)
    JACK = ("J", 10)
    QUEEN = ("Q", 10)
    KING = ("K", 10)


class Card:
    """Represents a single playing card"""
    
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
    
    def __str__(self):
        return f"{self.rank.value[0]}{self.suit.value}"
    
    def get_value(self):
        """Returns the card value (handles Ace as 11 or 1)"""
        return self.rank.value[1]


class Deck:
    """Manages a deck of playing cards"""
    
    def __init__(self, num_decks=1):
        self.cards = []
        self.num_decks = num_decks
        self.reset()
    
    def reset(self):
        """Create a fresh deck and shuffle"""
        self.cards = []
        for _ in range(self.num_decks):
            for suit in Suit:
                for rank in Rank:
                    self.cards.append(Card(suit, rank))
        random.shuffle(self.cards)
    
    def deal_card(self):
        """Deal a card from the deck"""
        if len(self.cards) < 10:  # Reshuffle when deck is low
            self.reset()
        return self.cards.pop()


class Hand:
    """Represents a player's hand of cards"""
    
    def __init__(self):
        self.cards = []
    
    def add_card(self, card):
        """Add a card to the hand"""
        self.cards.append(card)
    
    def get_value(self):
        """Calculate hand value (handles Ace as 1 or 11)"""
        value = 0
        aces = 0
        
        for card in self.cards:
            value += card.get_value()
            if card.rank == Rank.ACE:
                aces += 1
        
        # Adjust for aces if busting
        while value > 21 and aces > 0:
            value -= 10
            aces -= 1
        
        return value
    
    def is_blackjack(self):
        """Check if hand is a natural blackjack (21 with 2 cards)"""
        return len(self.cards) == 2 and self.get_value() == 21
    
    def is_bust(self):
        """Check if hand exceeds 21"""
        return self.get_value() > 21
    
    def display(self, name, hide_first=False):
        """Display the hand"""
        cards_str = ", ".join([f"[{card}]" for card in self.cards])
        value = "?" if hide_first else str(self.get_value())
        print(f"{name}: {cards_str} (Value: {value})")


class BlackjackGame:
    """Main blackjack game class"""
    
    def __init__(self, player_balance=100):
        self.deck = Deck(num_decks=6)  # Casino typically uses 6 decks
        self.player_balance = player_balance
        self.player_hand = None
        self.dealer_hand = None
        self.current_bet = 0
        self.game_over = False
    
    def display_header(self):
        """Display game header"""
        print("\n" + "=" * 50)
        print(" " * 15 + "BLACKJACK")
        print("=" * 50)
        print(f"Player Balance: ${self.player_balance:.2f}")
        print("=" * 50)
    
    def place_bet(self):
        """Get player's bet"""
        while True:
            try:
                bet = float(input(f"\nPlace your bet (balance: ${self.player_balance:.2f}): $"))
                if bet <= 0 or bet > self.player_balance:
                    print("Invalid bet amount!")
                    continue
                self.current_bet = bet
                self.player_balance -= bet
                return
            except ValueError:
                print("Please enter a valid number!")
    
    def deal_initial_hands(self):
        """Deal initial 2 cards to player and dealer"""
        self.player_hand = Hand()
        self.dealer_hand = Hand()
        
        # Deal 2 cards to each
        for _ in range(2):
            self.player_hand.add_card(self.deck.deal_card())
            self.dealer_hand.add_card(self.deck.deal_card())
    
    def show_hands(self, hide_dealer_first=True):
        """Display current hands"""
        print("\n" + "-" * 50)
        if hide_dealer_first:
            self.dealer_hand.display("DEALER", hide_first=True)
        else:
            self.dealer_hand.display("DEALER")
        self.player_hand.display("YOU")
        print("-" * 50)
    
    def check_initial_blackjack(self):
        """Check for natural blackjacks"""
        player_bj = self.player_hand.is_blackjack()
        dealer_bj = self.dealer_hand.is_blackjack()
        
        if player_bj and dealer_bj:
            print("\n🎰 Both have Blackjack! Push (Tie)")
            self.player_balance += self.current_bet
            return True
        elif player_bj:
            print("\n🎰 BLACKJACK! You Win!")
            self.player_balance += self.current_bet * 2.5  # 3:2 payout
            return True
        elif dealer_bj:
            print("\n🎰 Dealer has Blackjack! You Lose!")
            return True
        
        return False
    
    def player_turn(self):
        """Handle player's actions"""
        while True:
            self.show_hands(hide_dealer_first=True)
            
            if self.player_hand.is_bust():
                print("\n💥 BUST! You exceeded 21. You Lose!")
                return
            
            print("\nOptions: [H]it, [S]tand, [D]ouble Down")
            choice = input("Choose action: ").upper()
            
            if choice == "H":
                self.player_hand.add_card(self.deck.deal_card())
            elif choice == "S":
                return
            elif choice == "D":
                if len(self.player_hand.cards) == 2 and self.player_balance >= self.current_bet:
                    self.player_balance -= self.current_bet
                    self.current_bet *= 2
                    self.player_hand.add_card(self.deck.deal_card())
                    print("Doubled down!")
                    return
                else:
                    print("Cannot double down! Insufficient funds or not 2 cards.")
            else:
                print("Invalid choice! Please enter H, S, or D.")
    
    def dealer_turn(self):
        """Execute dealer's AI (must hit on 16 or less, stand on 17+)"""
        print("\n" + "-" * 50)
        print("Dealer's turn...")
        
        while self.dealer_hand.get_value() < 17:
            print("Dealer hits...")
            self.dealer_hand.add_card(self.deck.deal_card())
        
        self.dealer_hand.display("DEALER")
    
    def determine_winner(self):
        """Determine the winner and update balance"""
        player_value = self.player_hand.get_value()
        dealer_value = self.dealer_hand.get_value()
        
        print("\n" + "=" * 50)
        
        if self.player_hand.is_bust():
            print("RESULT: You Busted! 💥 You Lose!")
        elif self.dealer_hand.is_bust():
            print("RESULT: Dealer Busted! 🎉 You Win!")
            self.player_balance += self.current_bet * 2
        elif player_value > dealer_value:
            print("RESULT: You Win! 🎉")
            self.player_balance += self.current_bet * 2
        elif player_value < dealer_value:
            print("RESULT: Dealer Wins! You Lose!")
        else:
            print("RESULT: Push (Tie)! 🤝")
            self.player_balance += self.current_bet
        
        print("=" * 50)
    
    def play_hand(self):
        """Play a single hand"""
        self.display_header()
        self.place_bet()
        self.deal_initial_hands()
        self.show_hands()
        
        if self.check_initial_blackjack():
            return
        
        self.player_turn()
        
        if not self.player_hand.is_bust():
            self.dealer_turn()
        
        self.determine_winner()
    
    def play_game(self):
        """Main game loop"""
        print("\n🎰 Welcome to Blackjack! 🎰")
        
        while self.player_balance > 0:
            self.play_hand()
            
            choice = input("\nPlay another hand? (Y/N): ").upper()
            if choice != "Y":
                break
        
        print("\n" + "=" * 50)
        print("GAME OVER!")
        print(f"Final Balance: ${self.player_balance:.2f}")
        print("=" * 50)
        
        if self.player_balance > 0:
            print("Thanks for playing! Come back soon! 🎰")
        else:
            print("You're out of money! Better luck next time!")


def main():
    """Start the game"""
    try:
        while True:
            starting_balance = 100
            print("\n" + "=" * 50)
            print(" " * 10 + "CASINO BLACKJACK")
            print("=" * 50)
            print(f"Starting balance: ${starting_balance:.2f}")
            print("=" * 50)
            
            game = BlackjackGame(player_balance=starting_balance)
            game.play_game()
            
            play_again = input("\nStart a new game? (Y/N): ").upper()
            if play_again != "Y":
                print("\nThanks for playing! Goodbye! 👋")
                break
    
    except KeyboardInterrupt:
        print("\n\nGame interrupted. Goodbye! 👋")


if __name__ == "__main__":
    main()
