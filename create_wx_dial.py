import numpy as np
import math
import io
import os
import requests

def create_svg_dial(value, categories):
    cx, cy, radius = 125, 125, 95
    total_angle = 270
    start_angle = -225
    segment_angle = total_angle / len(categories)

    svg_parts = [f'<svg width="250" height="400" viewBox="0 0 250 200" xmlns="http://www.w3.org/2000/svg">']
    # Draw each arc
    for i, (label, color) in enumerate(categories):
        start = start_angle + i * segment_angle
        end = start + segment_angle
        path_d = describe_arc(cx, cy, radius, start, end)
        svg_parts.append(f'<path d="{path_d}" stroke="{color}" stroke-width="20" fill="none" stroke-linecap="butt" />')
    # Knob
    knob_angle = (value / 100) * total_angle + start_angle
    #const angle = (value / 100) * 270 - 135;
    knob_x, knob_y = polar_to_cartesian(cx, cy, radius, knob_angle)
    #svg_parts.append(f'<circle cx="{knob_x}" cy="{knob_y}" r="7" fill="white" stroke="#ccc" stroke-width="3"/>')
    # Replace the knob (circle) part with this triangle
    pointer_length = 20
    pointer_width = 20
    angle_rad = math.radians(knob_angle)

    # Triangle tip (at arc edge)
    tip_x = knob_x
    tip_y = knob_y

    # Base of triangle (move backward along the angle)
    base_center_x = cx + (radius - pointer_length) * math.cos(angle_rad)
    base_center_y = cy + (radius - pointer_length) * math.sin(angle_rad)

    # Compute the two base corners perpendicular to the angle
    perp_angle = angle_rad + math.pi / 2
    corner1_x = base_center_x + (pointer_width / 2) * math.cos(perp_angle)
    corner1_y = base_center_y + (pointer_width / 2) * math.sin(perp_angle)
    corner2_x = base_center_x - (pointer_width / 2) * math.cos(perp_angle)
    corner2_y = base_center_y - (pointer_width / 2) * math.sin(perp_angle)

    # Draw triangle instead of knob
    svg_parts.append(
        f'<polygon points="{tip_x},{tip_y} {corner1_x},{corner1_y} {corner2_x},{corner2_y}" '
        f'fill="white" stroke="#ccc" stroke-width="2"/>'
    )
    # Clamp value between 0 and 100
    clamped_value = max(0, min(value, 100))
    # Where the knob should point based on the input value, which is a percentage (0 to 100).
    index = int((clamped_value / 100) * len(categories))
    # If categories[int((value/100)*len(categories))][0] produces an index into the categories array than that is actually bigger than its length
    if index >= len(categories):
        index = len(categories) - 1
    label = categories[index][0]
    svg_parts.append(f'<text x="{cx}" y="125" text-anchor="middle" class="gauge-text" font-size="40" font-family="Arial" font-weight="bold">{value}⁰F</text>')
    svg_parts.append(f'<text x="{cx}" y="150" text-anchor="middle" class="gauge-label" font-size="30" fill="#333" font-family="Arial">{label}</text>')
    svg_parts.append('</svg>')
    return ''.join(part.strip() for part in svg_parts)

def generate_direction_ticks(cx=125, cy=125, radius=100, tick_length=10):
    ticks_svg = []
    for i in range(8):
        angle_deg = i * 45
        angle_rad = math.radians(angle_deg)

        x1 = cx + ((radius/2) - tick_length) * math.cos(angle_rad)
        y1 = cy + ((radius/2) - tick_length) * math.sin(angle_rad)
        x2 = cx + (radius/2) * math.cos(angle_rad)
        y2 = cy + (radius/2) * math.sin(angle_rad)

        ticks_svg.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="black" stroke-width="2"/>')

    return "\n".join(ticks_svg)

