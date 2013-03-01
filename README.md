OthelloServer
=============

An Othello (or [Reversi][1]) server developed in Django (*for academical purposes*). 

It might contain some rules specific to our assignment, so feel free to modify it if you want.

What is it for?
---

This server defines an HTTP API that will allow two users to play Othello. The responses will be JSON objects.

Documentation
---

If the server is running on **http://localhost/**, the following requests can be made:

#### Connect

This method should be called when two players want to start a game.

**Request:** `http://localhost/connect?p1=john&p2=mary`  
**Response:** `{'game': 'john-mary-1'}`  
**Additional info:** 

- The game won't start until both users call this method.
- The response is `player1-player2-id` where `player1` plays with **white** dics and `player2` with **black** ones.


#### Get Board

**Request:** `http://localhost/get_board?game=john-mary-1`  
**Response:** `{'board': '0000000000000000000000000001200000021000000000000000000000000000'}`  
**Additional info:** 

- The board is a string of 64 characters, representing a 8x8 board.
- The sample response is the initial board.

#### Is Turn

This method will return `True` if it is `player`'s turn.

**Request:** `http://localhost/is_turn?game=john-mary-1&player=john`  
**Response:** `{'status': True}`  
**Additional info:** 

#### Move

This method should be called when a player wants to play. **POST** has to be used.

**Request:** `http://localhost/move`  
**Data:** `game=john-mary-1&player=john&move=(3,2)`  
**Response:** `{'status': 'succeed'}` or `{'status': 'failed'}`

**Additional info:** 

- In the above example, the player `john` wants to insert a disc in the 3rd row and 2nd column.


#### General for all above methods

All the above methods can return an `error` field in the response. Eg.:

**Request:** `http://localhost/get_board?game=john-chris-1`  
**Response:** `{'error': 'Game john-chris-1 not found}`



How to run the server
---

    $ python manage.py runserver


Author
---

Oscar Mederos Oceja &lt;[omederos@gmail.com](mailto:omederos@gmail.com)>


[1]: http://en.wikipedia.org/wiki/Reversi