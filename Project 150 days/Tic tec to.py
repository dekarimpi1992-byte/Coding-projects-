import tkinter as tk
from tkinter import messagebox

window = tk.Tk()
window.title("Tic-Tac-Toe vs Computer")
window.geometry("300x300")
window.resizable(False, False)

buttons = []
board = [""] * 9
player_symbol = "X"
computer_symbol = "O"
game_over = False

winning_combos = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8],
    [0, 3, 6], [1, 4, 7], [2, 5, 8],
    [0, 4, 8], [2, 4, 6],
]


def check_winner(current_board):
    for combo in winning_combos:
        a, b, c = combo
        if current_board[a] and current_board[a] == current_board[b] == current_board[c]:
            return current_board[a]
    return None


def is_draw(current_board):
    return all(cell != "" for cell in current_board)


def disable_board():
    for button in buttons:
        button.config(state="disabled")


def end_game(message):
    global game_over
    game_over = True
    disable_board()
    messagebox.showinfo("Game Over", message)


def make_move(index, symbol):
    board[index] = symbol
    buttons[index].config(text=symbol, state="disabled")


def user_move(index):
    global game_over

    if game_over or board[index] != "":
        return

    make_move(index, player_symbol)

    winner = check_winner(board)
    if winner == player_symbol:
        end_game("You win!")
        return
    if is_draw(board):
        end_game("It's a draw!")
        return

    window.after(300, computer_turn)


def minimax(current_board, is_maximizing):
    winner = check_winner(current_board)
    if winner == computer_symbol:
        return 1
    if winner == player_symbol:
        return -1
    if is_draw(current_board):
        return 0

    if is_maximizing:
        best_score = -999
        for i, cell in enumerate(current_board):
            if cell == "":
                current_board[i] = computer_symbol
                score = minimax(current_board, False)
                current_board[i] = ""
                best_score = max(best_score, score)
        return best_score

    best_score = 999
    for i, cell in enumerate(current_board):
        if cell == "":
            current_board[i] = player_symbol
            score = minimax(current_board, True)
            current_board[i] = ""
            best_score = min(best_score, score)
    return best_score


def find_best_move():
    best_score = -999
    best_move = None

    for i, cell in enumerate(board):
        if cell == "":
            board[i] = computer_symbol
            score = minimax(board, False)
            board[i] = ""
            if score > best_score:
                best_score = score
                best_move = i

    return best_move


def computer_turn():
    global game_over

    if game_over:
        return

    move = find_best_move()
    if move is None:
        end_game("It's a draw!")
        return

    make_move(move, computer_symbol)

    winner = check_winner(board)
    if winner == computer_symbol:
        end_game("Computer wins!")
        return
    if is_draw(board):
        end_game("It's a draw!")


def reset_game():
    global board, game_over
    board = [""] * 9
    game_over = False
    for button in buttons:
        button.config(text="", state="normal", bg="white")


def create_board():
    for row in range(3):
        for col in range(3):
            index = row * 3 + col
            button = tk.Button(
                window,
                text="",
                font=("Arial", 24),
                width=4,
                height=2,
                command=lambda idx=index: user_move(idx),
                bg="white",
                borderwidth=2,
            )
            button.grid(row=row, column=col, padx=5, pady=5)
            buttons.append(button)


create_board()

reset_button = tk.Button(window, text="Restart", command=reset_game, font=("Arial", 12))
reset_button.grid(row=3, column=0, columnspan=3, sticky="ew", padx=5, pady=10)

window.mainloop()

