import time

def render(renderer, state_dict):
    """
    Renders 3 trains in the authentic WMATA PIDS layout (128x32).
    """
    predictions = state_dict.get("predictions", [])
    api_error = state_dict.get("api_error", False)
    
    renderer.clear()
    
    # 1. Draw Header (Red)
    # y=7 using font_wmata_5x7 (Cap height 7, Ascent 7, Descent 0) uses pixels 1-7
    header_y = 7
    font = renderer.font_wmata_5x7
    
    renderer.draw_text(font, 0, header_y, "RED", "LN")
    renderer.draw_text(font, 15, header_y, "RED", "CAR")
    renderer.draw_text(font, 36, header_y, "RED", "DEST")
    
    # Right align "MIN"
    min_width = renderer.draw_text(font, 0, -20, "RED", "MIN") # measure off-screen
    min_width = min_width if min_width > 0 else 18
    renderer.draw_text(font, 128 - min_width, header_y, "RED", "MIN")
    
    if api_error:
        renderer.draw_text(font, 36, 14, "AMBER", "API Error")
        return
        
    if not predictions:
        renderer.draw_text(font, 36, 14, "AMBER", "No Data")
        return

    # Draw up to 3 trains
    for i in range(3):
        # Rows at y=15, 23, 31 (Leaves exactly 1 pixel gap between rows)
        y = 15 + (i * 8)
        
        if i < len(predictions):
            p = predictions[i]
            
            # Line Abbreviation (e.g., "RD", "OR") natively colored
            color_key = f"LINE_{p.line}" if p.line else "WHITE"
            line_str = p.line if p.line else "--"
            renderer.draw_text(font, 0, y, color_key, line_str)
            
            # Car count (8-car trains are GREEN, others are WHITE)
            car_str = str(p.car_count) if p.car_count else "-"
            car_color = "GREEN" if car_str == "8" else "WHITE"
            renderer.draw_text(font, 18, y, car_color, car_str)
            
            # Minutes / Status (solid, no flashing)
            min_str = p.minutes if p.minutes else "---"
            m_width = renderer.draw_text(font, 0, -20, "WHITE", min_str)
            m_width = m_width if m_width > 0 else len(min_str) * 6
            
            # Destination (dynamically truncate to avoid hitting MIN)
            max_dest_pixels = (128 - m_width - 4) - 36 # 4 pixels of padding
            max_chars = max(0, max_dest_pixels // 6)
            dest = p.destination[:max_chars] if p.destination else "Unknown"
            
            renderer.draw_text(font, 36, y, "WHITE", dest)
            renderer.draw_text(font, 128 - m_width, y, "WHITE", min_str)
