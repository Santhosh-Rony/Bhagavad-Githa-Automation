import os
from PIL import Image, ImageDraw, ImageFont
from config import Config
from logger import logger
from models import CharacterPost

def load_font(font_path: str, size: int):
    try:
        return ImageFont.truetype(font_path, size)
    except IOError:
        return ImageFont.load_default()

def wrap_text(text: str, font, max_width: int, draw) -> str:
    lines = []
    words = text.split()
    current_line = []
    
    for word in words:
        current_line.append(word)
        test_line = " ".join(current_line)
        left, top, right, bottom = draw.textbbox((0, 0), test_line, font=font)
        if (right - left) > max_width and len(current_line) > 1:
            current_line.pop()
            lines.append(" ".join(current_line))
            current_line = [word]
            
    if current_line:
        lines.append(" ".join(current_line))
    return "\n".join(lines)

def draw_section(draw, title: str, content: str, y_start: int, max_width: int, title_font, content_font, x_margin: int) -> int:
    """Draws a section with a title and content, returns the new Y position."""
    # Dark brown/gold for section titles for high contrast
    title_color = (139, 69, 19, 255) # SaddleBrown
    content_color = (30, 30, 30, 255) # Almost black for high readability
    
    # Draw Title
    draw.text((x_margin, y_start), title, font=title_font, fill=title_color, stroke_width=1, stroke_fill=title_color) 
    
    left, top, right, bottom = draw.textbbox((0, 0), title, font=title_font, stroke_width=1)
    title_height = bottom - top
    y_content = y_start + title_height + 25
    
    # Wrap and Draw Content
    wrapped_content = wrap_text(content, content_font, max_width, draw)
    draw.multiline_text((x_margin, y_content), wrapped_content, font=content_font, fill=content_color, spacing=15)
    
    left, top, right, bottom = draw.multiline_textbbox((x_margin, y_content), wrapped_content, font=content_font, spacing=15)
    content_height = bottom - top
    
    return y_content + content_height + 40 # Return new Y position with extra padding

