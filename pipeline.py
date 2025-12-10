from PIL import Image, ImageOps, ImageFilter, ImageEnhance, ImageDraw, ImageFont

ASPECT_PRESETS = {
    'Square (1:1)': (1,1),
    'Portrait 3:4': (3,4),
    'Portrait 4:5': (4,5),
    'Landscape 16:9': (16,9),
    'Landscape 3:2': (3,2),
    'Vertical Reel 9:16': (9,16),
    'Ultrawide 21:9': (21,9),
}

QUALITY_PROFILES = {
    'Draft (1K)': '1K',
    'Standard (2K)': '2K',
    'Studio (4K)': '4K',
}

def get_pixel_dimensions(aspect_tuple, quality_profile):
    # Map quality profile labels '1K','2K','4K' to heights
    mapping = {'1K':1080, '2K':2160, '4K':3840}
    base_h = mapping.get(quality_profile, 2160)
    w_ratio, h_ratio = aspect_tuple
    height = base_h
    width = int(base_h * (w_ratio / h_ratio))
    return width, height

def contain_and_pad(img: Image.Image, target_w: int, target_h: int, fill=(0,0,0)):
    img_c = ImageOps.contain(img, (target_w, target_h))
    out = Image.new('RGB', (target_w, target_h), fill)
    x = (target_w - img_c.width) // 2
    y = (target_h - img_c.height) // 2
    out.paste(img_c, (x,y))
    return out

def apply_filters(img: Image.Image, brightness=1.0, contrast=1.0, saturation=1.0, sharpness=1.0, blur=0):
    if brightness != 1.0:
        img = ImageEnhance.Brightness(img).enhance(brightness)
    if contrast != 1.0:
        img = ImageEnhance.Contrast(img).enhance(contrast)
    if saturation != 1.0:
        img = ImageEnhance.Color(img).enhance(saturation)
    if sharpness != 1.0:
        img = ImageEnhance.Sharpness(img).enhance(sharpness)
    if blur > 0:
        img = img.filter(ImageFilter.GaussianBlur(radius=blur))
    return img

def add_watermark(img, text, opacity=180, margin=10, fontsize=24):
    base = img.convert('RGBA')
    txt = Image.new('RGBA', base.size, (255,255,255,0))
    d = ImageDraw.Draw(txt)
    try:
        font = ImageFont.truetype('DejaVuSans.ttf', fontsize)
    except:
        font = ImageFont.load_default()
    
    # textsize is deprecated in Pillow 10+
    left, top, right, bottom = d.textbbox((0,0), text, font=font)
    text_w = right - left
    text_h = bottom - top
    
    x = base.width - text_w - margin
    y = base.height - text_h - margin
    d.text((x,y), text, fill=(255,255,255, opacity), font=font)
    out = Image.alpha_composite(base, txt).convert('RGB')
    return out
