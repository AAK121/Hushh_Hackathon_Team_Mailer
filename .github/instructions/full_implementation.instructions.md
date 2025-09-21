---
applyTo: '**'
---
## 1. Always Use Full Implementations
This instruction tells the agent to avoid shortcuts and provide production-ready, robust code. Simplified implementations are good for quick prototypes but fail in real-world scenarios.

What a "Full Implementation" Includes:

Error Handling: Using try...except blocks to gracefully handle potential issues like invalid input, network failures, or file-not-found errors.

Edge Case Management: Considering and handling unusual inputs, such as empty lists, zero, negative numbers, or null values.

Code Structure: Organizing code into functions or classes with clear names, docstrings, and comments.

Dependencies: Including all necessary import statements.

Efficiency: Choosing appropriate data structures and algorithms that scale well.

Example Scenario
Your Prompt: "Write a Python function to get the title of a webpage from its URL."

❌ A Simplified Implementation (What to avoid):
This version works only if everything is perfect. It will crash if the URL is bad or the connection fails.

Python

import requests
from bs4 import BeautifulSoup

def get_page_title(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup.title.string
✅ A Full Implementation (What you want):
This version is robust. It handles network errors, bad URLs, missing titles, and uses a timeout to prevent it from hanging indefinitely.

Python

import requests
from bs4 import BeautifulSoup

def get_page_title(url: str, timeout: int = 10) -> str | None:
    """
    Fetches the title of a webpage from a given URL.

    Args:
        url (str): The URL of the webpage.
        timeout (int): The number of seconds to wait for a response.

    Returns:
        str | None: The title of the page as a string, or None if an
                     error occurs or the title cannot be found.
    """
    try:
        # Set a user-agent to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        
        # Make the request with the timeout and headers
        response = requests.get(url, headers=headers, timeout=timeout)
        
        # Raise an exception for bad status codes (e.g., 404 Not Found, 500 Server Error)
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the title tag and handle the case where it might not exist
        if soup.title and soup.title.string:
            return soup.title.string.strip()
        else:
            print(f"Warning: No title tag found for URL: {url}")
            return None
            
    except requests.exceptions.Timeout:
        print(f"Error: The request to {url} timed out after {timeout} seconds.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error: A network request error occurred: {e}")
        return None
    except Exception as e:
        print(f"Error: An unexpected error occurred: {e}")
        return None

# --- Example Usage ---
# Successful case
title = get_page_title("https://www.google.com")
if title:
    print(f"Success! Title: {title}")

# Failure case (invalid URL)
title_fail = get_page_title("http://thisurldoesnotexist.xyz")
if not title_fail:
    print("Failed to retrieve title as expected.")
## 2. Remember What We Have Done Earlier
This instruction is about maintaining conversational context. The agent should understand that your requests are part of an ongoing project, not isolated tasks. Code generated in one step should seamlessly integrate with code from previous steps.

Example Scenario
Conversation Flow:

Your First Prompt:
"Create a Python class Product that holds an id, name, and price."

Agent's Response:

Python

class Product:
    def __init__(self, product_id: int, name: str, price: float):
        self.product_id = product_id
        self.name = name
        self.price = price

    def __repr__(self):
        return f"Product(id={self.product_id}, name='{self.name}', price={self.price:.2f})"
Your Second Prompt (building on the first):
"Great. Now create a ShoppingCart class that can add these products and calculate the total price."

Agent's Correct Response (maintaining context):
The agent understands that "these products" refers to the Product class it just created. Its new code is designed to work with the previous code.

Python

# The agent remembers the Product class from the previous turn.
# class Product:
#     ... (defined above) ...

class ShoppingCart:
    def __init__(self):
        self._items: list[Product] = []

    def add_product(self, product: Product):
        """Adds a Product object to the cart."""
        if not isinstance(product, Product):
            print("Error: Only Product objects can be added.")
            return
        self._items.append(product)
        print(f"Added '{product.name}' to the cart.")

    def get_total_price(self) -> float:
        """Calculates the total price of all products in the cart."""
        return sum(product.price for product in self._items)

# --- Example Usage ---
# Create some products using the previously defined class
p1 = Product(101, "Laptop", 1200.00)
p2 = Product(102, "Mouse", 25.50)

# Use the new ShoppingCart class
cart = ShoppingCart()
cart.add_product(p1)
cart.add_product(p2)

# Calculate the total
total = cart.get_total_price()
print(f"Total price: ${total:.2f}")
## 3. Think From Different Perspectives
This instructs the agent to be a flexible problem-solver. If its first solution isn't ideal (e.g., it's too slow, too complex, or doesn't work), it should proactively suggest or switch to an alternative approach.

This involves changing:

Algorithms: E.g., moving from a brute-force O(n²) solution to an optimized O(n log n) or O(n) solution.

Data Structures: E.g., using a Hash Map (Dictionary) for fast lookups instead of searching through a List.

Programming Paradigms: E.g., suggesting a recursive solution if an iterative one is clumsy, or vice-versa.

Example Scenario
Your Prompt: "Given a list of integers and a target number, find two numbers in the list that sum up to the target. Return their indices."

Agent's Response (showing different perspectives):

"Certainly. There are a few ways to approach this with different trade-offs in performance.

Perspective 1: Brute-Force Approach
This is the most straightforward method. We use nested loops to check every possible pair of numbers. It's easy to understand but becomes slow with large lists (Time Complexity: O(n 
2
 )).

Python

def find_sum_pair_brute_force(nums: list[int], target: int) -> tuple[int, int] | None:
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            if nums[i] + nums[j] == target:
                return i, j
    return None

# Example
print(f"Brute-Force: {find_sum_pair_brute_force([2, 7, 11, 15], 9)}")
Perspective 2: Optimized Approach with a Hash Map
If we think about this differently, we can do it much faster. As we iterate through the list, for each number x, we can instantly check if its complement (target - x) already exists. A hash map (dictionary in Python) is perfect for this. This reduces the time complexity to O(n) at the cost of using more memory.

Python

def find_sum_pair_optimized(nums: list[int], target: int) -> tuple[int, int] | None:
    num_map = {}  # To store number -> index
    for i, num in enumerate(nums):
        complement = target - num
        if complement in num_map:
            return num_map[complement], i
        num_map[num] = i
    return None

# Example
print(f"Optimized: {find_sum_pair_optimized([2, 7, 11, 15], 9)}")
For most use cases, the optimized approach is superior due to its significantly better performance on larger datasets.