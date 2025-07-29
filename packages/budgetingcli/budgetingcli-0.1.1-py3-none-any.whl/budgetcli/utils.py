import datetime
import calendar
import click
from rich.console import Console
from rich.text import Text

def get_days_elapsed():
    """Get days elapsed in the current month"""
    today = datetime.datetime.now()
    first_day_of_month = today.replace(day=1)
    return (today - first_day_of_month).days + 1

def get_days_in_month():
    """Use calendar to get the number of days in the current month"""
    today = datetime.datetime.now()
    return calendar.monthrange(today.year, today.month)[1]

def project_spending(total_spending, days_elapsed, days_in_month):
    """Project spending based on the spending entry and goal"""
    if days_elapsed == 0:
        return total_spending # Avoid division by zero
    daily_avg = total_spending / days_elapsed
    projected_amount = daily_avg * days_in_month
    return projected_amount


def check_reset_expenses(user_json):
    """Reset all expenses for all categories"""
    # Check if we are at the end of the month, if so then reset expenses
    today = datetime.datetime.now()
    last_login = user_json.get('last_login', today.strftime('%Y-%m-%d'))
    click.echo(f"Last login date: {last_login}")
    if last_login:
        last_login_date = datetime.datetime.strptime(last_login, '%Y-%m-%d')
        if today.month != last_login_date.month or today.year != last_login_date.year:
            click.echo("Resetting expenses for the new month...")
            user_json = rewards_system(user_json)
            user_json['spending'] = {}
            user_json['notes'] = []
    else: 
        click.echo("No last login date found. Setting up for the first time.")
        user_json['last_login'] = today.strftime('%Y-%m-%d')
    
    # Update last login date
    user_json['last_login'] = today.strftime('%Y-%m-%d')
    click.echo(f"Last login date updated to {user_json['last_login']}.")
    return_streak(user_json)
    return user_json


def return_streak(user_json):
    """return the current streak and max streak"""
    console = Console()
    streak_text = Text()
    streak_text.append("🔥 Current Streak: ", style="bold green")
    streak_text.append(f"{user_json['current_streak']}", style="bold white")
    streak_text.append(" | 🏆 Max Streak: ", style="bold yellow")
    streak_text.append(f"{user_json['max_streak']}", style="bold white")
    console.print(streak_text)



def rewards_system(user_json):
    """Rewards system to track max_streak, current_streak, and some simple phrases"""
    user_json.setdefault('max_streak', 0)
    user_json.setdefault('current_streak', 0)
    user_json.setdefault('streak_phrases', [
        f"Good job {user_json['username']} :D",
        f"WOOOOOOO {user_json['username']}! LET'S GOOOOOOO!",
        f"Woowwwwww you are doing so well {user_json['username']}!",
        f"Keep it up {user_json['username']}!",
        f"Keep going {user_json['username']}!",
    ])
    user_json.setdefault('streak_reset_phrases', [
        f"Don't worry {user_json['username']}, you got this!",
        f"Keep trying {user_json['username']}, you can do it!",
        f"Don't give up {user_json['username']}!",
        f"If you did it once you can do it again {user_json['username']}!",
    ])
    # Phrases set, now check to set the streak
    # Check if all spending categories are less than the allocated goal budget
    goals = user_json.get('goals', {})
    spending = user_json.get('spending', {})
    all_within_budget = True
    for category, goal in goals.items():
        if category in spending:
            total_spent = sum(entry['amount'] for entry in spending[category])
            if total_spent > goal:
                all_within_budget = False
                break
    if all_within_budget:
        user_json['current_streak'] += 1
        if user_json['current_streak'] > user_json['max_streak']:
            user_json['max_streak'] = user_json['current_streak']
        display_reward(user_json)
    else:
        user_json['current_streak'] = 0
        display_reward_reset(user_json)    
    return user_json


def display_reward(user_json):
    console = Console()
    reward_text = Text()
    reward_text.append("🎉 ")
    reward_text.append(user_json['streak_phrases'][user_json['current_streak'] % len(user_json['streak_phrases'])], style="bold magenta")
    reward_text.append("🎉 ")

    console.print(reward_text)
    
def display_reward_reset(user_json):
    console = Console()
    reward_text = Text()
    reward_text.append("😔")
    reward_text.append(user_json['streak_phrases'][user_json['current_streak'] % len(user_json['streak_phrases'])], style="bold red")
    console.print(reward_text)