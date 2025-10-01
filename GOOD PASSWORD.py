import string
import sys
import hashlib
import requests
from colorama import Fore, Style, init
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

init(autoreset=True)

def check_hibp (password):
    """check password against HaveIBeenPwned API"""
    sha1_pw = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix, suffix = sha1_pw[:5], sha1_pw[5:]

    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    response = requests.get(url)
    if response.status_code !=200:
        raise RuntimeError(f"Error fetching HIBP API; {response.status_code}")
    
    hashes = (line.split(':') for line in response.text.splitlines())
    for h, count in hashes:
        if h == suffix:
            return int(count)
    return 0

def save_pdf_report(password, length, char_types, score, recommendation):
    file_name = "password_report.pdf"
    c = canvas.Canvas(file_name, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "🔐 Password Security Report")

    # Details
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 100, f"Password tested: {password}")
    c.drawString(50, height - 130, f"Length: {length} characters")
    c.drawString(50, height - 160, f"Character types: {char_types}/4")
    c.drawString(50, height - 190, f"Final Score: {score}/7")

    # Recommendation
    c.setFont("Helvetica-Oblique", 12)
    c.drawString(50, height - 230, f"Recommendation: {recommendation}")

    c.save()
    print("\n📄 Report saved as password_report.pdf")

print(Fore.CYAN + Style.BRIGHT + "\n Password Strength Checker\n"+ "-"*40)
password = input (Fore.YELLOW + "enter the password to test!:")

pwned_count = check_hibp (password)
if pwned_count > 0:
    print (Fore.RED +f" this password was found {pwned_count} times in data breaches!")
    print(Fore.RED + "DO NOT use this password. Score 0/7")
    save_pdf_report(password, len(password), 0, 0, "Password is unsafe. Choose a unique one.")
    sys.exit()

with open ("10k-most-common.txt", "r") as f:
    common = f.read().splitlines()

if password in common:
    print(Fore.RED + "password was found in common list. Score 0/7")
    save_pdf_report(password, len(password), 0, 0, "Password is too common. Avoid dictionary words.")
    sys.exit()

upper_case = any(c.isupper() for c in password)
lower_case = any(c.islower() for c in password)
digits = any(c.isdigit() for c in password)
special = any(c in string.punctuation for c in password)

characters = [upper_case, lower_case, special, digits]
length = len(password)
score = 0


if length > 8:
    score += 1
if length > 12:
    score += 1
if length > 17:
    score += 1
if length > 20:
    score += 1
print(f"Password length is {length}, adding {score} points!")

char_types = sum(characters)
if char_types > 1:
    score += char_types -1
print(f"Password has {char_types} character types,score so far: {score}/7 ")

print(Fore.CYAN + "\n📊 Password Security Report")
print(Fore.CYAN + "-"*40)
print(Fore.WHITE + f"Password length: {length} characters")
print(Fore.WHITE + f"Character types: {char_types} of 4 (upper, lower, digit, special)")

if score < 4:
    recommendation = "Use at least 12+ characters with multiple character types."
    print(Fore.RED + f"\n🔴 Weak password! Final Score: {score}/7")
    print(Fore.RED + "Recommendation: " + recommendation)

elif score == 4:
    recommendation = "Add more variety or length for better security."
    print(Fore.YELLOW + f"\n🟡 Okay password. Final Score: {score}/7")
    print(Fore.YELLOW + "Recommendation: " + recommendation)

elif 5 <= score <= 6:
    recommendation = "Already strong, but longer is always safer."
    print(Fore.GREEN + f"\n🟢 Pretty good password! Final Score: {score}/7")
    print(Fore.GREEN + "Recommendation: " + recommendation)

elif score == 7:
    recommendation = "Keep using unique passwords per account."
    print(Fore.GREEN + Style.BRIGHT + f"\n✅ Excellent! Strong password. Final Score: {score}/7")
    print(Fore.GREEN + Style.BRIGHT + "Recommendation: " + recommendation + "\n")

# ✅ Now the variable exists and is spelled correctly
save_pdf_report(password, length, char_types, score, recommendation)

