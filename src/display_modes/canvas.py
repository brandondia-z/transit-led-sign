def render(renderer, state_snapshot):
    canvas_data = state_snapshot["config"].canvas_data
    
    # Check if canvas_data is populated and valid (64x32 = 2048 pixels)
    if not canvas_data or len(canvas_data) != 2048:
        # If no canvas drawn yet, show a prompt or black screen
        renderer.draw_text(renderer.font_4x6, 2, 16, "WHITE", "Draw in Web UI")
        return

    # Loop through the flat array and render each pixel
    # The array is row-major: y goes from 0 to 31, x from 0 to 63
    for y in range(32):
        for x in range(64):
            idx = y * 64 + x
            color_hex = canvas_data[idx]
            
            if color_hex and color_hex.startswith("#") and len(color_hex) == 7:
                r = int(color_hex[1:3], 16)
                g = int(color_hex[3:5], 16)
                b = int(color_hex[5:7], 16)
                renderer.set_pixel(x, y, r, g, b)
