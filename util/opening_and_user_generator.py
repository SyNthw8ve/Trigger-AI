import sys
from pathlib import Path

if __name__ == "__main__":
    sys.path.append(str(Path('.').absolute().parent))
    sys.path.append(str(Path('..').absolute().parent))

from util.readers.reader import DataReaderOpenings, DataReaderUsers
import os
import random

base = r"examples\openings_users\users"
base_ = os.path.join(Path('..').absolute(), base)

users = [
    DataReaderUsers.populate(os.path.join(base_, file))
    for file in os.listdir(base_)
]

base = r"examples\openings_users\openings"
base_ = os.path.join(Path('..').absolute(), base)

openings = [
    DataReaderOpenings.populate(os.path.join(base_, file))
    for file in os.listdir(base_)
]

set_ss = set()
set_hs = set()

for sublist in openings:
    for opening in sublist:
        for hs in opening.hardSkills:
            set_hs.add(hs.name)

        for ss in opening.softSkills:
            set_ss.add(ss.name)

for sublist in users:
    for user in sublist:
        for hs in user.hardSkills:
            set_hs.add(hs.name)

        for ss in user.softSkills:
            set_ss.add(ss.name)

# print(set_ss)
# print(set_hs)

# https://zety.com/blog/hard-skills-soft-skills
set_ss.add("Decision Making")
set_ss.add("Listening")
set_ss.add("Time Management")
set_ss.add("Active Learning")
set_ss.add("Perceptiveness")
set_ss.add("Detail-Oriented")
set_ss.add("Persuasion")
set_ss.add("Compassion")
set_ss.add("Physically Fit")
set_ss.add("Self Motivated")
set_ss.add("Dependability")

# Me
set_ss.add("Eco-friendly")

# https://pdf4pro.com/fullscreen/hard-skills-list-excel-centre-keith-to-seminars-56a89b.html

