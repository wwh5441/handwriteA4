
import asyncio
from generate_page_screenshot import capture_first_page_screenshot

async def generate_png():
    html_file = "A4_complete_5000words_demo.html"
    output_file = "A4_complete_5000words_demo.png"
    try:
        await capture_first_page_screenshot(html_file, output_file)
    except Exception as e:
        print(f"Error generating screenshot: {e}")

if __name__ == "__main__":
    asyncio.run(generate_png())
