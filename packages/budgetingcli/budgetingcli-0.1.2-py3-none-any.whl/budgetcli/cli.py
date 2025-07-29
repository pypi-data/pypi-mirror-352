### leverage Click to create a CLI interface for budget management
import click
from .file_io import get_user, create_user, update_user
import time
from rich.console import Console
from rich.table import Table
import datetime
from .utils import get_days_elapsed, get_days_in_month, project_spending, check_reset_expenses
from .ai_chatting import generate_advice
import re


### Click group
@click.group()
def cli():
    """A simple CLI application for user management."""
    pass


### Create Login command
@click.command()
@click.option('--username', prompt='Username',help="Enter username!")
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help="Enter Password!")
def login(username, password):
    """authenticate user"""
    user = get_user(username, password)

    if user:
        user = check_reset_expenses(user)
        # update user with last login
        update_user(user['username'], user)
        dashboard(user)
        return user
    else:
        ### Create user
        click.echo("user not found. using creds to create user")
        if user is None:
            user = create_user(username, password)
        if user:
            click.echo("User created successfully. Proceed to setup-profile.")
            click.echo(f"Welcome {user['username']}!")
            user = setup_profile(user)
            # Update user
            update_user(user['username'], user)
            dashboard(user)
            return user
        else:
            click.echo("Failed to create user.")
            return None    


def dashboard(user_json=None):
    ### Display dashboard with possible options
    option = None
    while option != 11:
        forecast(user_json) # Show forecast at the start of the dashboard
        view_progress(user_json) # Show progress at the start of the dashboard
        click.echo("\n --- Budgeting Dashboard ---")
        click.echo("1. View Profile")
        click.echo("2. Update Profile")
        click.echo("3. Add Goals")
        click.echo("4. Modify Goals")
        click.echo("5. Log Spending")
        click.echo("6. Update Spending Entry")
        click.echo("7. Delete Spending Entry")
        click.echo("8. Talk to Qwen AI")
        click.echo("9. General Notes")
        click.echo("10. View Notes")
        click.echo("11. Exit")
        option = click.prompt("Please select an option", type=int)
        # Wait for 5 seconds
        time.sleep(2)
        ### Handle user options
        if option == 1:
            click.echo("Viewing Profile...")
            view_profile(user_json)
        elif option == 2:
            click.echo("Updating Profile...")
            user = update_profile(user_json)
            update_user(user['username'], user)
            
        elif option == 3:
            click.echo("Adding Goals...")
            user = add_goals(user_json)
            update_user(user['username'], user)
            # Here you would implement goal addition logic
        elif option == 4:
            user = modify_goals(user_json)
            update_user(user['username'], user)
        elif option == 5:
            click.echo("Logging Spending...")
            user = log_spending(user_json)
            update_user(user['username'], user)
        elif option == 6:
            click.echo("Updating Spending Entry...")
            user = update_spending(user_json)
            update_user(user['username'], user)
        elif option == 7:
            click.echo("Deleting Spending Entry...")
            user = delete_spending(user_json)
            update_user(user['username'], user)   
        elif option == 8:
            click.echo("Calling Qwen AI for you!") 
            talk_to_Qwen(user_json)
        elif option == 9:
            click.echo("Opening notes section")
            user = general_notes(user_json)
            update_user(user['username'], user)
        elif option == 10:
            view_notes(user_json)
        elif option == 11:
            click.echo("Exiting Dashboard. Goodbye!")
        else:
            click.echo("Invalid option. Please try again.")
        time.sleep(2)
        
        