new_hss = [
    "Budgeting", "Business Planning", "Business Re-engineering Change Management", "Consolidation", "Cost Control Decision Making", "Developing Policies", "Diversification Employee Evaluation", "Financing", "Government Relations Hiring", "International Management", "Investor Relations IPO", "Joint Ventures", "Labour Relations Merger & Acquisitions", "Multi-sites Management", "Negotiation Profit & Loss", "Organizational Development", "Project Management Staff Development", "Strategic Partnership", "Strategic Planning Supervision",
    "Bidding", "Call Centre Operations", "Continuous Improvement Contract Management", "Environmental Protection", "Facility Management Inventory Control", "Manpower Planning", "Operations Research Outsourcing", "Policies & Procedures", "Project Co-ordination Project Management",
    "Equipment Design", "Equipment Maintenance & Repair", "Equipment Management", "ISO 9XXX / 1XXXXX", "TQM Order Processing", "Plant Design & Layout", "Process Engineering Production Planning", "Quality Assurance", "Safety Engineering ",
    "Distribution", "Transportation", "JIT Purchasing & Procurement Shipping", "Traffic Management Warehousing ",
    "Design & Specification", "Diagnostics", "Feasibility Studies Field Studies", "Lab Management", "Lab Design New Equipment Design", "Patent Application", "Product Development Product Testing", "Prototype Development", "R&D Management Simulation Dev.", "Statistical Analysis", "Technical Writing",
    "Account Management", "B2B", "Contract Negotiation Customer Relations", "Customer Service", "Direct Sales Distributor Relations", "E-Commerce", "Forecasting Incentive Programs", "International Business Development International Expansion", "New Account Development", "Proposal Writing Product Demonstrations", "Telemarketing", "Trade Shows", "Sales Administration", "Sales Analysis", "Sales Kits Sales Management", "Salespersons Recruitment", "Show Room Management Sales Support", "Sales Training",
    "Advertising", "Brand Management", "Channel Marketing Competitive Analysis", "Copywriting", "Corporate Identity Image Development", "Logo Development", "Market Research & Analysis Marketing Communication", "Marketing Plan", "Marketing promotions Media Buying/Evaluation Media Relations", "Merchandising New Product Development", "Online Marketing", "Packaging Pricing", "Product Launch",
    "Contract Negotiation", "Equipment Purchasing", "Forms and Methods Leases", "Mailroom Management", "Office Management Policies & Procedures", "Reception", "Records Management Security", "Space Planning", "Word Processing ",
    "Contract Preparation", "Copyrights & Trademarks", "Corporate Law Company Secretary", "Employment Ordinance", "IPO Intellectual Property", "International Agreements", "Licensing Mergers & Acquisitions", "Patents", "Shareholder proxies Stock Administration",
    "Accounting Management", "Accounts Payable", "Venture Capital Relations Accounts Receivable", "Acquisitions & Mergers", "Actuarial/Rating Analysis Auditing", "Banking Relations", "Budget Control Capital Budgeting", "Capital Investment", "Cash Management Cost Accounting", "Cost Control", "Credit/Collections Debt Negotiations", "Equity/Debt Management", "Feasibility StudiesFinancial Analysis", "Financial Reporting", "Financing Forecasting", "Foreign Exchange", "General Ledger Insurance", "Internal Controls", "Investor Relations IPO", "Lending", "Lines of Credit Management Reporting", "Payroll", "Fund Management Profit Planning", "Risk Management", "Stockholder Relations Tax", "Treasury", "Investor Presentations",
    "Arbitration/Mediation", "Career Counseling", "Career Coaching Classified Advertisements", "Company Orientation", "Workforce Forecast/Planning Compensation & Benefits", "Corporate Culture", "Training Administration", "Employee Discipline", "Employee Selection", "Executive Recruiting Grievance Resolution", "Human Resources Management Industrial Relations", "Job Analysis", "Labour Negotiations Outplacement", "Performance Appraisal", "Salary Administration Succession Planning", "Team Building", "Training ",
    "Algorithm Development", "Application Database Administration Applications Development", "Business Systems Planning", "Web Site Editor Capacity Planning", "CRM", "CAD EDI", "Enterprise Asset Management", "EAP Enterprise Resource Planning ERP", "Hardware Management Information Management", "Integration Software", "Intranet Development Languages - JAVA", "C+++", "etc", "Portal Design/Development Software Customization", "Software Development", "System Analysis System Design", "System Development", "Technical Evangelism Technical Support", "Technical Writing", "Telecommunications Tracking System", "UNIX", "Usability Engineering User Education", "User Documentation", "User Interface Vendor Sourcing", "Voice & Data Communications Web Development/Design", "Web Site Content Writer", "Word Processing",
    "Character Development", "Creative Writing", "Drawing Musical Composition", "Story Line Development", "Visual Composition",
    "Colour Theory", "Dreamweaver", "Flash Freehand", "Illustrator", "Photoshop Picasa", "Corel Draw", "Typography Print Design & Layout", "Photography",
    "B2B Communication", "Community Relations", "Speech Writing Corporate Image", "Corporate Philanthropy", "Corporate Publications Corporate Relations", "Employee Communication", "Event Planning Fund Raising", "Government Relations", "Investor Collateral Media Presentations", "Press Release", "Risk Mgt Communicat",
]

for new_hs in new_hss:
    set_hs.add(new_hs)

hs_law = ["Contract Preparation", "Copyrights & Trademarks", "Corporate Law Company Secretary", "Employment Ordinance", "IPO Intellectual Property",
          "International Agreements", "Licensing Mergers & Acquisitions", "Patents", "Shareholder proxies Stock Administration"]
hs_accounting = ["Math", "Accounting Management", "Accounts Payable", "Venture Capital Relations Accounts Receivable", "Acquisitions & Mergers", "Actuarial/Rating Analysis Auditing", "Banking Relations", "Budget Control Capital Budgeting", "Capital Investment", "Cash Management Cost Accounting", "Cost Control", "Credit/Collections Debt Negotiations", "Equity/Debt Management",
                 "Feasibility StudiesFinancial Analysis", "Financial Reporting", "Financing Forecasting", "Foreign Exchange", "General Ledger Insurance", "Internal Controls", "Investor Relations IPO", "Lending", "Lines of Credit Management Reporting", "Payroll", "Fund Management Profit Planning", "Risk Management", "Stockholder Relations Tax", "Treasury", "Investor Presentations"]


