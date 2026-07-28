import time

def render(renderer, state_dict):
    """
    Renders 3 trains in the authentic WMATA PIDS layout (128x32).
    """
    predictions = state_dict.get("predictions", [])
    api_error = state_dict.get("api_error", False)
    
    renderer.clear()
    
    # 1. Draw Header (Red)
    # y=6 using font_6x10 (Cap height 7) occupies pixels 0-6 (0 top padding)
    header_y = 6
    font = renderer.font_6x10
    
    renderer.draw_text(font, 0, header_y, "RED", "LN")
    renderer.draw_text(font, 19, header_y, "RED", "CAR")
    renderer.draw_text(font, 38, header_y, "RED", "DEST")
    
    # Right align "MIN"
    min_width = renderer.draw_text(font, 0, -20, "RED", "MIN") # measure off-screen
    min_width = min_width if min_width > 0 else 18
    renderer.draw_text(font, 128 - min_width, header_y, "RED", "MIN")
    
    if api_error:
        renderer.draw_text(font, 38, 14, "AMBER", "API Error")
        return
        
    if not predictions:
        renderer.draw_text(font, 38, 14, "AMBER", "No Data")
        return

    # Draw up to 3 trains
    for i in range(3):
        # Rows at y=14, 22, 30 (Leaves exactly 1 pixel gap between rows)
        y = 14 + (i * 8)
        
        if i < len(predictions):
            p = predictions[i]
            
            # Line Abbreviation (e.g., "RD", "OR") natively colored
            color_key = f"LINE_{p.line}" if p.line else "WHITE"
            line_str = p.line if p.line else "--"
            renderer.draw_text(font, 0, y, color_key, line_str)
            
            # Car count
            car_str = str(p.car_count) if p.car_count else "-"
            renderer.draw_text(font, 22, y, "AMBER", car_str)
            
            # Destination (up to 14 chars to avoid hitting MIN)
            dest = p.destination[:14] if p.destination else "Unknown"
            renderer.draw_text(font, 38, y, "AMBER", dest)
            
            # Minutes / Status (solid, no flashing)
            min_str = p.minutes if p.minutes else "---"
            
            # Draw right-aligned minutes
            m_width = renderer.draw_text(font, 0, -20, "WHITE", min_str)
            m_width = m_width if m_width > 0 else len(min_str) * 6
            renderer.draw_text(font, 128 - m_width, y, "WHITE", min_str)