def create_svg_dial_wind(value, categories, wind_dir):
    cx, cy, radius = 125, 125, 95
    total_angle = 270
    start_angle = -225
    # segment_angle = total_angle / len(categories)

    gap = 5  # degrees of empty space between each segment
    n = len(categories)
    segment_angle = (total_angle - gap * (n - 1)) / n
    svg_parts = [f'<svg width="250" height="400" viewBox="0 0 250 200">']
    # Draw each arc
    for i, (label, color) in enumerate(categories):
        start = start_angle + i * (segment_angle + gap)
        end = start + segment_angle
        path_d = describe_arc(cx, cy, radius, start, end)
        svg_parts.append(f'<path d="{path_d}" stroke="{color}" stroke-width="20" fill="none" stroke-linecap="butt" />')

    # Knob
    knob_angle = (value / 100) * total_angle + start_angle
    #const angle = (value / 100) * 270 - 135;
    knob_x, knob_y = polar_to_cartesian(cx, cy, radius, knob_angle)
    #svg_parts.append(f'<circle cx="{knob_x}" cy="{knob_y}" r="7" fill="white" stroke="#ccc" stroke-width="3"/>')
    # Replace the knob (circle) part with this triangle
    pointer_length = 20
    pointer_width = 20
    angle_rad = math.radians(knob_angle)

    # Triangle tip (at arc edge)
    tip_x = knob_x
    tip_y = knob_y

    # Base of triangle (move backward along the angle)
    base_center_x = cx + (radius - pointer_length) * math.cos(angle_rad)
    base_center_y = cy + (radius - pointer_length) * math.sin(angle_rad)

    # Compute the two base corners perpendicular to the angle
    perp_angle = angle_rad + math.pi / 2
    corner1_x = base_center_x + (pointer_width / 2) * math.cos(perp_angle)
    corner1_y = base_center_y + (pointer_width / 2) * math.sin(perp_angle)
    corner2_x = base_center_x - (pointer_width / 2) * math.cos(perp_angle)
    corner2_y = base_center_y - (pointer_width / 2) * math.sin(perp_angle)

    # Draw triangle instead of knob
    svg_parts.append(
        f'<polygon points="{tip_x},{tip_y} {corner1_x},{corner1_y} {corner2_x},{corner2_y}" '
        f'fill="white" stroke="#ccc" stroke-width="2"/>'
    )
    svg_parts.append(generate_direction_ticks())
    # Text
    # Clamp value between 0 and 100
    clamped_value = max(0, min(value, 100))
    # Where the knob should point based on the input value, which is a percentage (0 to 100).
    index = int((clamped_value / 100) * len(categories))
    # If categories[int((value/100)*len(categories))][0] produces an index into the categories array than that is actually bigger than its length
    if index >= len(categories):
        index = len(categories) - 1
    label = categories[index][0]
    #svg_parts.append(f'<text x="{cx}" y="125" text-anchor="middle" class="gauge-text" font-size="40" font-family="Arial" weight = "bold">{value}⁰F</text>')
    #svg_parts.append(f'<text x="{cx}" y="150" text-anchor="middle" class="gauge-label" font-size="30" fill="#333" font-family="Arial">{label}</text>')
    svg_parts.append(f'<circle cx="{cx}" cy="{cy}" r="{radius/2}" fill="white" stroke="#ccc" stroke-width="3"/>')

    # Position for South text marker
    x1 = cx
    y1 = 25 + cy + radius / 2

    # Position for North text marker
    x2 = cx
    y2 = cy - (radius / 2)

    # Position for East text marker
    x3 = 15 + cx + radius / 2
    y3 = cy + 10

    # Position for West text marker
    x4 = cx - (radius / 2) - 15
    y4 = cy + 10
    svg_parts.append(f'<text x="{x1}" y="{y1}" text-anchor="middle" class="gauge-label" font-size="30" fill="#333" font-family="Arial">S</text>')
    svg_parts.append(f'<text x="{x2}" y="{y2}" text-anchor="middle" class="gauge-label" font-size="30" fill="#333" font-family="Arial">N</text>')
    svg_parts.append(f'<text x="{x3}" y="{y3}" text-anchor="middle" class="gauge-label" font-size="30" fill="#333" font-family="Arial">E</text>')
    svg_parts.append(f'<text x="{x4}" y="{y4}" text-anchor="middle" class="gauge-label" font-size="30" fill="#333" font-family="Arial">W</text>')

    svg_parts.append(f'<g transform="rotate({wind_dir}, {cx}, {cy})"><rect x="{cx-5}" y="{cy}" width="4" height="{radius/2}"/></g>')
    svg_parts.append('</svg>')

    return ''.join(svg_parts)