hs_map = {
    "Archaeology": ["Archaeology"],
    "Security": ["Military Training"],
    "Military": ["Military Training", "Mechanical Engineering"],
    "Environment": ["Math", "Mechanical Engineering"],
    "Law": hs_law,
    "Accounting": hs_accounting,
    "Human Interaction": ["Design", "Computer Science", "Psychology"],
    "Networks": ["UNIX", "HTTP", "Internet", "API", "Scraping", "Web Server", "JavaScript", "Typescript", "React", "Angular", "Web"],
    "Software": ["Processes", "Software development", "Computer Engineering", "Web Application"],
    "Signal Transmission": ["Physics", "Math"],
    "UI": ["JavaScript", "Typescript", "React", "Angular", "Web", "HTML", "CSS"],
    "Mobile App": ["Android", "Java", "Computer Engineering"],
    "Bank": ["Math", "Money"],
    "Art": ["Art"],
    "Market Study": ["Sociology", "Finances"],
    "Gastronomy": ["Gastronomy"],
    "Construction": ["Construction"],
    "Psychology": ["Psychology", "Sociology"],
    "Medicine": ["Medicine"],
    "Agriculture": ["Agriculture"],
    "Management": ["Budgeting", "Business Planning", "Business Re-engineering Change Management", "Consolidation", "Cost Control Decision Making", "Developing Policies", "Diversification Employee Evaluation", "Financing", "Government Relations Hiring", "International Management", "Investor Relations IPO", "Joint Ventures", "Labour Relations Merger & Acquisitions", "Multi-sites Management", "Negotiation Profit & Loss", "Organizational Development", "Project Management Staff Development", "Strategic Partnership", "Strategic Planning Supervision"],
    "Operations": ["Bidding", "Call Centre Operations", "Continuous Improvement Contract Management", "Environmental Protection", "Facility Management Inventory Control", "Manpower Planning", "Operations Research Outsourcing", "Policies & Procedures", "Project Co-ordination Project Management"],
    "Production": ["Equipment Design", "Equipment Maintenance & Repair", "Equipment Management", "ISO 9XXX / 1XXXXX", "TQM Order Processing", "Plant Design & Layout", "Process Engineering Production Planning", "Quality Assurance", "Safety Engineering "],
    "Logistics": ["Distribution", "Transportation", "JIT Purchasing & Procurement Shipping", "Traffic Management Warehousing "],
    "Research & Development": ["Design & Specification", "Diagnostics", "Feasibility Studies Field Studies", "Lab Management", "Lab Design New Equipment Design", "Patent Application", "Product Development Product Testing", "Prototype Development", "R&D Management Simulation Dev.", "Statistical Analysis", "Technical Writing"],
    "Sales": ["Account Management", "B2B", "Contract Negotiation Customer Relations", "Customer Service", "Direct Sales Distributor Relations", "E-Commerce", "Forecasting Incentive Programs", "International Business Development International Expansion", "New Account Development", "Proposal Writing Product Demonstrations", "Telemarketing", "Trade Shows", "Sales Administration", "Sales Analysis", "Sales Kits Sales Management", "Salespersons Recruitment", "Show Room Management Sales Support", "Sales Training"],
    "Marketing": ["Advertising", "Brand Management", "Channel Marketing Competitive Analysis", "Copywriting", "Corporate Identity Image Development", "Logo Development", "Market Research & Analysis Marketing Communication", "Marketing Plan", "Marketing promotions Media Buying/Evaluation Media Relations", "Merchandising New Product Development", "Online Marketing", "Packaging Pricing", "Product Launch"],
    "Administration": ["Contract Negotiation", "Equipment Purchasing", "Forms and Methods Leases", "Mailroom Management", "Office Management Policies & Procedures", "Reception", "Records Management Security", "Space Planning", "Word Processing "],
    "Legal": hs_law,
    "Finance & Accounting": hs_accounting,
    "Human Resources": ["Arbitration/Mediation", "Career Counseling", "Career Coaching Classified Advertisements", "Company Orientation", "Workforce Forecast/Planning Compensation & Benefits", "Corporate Culture", "Training Administration", "Employee Discipline", "Employee Selection", "Executive Recruiting Grievance Resolution", "Human Resources Management Industrial Relations", "Job Analysis", "Labour Negotiations Outplacement", "Performance Appraisal", "Salary Administration Succession Planning", "Team Building", "Training "],
    "Information Technology": ["Algorithm Development", "Application Database Administration Applications Development", "Business Systems Planning", "Web Site Editor Capacity Planning", "CRM", "CAD EDI", "Enterprise Asset Management", "EAP Enterprise Resource Planning ERP", "Hardware Management Information Management", "Integration Software", "Intranet Development Languages – JAVA", "C+++", "etc", "Portal Design/Development Software Customization", "Software Development", "System Analysis System Design", "System Development", "Technical Evangelism Technical Support", "Technical Writing", "Telecommunications Tracking System", "UNIX", "Usability Engineering User Education", "User Documentation", "User Interface Vendor Sourcing", "Voice & Data Communications Web Development/Design", "Web Site Content Writer", "Word Processing"],
    "Creative": ["Character Development", "Creative Writing", "Drawing Musical Composition", "Story Line Development", "Visual Composition"],
    "Design": ["Colour Theory", "Dreamweaver", "Flash Freehand", "Illustrator", "Photoshop Picasa", "Corel Draw", "Typography Print Design & Layout", "Photography"],
    "Public Relation": ["B2B Communication", "Community Relations", "Speech Writing Corporate Image", "Corporate Philanthropy", "Corporate Publications Corporate Relations", "Employee Communication", "Event Planning Fund Raising", "Government Relations", "Investor Collateral Media Presentations", "Press Release", "Risk Mgt Communicat"],
}

