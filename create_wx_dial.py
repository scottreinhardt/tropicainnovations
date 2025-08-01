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
        ("Extreme Cold (Frostbite Risk)", "#4B0082"),     # -40 to -10°F — Deep indigo (dangerously cold)
        ("Very Cold", "#1E90FF"),                         # -10 to 20°F — Dodger blue (very cold, but manageable)
        ("Cold", "#00BFFF"),                              # 20 to 40°F — Deep sky blue (chilly, jacket weather)
        ("Cool", "#87CEEB"),                              # 40 to 50°F — Light blue (mildly cool, light layer)
        ("Comfortable", "#2ECC71"),                       # 50 to 70°F — Soft green (ideal weather)
        ("Mildly Warm", "#F4D03F"),                       # 70 to 80°F — Golden yellow (sunny, pleasant)
        ("Warm", "#FFA500"),                              # 80 to 90°F — Orange (hot, caution in prolonged exposure)
        ("Hot", "#FF4500"),                               # 90 to 100°F — Orange-red (very hot, dehydration risk)
        ("Very Hot (Heat Exhaustion Risk)", "#FF0000"),   # 100 to 110°F — Red (danger of heat stress)
        ("Extreme Heat (Heat Stroke Risk)", "#8B0000")    # 110 to 120°F — Dark red (life-threatening)
    ]

    dewpoint_categories = [
        ("Extremely Dry", "#8B4513"),        # < 0°F — SaddleBrown (very dry, static risk)
        ("Very Dry", "#A0522D"),             # 0–10°F — Sienna (dry, lips/chapped skin)
        ("Dry", "#CD853F"),                  # 10–20°F — Peru (dry but not extreme)
        ("Comfortably Dry", "#DAA520"),      # 20–35°F — Goldenrod (cool, low humidity)
        ("Comfortable", "#2ECC71"),          # 35–55°F — Green (ideal comfort range)
        ("Noticeably Humid", "#F1C40F"),     # 55–60°F — Yellow (some may notice stickiness)
        ("Humid", "#FFA500"),                # 60–65°F — Orange (muggy, unpleasant for many)
        ("Very Humid", "#FF6347"),           # 65–70°F — Tomato (sweaty, uncomfortable)
        ("Oppressive", "#FF0000"),           # 70–75°F — Red (air feels heavy, hard to cool off)
        ("Extremely Oppressive", "#8B0000")  # >75°F — DarkRed (dangerous for prolonged exertion)
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