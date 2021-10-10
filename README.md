# FlipChess

There is an old game called Miki's World, which is almost nowhere to be found now. (If you still have an old Nokia phone, maybe you can find it) After you got enough points in that game, a bonus game mode would be unlocked, from which my game comes.

Its rules are as followings:

- Two players take turns to play a double-sided piece on the grids of the board. One player controls one side and the other player controls the other side.
- Players are not allowed to play pieces to grids with the opponent pieces.
- When the number of pieces in one grid reaches the number of its neighbor grids:
  - move all its pieces to its neighbors, one to one.
  - flip all the opponent pieces in neighbor grids, and change their owner.
  - repeat, until no grids match the condition or the winner is decided.
- If a player owns all of the pieces, he will be the winner. (Of course, the number of pieces must be greater than 2)

In my game, some changes were made:

- Grid checking and piece moving will not work one grid by one. After one move is done, I will check all of the grids at the same time and move pieces, in order to avoid  ambiguity results.
- I designed a new thinking program in the human-machine battle, which may be a little stronger than the origin one.

OK, if you are interested in this game, you can install pygame and run it with Python3.

The background image and the piece images are from Genshin Impact. The used font is 方正姚体. You can replace them to make this game more beautiful.