def view_profile(user_json):
    """View user profile"""
    console = Console()
    
    # Create a table for profile information
    profile_table = Table(title="User Profile", show_header=True, header_style="bold magenta")
    profile_table.add_column("Field", style="cyan", no_wrap=True)
    profile_table.add_column("Value", style="green")
    
    # Add profile data
    profile_table.add_row("Username", user_json['username'])
    profile_table.add_row("Yearly Salary", f"${user_json.get('salary', 'Not set'):,.2f}" if user_json.get('salary') else "Not set")
    
    console.print(profile_table)
    
    # Create a separate table for goals if they exist
    # goals come from user_json['goals'] if it exists
    goals = user_json.get('goals', {})
    if not isinstance(goals, dict):
        click.echo("Goals data is not in the expected format.")
        return
    if not goals:
        click.echo("No goals set for this user.")
        return
    
    if goals:
        goals_table = Table(title="Goals", show_header=True, header_style="bold blue")
        goals_table.add_column("Goal Name", style="cyan")
        goals_table.add_column("Target Amount", style="yellow")
        
        for goal_name, goal_amount in goals.items():
            goals_table.add_row(goal_name, f"${goal_amount:,.2f}")
        
        console.print(goals_table)
    else:
        console.print("[italic red]No goals set[/italic red]")



def update_profile(user_json):
    """Update user profile"""
    click.echo("\n --- Update Profile ---")
    new_salary = click.prompt("Please enter your new yearly salary", type=float)
    user_json['salary'] = new_salary
    click.echo("Profile updated successfully!")
    return user_json



def setup_profile(user_json):
    ### Set up profile with salary
    username = user_json['username']
    click.echo(f"Hello {username}, let's set up the profile")
    salary = click.prompt("Please enter your yearly salary", type=float)
    user_json['salary'] = salary
    click.echo("Setup Complete!")
    return user_json



def add_goals(user_json):
    """add goals for budgeting"""
    goal_name = click.prompt("Enter goal name")
    goal_amount = click.prompt("Enter goal amount", type=float)
    click.echo("Type DONE with done adding goals or exit")
    while True:
        click.echo(f"Goal Name: {goal_name}, Goal Amount: {goal_amount}")
        # Here you would implement logic to save the goal
        # nested dict for json structure
        user_json.setdefault('goals', {})
        user_json['goals'][goal_name] = goal_amount
        
        goal_name = click.prompt("Enter next goal name or type DONE to finish")
        if goal_name.lower() == "done" or goal_name.lower() == "exit":
            break
        goal_amount = click.prompt("Enter goal amount", type=float)
    
    return user_json
   
def modify_goals(user_json):
    """ability to delete or update goals"""
    click.echo("\n --- Modify Goals ---")
    goals = user_json.get('goals', {})
    if not isinstance(goals, dict):
        click.echo("Goals data is not in the expected format.")
        return user_json
    if not goals:
        click.echo("No goals set. Please add goals first.")
        return user_json
    click.echo("Available goals:")
    for i, (goal_name, goal_amount) in enumerate(goals.items(), start=1):
        click.echo(f"{i}. {goal_name} - ${goal_amount:,.2f}")
    choice = click.prompt("Select an option: 1. Update Goal 2. Delete Goal", type=int)
    if choice == 1:
        goal_index = click.prompt("Enter the number of the goal to update", type=int) - 1
        if goal_index < 0 or goal_index >= len(goals):
            click.echo("Invalid goal selection.")
            return user_json
        goal_name = list(goals.keys())[goal_index]
        new_goal_name = click.prompt(f"Enter new name for goal '{goal_name}'", default=goal_name)
        new_goal_amount = click.prompt(f"Enter new amount for goal '{new_goal_name}'", type=float, default=goals[goal_name])
        # Update the goal
        del user_json['goals'][goal_name]
        user_json['goals'][new_goal_name] = new_goal_amount
        click.echo("Goal updated successfully!")
       
    elif choice == 2:
        goal_index = click.prompt("Enter the number of the goal to delete", type=int) - 1
        if goal_index < 0 or goal_index >= len(goals):
            click.echo("Invalid goal selection.")
            return user_json
        goal_name = list(goals.keys())[goal_index]
        confirm = click.confirm(f"Are you sure you want to delete the goal '{goal_name}'?", default=True)
        if confirm:
            del user_json['goals'][goal_name]
            click.echo("Goal deleted successfully!")
        else:
            click.echo("Goal deletion cancelled.")
    else:
        click.echo("Invalid option selected. Please try again.")   
    return user_json
    
   
        
