
from .fade import vertical_fade_text

schemes = {
    "orange_to_white":    ((255, 87, 34), (255, 255, 255)),
    "green_to_blue":      ((0, 255, 0), (0, 0, 255)),
    "rose_to_white":      ((255, 102, 178), (255, 255, 255)),
    "blue_to_white":      ((0, 120, 255), (255, 255, 255)),
    "cyan_to_white":      ((0, 255, 255), (255, 255, 255)),
    "velvet_to_white":    ((128, 0, 128), (255, 255, 255)),
    "pink_to_white":      ((255, 105, 180), (255, 255, 255)),
    "red_to_yellow":      ((255, 0, 0), (255, 255, 0)),
}

def fade(text, scheme="orange_to_white"):
    if scheme not in schemes:
        raise ValueError(f"Unknown scheme '{scheme}'. Available: {list(schemes)}")
    
    start_color, end_color = schemes[scheme]
    vertical_fade_text(text, start_color, end_color)
