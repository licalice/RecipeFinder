import streamlit as st
import requests
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('SPOONACULAR_API_KEY')

def fetch_recipes(ingredients, exclude_ingredients, number_of_recipes, diet=None):
    url = f"https://api.spoonacular.com/recipes/findByIngredients?ingredients={ingredients}&number={number_of_recipes}&diet={diet}&apiKey={api_key}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  
        recipes = response.json()
        
        if exclude_ingredients:
            exclude_list = [item.strip().lower() for item in exclude_ingredients.split(',')]
            filtered_recipes = []
            for recipe in recipes:
                ingredients_in_recipe = [ing['name'].lower() for ing in recipe['usedIngredients']] + \
                                        [ing['name'].lower() for ing in recipe['missedIngredients']]
                if not any(excluded in ingredients_in_recipe for excluded in exclude_list):
                    filtered_recipes.append(recipe)
            return filtered_recipes
        return recipes
    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error occurred: {http_err}")
    except Exception as err:
        st.error(f"Error occurred: {err}")
    return []

def get_recipe_instructions(recipe_id):
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/analyzedInstructions?apiKey={api_key}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        instructions = response.json()
        return instructions
    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error occurred: {http_err}")
    except Exception as err:
        st.error(f"Error occurred: {err}")
    return []

def get_recipe_nutrition(recipe_id):
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/nutritionWidget.json?apiKey={api_key}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        nutrition = response.json()
        return nutrition
    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error occurred: {http_err}")
    except Exception as err:
        st.error(f"Error occurred: {err}")
    return {}

def format_instructions(instructions):
    formatted_instructions = []
    
    if instructions and len(instructions) > 0:
        steps = instructions[0].get('steps', [])
        
        for step in steps:
            step_number = step.get('number', '')
            step_description = step.get('step', '')
            formatted_instructions.append(f"Step {step_number}: {step_description}")
    
    return formatted_instructions

def format_nutrition(nutrition):
    nutrition_info = ""
    if nutrition:
        nutrition_info += f"<p>Calories: {nutrition.get('calories', 'N/A')} kcal</p>"
        nutrition_info += f"<p>Protein: {nutrition.get('protein', 'N/A')} g</p>"
        nutrition_info += f"<p>Carbs: {nutrition.get('carbs', 'N/A')} g</p>"
        nutrition_info += f"<p>Fat: {nutrition.get('fat', 'N/A')} g</p>"
    
    return nutrition_info

# Page
st.set_page_config(page_title="Recipe Finder", page_icon="🍲", layout="wide")
st.title("Recipe Finder by Ingredients")
st.sidebar.header("Search Ingredients and Preferences")

ingredients_input = st.sidebar.text_input("Enter ingredients you have (comma-separated):")
diet_input = st.sidebar.selectbox("Dietary preference (optional):", [None, "gluten free", "vegetarian", "vegan", "dairy free"])
exclude_ingredients_input = st.sidebar.text_input("Enter ingredients to exclude (optional, comma-separated):")
number_of_recipes = st.sidebar.number_input("Number of recipes to fetch:", min_value=1, max_value=10, value=5)
st.sidebar.markdown("""
**Note:**
There is a daily quota limit for recipe searches using the Spoonacular API. 
If the quota is exceeded, you may not be able to fetch recipes until the next day. 
Please try again later if this happens.
""")

if st.sidebar.button("Find Recipes"):
    if ingredients_input:
        recipes = fetch_recipes(ingredients_input, exclude_ingredients_input, number_of_recipes, diet_input)
        
        if recipes:
            st.success(f"Found {len(recipes)} recipes based on your search!")

            # Display each recipe
            for recipe in recipes:
                st.subheader(recipe['title'])
                st.image(recipe['image'], width=300)

                # Display the ingredients the user already has
                st.markdown("**Ingredients you have**")
                for ingredient in recipe['usedIngredients']:
                    st.markdown(f"- {ingredient['name']}")

                # Display the missing ingredients
                if recipe['missedIngredients']:
                    st.markdown("**Missing Ingredients**")
                    for missed_ingredient in recipe['missedIngredients']:
                        st.markdown(f"- {missed_ingredient['name']}")
                
                # Display the nutrition facts
                st.markdown("**Nutrition Facts**")
                nutrition = get_recipe_nutrition(recipe['id'])
                if nutrition:
                    formatted_nutrition = format_nutrition(nutrition)
                    st.markdown(f"<div style='font-size:14px;'>{formatted_nutrition}</div>", unsafe_allow_html=True)
                
                # Display the cooking instructions
                instructions = get_recipe_instructions(recipe['id'])
                if instructions:
                    st.markdown("**Instructions**")
                    formatted_instructions = format_instructions(instructions)
                    for step in formatted_instructions:
                        st.markdown(f"- {step}")           
                st.write("\n")
        else:
            st.warning("No recipes found based on your search.")
    else:
        st.error("Please enter some ingredients to search for recipes.")
