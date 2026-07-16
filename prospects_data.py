"""
prospects_data.py
The 60-company research list, ported from the old local-Excel generator
(build_outreach_tracker.mjs). Each row: [Category, Company, Area, Website,
Specialty, Pain Hypothesis].

This is raw research data, not send-ready leads -- none of these have a
Contact Name or Business Email yet. See import_prospects.py.
"""

PROSPECTS = [
    # HVAC
    ["HVAC", "Frio Air Systems", "Houston", "https://www.frioairsystems.com/", "Residential & commercial HVAC", "Calls and estimates can arrive after hours; protect response speed and quote opportunities."],
    ["HVAC", "Climate by Design", "Houston", "https://climatebydesignllc.com/", "Residential & light commercial HVAC", "Preventive-maintenance and repair inquiries need fast qualification and scheduling."],
    ["HVAC", "Golden Rule Air Conditioning & Heating", "Houston", "https://goldenrulecomfort.com/", "Full-service HVAC", "Service requests, maintenance, and installations create repeatable front-office demand."],
    ["HVAC", "VeriChill", "Houston", "https://www.verichill.com/", "Residential HVAC", "Inbound AC requests should be captured and booked during peak demand."],
    ["HVAC", "Adams Air Conditioning", "Houston", "https://www.adams-air.com/houston/", "24/7 HVAC service", "Emergency availability makes after-hours answering and rapid dispatch especially valuable."],
    ["HVAC", "75 Degree AC", "Houston", "https://www.75degreeac.com/", "HVAC repair and installation", "High-volume homeowner inquiries require quick triage, estimate follow-up, and booking."],
    ["HVAC", "A/C Nation", "Houston", "https://www.acnationhvac.com/", "HVAC construction and service", "A mix of construction and service work can create scheduling and follow-up bottlenecks."],
    ["HVAC", "Air Champion", "Houston", "https://www.airchampion.com/", "Air conditioning and heating", "Seasonal calls and maintenance reminders benefit from dependable coverage."],
    ["HVAC", "Barker's Heating & Cooling", "Katy / Houston area", "https://www.barkers.com/", "Heating and cooling service", "Customer comfort emergencies need a consistent answer and fast next step."],
    ["HVAC", "First Rate Heating & Air", "Houston", "https://www.firstrateheatingandair.com/", "Heating and air conditioning", "Lead response and estimate follow-up can slip while technicians are in the field."],
    ["HVAC", "Westair Air Conditioning & Heating", "Houston", "https://www.westairac.com/", "Air conditioning and heating", "Service and replacement requests need routing without adding office workload."],
    ["HVAC", "Allgood Electric, Plumbing, Heating & Air", "Houston", "https://www.callallgood.com/houston/", "Home services", "Multi-trade calls require accurate qualification and routing every time."],
    ["HVAC", "Air Tech of Houston", "Houston", "https://www.airtechofhouston.com/", "Residential HVAC", "Missed repair calls and delayed callbacks are direct revenue risks."],
    ["HVAC", "Air Houston Mechanical", "Houston", "https://www.airhoustonmechanical.com/", "Commercial HVAC", "Commercial service coordination often depends on prompt, documented intake."],
    ["HVAC", "Quality Air Houston", "Houston area", "https://qualityairhouston.com/", "HVAC service and replacement", "Replacement and repair requests require timely nurturing and appointment booking."],
    # Electrical
    ["Electrical", "Sabre Electric", "Houston", "https://sabreelectrichouston.com/", "Residential and commercial electrical", "Residential emergencies and commercial project inquiries need reliable intake and routing."],
    ["Electrical", "Aaron-Carter Electric", "Houston", "https://www.aaroncarterelectric.com/", "Electrical contractor", "Estimate requests and safety-related calls need a quick, confident response."],
    ["Electrical", "Southern Electrical Services", "Houston", "https://www.southernelectrical.com/", "Commercial and industrial electrical", "Project qualification and preventative-maintenance follow-up can overwhelm a small office."],
    ["Electrical", "Mister Sparky of Houston", "Houston", "https://www.mistersparky.com/houston/", "Residential electrical service", "Urgent home electrical calls need 24/7 capture and clear escalation."],
    ["Electrical", "Mr. Electric of Houston", "Houston", "https://mrelectric.com/houston", "Residential and commercial electrical", "Inbound jobs need qualification, booking, and consistent CRM handoff."],
    ["Electrical", "Right Touch Electrical", "Houston", "https://righttouchelectrical.com/", "Residential electrical", "Homeowner questions and estimate requests compete with fieldwork for attention."],
    ["Electrical", "Absolute Power Electrical Contractors", "Houston", "https://absolutepowerllc.com/", "Electrical contractor", "Project and service prospects need consistent first response and follow-up."],
    ["Electrical", "Citywide Electrical", "Houston", "https://citywideelectrical.com/", "Commercial electrical", "Dispatch and job-status calls create repetitive, time-sensitive office work."],
    ["Electrical", "ACE Electrical Services", "Houston", "https://aceelectricalservices.com/", "Electrical services", "Scheduling and inbound service requests can be handled without more office headcount."],
    ["Electrical", "Jayk Electric", "Houston", "https://jaykelectric.com/", "Electrical contractor", "Quote requests and callbacks need a dependable, trackable workflow."],
    ["Electrical", "Texas Electrical Services", "Houston", "https://texaselectricalservices.com/", "Electrical contractor", "Field teams need leads captured and qualified while they are on-site."],
    ["Electrical", "Houston Electric", "Houston", "https://houstonelectric.com/", "Electrical service", "Safety-conscious callers benefit from immediate answers and correct routing."],
    ["Electrical", "Pro Max Electrical", "Houston / Cypress", "https://promaxelectrical.com/", "Local electrical service", "Service inquiries need fast booking before prospective customers call another provider."],
    ["Electrical", "Warrior Electric", "Houston", "https://warriorelectrichouston.com/", "Electrical contractor", "Hiring, field operations, and customer requests can strain front-office capacity."],
    ["Electrical", "Superior Power", "Houston", "https://superiorpower.com/", "Commercial electrical", "Commercial jobs benefit from documented intake, dispatch coordination, and follow-up."],
    # Dental
    ["Dental", "URBN Dental", "Houston", "https://urbndental.com/", "Multi-location dental practice", "New-patient calls, eligibility questions, and appointment requests need rapid response."],
    ["Dental", "MINT dentistry", "Houston", "https://mintdentistry.com/", "Dental group", "A multi-location practice needs consistent intake and booking across sites."],
    ["Dental", "Lovett Dental", "Houston", "https://lovettdental.com/", "Multi-location dental group", "New-patient conversion and reminders are critical across a distributed practice."],
    ["Dental", "Houston Dental", "Houston", "https://houstondental.com/", "General and cosmetic dentistry", "Web leads and incoming calls need swift qualification and calendar handoff."],
    ["Dental", "Memorial Park Dental Spa", "Houston", "https://memorialparkdentalspa.com/", "Cosmetic and general dentistry", "High-intent cosmetic inquiries need a polished, immediate response."],
    ["Dental", "Tanglewood Dental", "Houston", "https://tanglewooddental.com/", "General dentistry", "Patient scheduling and routine questions consume valuable front-desk time."],
    ["Dental", "River Oaks Dental", "Houston", "https://riveroaksdental.com/", "Cosmetic and restorative dentistry", "Consult requests and patient follow-up benefit from a consistent premium experience."],
    ["Dental", "Bayou City Smiles", "Houston", "https://bayoucitysmiles.com/", "General and cosmetic dentistry", "Appointment inquiries and missed calls can affect new-patient growth."],
    ["Dental", "Montrose Dental", "Houston", "https://montrosedental.com/", "General dentistry", "Front-desk teams need room to focus on in-office patients without losing new inquiries."],
    ["Dental", "Midtown Dentistry", "Houston", "https://midtowndentistry.com/", "General dentistry", "Patients expect simple, quick booking and confirmation, including outside office hours."],
    ["Dental", "West U Dental", "Houston", "https://westudental.com/", "General and cosmetic dentistry", "New patient, treatment, and recall conversations create repetitive admin work."],
    ["Dental", "Smile Texas", "Houston", "https://smiletexas.com/", "Dental practice", "Competitive patient acquisition makes immediate response and follow-up valuable."],
    ["Dental", "Spring Branch Dental Care", "Houston", "https://springbranchdentalcare.com/", "Family dentistry", "The front desk has to balance live patient care with new appointment inquiries."],
    ["Dental", "Heights Modern Dentistry", "Houston", "https://heightsmoderndentistry.com/", "General dentistry", "Online appointment interest needs prompt and consistent conversion to booked visits."],
    ["Dental", "Whole Health Dentistry", "Houston", "https://wholehealthdentistry.com/", "Holistic dentistry", "A differentiated patient experience starts with a thoughtful and reliable first interaction."],
    # Personal injury / accident law
    ["Accident Law", "Molina Law Firm", "Houston", "https://molinalawfirm.com/", "Personal injury and accident law", "Accident leads are time-sensitive; fast intake and compassionate follow-up can protect conversion."],
    ["Accident Law", "Jim Adler & Associates", "Houston", "https://www.jimadler.com/", "Personal injury law", "High call volumes need reliable 24/7 intake, qualification, and escalation."],
    ["Accident Law", "Arnold & Itkin", "Houston", "https://www.arnolditkin.com/", "Catastrophic injury law", "A premium client experience requires responsive, documented intake without burdening legal staff."],
    ["Accident Law", "Sutliff & Stout", "Houston", "https://sutliffstout.com/", "Personal injury law", "New injury inquiries need immediate acknowledgement and a clear next step."],
    ["Accident Law", "Stewart J. Guss, Injury Accident Lawyers", "Houston", "https://attorneyguss.com/", "Personal injury law", "Lead response and referral follow-up need to remain dependable around the clock."],
    ["Accident Law", "The Krist Law Firm", "Houston", "https://www.houstoninjurylawyer.com/", "Personal injury and maritime law", "Complex case inquiries need structured intake and prompt human escalation."],
    ["Accident Law", "Terry Bryant Accident & Injury Law", "Houston", "https://www.terrybryant.com/", "Accident and injury law", "Phone and web leads should be captured and qualified before urgency fades."],
    ["Accident Law", "Baumgartner Law Firm", "Houston", "https://baumgartnerlawyers.com/", "Personal injury law", "A busy practice needs after-hours lead coverage without adding intake overhead."],
    ["Accident Law", "Law Offices of Hilda Sibrian", "Houston", "https://www.hildasibrian.com/", "Personal injury law", "Bilingual, responsive intake and follow-up can help ensure each inquiry gets a next step."],
    ["Accident Law", "J. Gonzalez Law Firm", "Houston", "https://jgonzalezlawfirm.com/", "Personal injury law", "High-intent accident inquiries need quick capture, qualification, and routing."],
    ["Accident Law", "Patrick Daniel Law", "Houston", "https://patrickdaniellaw.com/", "Personal injury law", "Response speed and consistent intake are essential for accident-case opportunities."],
    ["Accident Law", "The Amaro Law Firm", "Houston", "https://amarolawfirm.com/", "Personal injury law", "Client inquiries need a compassionate first response and a reliable escalation path."],
    ["Accident Law", "Simmons and Fletcher", "Houston", "https://www.simmonsandfletcher.com/", "Personal injury law", "Lead intake, case-status questions, and follow-up can pull attention from legal work."],
    ["Accident Law", "The Hadi Law Firm", "Houston", "https://www.hadilawfirm.com/", "Personal injury law", "Accident leads need rapid response and clear, reviewable handoff to the team."],
    ["Accident Law", "Joe Stephens Law", "Houston", "https://www.joestephenslaw.com/", "Personal injury law", "Potential clients need a quick, respectful response before they keep searching."],
]