sector = ["Public", "Private"]

it = [("Creativity", 70), ("Teamwork", 40),
      ("Autonomy", 40), ("Active Learning", 80), ("Leadership", 40)]

law = [("Critical Thinking", 70), ("Detail-Oriented", 40),
       ("Communication", 70), ("Creativity", 40)]

accounting = [("Critical Thinking", 60),
              ("Detail-Oriented", 50), ("Hard-working", 10), ("Teamwork", 30)]

art = [("Creativity", 90), ("Time Management", 40),
       ("Detail-Oriented", 40), ("Individuality", 40), ("Self-Motivated", 60)]

marketing = [("Detail-Oriented", 70),
             ("Creativity", 50), ("Perceptiveness", 70)]

ss_map = {
    "Archaeology": [("Eco-friendly", 50), ("Hard-working", 50), ("Detail-Oriented", 50)],
    "Security": [("Physically Fit", 95), ("Hard-working", 50), ("Perceptiveness", 50), ("Dependability", 70)],
    "Military": [("Leadership", 40), ("Eco-friendly", 10), ("Physically Fit", 50), ("Self Motivated", 70), ("Hard-working", 50)],
    "Environment": [("Eco-friendly", 80), ("Positive Attitude", 40), ("Individuality", 40)],
    "Management": [("Leadership", 50), ("Decision Making", 60), ("Time Management", 30), ("Compassion", 40), ("Communication", 50)],
    "Operations": [("Perceptiveness", 60), ("Time Management", 50), ("Critical Thinking", 30)],
    "Production": [("Decision Making", 50), ("Time Management", 20), ("Detail-Oriented", 60), ("Hard-working", 40), ("Autonomy", 60)],
    "Logistics": [("Detail-Oriented", 80), ("Decision Making", 30)],
    "Research & Development": [("Active Learning", 50), ("Self Motivated", 40), ("Creativity", 70), ("Autonomy", 60)],
    "Sales": [("Communication", 90), ("Compassion", 40), ("Listening", 40), ("Persuasion", 70), ("Physically Fit", 10), ("Positive Attitude", 30)],
    "Marketing": marketing,
    "Administration": [("Decision Making", 70), ("Leadership", 70), ("Time Management", 60), ("Detail-Oriented", 20), ("Compassion", 50), ("Communication", 50)],
    "Legal": law,
    "Law": law,
    "Finance & Accounting": accounting,
    "Accounting": accounting,
    "Human Interaction": [("Communication", 90), ("Compassion", 40), ("Listening", 40), ("Teamwork", 50)],
    "Human Resources": [("Teamwork", 70), ("Communication", 40), ("Detail-Oriented", 40), ("Compassion", 40)],
    "Information Technology": it,
    "Networks": it,
    "Software": it,
    "Signal Transmission": it,
    "UI": it,
    "Mobile App": it,
    "Creative": art,
    "Bank": accounting,
    "Art": art,
    "Market Study": marketing,
    "Gastronomy":  [("Detail-Oriented", 90), ("Perceptiveness", 50)],
    "Design": [("Creativity", 70), ("Time Management", 40), ("Detail-Oriented", 50), ("Teamwork", 40)],
    "Public Relation": [("Communication", 90), ("Compassion", 40), ("Listening", 40), ("Positive Attitude", 70), ("Physically Fit", 10)],
    "Construction": [("Physically Fit", 70), ("Self Motivated", 70), ("Hard-working", 70)],
    "Psychology": [("Listening", 90), ("Compassion", 70), ("Communication", 80)],
    "Medicine": [("Detail-Oriented", 90), ("Time Management", 50), ("Hard-working", 70), ("Compassion", 50)],
    "Agriculture": [("Detail-Oriented", 50), ("Self Motivated", 20), ("Hard-working", 70), ("Perceptiveness", 30)],
}

