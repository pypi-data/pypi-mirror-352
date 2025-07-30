p9 =  """
# Install required libraries 
!pip install wikipedia-api pydantic  
from pydantic import BaseModel  
from typing import List, Optional 
import wikipediaapi  
class InstitutionDetails(BaseModel): 
founder: Optional[str] 
founded: Optional[str] 
branches: Optional[List[str]] 
number_of_employees: Optional[int]  
summary: Optional[str] 
def fetch_institution_details(institution_name: str) -> InstitutionDetails: 
# Define a user-agent as per Wikipedia's policy  
user_agent = "MyJupyterNotebook/1.0 (contact: myemail@example.com)"  
wiki_wiki = wikipediaapi.Wikipedia(user_agent=user_agent, language='en')  
page = wiki_wiki.page(institution_name) 
if not page.exists(): 
raise ValueError(f"The page for '{institution_name}' does not exist on Wikipedia.")  
# Initialize variables 
founder = None 
founded = None  
branches = [] 
number_of_employees = None 
# Extract summary  
summary = page.summary[:500] # Limiting summary to 500 characters 
# Extract information from the infobox 
infobox = page.text.split('\n')  
for line in infobox: 
if 'Founder' in line:  
founder = line.split(':')[-1].strip()  
elif 'Founded' in line: 
founded = line.split(':')[-1].strip() 
elif 'Branches' in line: 
branches = [branch.strip() for branch in line.split(':')[-1].split(',')] 
elif 'Number of employees' in line:  
try: number_of_employees = int(line.split(':')[-1].strip().replace(',', '')) 
except ValueError: 
number_of_employees = None 
return InstitutionDetails( founder=founder, 
founded=founded, 
branches=branches if branches else None, number_of_employees=number_of_employees, 
summary=summary )  
# Import necessary libraries from IPython.display 
import display import ipywidgets as widgets  
# Function to display institution details  
def display_institution_details(details: InstitutionDetails):  
print(f"Founder: {details.founder or 'N/A'}") 
print(f"Founded: {details.founded or 'N/A'}") 
print(f"Branches: {', '.join(details.branches) if details.branches else 'N/A'}") 
print(f"Number of Employees: {details.number_of_employees or 'N/A'}") 
print(f"Summary: {details.summary or 'N/A'}") 
# Function to handle button click 
def on_button_click(b):  
institution_name = text_box.value 
try: 
details = fetch_institution_details(institution_name)  
display_institution_details(details) 
except ValueError as e:  
print(e) 
# Create input box and button  
text_box = widgets.Text( value='', placeholder='Enter the institution name', description='Institution:', 
disabled=False ) 
button = widgets.Button( description='Fetch Details', disabled=False, button_style='', tooltip='Click 
to fetch institution details', icon='search' ) 
# Set up button click event 
button.on_click(on_button_click)  
# Display input box and button  
display(text_box, button) """