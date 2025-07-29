# Syqlorix: Build Hyper-Minimal Web Pages in Pure Python

<p align="center">
  <img src="https://raw.githubusercontent.com/Syqlorix/Syqlorix/refs/heads/main/syqlorix-logo.svg" alt="Syqlorix Logo" width="250"/>
</p>


## Overview

**Syqlorix** is a futuristic Python package inspired by Flask and Dominate, designed to build full HTML documents—including **CSS** and **JavaScript**—from a **single Python script**. It offers a pure Python DSL (Domain-Specific Language) for authoring web interfaces, making it a single-file web page builder that is zero-dependency, readable, and easily embeddable for dynamic web content creation.

## Goals & Design Philosophy

🔹 **Simpler than Dominate**
🔹 **More readable than raw HTML**
🔹 **No need for separate `.html`, `.css`, or `.js` files**

### Core Design Principles

*   **All-in-One**: Write entire pages in one `.py` file.
*   **Minimal API**: Small surface area, quick to learn.
*   **Super Readable**: Feels like Markdown, acts like HTML.
*   **Framework-Ready**: Works seamlessly with Flask, Starlette, etc.
*   **Tech-Aesthetic**: Feels modern, futuristic, efficient.

## Example Usage

### Single Page Generation

```python
from syqlorix import Page

page = Page(title="Welcome to Syqlorix")

with page.body:
    page.h1("Build Pages in Python")
    page.p("No need for HTML files. This is all Python.")
    with page.div(id="features"):
        page.h2("Key Features")
        page.ul(
            page.li("HTML via functions"),
            page.li("Inline CSS/JS blocks"),
            page.li("Flask integration"),
        )
    page.button("Click Me", id="btn", _class="my-button")

page.style("""
    body { font-family: system-ui; margin: 40px; }
    #features { background: #f0f0f0; padding: 10px; border-radius: 6px; }
    .my-button { background: #0d6efd; color: white; border: none; padding: 10px 15px; border-radius: 4px; cursor: pointer; }
    .my-button:hover { background: #0a58ca; }
""")

page.script("""
    document.getElementById('btn').onclick = function() {
        alert('Clicked with Syqlorix!');
    };
""")

html_output = page.render()
print(html_output)
```

### Multi-Page Development Server

Create an `examples/multi_page_site.py` file to define your site's routes:

```python
# examples/multi_page_site.py
from syqlorix import Page, css
import datetime

def common_header(page_instance: Page):
    with page_instance.header(_class="site-header"):
        page_instance.h1("Syqlorix Site")
        with page_instance.nav(_class="site-nav"):
            page_instance.a("Home", href="/")
            page_instance.a("About", href="/about")
            page_instance.a("Dynamic", href="/dynamic")
            page_instance.a("Static Assets", href="/static-demo")

def common_footer(page_instance: Page):
    page_instance.footer(f"© {datetime.datetime.now().year} Syqlorix Demo Site")

base_styles_dict = {
    "body": {
        "font_family": "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
        "margin": "0",
        "padding": "0",
        "background": "#f8f9fa",
        "color": "#333",
        "line_height": "1.6"
    },
    ".site-header": {
        "background_color": "#0d6efd",
        "color": "white",
        "padding": "20px 40px",
        "text_align": "center"
    },
    ".site-nav a": {
        "color": "white",
        "margin": "0 15px",
        "text_decoration": "none",
        "font_weight": "bold"
    },
    ".site-nav a:hover": {
        "text_decoration": "underline"
    },
    "main": {
        "padding": "20px 40px",
        "max_width": "800px",
        "margin": "20px auto",
        "background": "white",
        "border_radius": "8px",
        "box_shadow": "0 2px 10px rgba(0,0,0,0.05)"
    },
    "footer": {
        "text_align": "center",
        "padding": "20px",
        "margin_top": "50px",
        "color": "#666",
        "border_top": "1px solid #eee"
    }
}
base_styles = css(**base_styles_dict)


home_page = Page(title="Home - My Syqlorix Site")
home_page.style(base_styles)
home_page.link_css(href="/static/css/main.css")

with home_page.body:
    common_header(home_page)
    with home_page.main():
        home_page.h1("Welcome to Syqlorix Site!")
        home_page.p("This is the home page. Explore the new features!")
        home_page.p("This page links to an external CSS file: `static/css/main.css`.")
        home_page.p("The header and footer are reusable Python components.")
        home_page.p("Also, the `meta` and `title` tags are now directly addable.")
    common_footer(home_page)

about_page = Page(title="About Us")
about_page.style(base_styles)
with about_page.body:
    common_header(about_page)
    with about_page.main():
        about_page.h1("About Our Project")
        about_page.p("Syqlorix is an amazing Python DSL for web development.")
        about_page.p("It aims to simplify creating web interfaces directly in Python.")
    common_footer(about_page)

def create_dynamic_page() -> Page:
    dynamic_page = Page(title="Dynamic Content")
    dynamic_page.style(base_styles)
    with dynamic_page.body:
        common_header(dynamic_page)
        with dynamic_page.main():
            dynamic_page.h1("Current Time")
            dynamic_page.p(f"The current time is: {datetime.datetime.now().strftime('%H:%M:%S')}")
            dynamic_page.p("This content is generated fresh on each request.")
        common_footer(dynamic_page)
    return dynamic_page

static_demo_page = Page(title="Static Assets Demo")
static_demo_page.style(base_styles)
static_demo_page.link_css(href="/static/css/main.css") 
static_demo_page.link_js(src="/static/js/app.js", defer=True)

with static_demo_page.body:
    common_header(static_demo_page)
    with static_demo_page.main():
        static_demo_page.h1("External Static Assets")
        static_demo_page.p("This page uses an external CSS file and an external JavaScript file.")
        static_demo_page.div("This box is styled by `static/css/main.css`.", _class="external-box")
        static_demo_page.button("Click Me (External JS)", id="externalBtn")
        static_demo_page.p("Check the browser's console for a message from `static/js/app.js`.")
    common_footer(static_demo_page)


routes = {
    "/": home_page,
    "/about": about_page,
    "/dynamic": create_dynamic_page,
    "/static-demo": static_demo_page,
}

if __name__ == '__main__':
    from syqlorix import serve_pages_dev
    serve_pages_dev(routes, port=8000)
```

