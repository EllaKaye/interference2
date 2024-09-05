from shiny import App, render, ui, reactive
import random

# Card constants
CARD_VALUES = ["2", "3", "4", "5", "6", "7", "8", "9", "0", "J", "Q", "K", "A"]
CARD_SUITS = ["S", "H", "D", "C"]
VALUES_INT = {value: index for index, value in enumerate(CARD_VALUES)}

# Define the Card class
class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value
        self.value_int = VALUES_INT[value]

    def image_path(self):
        return f"https://deckofcardsapi.com/static/img/{self.value}{self.suit}.png"

    def __str__(self):
        return f"{self.value}{self.suit}"

class Deck:
    def __init__(self):
        self.cards = [
            Card(suit, value)
            for suit in CARD_SUITS
            for value in CARD_VALUES
        ]

    def shuffle(self):
        random.shuffle(self.cards)

    def __str__(self):
        return " ".join(str(card) for card in self.cards)

    def to_rows(self):
        rows = Rows(self.cards)
        return rows

class Row(list):
    def __init__(self, cards):
        super().__init__(cards)

class Rows(list):
    def __init__(self, deck):
        super().__init__()
        for i in range(4):
            self.append(Row(deck[i*13:(i+1)*13]))

    def is_valid_move(self, card1, card2):
        if card1.suit == card2.suit or card1.value == card2.value:
            return True
        return False

    def swap_cards(self, card1, card2):
        if not self.is_valid_move(card1, card2):
            print(f"Invalid move: {card1.value}{card1.suit} with {card2.value}{card2.suit}")
            return False

        pos1 = pos2 = None
        for i, row in enumerate(self):
            for j, card in enumerate(row):
                if card.value == card1.value and card.suit == card1.suit:
                    pos1 = (i, j)
                elif card.value == card2.value and card.suit == card2.suit:
                    pos2 = (i, j)
                if pos1 and pos2:
                    break
            if pos1 and pos2:
                break
        
        if pos1 and pos2:
            self[pos1[0]][pos1[1]], self[pos2[0]][pos2[1]] = self[pos2[0]][pos2[1]], self[pos1[0]][pos1[1]]
            print(f"Swapped cards: {card1.value}{card1.suit} with {card2.value}{card2.suit}")  # Debug print
            return True
        print(f"Failed to swap cards: {card1.value}{card1.suit} with {card2.value}{card2.suit}")  # Debug print
        return False

# Generate the deck and create Rows object
deck = Deck()
deck.shuffle()
rows = deck.to_rows()

# Function to create a card element (as an individual UI element)
def card_ui(card_id, card):
    return ui.div(
        ui.img(src=card.image_path(), class_="card-image"),
        class_="card",
        id=card_id,
        **{"data-card": f"{card.value}{card.suit}"}
    )

# Helper function to find card position
def find_card_position(rows, card):
    for i, row in enumerate(rows):
        for j, c in enumerate(row):
            if c.value == card.value and c.suit == card.suit:
                return i, j
    return None, None

# Define the UI layout
app_ui = ui.page_fluid(
    ui.h2("52 Playing Cards"),
    ui.div(
        # Create 4 rows, each containing 13 card elements
        *[ui.div(
            *[ui.output_ui(f"card_{i*13+j}") for j in range(13)],
            class_="row",
        ) for i in range(4)],
        class_="cards-container"
    ),
    ui.tags.script("""
        let selectedCard = null;

        $(document).on('click', '.card', function() {
            if (selectedCard === null) {
                selectedCard = this;
                $(this).addClass('selected');
            } else {
                let card1 = selectedCard.getAttribute('data-card');
                let card2 = this.getAttribute('data-card');
                
                if (card1 !== card2) {
                    Shiny.setInputValue('swap_cards', {card1: card1, card2: card2});
                }
                
                $(selectedCard).removeClass('selected');
                selectedCard = null;
            }
        });
    """),
    ui.tags.style("""
        .cards-container {
            display: grid;
            grid-template-columns: repeat(13, 1fr); /* 13 cards per row */
            gap: calc(2vw + 2px) 1px; /* Responsive gap between rows */
            justify-items: center; /* Center cards horizontally */
        }
        .row {
            display: contents; /* Ensures each card in the row occupies the correct grid space */
        }
        .card {
            box-shadow: none;
            border: none;
            margin: 0;
            cursor: pointer;
        }
        .card-image {
            width: 120%; /* Full width of the grid cell */
            height: auto; /* Maintain aspect ratio */
            max-width: calc(100vw / 15);  /* Responsive card width */
        }
        .card.selected {
            box-shadow: 0 0 10px 5px rgba(0,0,255,0.5);
        }
        @media (max-width: 1200px) {
            .cards-container {
                gap: calc(1.5vw + 5px) 1px; /* Slightly smaller gap for medium screens */
            }
            .card-image {
                max-width: calc(100vw / 14);  /* Slightly larger cards on medium screens */
            }
        }
        @media (max-width: 900px) {
            .cards-container {
                gap: calc(1vw + 5px) 1px; /* Even smaller gap for smaller screens */
            }
            .card-image {
                max-width: calc(100vw / 13);  /* Larger cards on smaller screens */
            }
        }
        @media (max-width: 600px) {
            .cards-container {
                gap: calc(0.5vw + 5px) 1px; /* Smallest gap for mobile screens */
            }
            .card-image {
                max-width: calc(100vw / 12);  /* Largest cards on mobile screens */
            }
        }
    """)
)

# Define the server logic
def server(input, output, session):
    grid = reactive.Value(rows)

    # Create a render function for each card
    def create_card_render(i, j):
        @output(id=f"card_{i*13+j}")
        @render.ui
        def _():
            return card_ui(f"card_{i*13+j}", grid.get()[i][j])

    # Initialize all card outputs
    for i in range(4):
        for j in range(13):
            create_card_render(i, j)

    @reactive.Effect
    @reactive.event(input.swap_cards)
    def _():
        if input.swap_cards() is None:
            return

        card1_str = input.swap_cards()['card1']
        card2_str = input.swap_cards()['card2']

        card1 = Card(card1_str[1], card1_str[0])
        card2 = Card(card2_str[1], card2_str[0])

        current_grid = grid.get()
        if current_grid.swap_cards(card1, card2):
            grid.set(current_grid)

            # Find positions of swapped cards
            pos1 = find_card_position(current_grid, card1)
            pos2 = find_card_position(current_grid, card2)

            # Trigger updates for the swapped cards
            if pos1[0] is not None and pos2[0] is not None:
                output.invalidate(f"card_{pos1[0]*13+pos1[1]}")
                output.invalidate(f"card_{pos2[0]*13+pos2[1]}")

# Create the Shiny app
app = App(app_ui, server)