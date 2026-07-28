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
    is_fetching = state_dict.get("is_fetching", False)
    
    # Right align "MIN" (calculate off-screen first)
    min_width = renderer.draw_text(font, 0, -20, "RED", "MIN") 
    min_width = min_width if min_width > 0 else 18
    
    if is_fetching:
        renderer.draw_text(font, 0, header_y, "RED", "UPDATING")
        renderer.draw_text(font, 128 - min_width, header_y, "RED", "MIN")
        
        s_name = state_dict.get("fetching_station_name", "")[:16]
        d_name = state_dict.get("fetching_direction_name", "")[:18]
        
        renderer.draw_text(font, 0, 15, "WARM_YELLOW", "Fetching trains...")
        renderer.draw_text(font, 0, 23, "WARM_YELLOW", f"from {s_name}")
        renderer.draw_text(font, 0, 31, "WARM_YELLOW", f"to {d_name}")
        return
        
    renderer.draw_text(font, 0, header_y, "RED", "LN")
    renderer.draw_text(font, 15, header_y, "RED", "CAR")
    renderer.draw_text(font, 36, header_y, "RED", "DEST")
    renderer.draw_text(font, 128 - min_width, header_y, "RED", "MIN")
    
    if api_error:
        if not state_dict.get("has_connected_once", False):
            renderer.draw_text(font, 25, 15, "WARM_YELLOW", "Connecting...")
        else:
            renderer.draw_text(font, 36, 15, "WARM_YELLOW", "API Error")
        return
        
    if not predictions:
        renderer.draw_text(font, 36, 15, "WARM_YELLOW", "No Trains")
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
            
            # Car count (8-car trains are GREEN/TEAL, others are WARM_YELLOW/CREAM)
            car_str = str(p.car_count) if p.car_count else "-"
            car_color = "GREEN" if car_str == "8" else "WARM_YELLOW"
            renderer.draw_text(font, 18, y, car_color, car_str)
            
            # Minutes / Status (BRD/ARR are WHITE, others are WARM_YELLOW)
            min_str = p.minutes if p.minutes else "---"
            min_color = "WHITE" if min_str in ["BRD", "ARR"] else "WARM_YELLOW"
            m_width = renderer.draw_text(font, 0, -20, min_color, min_str)
            m_width = m_width if m_width > 0 else len(min_str) * 6
            
            # Destination (dynamically truncate to avoid hitting MIN)
            max_dest_pixels = (128 - m_width - 4) - 36 # 4 pixels of padding
            max_chars = max(0, max_dest_pixels // 6)
            dest = p.destination[:max_chars] if p.destination else "Unknown"
            
            renderer.draw_text(font, 36, y, "WARM_YELLOW", dest)
            renderer.draw_text(font, 128 - m_width, y, min_color, min_str)
