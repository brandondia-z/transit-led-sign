import time

def render(renderer, state_dict):
    """
    Renders 3 trains (compact mode).
    Takes a renderer instance and a snapshot of the current state.
    """
    predictions = state_dict.get("predictions", [])
    alerts = state_dict.get("alerts", [])
    api_error = state_dict.get("api_error", False)
    
    renderer.clear()
    
    if api_error:
        renderer.draw_text(renderer.font_6x10, 30, 20, "AMBER", "API Error")
        return
        
    if not predictions:
        renderer.draw_text(renderer.font_6x10, 35, 20, "AMBER", "No Data")
        return

    # Draw up to 3 trains
    for i in range(3):
        y_offset = i * 11
        
        # Separator line above train 2 and 3
        if i > 0:
            renderer.draw_line(0, y_offset - 1, 127, y_offset - 1, "DARK_GRAY")
            
        if i < len(predictions):
            p = predictions[i]
            
            # Draw line color badge (4x4 square)
            color_key = f"LINE_{p.line}" if p.line else "WHITE"
            renderer.draw_rect(0, y_offset + 3, 4, 4, color_key)
            
            # Draw destination
            renderer.draw_text(renderer.font_5x8, 8, y_offset + 8, "AMBER", p.destination[:13])
            
            # Draw minutes / status
            # Blink ARR and BRD every 500ms
            blink_on = int(time.time() * 2) % 2 == 0
            if p.minutes in ["ARR", "BRD"]:
                if blink_on:
                    renderer.draw_text(renderer.font_5x8, 108, y_offset + 8, "WHITE", p.minutes)
            else:
                # E.g. "5 min" or just "5"
                text = f"{p.minutes}" if p.minutes == "---" else f"{p.minutes}m"
                renderer.draw_text(renderer.font_5x8, 108, y_offset + 8, "WHITE", text)
        else:
            # Empty slot
            renderer.draw_text(renderer.font_5x8, 8, y_offset + 8, "DARK_GRAY", "---")

    # If there are alerts, we could draw a marquee over the 3rd row, but for V1 let's stick to 3 trains.