def log_spending(user_json):
    """Log spending for the user for the given username and category"""
    click.echo(f"Logging spending for {datetime.datetime.now().strftime('%Y-%m-%d')}")
    
    # List all goals the user can choose from
    categories = list(user_json.get('goals', {}).keys())
    if not categories:
        click.echo("No goals set. Please add goals first.")
        return user_json
    click.echo("Available spending categories:")
    for i, category in enumerate(categories, start=1):
        click.echo(f"{i}. {category}")
    
    category = click.prompt("Enter spending category [Enter the number]", type=int)
    if category < 1 or category > len(categories):
        click.echo("Invalid category selection.")
        return user_json
    category = categories[category - 1]  # Adjust for zero-based index
    amount = click.prompt("Enter amount spent", type=float)
    date = click.prompt("Enter date (YYYY-MM-DD)", default=datetime.datetime.now().strftime('%Y-%m-%d'))
    location = click.prompt("Enter location of spending", default="Unknown")
    click.echo(f"Spending logged: {category} - ${amount:.2f} on {date} at {location}")
    # Create a spending entry
    user_json.setdefault('spending', {})
    # Add the spending entry and if one exists for the given day then add to it
    # format: {spending: {category: {amount: amount, location: location, date: date}}}
    # Check if the category exists, if not create it
    user_json['spending'][category] = user_json['spending'].get(category, [])
    user_json['spending'][category].append({
        'amount': amount,
        'location': location,
        'date': date
    })
    click.echo("Spending logged successfully!")
    click.echo(user_json['spending'])
    return user_json

def update_spending(user_json):
    """Update a specific spending entry"""
    categories = list(user_json.get('spending', {}).keys())
    if not categories:
        click.echo("No spending categories found. Please log spending first.")
        return user_json
    click.echo("Available spending categories:")
    for i, category in enumerate(categories, start=1):
        click.echo(f"{i}. {category}")
    category_index = click.prompt("Select a category by number", type=int)-1
    if category_index < 0 or category_index > len(categories):
        click.echo("Invalid category selection.")
        return user_json
    category = categories[category_index]
    entries = user_json['spending'].get(category, [])
    if not entries:
        click.echo(f"No spending entries found for category '{category}'.")
        return user_json
    click.echo(f"Spending entries for category '{category}':")
    for i, entry in enumerate(entries, start=1):
        click.echo(f"{i}. Amount: ${entry['amount']:.2f}, Date: {entry['date']}, Location: {entry.get('location', 'Unknown')}")
    entry_index = click.prompt("Select an entry to update by number", type=int)-1
    if entry_index < 0 or entry_index >= len(entries):
        click.echo("Invalid entry selection.")
        return user_json
    entry = entries[entry_index]
    # Update entry
    new_amount = click.prompt("Enter new amount", type=float, default=entry['amount'])
    new_date = click.prompt("Enter new date (YYYY-MM-DD)", default=entry['date'])
    new_location = click.prompt("Enter new location", default=entry.get('location', 'Unknown'))
    # Update the entry in the spending data
    user_json['spending'][category][entry_index] = {
        'amount': new_amount,
        'date': new_date,
        'location': new_location
    }
    click.echo("Spending entry updated successfully!")
    click.echo(user_json['spending'])
    return user_json

def delete_spending(user_json):    
    """Delete spending entry"""
    categories = list(user_json.get('spending', {}).keys())
    if not categories:
        click.echo("No spending categories found. Please log spending first.")
        return user_json
    click.echo("Available spending categories:")
    for i, category in enumerate(categories, start=1):
        click.echo(f"{i}. {category}")
    category_index = click.prompt("Select a category by number", type=int)-1
    if category_index < 0 or category_index > len(categories):
        click.echo("Invalid category selection.")
        return user_json
    category = categories[category_index]
    entries = user_json['spending'].get(category, [])
    if not entries:
        click.echo(f"No spending entries found for category '{category}'.")
        return user_json
    click.echo(f"Spending entries for category '{category}':")
    for i, entry in enumerate(entries, start=1):
        click.echo(f"{i}. Amount: ${entry['amount']:.2f}, Date: {entry['date']}, Location: {entry.get('location', 'Unknown')}")
    entry_index = click.prompt("Select an entry to update by number", type=int)-1
    if entry_index < 0 or entry_index >= len(entries):
        click.echo("Invalid entry selection.")
        return user_json
    entry = entries[entry_index]
    # confirm deletion
    confirm = click.confirm(f"Are you sure you want to delete the entry: Amount: ${entry['amount']:.2f}, Date: {entry['date']}, Location: {entry.get('location', 'Unknown')}?", default=True)
    if confirm:
        # Delete the entry from the spending data
        del user_json['spending'][category][entry_index]
        click.echo("Spending entry deleted successfully!")
        # If the category is empty, remove it
        if not user_json['spending'][category]:
            del user_json['spending'][category]
        click.echo(user_json['spending'])
    else:
        click.echo("Deletion cancelled.")
    return user_json
    
    
    
