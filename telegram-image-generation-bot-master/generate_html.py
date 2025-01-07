import os
import json

# Folder containing the images and metadata
image_folder = os.path.join("bot", "image")

# Output HTML file
output_file = "index.html"

# Start of the HTML structure
# I mean there is css code first for style design ig you do not need comments on it :/
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Creative Image Gallery</title>
    <style> 
        body {
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #f0f8ff, #e6e6fa);
        }
        .filter-container {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: 30px;
            padding: 20px;
            background: linear-gradient(135deg, #ffffff, #f1f1f1);
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            border-radius: 20px;
        }
        .filter-container input, .filter-container select {
            margin: 0 10px;
            padding: 12px 15px;
            border: 1px solid #ddd;
            border-radius: 30px;
            font-size: 14px;
            box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.05);
            transition: box-shadow 0.3s, transform 0.2s;
        }
        .filter-container input:focus, .filter-container select:focus {
            outline: none;
            box-shadow: 0 3px 8px rgba(0, 0, 0, 0.2);
            transform: scale(1.05);
        }
        .filter-container input::placeholder {
            font-style: italic;
            color: #aaa;
        }
        .gallery {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
        }
        .gallery-item {
            margin: 15px;
            border: 2px solid #ddd;
            border-radius: 15px;
            overflow: hidden;
            background-color: #fff;
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s, box-shadow 0.2s;
            width: 300px;
        }
        .gallery-item:hover {
            transform: scale(1.05);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
        }
        .gallery-item img {
            width: 100%;
            height: auto;
        }
        .gallery-item p {
            margin: 10px;
            font-size: 14px;
            color: #444;
            text-align: center;
            padding: 5px 10px;
            background: linear-gradient(135deg, #ffefd5, #ffe4e1);
            border-radius: 10px;
            font-weight: bold;
        }
        .gallery-item p span {
            color: #ff4500;
        }
        .price {
            position: relative;
            display: inline-block;
        }
        .price .tooltip {
            visibility: hidden;
            width: auto;
            max-width: 250px;
            background-color: #555;
            color: #fff;
            text-align: center;
            border-radius: 5px;
            padding: 8px;
            position: absolute;
            z-index: 1;
            bottom: 120%;
            left: 90%;
            transform: translateX(-50%);
            opacity: 0;
            transition: opacity 0.3s;
            white-space: nowrap;
        }
        .price .tooltip::after {
            content: "";
            position: absolute;
            top: 100%;
            left: 50%;
            transform: translateX(-50%);
            border-width: 5px;
            border-style: solid;
            border-color: #555 transparent transparent transparent;
        }
        .price:hover .tooltip {
            visibility: visible;
            opacity: 1;
        }
        h1 {
            width: 100%;
            text-align: center;
            color: #4b0082;
            text-shadow: 2px 2px 5px #aaa;
            margin-bottom: 30px;
        }
        footer {
            text-align: center;
            margin-top: 30px;
            padding: 10px;
            background-color: #e6e6fa;
            border-top: 2px solid #ddd;
            color: #444;
        }
    </style>
    <script> // JavaScript function to filter gallery items based on user input
        function filterGallery() {
            const promptFilter = document.getElementById("prompt-filter").value.toLowerCase();
            const styleFilter = document.getElementById("style-filter").value.toLowerCase();
            const userFilter = document.getElementById("user-filter").value.toLowerCase();
            const priceFilter = parseFloat(document.getElementById("price-filter").value) || 0;

            const items = document.querySelectorAll(".gallery-item");
            items.forEach(item => {
                const prompt = item.getAttribute("data-prompt").toLowerCase();
                const style = item.getAttribute("data-style").toLowerCase();
                const user = item.getAttribute("data-user").toLowerCase();
                const price = parseFloat(item.getAttribute("data-price")) || 0;

                if (
                    (prompt.includes(promptFilter)) &&
                    (style.includes(styleFilter)) &&
                    (user.includes(userFilter)) &&
                    (price >= priceFilter)
                ) {
                    item.style.display = "block";
                } else {
                    item.style.display = "none";
                }
            });
        }
    </script>
</head>
<body>
    <h1>🎨 Creative Image Gallery</h1>
    <div class="filter-container">
        <input type="text" id="prompt-filter" placeholder="🔍 Filter by Prompt" oninput="filterGallery()">
        <input type="text" id="style-filter" placeholder="🎨 Filter by Style" oninput="filterGallery()">
        <input type="text" id="user-filter" placeholder="👤 Filter by User" oninput="filterGallery()">
        <input type="number" id="price-filter" placeholder="💰 Minimum Price ($)" oninput="filterGallery()">
    </div>
    <div class="gallery">
"""

# Loop through files in the image folder to generate gallery items
for filename in os.listdir(image_folder):
    if filename.endswith(".png"):
        image_path = os.path.join("bot", "image", filename).replace("\\", "/")

        # Find the corresponding .txt file
        txt_filename = filename.replace(".png", ".txt")
        metadata_file = os.path.join(image_folder, txt_filename)

        # Default metadata values (in case no metadata file exists)
        prompt = "No prompt available"
        style = "Unknown style"
        size = "Unknown size"
        user = "Anonymous"
        price = "Not for sale"
        tooltip = ""

        # Check if the .txt file exists and read metadata , details
        if os.path.exists(metadata_file):
            with open(metadata_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines:
                    # Extract details from metadata file lines
                    if line.startswith("Prompt:"):
                        prompt = line.replace("Prompt:", "").strip()
                    elif line.startswith("Style:"):
                        style = line.replace("Style:", "").strip()
                    elif line.startswith("Size:"):
                        size = line.replace("Size:", "").strip()
                    elif line.startswith("User:"):
                        user = line.replace("User:", "").strip()
                    elif line.startswith("Full User:"):
                        # Parse user details (if available) for tooltips
                        full_user_str = line.replace("Full User:", "").strip()
                        try:
                            full_user = json.loads(full_user_str)
                            tooltip = f"Contact User: {full_user.get('first_name', '')} {full_user.get('last_name', '')}".strip()
                            if full_user.get("username"):
                                tooltip += f" (@{full_user['username']})"
                        except json.JSONDecodeError:
                            tooltip = "Full user details unavailable"
                    elif line.startswith("Price:"):
                        price_line = line.replace("Price:", "").strip()
                        if price_line.lower() != "no":
                            price = f"${price_line}"

        # Convert price to a numeric value (used for filtering)
        numeric_price = float(price.replace("$", "")) if price != "Not for sale" else 0

        # Add the image and metadata to the HTML
        html_content += f"""
        <div class="gallery-item" 
             data-prompt="{prompt}" 
             data-style="{style}" 
             data-user="{user}" 
             data-price="{numeric_price}">
            <img src="{image_path}" alt="{filename}">
            <p><strong>Prompt:</strong> {prompt}</p>
            <p><strong>Style:</strong> {style}</p>
            <p><strong>Size:</strong> {size}</p>
            <p><strong>User:</strong> {user}</p>
            <p class="price"><strong>Price:</strong> {price}
                <span class="tooltip">{tooltip}</span>
            </p>
        </div>
        """

# End of the HTML structure
html_content += """
    </div>
    <footer>
        <p>Powered by Your Creative Bot ✨</p>
    </footer>
</body>
</html>
"""

# Write the HTML content to the output file
with open(output_file, "w", encoding="utf-8") as file:
    file.write(html_content)

# Print success message YAY I FINALLY DID IT
print(f"HTML file '{output_file}' has been generated with enhanced styling functionality!")