base = r"files.php_f=names.txt&downloadcode=yes.txt"
base_ = os.path.join(Path('..').absolute(), base)

with open(base_, 'r') as f:
    names = [line.strip() for line in f.readlines()]

base = r"users.txt"
base_ = os.path.join(Path('..').absolute(), base)

with open(base_, 'w') as f:
    for i in range(100):
        name = random.choice(names)
        f.write("User: " + name + "\n")

        n_hs = int(random.uniform(1, 3.5))
        hardskills = random.sample(set_hs, n_hs)

        f.write("Hardskills: " + ','.join(hardskills) + "\n")

        n_ss = int(random.uniform(3, 5.5))
        softskills = random.sample(set_ss, n_ss)

        f.write("Softskills: " + ','.join(softskills) + "\n")
        f.write("\n")

base = r"openings.txt"
base_ = os.path.join(Path('..').absolute(), base)

with open(base_, 'w') as f:
    for i in range(2000):
        sector = random.choice(["Public", "Private"])
        f.write("Sector: " + sector + "\n")

        area = random.choice(list(hs_map.keys()))
        f.write("Area: " + area + "\n")

        possible_hss = hs_map[area]

        n_hs = int(random.uniform(1, len(possible_hss)))
        hardskills = random.sample(possible_hss, n_hs)

        f.write("Hardskills: " + ','.join(hardskills) + "\n")

        possible_sss = ss_map[area]

        softskills = set()

        for (possible_ss, chance) in possible_sss:
            roll = random.randint(0, 100)
            # print(roll, chance, possible_ss)
            if roll <= chance:
                softskills.add(possible_ss)

        while len(softskills) < 3:
            another = random.sample(set_ss, 1)[0]
            softskills.add(another)

        # MUTATION BOY
        roll = random.randint(0, 100)
        if roll <= 10:
            mutated = random.sample(set_ss, 1)[0]
            softskills.add(mutated)

        f.write("Softskills: " + ','.join(list(softskills)) + "\n")
        f.write("\n")