def polar_to_cartesian(cx, cy, r, angle_deg):
    rad = math.radians(angle_deg)
    return (cx + r * math.cos(rad), cy + r * math.sin(rad))

def describe_arc(cx, cy, radius, start_angle, end_angle):
    start_pt = polar_to_cartesian(cx, cy, radius, end_angle)
    end_pt = polar_to_cartesian(cx, cy, radius, start_angle)
    large_arc = 1 if (end_angle - start_angle) > 180 else 0
    return f'M {start_pt[0]},{start_pt[1]} A {radius},{radius} 0 {large_arc},0 {end_pt[0]},{end_pt[1]}'

def describe_smaller_arc(cx, cy, radius, start_angle, end_angle):
    start_pt = polar_to_cartesian(cx, cy, radius, end_angle)
    end_pt = polar_to_cartesian(cx,cy, radius, start_angle)
    large_arc = 1 if (end_angle - start_angle) > 180 else 0
    return f'M {start_pt[0]}, {start_pt[1]} A {radius}, {radius} 0 {large_arc}, 0 {end_pt[0]}, {end_pt[1]}'
def create_dial(temperature, dewpoint, speed, direction):
    temperature_categories = [
        ("Extreme Cold (Frostbite Risk)", "#FFEFF4"),     # -40 to -10°F — Very light pink (frosty cold)
        ("Bitter Cold", "#F8C8DC"),                       # -10 to 0°F — Frosty blush (muted pink)
        ("Very Cold", "#FFCCE5"),                         # 0 to 20°F — Soft baby pink
        ("Cold", "#AEC6CF"),                              # 20 to 40°F — Pastel blue (cool but not too saturated)
        ("Cool", "#4B9CD3"),                              # 40 to 50°F — Muted cool blue
        ("Comfortable", "#2ECC71"),                       # 50 to 60°F — Soft green
        ("Mild", "#A2D95F"),                              # 60 to 70°F — Spring green
        ("Warm", "#F4D03F"),                              # 70 to 80°F — Golden yellow
        ("Hot", "#FF6347"),                               # 80 to 90°F — Orange
        ("Very Hot", "#FF0000"),                          # 90 to 100°F — Tomato red-orange
        ("Scorching", "#800080"),                         # 100 to 110°F — Red
        ("Extreme Heat", "#8B00FF"),                      # 110 to 120°F — Purple
        ]

    dewpoint_categories = [
        ("Extremely Dry", "#5C4033"),        # < 0°F — Dark brown (very dry, static risk)
        ("Very Dry", "#7B4D1C"),             # 0–10°F — Saddle brown
        ("Dry", "#A0522D"),                  # 10–20°F — Sienna (dry but tolerable)
        ("Comfortably Dry", "#C19A6B"),      # 20–35°F — Tan (cool, dry air)
        ("Comfortable", "#ADFFB0"),          # 35–55°F — Light mint green (ideal comfort range)
        ("Muggy-lite", "#7CFC00"),     # 55–60°F — Lawn green (fresh but sticky)
        ("Humid", "#32CD32"),                # 60–65°F — Lime green (muggy)
        ("Very Humid", "#228B22"),           # 65–70°F — Forest green (air feels heavy)
        ("Oppressive", "#006400"),           # 70–75°F — Dark green (suffocating)
        ("Miserable", "#013220")  # >75°F — Deep jungle green (extremely humid)
    ]



    wind_categories = [
        ("Light", "#88C0D0"),
        ("Moderate", "#EBCB8B"),
        ("Extreme", "#BF616A"),
    ]

    # Create Temperature Dial
    svg_dial_temperature = create_svg_dial(round(temperature), temperature_categories)

    svg_dial_dewpoint = create_svg_dial(round(dewpoint), dewpoint_categories)
    if speed:
        svg_dial_wind = create_svg_dial_wind(speed, wind_categories, direction)
    return [svg_dial_temperature, svg_dial_dewpoint, svg_dial_wind]

"""
svg = create_dial(60.0, 5.0, 180.0)
print(svg)

with open("debug_dial.svg", "w") as f:
    f.write(svg)
"""
