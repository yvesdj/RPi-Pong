from Model.Paddle import Paddle


class Player:
    def __init__(self, paddle: Paddle, score: int, tmpScore: int):
        self.paddle = paddle
        self.score = score
        self.tmpScore = tmpScore