def render_reel_image(post: CharacterPost, template_path: str, output_path: str):
    logger.info(f"Rendering character post for {post.title}")
    
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template not found at {template_path}. Please add your 9:16 template here.")
        
    try:
        # Default fixed sizes for premium aesthetic
        base_content_size = 34
        base_title_size = 40
        
        while base_content_size >= 28:
            font_path = "assets/NotoSansTelugu-Bold.ttf"
            font_italic_path = "assets/NotoSansTelugu-Regular.ttf"
            
            title_font = load_font(font_path, 80)
            section_title_font = load_font(font_path, base_title_size)
            content_font = load_font(font_path, base_content_size)
            quiz_font = load_font(font_path, base_content_size)
            
            img_width, img_height = 1080, 1920
            x_margin = 100
            max_width = img_width - (x_margin * 2) - 80
            
            def _layout_pass(draw, spacing_bonus=0):
                """Executes layout logic and returns the final bottom Y-coordinate."""
                # Main Title
                if "|" in post.title:
                    parts = post.title.split("|")
                    char_name = parts[0].strip().upper()
                    epithet = parts[1].strip()
                    
                    name_font = load_font(font_path, 100)
                    draw.text((img_width/2, 190), char_name, font=name_font, fill=(90, 40, 10, 255), anchor="ms", stroke_width=1, stroke_fill=(90, 40, 10, 255))
                    
                    left, top, right, bottom = draw.textbbox((0, 0), char_name, font=name_font, stroke_width=1)
                    text_w = right - left
                    line_y = 210
                    draw.line([(img_width/2 - text_w/2, line_y), (img_width/2 + text_w/2, line_y)], fill=(90, 40, 10, 255), width=5)
                    
                    epithet_font = load_font(font_italic_path, 50)
                    draw.text((img_width/2, 280), epithet, font=epithet_font, fill=(90, 40, 10, 255), anchor="ms", stroke_width=1, stroke_fill=(90, 40, 10, 255))
                    
                    current_y = 320 + spacing_bonus
                else:
                    title_text = post.title.upper()
                    title_size = 80
                    t_font = load_font(font_path, title_size)
                    left, top, right, bottom = draw.textbbox((0, 0), title_text, font=t_font, stroke_width=1)
                    while (right - left) > (img_width - 100) and title_size > 30:
                        title_size -= 2
                        t_font = load_font(font_path, title_size)
                        left, top, right, bottom = draw.textbbox((0, 0), title_text, font=t_font, stroke_width=1)
                        
                    draw.text((img_width/2, 150), title_text, font=t_font, fill=(90, 40, 10, 255), anchor="ms", stroke_width=1, stroke_fill=(90, 40, 10, 255))
                    current_y = 280 + spacing_bonus
                
                # Content Sections
                current_y += 30
                for section in post.sections:
                    title_color = (139, 69, 19, 255)
                    content_color = (30, 30, 30, 255)
                    
                    # Hard Truncation Safety Net for Rogue AI
                    safe_content = section.content
                    if len(safe_content) > 180:
                        safe_content = safe_content[:177] + "..."
                        
                    draw.text((x_margin, current_y), section.title, font=section_title_font, fill=title_color, stroke_width=1, stroke_fill=title_color) 
                    left, top, right, bottom = draw.textbbox((0, 0), section.title, font=section_title_font, stroke_width=1)
                    
                    y_content = current_y + (bottom - top) + 10
                    
                    wrapped_content = wrap_text(safe_content, content_font, max_width, draw)
                    draw.multiline_text((x_margin, y_content), wrapped_content, font=content_font, fill=content_color, spacing=10)
                    
                    left, top, right, bottom = draw.multiline_textbbox((x_margin, y_content), wrapped_content, font=content_font, spacing=10)
                    current_y = y_content + (bottom - top) + 20 + spacing_bonus
                
                # Quiz Section
                quiz_y = current_y
                draw.text((x_margin, quiz_y), "ప్రశ్న :", font=section_title_font, fill=(139, 69, 19, 255), stroke_width=1, stroke_fill=(139, 69, 19, 255))
                quiz_y += 50
                
                q_wrapped = wrap_text(post.quiz.question, quiz_font, max_width, draw)
                draw.multiline_text((x_margin, quiz_y), q_wrapped, font=quiz_font, fill=(30, 30, 30, 255), spacing=10, align="left")
                
                left, top, right, bottom = draw.multiline_textbbox((x_margin, quiz_y), q_wrapped, font=quiz_font, spacing=10)
                quiz_y += (bottom - top) + 20
                
                # Quiz Options Safety Net
                safe_opts = [opt.text[:35] + "..." if len(opt.text) > 38 else opt.text for opt in post.quiz.options]
                opt_row1 = f"- {safe_opts[0]}      - {safe_opts[1]}"
                opt_row2 = f"- {safe_opts[2]}      - {safe_opts[3]}"
                
                left1, top1, right1, bottom1 = draw.textbbox((0, 0), opt_row1, font=quiz_font)
                left2, top2, right2, bottom2 = draw.textbbox((0, 0), opt_row2, font=quiz_font)
                
                if (right1 - left1) > max_width or (right2 - left2) > max_width:
                    for i, opt_text in enumerate(safe_opts):
                        letter = ["A", "B", "C", "D"][i]
                        full_opt = f"{letter}: {opt_text}"
                        opt_wrapped = wrap_text(full_opt, quiz_font, max_width, draw)
                        draw.multiline_text((x_margin, quiz_y), opt_wrapped, font=quiz_font, fill=(30, 30, 30, 255), spacing=8)
                        left, top, right, bottom = draw.multiline_textbbox((x_margin, quiz_y), opt_wrapped, font=quiz_font, spacing=8)
                        quiz_y += (bottom - top) + 12
                else:
                    draw.text((x_margin, quiz_y), opt_row1, font=quiz_font, fill=(30, 30, 30, 255))
                    quiz_y += (bottom1 - top1) + 12
                    draw.text((x_margin, quiz_y), opt_row2, font=quiz_font, fill=(30, 30, 30, 255))
                
                # Comment Call to Action
                quiz_y += 60 + spacing_bonus
                draw.text((x_margin, quiz_y), "సరైన సమాధానాన్ని కామెంట్ చేయండి!", font=section_title_font, fill=(139, 69, 19, 255), stroke_width=1, stroke_fill=(139, 69, 19, 255))
                
                left, top, right, bottom = draw.textbbox((x_margin, quiz_y), "సరైన సమాధానాన్ని కామెంట్ చేయండి!", font=section_title_font)
                return bottom
                
            # PASS 1: MEASURE HEIGHT ON DUMMY IMAGE
            dummy_img = Image.new("RGBA", (img_width, img_height))
            dummy_draw = ImageDraw.Draw(dummy_img)
            
            final_y = _layout_pass(dummy_draw, spacing_bonus=0)
            target_bottom = 1750
            
            if final_y > target_bottom:
                if base_content_size > 28:
                    logger.warning(f"Text overflowed perfectly fixed layout (Y={final_y} > {target_bottom}). Triggering Emergency Shrink.")
                    base_content_size -= 2
                    base_title_size -= 2
                    continue
                else:
                    logger.warning(f"Text STILL overflowed even at minimum safe size! (Y={final_y} > {target_bottom}). Content will clip slightly.")
                    spacing_bonus = 0
            else:
                empty_space = target_bottom - final_y
                spacing_bonus = int(empty_space / 7)
                logger.info(f"Layout fits beautifully at font size {base_content_size}px! Distributing {empty_space}px of extra space as a {spacing_bonus}px gap bonus.")
            
            # PASS 2: FINAL RENDER
            with Image.open(template_path) as img:
                draw = ImageDraw.Draw(img)
                _layout_pass(draw, spacing_bonus=spacing_bonus)
                
                watermark_text = "@mahabharata_chronicles"
                english_font_path = "assets/NotoSerif-VariableFont_wdth,wght.ttf"
                watermark_font = load_font(english_font_path, 30)
                draw.text((img_width/2, 1840), watermark_text, font=watermark_font, fill=(139, 69, 19, 200), anchor="ms")
                
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                img.save(output_path, "PNG", quality=95)
                logger.info("Successfully rendered Reel image.")
                return
                
        logger.error("Could not fit text even with minimum font sizes!")
            
    except Exception as e:
        logger.error(f"Failed to render image: {e}")
        raise
