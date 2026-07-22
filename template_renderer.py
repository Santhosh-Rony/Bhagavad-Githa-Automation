import os
from PIL import Image, ImageDraw, ImageFont
from config import Config
from logger import logger
from models import GitaPost

# ── Fonts (same as Mahabharata automation) ─────────────────────────────────
FONT_BOLD    = "assets/NotoSansTelugu-Bold.ttf"
FONT_REGULAR = "assets/NotoSansTelugu-Regular.ttf"
FONT_SERIF   = "assets/NotoSerif-VariableFont_wdth,wght.ttf"   # for Sanskrit & watermark

# ── Colors (identical to Mahabharata automation) ───────────────────────────
COLOR_TITLE   = (90,  40,  10,  255)   # Dark brown  — main title
COLOR_SECTION = (139, 69,  19,  255)   # SaddleBrown — section labels
COLOR_CONTENT = (30,  30,  30,  255)   # Almost black — body text
COLOR_WM      = (139, 69,  19,  200)   # SaddleBrown semi-transparent — watermark


def load_font(path: str, size: int):
    try:
        return ImageFont.truetype(path, size)
    except IOError:
        return ImageFont.load_default()


def wrap_text(text: str, font, max_width: int, draw) -> str:
    """Word-wraps text to fit within max_width pixels, preserving original newlines."""
    wrapped_lines = []
    for paragraph in text.split('\n'):
        words = paragraph.split(' ')
        current_line = []
        for word in words:
            if not word:
                continue
            current_line.append(word)
            test = " ".join(current_line)
            l, t, r, b = draw.textbbox((0, 0), test, font=font)
            if (r - l) > max_width and len(current_line) > 1:
                current_line.pop()
                wrapped_lines.append(" ".join(current_line))
                current_line = [word]
        if current_line:
            wrapped_lines.append(" ".join(current_line))
    return "\n".join(wrapped_lines)


