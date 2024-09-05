from shiny import App, render, ui, reactive
import random

# Card constants
CARD_VALUES = ["2", "3", "4", "5", "6", "7", "8", "9", "0", "J", "Q", "K", "B"]
CARD_SUITS = ["S", "H", "D", "C"]
VALUES_INT = {value: index for index, value in enumerate(CARD_VALUES)}

class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value
        self.value_int = VALUES_INT[value]

    def image_path(self):
        if self.value == "B":
            return "https://raw.githubusercontent.com/EllaKaye/interference/main/www/img/blank.png"  # You'll need to provide this
        return f"https://deckofcardsapi.com/static/img/{self.value}{self.suit}.png"

    def __str__(self):
        return f"{self.value}{self.suit}"

class Row(list):
    def is_stuck(self):
        last_card_was_K = False
        for card in self:
            if card.value == "K":
                last_card_was_K = True
            elif card.value == "B":
                if not last_card_was_K:
                    return False
            else:
                last_card_was_K = False
        return True

    def split_index(self):
        if self[0].value != "2":
            return 0
        suit = self[0].suit
        for i in range(1, len(self)):
            if self[i].suit != suit or self[i].value_int != i:
                return i
        return len(self) - 1

    def split(self, index):
        return self[:index], self[index:]

    def fill_row(self, deck):
        while len(self) < 13:
            self.append(deck.pop())
        return self

    def is_ordered(self):
        return self.split_index() == 12

class Deck:
    def __init__(self):
        self.cards = [Card(suit, value) for suit in CARD_SUITS for value in CARD_VALUES]

    def shuffle(self):
        random.shuffle(self.cards)

    def pop(self):
        return self.cards.pop()

def card_ui(card_id, card):
    return ui.div(
        ui.img(src=card.image_path(), class_="card-image"),
        class_="card",
        id=card_id,
        **{"data-card": f"{card.value}{card.suit}"}
    )

app_ui = ui.page_fluid(
    ui.h2("52 Playing Cards"),
    ui.div(
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
            grid-template-columns: repeat(13, 1fr);
            gap: calc(2vw + 2px) 1px;
            justify-items: center;
        }
        .row {
            display: contents;
        }
        .card {
            box-shadow: none;
            border: none;
            margin: 0;
            cursor: pointer;
        }
        .card-image {
            width: 120%;
            height: auto;
            max-width: calc(100vw / 15);
        }
        .card.selected {
            box-shadow: 0 0 10px 5px rgba(0,0,255,0.5);
        }
        @media (max-width: 1200px) {
            .cards-container {
                gap: calc(1.5vw + 5px) 1px;
            }
            .card-image {
                max-width: calc(100vw / 14);
            }
        }
        @media (max-width: 900px) {
            .cards-container {
                gap: calc(1vw + 5px) 1px;
            }
            .card-image {
                max-width: calc(100vw / 13);
            }
        }
        @media (max-width: 600px) {
            .cards-container {
                gap: calc(0.5vw + 5px) 1px;
            }
            .card-image {
                max-width: calc(100vw / 12);
            }
        }
    """)
)

def server(input, output, session):
    deck = Deck()
    deck.shuffle()
    
    rows = [Row().fill_row(deck) for _ in range(4)]
    card_positions = [[reactive.Value(card) for card in row] for row in rows]

    def create_card_render(i, j):
        @output(id=f"card_{i*13+j}")
        @render.ui
        def _():
            return card_ui(f"card_{i*13+j}", card_positions[i][j]())

    for i in range(4):
        for j in range(13):
            create_card_render(i, j)

    def is_valid_move(card1, card2):
        return card1.suit == card2.suit or card1.value == card2.value

    def find_card_position(card):
        for i, row in enumerate(card_positions):
            for j, c in enumerate(row):
                if c().value == card.value and c().suit == card.suit:
                    return i, j
        return None, None

    @reactive.Effect
    @reactive.event(input.swap_cards)
    def _():
        if input.swap_cards() is None:
            return

        card1_str = input.swap_cards()['card1']
        card2_str = input.swap_cards()['card2']

        card1 = Card(card1_str[1], card1_str[0])
        card2 = Card(card2_str[1], card2_str[0])

        if is_valid_move(card1, card2):
            pos1 = find_card_position(card1)
            pos2 = find_card_position(card2)

            if pos1[0] is not None and pos2[0] is not None:
                # Swap the cards in both card_positions and rows
                card_positions[pos1[0]][pos1[1]].set(card2)
                card_positions[pos2[0]][pos2[1]].set(card1)
                rows[pos1[0]][pos1[1]], rows[pos2[0]][pos2[1]] = rows[pos2[0]][pos2[1]], rows[pos1[0]][pos1[1]]

                # You can add game logic here using the rows, e.g.:
                # for row in rows:
                #     if row.is_ordered():
                #         print("A row is fully ordered!")

app = App(app_ui, server)