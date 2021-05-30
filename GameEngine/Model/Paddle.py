class Paddle:
    def __init__(self, side: str, x: int, y: int, width: int, height: int, speed: int, decrementSpeed: bool):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed
        self.decrementSpeed = decrementSpeed
        self.side = side