def render_gita_image(post: GitaPost, cta_text: str, template_path: str, output_path: str):
    """
    Renders the Telugu Bhagavad Gita layout onto the background template.
    """
    logger.info(f"Rendering Bhagavad Gita image: Chapter {post.chapter}, Verse {post.verse}")

    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template not found: {template_path}")

    try:
        # ── Auto-shrink loop (same pattern as Mahabharata) ────────────────
        base_content_size = 34
        base_title_size   = 40

        while base_content_size >= 28:

            # Load fonts at current sizes
            title_font        = load_font(FONT_BOLD,    80)               # శ్రీమద్భగవద్గీత
            badge_font        = load_font(FONT_REGULAR, 44)               # అధ్యాయం X • శ్లోకం Y
            section_title_font = load_font(FONT_BOLD,   base_title_size)  # section labels
            content_font      = load_font(FONT_BOLD,    base_content_size) # body text
            sloka_font        = load_font(FONT_BOLD,    base_content_size) # Telugu script

            img_width  = 1080
            img_height = 1920
            x_margin   = 140                                 # Balanced left margin so text isn't extreme left
            right_pad  = 220                                 # Clear the right tree trunk
            max_width  = img_width - x_margin - right_pad    # 720px safe content area

            def _layout_pass(draw, spacing_bonus=0):
                """Full layout — returns the final bottom Y coordinate."""

                # ── 1. HEADER: శ్రీమద్భగవద్గీత (centered perfectly in the middle of the template) ──
                header = "శ్రీమద్భగవద్గీత"
                draw.text(
                    (img_width / 2, 225),
                    header,
                    font=title_font,
                    fill=COLOR_TITLE,
                    anchor="ms",
                    stroke_width=1,
                    stroke_fill=COLOR_TITLE
                )
                l, t, r, b = draw.textbbox((0, 0), header, font=title_font, stroke_width=1)
                text_w = r - l
                # Underline below header
                draw.line(
                    [(img_width / 2 - text_w / 2, 245),
                     (img_width / 2 + text_w / 2, 245)],
                    fill=COLOR_TITLE, width=5
                )

                # ── 2. BADGE: అధ్యాయం X - శ్లోకం Y ──
                badge = f"అధ్యాయం {post.chapter}  -  శ్లోకం {post.verse}"
                draw.text(
                    (img_width / 2, 320),
                    badge,
                    font=badge_font,
                    fill=COLOR_SECTION,
                    anchor="ms",
                    stroke_width=1,
                    stroke_fill=COLOR_SECTION
                )

                # Start the sloka slightly lower to add breathing room from the badge
                current_y = 425

                # ── 3. SLOKA section ──────────────────────────────────────
                sloka_title = f"శ్లోకం (భగవద్గీత {post.chapter}.{post.verse})"
                current_y = _draw_section(
                    draw, sloka_title, post.sloka,
                    current_y, x_margin, max_width,
                    section_title_font, sloka_font, spacing_bonus
                )

                # ── 4. ARTHA section ──────────────────────────────────────
                safe_artha = post.artha if len(post.artha) <= 450 else post.artha[:447] + "..."
                current_y = _draw_section(
                    draw, "అర్థం (సులభమైన తెలుగులో)", safe_artha,
                    current_y, x_margin, max_width,
                    section_title_font, content_font, spacing_bonus
                )

                # ── 5. TEACHING section ───────────────────────────────────
                current_y = _draw_section(
                    draw, "ఈ శ్లోకం మనకు నేర్పేది :", "",
                    current_y, x_margin, max_width,
                    section_title_font, content_font, spacing_bonus,
                    bullet_points=post.teaching
                )

                # ── 6. CTA line ───────────────────────────────────────────
                current_y += (spacing_bonus // 2)  # Slight extra breathing room for the final CTA
                safe_cta = cta_text if len(cta_text) <= 200 else cta_text[:197] + "..."
                wrapped_cta = wrap_text(safe_cta, section_title_font, max_width, draw)
                draw.multiline_text(
                    (x_margin, current_y),
                    wrapped_cta,
                    font=section_title_font,
                    fill=COLOR_SECTION,
                    spacing=10
                )
                l, t, r, b = draw.multiline_textbbox(
                    (x_margin, current_y), wrapped_cta,
                    font=section_title_font, spacing=10
                )
                return b

            def _draw_section(draw, label, content, y, x_margin, max_w,
                               label_font, body_font, spacing_bonus, bullet_points=None):
                """Draws a label + content block (or bulleted list with hanging indents), returns next Y."""
                # Label (SaddleBrown, bold, left-aligned)
                draw.text(
                    (x_margin, y), label,
                    font=label_font,
                    fill=COLOR_SECTION,
                    stroke_width=1,
                    stroke_fill=COLOR_SECTION
                )
                l, t, r, b = draw.textbbox((0, 0), label, font=label_font, stroke_width=1)
                y_content = y + (b - t) + 12

                if bullet_points:
                    bullet_text = "-  "
                    bullet_bbox = draw.textbbox((0, 0), bullet_text, font=body_font)
                    bullet_w = bullet_bbox[2] - bullet_bbox[0]
                    text_max_w = max_w - bullet_w
                    
                    current_y_point = y_content
                    for point in bullet_points:
                        point_clean = point.strip("- •* ")
                        wrapped = wrap_text(point_clean, body_font, text_max_w, draw)
                        
                        # Draw bullet mark
                        draw.text((x_margin, current_y_point), "- ", font=body_font, fill=COLOR_CONTENT)
                        
                        # Draw wrapped text with hanging indent
                        draw.multiline_text(
                            (x_margin + bullet_w, current_y_point),
                            wrapped,
                            font=body_font,
                            fill=COLOR_CONTENT,
                            spacing=12
                        )
                        l, t, r, b = draw.multiline_textbbox(
                            (x_margin + bullet_w, current_y_point), wrapped,
                            font=body_font, spacing=12
                        )
                        current_y_point = b + 15 # spacing between bullet points
                    
                    # Return next Y coordinate, adjusting for the last bullet point's padding
                    return (current_y_point - 15) + 35 + spacing_bonus

                else:
                    # Content (almost black, left-aligned)
                    wrapped = wrap_text(content, body_font, max_w, draw)
                    draw.multiline_text(
                        (x_margin, y_content),
                        wrapped,
                        font=body_font,
                        fill=COLOR_CONTENT,
                        spacing=12
                    )
                    l, t, r, b = draw.multiline_textbbox(
                        (x_margin, y_content), wrapped,
                        font=body_font, spacing=12
                    )
                    # Base gap of 35px + capped dynamic bonus
                    return b + 35 + spacing_bonus

            # ── PASS 1: Measure on dummy image ────────────────────────────
            dummy_img  = Image.new("RGBA", (img_width, img_height))
            dummy_draw = ImageDraw.Draw(dummy_img)
            final_y    = _layout_pass(dummy_draw, spacing_bonus=0)
            target_bottom = 1550

            if final_y > target_bottom:
                if base_content_size > 28:
                    logger.warning(
                        f"Text overflowed (Y={final_y} > {target_bottom}). "
                        f"Shrinking font to {base_content_size - 2}px."
                    )
                    base_content_size -= 2
                    base_title_size   -= 2
                    continue
                else:
                    logger.warning("Text still overflowed at minimum size. Content may clip slightly.")
                    spacing_bonus = 0
            else:
                empty_space = target_bottom - final_y
                # Distribute space evenly between the 3 main gaps (Sloka->Artha, Artha->Teaching, Teaching->CTA)
                # But CAP it at 50px so they never look disjointed and weirdly far apart.
                spacing_bonus = min(50, int(empty_space / 3.5))
                logger.info(
                    f"Layout fits at {base_content_size}px. "
                    f"Applying dynamic spacing bonus of {spacing_bonus}px between sections."
                )

            # ── PASS 2: Final render on real template ──────────────────────
            with Image.open(template_path) as img:
                # Force image to exact 1080x1920 to fix FFmpeg 'width not divisible by 2' error 
                # and ensure all our hardcoded layout coordinates perfectly match the image.
                img = img.resize((img_width, img_height), Image.Resampling.LANCZOS)
                
                draw = ImageDraw.Draw(img)
                _layout_pass(draw, spacing_bonus=spacing_bonus)

                # Watermark — use FONT_SERIF so English characters render properly
                watermark_font = load_font(FONT_SERIF, 30)
                draw.text(
                    (img_width / 2, 1840),
                    "@bhagavadgita_telugu",
                    font=watermark_font,
                    fill=COLOR_WM,
                    anchor="ms"
                )

                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                img.save(output_path, "PNG", quality=95)
                logger.info("Successfully rendered Gita Reel image.")
                return

        logger.error("Could not fit text even at minimum font sizes!")

    except Exception as e:
        logger.error(f"Failed to render Gita image: {e}")
        raise
