import os
from playwright.async_api import async_playwright
import uuid

class SlideService:
    def __init__(self):
        self.output_dir = os.path.join(os.getcwd(), "data", "outputs", "slides")
        os.makedirs(self.output_dir, exist_ok=True)

    async def generate_slide_image(self, html_content: str, css_content: str = "") -> str:
        """
        Renders HTML+CSS to an image using Playwright.
        Returns the path to the generated image.
        """
        
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ 
                    margin: 0; 
                    padding: 0; 
                    width: 1920px; 
                    height: 1080px; 
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    background: #1e1e1e; /* Fallback */
                }}
                {css_content}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        filename = f"{uuid.uuid4()}.png"
        filepath = os.path.join(self.output_dir, filename)

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page(viewport={"width": 1920, "height": 1080})
            await page.set_content(full_html)
            await page.screenshot(path=filepath)
            await browser.close()
            
        return filepath

slide_service = SlideService()
