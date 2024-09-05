from shiny import App, render, ui, reactive

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

# Define Row and Rows classes for game logic
class Row:
    def __init__(self, cards):
        self.cards = cards

class Rows:
    def __init__(self, deck):
        self.rows = [Row(deck[i:i+13]) for i in range(0, 52, 13)]

# Generate the deck and create Rows object
deck = [Card(suit, value) for suit in CARD_SUITS for value in CARD_VALUES]
rows = Rows(deck)

# Function to create a card element (as an individual UI element)
def card_ui(card_id, card):
    return ui.div(
        ui.img(src=card.image_path(), class_="card-image"),
        class_="card",
        id=card_id
    )

# Define the UI layout
app_ui = ui.page_fluid(
    ui.h2("52 Playing Cards"),
    ui.div(
        # Create 4 rows, each containing 13 card elements
        *[ui.div(
            *[card_ui(f"card_{i*13+j}", card) for j, card in enumerate(row.cards)],
            class_="row",
        ) for i, row in enumerate(rows.rows)],
        class_="cards-container"
    ),
    ui.tags.style("""
        .cards-container {
            display: grid;
            grid-template-columns: repeat(13, 1fr); /* 13 cards per row */
            gap: 20px 1px; /* Gap between rows */
            justify-items: center; /* Center cards horizontally */
        }
        .row {
            display: contents; /* Ensures each card in the row occupies the correct grid space */
        }
        .card {
            box-shadow: none;
            border: none;
            margin: 0;
        }
        .card-image {
            width: 120%; /* Full width of the grid cell */
            height: auto; /* Maintain aspect ratio */
            max-width: calc(100vw / 15);  /* Responsive card width */
        }
        @media (max-width: 600px) {
            .card-image {
                max-width: calc(100vw / 12);  /* Larger cards on small screens */
            }
        }
    """)
)

# Define the server logic
def server(input, output, session):
    pass

# Create the Shiny app
app = App(app_ui, server)