Then run from your terminal:
```bash
syqlorix serve examples/multi_page_site.py
```
(Ctrl+Click the link printed in the terminal to view in browser.)

### Static Site Generation (CLI)

Using the `examples/multi_page_site.py` as your site definition:
```bash
syqlorix build examples/multi_page_site.py --output public
```
This will generate `public/index.html`, `public/about/index.html`, `public/dynamic/index.html`, and `public/static/` directory with your assets.

### Flask Integration

```python
from flask import Flask, render_template_string
from syqlorix import Page

app = Flask(__name__)

@app.route('/')
def home():
    page = Page(title="Syqlorix with Flask")
    with page.body:
        page.h1("Hello from Flask and Syqlorix!")
        page.p("This page was generated entirely using Syqlorix within a Flask app.")
        page.div("No separate HTML templates needed!", _class="flask-info")
        page.button("Click me!", id="flaskBtn")

    page.style("""
        body { font-family: 'Arial', sans-serif; margin: 60px; background: #f8f9fa; color: #495057; text-align: center; }
        h1 { color: #6f42c1; margin-bottom: 20px; }
        .flask-info { background: #e9ecef; padding: 25px; border-radius: 8px; margin: 30px auto; max-width: 600px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        button { background: #007bff; color: white; border: none; padding: 15px 30px; border-radius: 25px; cursor: pointer; font-size: 1.2em; transition: background 0.3s ease; }
        button:hover { background: #0056b3; }
    """)

    page.script("""
        document.getElementById('flaskBtn').onclick = function() {
            alert('Flask page clicked via Syqlorix JS!');
        };
    """)

    html_output = page.render()
    return render_template_string(html_output)

if __name__ == '__main__':
    # Install Flask: pip install Flask
    print("\n" + "="*50)
    print(" Flask App with Syqlorix ")
    print(" Open your browser to: http://127.0.0.1:5000/ ")
    print("="*50 + "\n")
    app.run(debug=True, port=5000)
```

## Key API Features

*   `Page(...)` → Main class to construct a page.
*   `page.h1()`, `page.div()`, `page.ul()` → HTML tag functions.
*   `with page.body:` → Context-managed content creation for nesting.
*   **Components:** Python functions can serve as reusable components. Just define a function that takes a `Page` instance (or implicitly uses the `page` object if it's accessible in its scope) and generates HTML. Call the function within your page building logic.
*   `page.style(css_str)` → Add CSS inline within a `<style>` tag in the `<head>`.
*   `syqlorix.css(**rules)` → Programmatic CSS DSL to generate CSS strings from Python dictionaries.
*   `page.link_css(href='...')` → Add an external CSS file link to the `<head>`.
*   `page.script(js_str)` → Add JS inline within a `<script>` tag before `</body>`.
*   `page.link_js(src='...')` → Add an external JavaScript file link to the `</body>`.
*   `page.meta(...)`, `page.link(...)`, `page.base(...)`, `page.title(...)` → These tags can now be directly called on the `page` object and are automatically added to the `<head>`.
*   `page.render()` → Outputs the full HTML page string including `<!DOCTYPE html>`.
*   `syqlorix serve <routes_file.py>` → CLI command to start a multi-page development server, serving pages and static assets from the project root, providing a clickable link and auto-detection in Codespaces.
*   `syqlorix build <routes_file.py> -o <output_dir>` → CLI command to generate a static site from a routes file, including copying static assets.

## Target Use Cases

*   **Fast Prototyping**: Quickly mock up HTML content without juggling multiple files, using `syqlorix serve`.
*   **Dynamic HTML Generation**: For developers who need to generate HTML on the fly without a full-blown templating engine.
*   **Educational Tools**: A clear, Python-only way to demonstrate HTML structure.
*   **Static Site Generation**: Build simple static sites purely with Python scripts using `syqlorix build`.
*   **Small Web Services**: Embed HTML generation directly into Flask/Starlette applications.

## Name Rationale: “Syqlorix”

*   💡 *Invented word*: completely unique and claimable.
*   🧠 *Tech-aesthetic*: futuristic, protocol-sounding.
*   💎 *Rare*: zero collisions on Google, PyPI, or GitHub.
*   ⚡ *Brand-ready*: distinctive and pronounceable.

## Future Directions

*   More specialized element helpers for forms, media etc.
*   Advanced component system (e.g., with explicit component definition APIs).

## Get Started (Local Installation)

1.  **Clone this repository**
2.  **Navigate to the project root** in your terminal.
3.  **Install in editable mode** (for development) or as a regular package:

    ```bash
    pip install .
    ```

    Once published to PyPI, you can install directly:
    ```bash
    pip install syqlorix
    ```

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.