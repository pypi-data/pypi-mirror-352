class Time:
    def __init__(self):
        self.dt = 0
        self.fps = 0
        
    def _update(self,dt):
        self.dt = dt
    
time = Time()