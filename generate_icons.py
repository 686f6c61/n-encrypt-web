from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, output_path):
    # Create a new image with a light blue background
    image = Image.new('RGB', (size, size), '#F0F8FF')
    draw = ImageDraw.Draw(image)
    
    # Draw a blue circle in the center
    circle_size = int(size * 0.8)
    circle_pos = ((size - circle_size) // 2, (size - circle_size) // 2)
    draw.ellipse([circle_pos[0], circle_pos[1], 
                 circle_pos[0] + circle_size, circle_pos[1] + circle_size], 
                 fill='#3B82F6')
    
    # Draw a simplified lock shape in white
    lock_width = int(size * 0.4)
    lock_height = int(size * 0.5)
    lock_x = (size - lock_width) // 2
    lock_y = (size - lock_height) // 2
    
    # Lock body (rectangle)
    draw.rectangle([lock_x, lock_y + int(size * 0.15), 
                   lock_x + lock_width, lock_y + lock_height], 
                   fill='white')
    
    # Lock shackle (arc)
    shackle_width = int(lock_width * 0.8)
    shackle_height = int(size * 0.25)
    shackle_x = (size - shackle_width) // 2
    draw.arc([shackle_x, lock_y - int(size * 0.1),
             shackle_x + shackle_width, lock_y + shackle_height],
             0, 180, fill='white', width=int(size * 0.1))
    
    # Save the image
    image.save(output_path)

# Create icons directory if it doesn't exist
os.makedirs('extension', exist_ok=True)

# Generate icons in different sizes
sizes = [(16, 'icon16.png'), (48, 'icon48.png'), (128, 'icon128.png')]
for size, filename in sizes:
    create_icon(size, f'extension/{filename}')

print("Icons generated successfully!")