def view_progress(user_json):
    """Using Rich create progress bars for all user goals and spendings that are logged"""
    console = Console()
    # Create progress bar for all goals
    goals = user_json.get('goals', {})
    spending = user_json.get('spending', {})
    if not isinstance(goals, dict):
        click.echo("Goals data is not in the expected format.")
        return
    if not goals:
        click.echo("No goals set for this user.")
        return
    # Should have the Goal name, the target amount, and current amount spent
    # If less than target then have a green bar, if more than target then have a red bar, if halfway then have a yellow bar
    # Static progress bar using tqdm
    
    progress_table = Table(title="Goal Progress", show_header=True, header_style="bold green")
    progress_table.add_column("Goal Name", style="cyan")
    progress_table.add_column("Target Amount", style="yellow")
    progress_table.add_column("Amount Spent", style="red")
    progress_table.add_column("Remaining", style="green")
    progress_table.add_column("Progress", style="blue")
    
    for goal_name, target_amount in goals.items():
        # Calculate total spent for this goal category
        spent_amount = 0
        if goal_name in spending:
            for entry in spending[goal_name]:
                spent_amount += entry['amount']
        
        remaining_amount = target_amount - spent_amount
        progress_percentage = min((spent_amount / target_amount) * 100, 100) if target_amount > 0 else 0
        
        # Determine progress bar color based on spending
        if spent_amount > target_amount:
            progress_color = "red"
            status = "OVER BUDGET"
        elif progress_percentage >= 50:
            progress_color = "yellow"
            status = f"{progress_percentage:.1f}%"
        else:
            progress_color = "green"
            status = f"{progress_percentage:.1f}%"
        
        # Create visual progress bar
        bar_length = 20
        filled_length = int(bar_length * min(progress_percentage / 100, 1))
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        
        progress_display = f"[{progress_color}]{bar}[/{progress_color}] {status}"
        
        progress_table.add_row(
            goal_name,
            f"${target_amount:,.2f}",
            f"${spent_amount:,.2f}",
            f"${remaining_amount:,.2f}" if remaining_amount >= 0 else f"[red]-${abs(remaining_amount):,.2f}[/red]",
            progress_display
        )
    
    console.print(progress_table)

    
    time.sleep(2)
    # Create a table for spending
    spending_table = Table(title="Expenditure Tracker", show_header=True, header_style="bold blue")
    spending_table.add_column("Category", style="cyan")
    spending_table.add_column("Amount", style="yellow")
    spending_table.add_column("Date", style="green")
    spending_table.add_column("Location", style="blue")
    spending_data = user_json.get('spending', {})
    if not isinstance(spending_data, dict):
        click.echo("Spending data is not in the expected format.")
        return
    if not spending_data:
        click.echo("No spending logged for this user.")
        return
    for category, entries in spending_data.items():
        for entry in entries:
            spending_table.add_row(category, f"${entry['amount']:.2f}", entry['date'], entry.get('location', 'Unknown'))
    console.print(spending_table)


