import os
import re
from bs4 import BeautifulSoup

base_dir = r"d:\portfolio\personal_portfolio"

sections = [
    ("hero section/harsit-portfolio-hero.html", "hero"),
    ("about/harsit-about.html", "about"),
    ("journey/harsit-journey-1.html", "journey"),
    ("skill/skills-section.html", "skills"),
    ("project/harsit-projects.html", "projects"),
    ("certification/harsit-certifications.html", "certifications"),
    ("testimonial/contact-section.html", "contact"),
    ("footer/footer-section.html", "footer")
]

combined_html = ""
combined_css = ""
combined_js = ""
fonts = set()

# Process first file (Hero) to get the base structure
with open(os.path.join(base_dir, sections[0][0]), "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

for link in soup.find_all("link"):
    fonts.add(str(link))

# Extract original CSS from Hero
hero_style = soup.find("style").string if soup.find("style") else ""
# Remove overflow: hidden and height: 100% from html and body
hero_style = re.sub(r'html\s*\{[^}]*overflow:\s*hidden[^}]*\}', 'html { scroll-behavior: smooth; }', hero_style)
hero_style = re.sub(r'height:\s*100%;', '', hero_style)
hero_style = re.sub(r'overflow:\s*hidden;', '', hero_style)

combined_css += hero_style + "\n"

# Extract JS from Hero
hero_script = soup.find("script").string if soup.find("script") else ""
combined_js += hero_script + "\n"

# Get body content from Hero
body = soup.find("body")

# Change Hero's nav links to point to sections
nav = body.find("nav")
if nav:
    ul = nav.find("ul")
    if ul:
        links = ul.find_all("a")
        if len(links) >= 4:
            links[0]['href'] = "#top"      # Home
            links[1]['href'] = "#about"    # About
            links[2]['href'] = "#projects" # Projects
            links[3]['href'] = "#contact"  # Contact
            # We'll add Journey, Skills, Certifications back

mobile_menu = body.find("div", class_="mobile-menu")
if mobile_menu:
    mobile_links = mobile_menu.find_all("a")
    if len(mobile_links) >= 4:
        mobile_links[0]['href'] = "#top"
        mobile_links[1]['href'] = "#about"
        mobile_links[2]['href'] = "#projects"
        mobile_links[3]['href'] = "#contact"

# Give hero section an ID
hero_sec = body.find("section", class_="hero")
if hero_sec:
    hero_sec['id'] = "top"

# Now parse the rest of the sections
for filepath, sec_id in sections[1:]:
    with open(os.path.join(base_dir, filepath), "r", encoding="utf-8") as f:
        s = BeautifulSoup(f.read(), "html.parser")
    
    # Collect fonts
    for link in s.find_all("link"):
        fonts.add(str(link))
        
    # Collect styles (avoiding global duplicates)
    style = s.find("style")
    if style:
        css = style.string
        # Remove common resets and global tags to avoid overwriting hero
        css = re.sub(r'\*,\s*\*\:\:before,\s*\*\:\:after\s*\{[^}]*\}', '', css)
        css = re.sub(r':root\s*\{[^}]*\}', '', css) # remove root variables except if specific
        css = re.sub(r'html,\s*body\s*\{[^}]*\}', '', css)
        css = re.sub(r'html\s*\{[^}]*\}', '', css)
        css = re.sub(r'body\s*\{[^}]*\}', '', css)
        css = re.sub(r'::-webkit-scrollbar\s*\{[^}]*\}', '', css)
        css = re.sub(r'#grain\s*\{[^}]*\}', '', css)
        css = re.sub(r'@keyframes grain\s*\{[^}]*\}', '', css)
        css = re.sub(r'#cursor-orb\s*\{[^}]*\}', '', css)
        css = re.sub(r'#cursor-trail\s*\{[^}]*\}', '', css)
        css = re.sub(r'\.blob\s*\{[^}]*\}', '', css)
        css = re.sub(r'\.blob-\d+\s*\{[^}]*\}', '', css)
        css = re.sub(r'@keyframes bdrift\s*\{[^}]*\}', '', css)
        css = re.sub(r'@keyframes bd\s*\{[^}]*\}', '', css)
        css = re.sub(r'nav\s*\{[^}]*\}', '', css)
        css = re.sub(r'nav\.scrolled\s*\{[^}]*\}', '', css)
        css = re.sub(r'\.nav-logo.*?(?=\})\}', '', css, flags=re.DOTALL)
        css = re.sub(r'\.nav-links.*?(?=\})\}', '', css, flags=re.DOTALL)
        css = re.sub(r'\.hamburger.*?(?=\})\}', '', css, flags=re.DOTALL)
        css = re.sub(r'\.mobile-menu.*?(?=\})\}', '', css, flags=re.DOTALL)
        
        # Scoped classes prefix
        combined_css += f"\n/* CSS from {sec_id} */\n" + css + "\n"

    # Collect JS (only specific stuff)
    script = s.find("script")
    if script:
        js = script.string
        # Remove cursor, grain, navbar logic from subsequent scripts
        js = re.sub(r'/\*\s*──\s*CURSOR.*?(?=/\*|$)', '', js, flags=re.DOTALL)
        js = re.sub(r'const\s+orb\s*=.*?\(\);', '', js, flags=re.DOTALL)
        js = re.sub(r'/\*\s*──\s*NAVBAR.*?}\);', '', js, flags=re.DOTALL)
        js = re.sub(r'const\s+nav\s*=.*?\);', '', js, flags=re.DOTALL)
        js = re.sub(r'/\*\s*──\s*HAMBURGER.*?}\)\);', '', js, flags=re.DOTALL)
        js = re.sub(r'const\s+ham\s*=.*?\)\);', '', js, flags=re.DOTALL)

        combined_js += f"\n/* JS from {sec_id} */\n" + js + "\n"
        
    # Collect Body Content
    s_body = s.find("body")
    
    # We want to extract just the section or page div
    # Some use <div class="page"><section>...</section></div>
    # Footer uses <footer class="site-footer">
    
    if sec_id == "footer":
        footer_el = s_body.find("footer")
        if footer_el:
            body.append(footer_el)
    else:
        page_div = s_body.find("div", class_="page")
        if page_div:
            # add the section ID
            sec_el = page_div.find("section")
            if sec_el and not sec_el.has_attr("id"):
                sec_el["id"] = sec_id
            body.append(page_div)
        else:
            sec_el = s_body.find("section")
            if sec_el:
                if not sec_el.has_attr("id"):
                    sec_el["id"] = sec_id
                body.append(sec_el)

# Unify navigation
if nav:
    ul = nav.find("ul")
    if ul:
        ul.clear()
        menu_items = [
            ("Home", "#top"),
            ("About", "#about"),
            ("Journey", "#journey"),
            ("Skills", "#skills"),
            ("Projects", "#projects"),
            ("Certifications", "#certs"),
            ("Contact", "#contact")
        ]
        for name, link in menu_items:
            li = soup.new_tag("li")
            a = soup.new_tag("a", href=link)
            a.string = name
            li.append(a)
            ul.append(li)

if mobile_menu:
    mobile_menu.clear()
    for name, link in menu_items:
        a = soup.new_tag("a", href=link)
        a.string = name
        mobile_menu.append(a)


# Build final HTML
final_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Harsit Chavda — Portfolio</title>
{"".join(fonts)}
<style>
{combined_css}
</style>
</head>
<body>
{body.decode_contents()}
<script>
{combined_js}
</script>
</body>
</html>'''

with open(os.path.join(base_dir, "index.html"), "w", encoding="utf-8") as f:
    f.write(final_html)

print("index.html created successfully.")
