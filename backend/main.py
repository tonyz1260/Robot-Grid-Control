from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional
import csv
from io import StringIO

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define circle colors
class CircleColor:
    RED = "red"
    GREEN = "green"
    BLUE = "blue"

# Circle object representing each element in the grid
class Circle:
    def __init__(self, color: str, x: int, y: int):
        self.color = color
        self.x = x
        self.y = y

# Robot class to manage its state and actions
class Robot:
    def __init__(self):
        self.x = 0  # Robot starts at (0, 0)
        self.y = 0
        self.held_circle: Optional[Circle] = None
        self.history = []

    def move(self, direction: str, grid_width: int, grid_height: int):
        new_x, new_y = self.x, self.y
        if direction == "up":
            new_y -= 1
        elif direction == "down":
            new_y += 1
        elif direction == "left":
            new_x -= 1
        elif direction == "right":
            new_x += 1
        else:
            raise HTTPException(status_code=400, detail="Invalid move direction")
        
        # Check bounds
        if 0 <= new_x < grid_width and 0 <= new_y < grid_height:
            self.x, self.y = new_x, new_y
            self.history.append(f"Robot moved to ({self.x}, {self.y})")
            return {"status": "moved", "x": self.x, "y": self.y}
        else:
            raise HTTPException(status_code=400, detail="Move out of bounds")

    def pick_up_circle(self, circles: List[Circle]):
        if not self.held_circle:
            # create a copy of the list to avoid modifying the original list and reverse it to pick up the top circle
            circles1 = circles.copy()
            circles1.reverse()
            for circle in circles1:
                if circle.x == self.x and circle.y == self.y:
                    self.held_circle = circle
                    circles.remove(circle)
                    self.history.append(f"Robot picked up {circle.color} circle")
                    return {"status": "picked up", "color": circle.color}
            raise HTTPException(status_code=400, detail="No circle to pick up")
        else:
            raise HTTPException(status_code=400, detail="Already holding a circle")

    def place_circle(self, circles: List[Circle]):
        if not self.held_circle:
            raise HTTPException(status_code=400, detail="No circle to place")
        
        circles1 = circles.copy()
        circles1.reverse()
        
        for circle in circles1:
            if circle.x == self.x and circle.y == self.y:
                if circle.color == CircleColor.RED:
                    raise HTTPException(status_code=400, detail="Red cannot have any circles above it")
                if circle.color == CircleColor.BLUE and self.held_circle.color != CircleColor.RED:
                    raise HTTPException(status_code=400, detail="Blue can only have red above it")
                break   # ONLY check the top circle of the stack
        
        self.held_circle.x, self.held_circle.y = self.x, self.y
        circles.append(self.held_circle)
        self.history.append(f"Robot placed {self.held_circle.color} circle at ({self.x}, {self.y})")
        self.held_circle = None
        return {"status": "placed"}

# Grid to manage movement and stacking rules
class Grid:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.circles: List[Circle] = []
        self.robot = Robot()

    def get_grid_state(self):
        return {
            "robot": (self.robot.x, self.robot.y),
            "held_circle": self.robot.held_circle.color if self.robot.held_circle else None,
            "circles": [(c.color, c.x, c.y) for c in self.circles]
        }
    
    def export_history_csv(self):
        output = StringIO()
        writer = csv.writer(output)
        for row in self.robot.history:
            writer.writerow([row])
        # output.seek(0)
        # return output.getvalue()
        response = Response(content=output.getvalue(), media_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=movement-history.csv"
        return response

# Initialize the grid
grid = Grid(width=3, height=3)

grid.circles.append(Circle(CircleColor.RED, 0, 2))
grid.circles.append(Circle(CircleColor.RED, 2, 0))
grid.circles.append(Circle(CircleColor.RED, 1, 1))

grid.circles.append(Circle(CircleColor.GREEN, 1, 0))
grid.circles.append(Circle(CircleColor.GREEN, 2, 1))
grid.circles.append(Circle(CircleColor.GREEN, 1, 2))

grid.circles.append(Circle(CircleColor.BLUE, 0, 0))
grid.circles.append(Circle(CircleColor.BLUE, 0, 1))
grid.circles.append(Circle(CircleColor.BLUE, 2, 2))

@app.post("/move")
def move_robot(direction: str):
    return grid.robot.move(direction, grid.width, grid.height)

@app.post("/pickup")
def pick_up():
    return grid.robot.pick_up_circle(grid.circles)

@app.post("/place")
def place():
    return grid.robot.place_circle(grid.circles)

@app.get("/grid")
def get_grid():
    return grid.get_grid_state()

@app.get("/history")
def get_history():
    return grid.export_history_csv()