def forecast(user_json):
    """Forecast user spending based on goals/spending/"""
    # Helper methods to create: get_days_elapsed, get_days_in_month, project_spending(spending_entry, goal)
    console = Console()
    # Create a table for forecast
    forecast_table = Table(title="Spending Forecast", show_header=True, header_style="bold magenta")
    forecast_table.add_column("Category", style="cyan")
    forecast_table.add_column("Projected Amount", style="yellow")
    forecast_table.add_column("Days Elapsed", style="green")
    forecast_table.add_column("Days Remaining", style="blue")
    forecast_table.add_column("Forecasted Date", style="red")
    spending_data = user_json.get('spending', {})
    if not isinstance(spending_data, dict):
        click.echo("Spending data is not in the expected format.")
        return
    if not spending_data:
        click.echo("No spending logged for this user.")
        return
    days_elapsed = get_days_elapsed()
    days_in_month = get_days_in_month()
    for category, entries in spending_data.items():
        total = sum(entry['amount'] for entry in entries)
        projected_amount = project_spending(total, days_elapsed, days_in_month)    
        forecasted_date = datetime.datetime.now() + datetime.timedelta(days=(days_in_month - days_elapsed))
        forecast_table.add_row(
            category,
            f"${projected_amount:,.2f}",
            str(days_elapsed),
            str(days_in_month - days_elapsed),
            forecasted_date.strftime('%Y-%m-%d')
        )
    # If less than target have green checkmark, if more than target have red cross
    # if greater than 50% of target then have yellow warning
    # Add a column for this status
    forecast_table.add_column("Status", style="white")
    
    # Add status data to each row
    goals = user_json.get('goals', {})
    for category, entries in spending_data.items():
        total = sum(entry['amount'] for entry in entries)
        projected_amount = project_spending(total, days_elapsed, days_in_month)
        forecasted_date = datetime.datetime.now() + datetime.timedelta(days=(days_in_month - days_elapsed))
        
        # Determine status based on goal comparison
        status = "[white]No Goal Set[/white]"
        if category in goals:
            target_amount = goals[category]
            if projected_amount > target_amount:
                status = "[red]❌ Over Budget[/red]"
            elif projected_amount > target_amount * 0.5:
                status = "[yellow]⚠️ Warning[/yellow]"
            else:
                status = "[green]✅ On Track[/green]"
        
        forecast_table.add_row(
            category,
            f"${projected_amount:,.2f}",
            str(days_elapsed),
            str(days_in_month - days_elapsed),
            forecasted_date.strftime('%Y-%m-%d'),
            status
        )
    
    forecast_table.add_column("Leftover Budget", style="magenta")
    # Calculate leftover budget for each category
    for category, entries in spending_data.items():
        total = sum(entry['amount'] for entry in entries)
        projected_amount = project_spending(total, days_elapsed, days_in_month)
        leftover_budget = 0
        if category in goals:
            target_amount = goals[category]
            leftover_budget = target_amount - projected_amount
            
        forecast_table.add_row(
            category,
            f"${projected_amount:,.2f}",
            str(days_elapsed),
            str(days_in_month - days_elapsed),
            forecasted_date.strftime('%Y-%m-%d'),
            status,
            f"[green]${leftover_budget:,.2f}[/green]" if leftover_budget >= 0 else f"[red]-${abs(leftover_budget):,.2f}[/red]"
            
        )
    console.print(forecast_table)
 

def talk_to_Qwen(user_json):
    """Talk to Qwen ai"""
    click.echo("Starting AI chat. Type 'exit' or '/bye' to leave.\n")
    while True:
        user_input = input("\n\nYou: ")
        if re.search(r'\b(bye|exit|quit|done)\b', user_input.lower()):
            break
        generate_advice(user_json, user_input)
        
def general_notes(user_json):
    """General Notes the user can add"""
    # Add notes to user_json
    user_json.setdefault('notes', [])
    while True:
        note = click.prompt("Enter notes (type 'exit' when done)", type = str)
        if re.search(r'\b(exit|done|quit)\b', note.lower()):
            click.echo("Exiting notes section.")
            break
        user_json['notes'].append({
            "text": note,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    return user_json
    
def view_notes(user_json):
    """General Notes the user can view"""
    click.echo("\n --- View Notes ---")
    notes = user_json.get('notes', [])
    if not notes:
        click.echo("No notes found.")
        return
    console = Console()
    notes_table = Table(title="User Notes", show_header=True, header_style="bold blue")
    notes_table.add_column("Note", style="cyan")
    for note in notes:
        notes_table.add_row(note)
    console.print(notes_table)
    
cli.add_command(login)