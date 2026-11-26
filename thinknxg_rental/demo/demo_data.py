"""thinkNXG Rental - demo dataset (AED, UAE / GCC formwork, scaffolding and shoring hire).

Load:    bench --site <site> execute thinknxg_rental.demo.demo_data.load
Reload:  bench --site <site> execute thinknxg_rental.demo.demo_data.load --kwargs '{"company": "My AED Company"}'
Remove:  bench --site <site> execute thinknxg_rental.demo.demo_data.clear

What it creates (all names carry a "DM-" / "Demo" marker so they are easy to find and to clear):
  masters      company in AED (an existing AED company is reused), 3 yards, item groups, 22 rental items with Rental Item
               Profiles and opening stock, 4 Job Types, 8 customers, 10 projects and rental sites, 2 rate cards, 2 suppliers
  hire         Hire Orders (draft, open, contracted), Rental Contracts, Reservations, Hire Delivery Orders, partial and full
               Off-Hire Notes, Return Inspections with repairable and damaged material, billing schedules and Sales Invoices
  job type     Hire Order Contracts with exploded materials, Rental Contracts, Job Completion Reports (within contract,
               in excess, dismantled)
  cross hire   Cross Hire Order -> Purchase Order -> receipt -> delivery to a customer site

Dates are relative to today, so the data always looks current. Safe to re-run: every record is looked up first.
Each section runs on its own: a failure is logged and printed, and the rest continues.
"""
import traceback

import frappe
from frappe.utils import add_days, cint, flt, nowdate

PREFIX = "DM-"
CURRENCY = "AED"
LOG = []


# --------------------------------------------------------------------------- helpers
def say(msg):
	LOG.append(msg)
	print(msg)


def day(offset):
	return add_days(nowdate(), offset)


def section(title):
	def wrap(fn):
		def run(*a, **k):
			say(f"\n== {title}")
			frappe.db.savepoint("demo_section")
			try:
				out = fn(*a, **k)
				frappe.db.commit()
				return out
			except Exception:
				frappe.db.rollback(save_point="demo_section")
				say(f"   !! {title} failed:\n{traceback.format_exc(limit=4)}")
				frappe.log_error(title=f"thinkNXG Rental demo: {title}", message=traceback.format_exc())
				return None

		return run

	return wrap


def leaf(doctype, **filters):
	return frappe.db.get_value(doctype, {"is_group": 0, **filters}, "name")


def make(doc, submit=False):
	doc = frappe.get_doc(doc) if isinstance(doc, dict) else doc
	doc.flags.ignore_permissions = True
	doc.insert()
	if submit:
		doc.submit()
	return doc


def find(doctype, **filters):
	return frappe.db.get_value(doctype, filters, "name")


# --------------------------------------------------------------------------- data
YARDS = [  # warehouse name, location label
	("Dubai Yard - Jebel Ali", "Dubai"),
	("Abu Dhabi Yard - Mussafah", "Abu Dhabi"),
	("Sharjah Yard - Industrial Area 4", "Sharjah"),
]

ITEM_GROUPS = ["Formwork", "Scaffolding", "Shoring and Props", "Rental Accessories"]

# code, name, group, category, daily, weekly, monthly, replacement, repair, weight kg, dimensions, stock {yard index: qty}
ITEMS = [
	("FW-PLY-244", "Plywood Shuttering Panel 2440 x 1220 mm", "Formwork", "Formwork", 1.5, 8, 22, 180, 25, 28, "2440x1220x18 mm", {0: 900, 1: 400, 2: 400}),
	("FW-AL-6024", "Aluminium Wall Formwork Panel 600 x 2400", "Formwork", "Formwork", 4, 22, 65, 620, 80, 21, "600x2400 mm", {0: 700, 1: 300}),
	("FW-AL-3024", "Aluminium Wall Formwork Panel 300 x 2400", "Formwork", "Formwork", 3, 16, 48, 460, 60, 14, "300x2400 mm", {0: 500, 1: 200}),
	("FW-SLAB-TBL", "Slab Formwork Table 2.0 x 1.0 m", "Formwork", "Formwork", 9, 50, 150, 1450, 180, 62, "2000x1000 mm", {0: 120, 2: 80}),
	("FW-COL-CLP", "Adjustable Column Clamp 400-800 mm", "Formwork", "Formwork", 2.5, 14, 40, 340, 45, 18, "800 mm", {0: 260, 1: 100}),
	("FW-TIE-15", "Tie Rod 15 mm x 1.0 m", "Formwork", "Accessories", 0.4, 2, 6, 24, 4, 1.4, "15 mm x 1000 mm", {0: 6000, 1: 2500, 2: 1500}),
	("FW-WING-NUT", "Wing Nut and Plate 15 mm", "Formwork", "Accessories", 0.25, 1.4, 4, 12, 2, 0.5, "15 mm", {0: 6000, 1: 2500, 2: 1500}),
	("SC-CUP-V25", "Cuplock Vertical 2.5 m", "Scaffolding", "Scaffolding", 0.9, 5, 15, 95, 12, 9.5, "2500 mm", {0: 1800, 1: 900, 2: 700}),
	("SC-CUP-L18", "Cuplock Ledger 1.8 m", "Scaffolding", "Scaffolding", 0.6, 3.4, 10, 62, 8, 6.2, "1800 mm", {0: 3000, 1: 1400, 2: 1000}),
	("SC-TUBE-6M", "Steel Scaffold Tube 48.3 mm x 6 m", "Scaffolding", "Scaffolding", 1.4, 8, 24, 160, 20, 21.7, "48.3 mm x 6 m", {0: 2400, 1: 1000, 2: 800}),
	("SC-CPL-FIX", "Fixed Coupler 48.3 mm", "Scaffolding", "Accessories", 0.3, 1.6, 5, 14, 2, 1.0, "48.3 mm", {0: 9000, 1: 4000, 2: 3000}),
	("SC-CPL-SWV", "Swivel Coupler 48.3 mm", "Scaffolding", "Accessories", 0.35, 2, 6, 16, 2, 1.1, "48.3 mm", {0: 6000, 1: 3000, 2: 2000}),
	("SC-PLANK-39", "Steel Scaffold Plank 3.9 m", "Scaffolding", "Scaffolding", 1.1, 6, 18, 120, 15, 17.5, "3900x225 mm", {0: 1600, 1: 700, 2: 500}),
	("SC-BASE-JACK", "Adjustable Base Jack 600 mm", "Scaffolding", "Scaffolding", 0.5, 2.8, 8, 38, 6, 3.6, "600 mm", {0: 2200, 1: 900, 2: 700}),
	("SC-HFRAME-17", "H-Frame 1.7 x 1.2 m", "Scaffolding", "Scaffolding", 1.2, 6.5, 19, 130, 18, 14, "1700x1200 mm", {0: 800, 1: 350, 2: 250}),
	("SC-XBRACE", "Cross Brace 1.8 m", "Scaffolding", "Accessories", 0.35, 2, 6, 22, 3, 2.9, "1800 mm", {0: 1600, 1: 700, 2: 500}),
	("SH-PROP-35", "Adjustable Steel Prop 2.0 - 3.5 m", "Shoring and Props", "Shoring / Props", 1.0, 5.5, 16, 110, 14, 14.5, "2.0-3.5 m", {0: 2500, 1: 1200, 2: 800}),
	("SH-PROP-48", "Adjustable Steel Prop 2.9 - 4.8 m", "Shoring and Props", "Shoring / Props", 1.6, 9, 26, 190, 24, 22, "2.9-4.8 m", {0: 1200, 1: 600}),
	("SH-UHEAD", "U-Head Jack 38 mm", "Shoring and Props", "Accessories", 0.45, 2.5, 7, 34, 5, 3.2, "38 mm", {0: 2200, 1: 900, 2: 700}),
	("SH-TOWER-LEG", "Heavy Duty Shoring Tower Leg 1.5 m", "Shoring and Props", "Shoring / Props", 3.2, 18, 52, 380, 50, 28, "1500 mm", {0: 360, 1: 160}),
	("AC-TOEBOARD", "Toe Board 3.0 m", "Rental Accessories", "Accessories", 0.3, 1.6, 5, 28, 4, 5.4, "3000x150 mm", {0: 1500, 1: 600, 2: 400}),
	("AC-STAIR", "Aluminium Stair Unit 2.0 m", "Rental Accessories", "Accessories", 6, 34, 100, 760, 90, 34, "2000 mm", {0: 90, 1: 40, 2: 30}),
]

# job type code, name, description, [(item, qty per job)]
JOB_TYPES = [
	("JT-WALL-AL", "Aluminium Wall Formwork - per m2 of wall", "Aluminium wall formwork set, erected and struck by the customer.",
		[("FW-AL-6024", 2), ("FW-AL-3024", 1), ("FW-TIE-15", 8), ("FW-WING-NUT", 8)]),
	("JT-SLAB-TBL", "Slab Formwork Table Set - 100 m2 floor", "Table formwork with props for a 100 m2 slab pour.",
		[("FW-SLAB-TBL", 50), ("SH-PROP-35", 150), ("SH-UHEAD", 150)]),
	("JT-CUP-BAY", "Cuplock Scaffold Bay - 3 levels", "One cuplock bay, three working levels, with planks and toe boards.",
		[("SC-CUP-V25", 8), ("SC-CUP-L18", 18), ("SC-PLANK-39", 6), ("SC-BASE-JACK", 4), ("AC-TOEBOARD", 4)]),
	("JT-SHORE-TWR", "Heavy Duty Shoring Tower", "Shoring tower for transfer slabs and long-span beams.",
		[("SH-TOWER-LEG", 12), ("SH-UHEAD", 4), ("SC-XBRACE", 12)]),
]

# name, tax id, contact, phone, email, emirate
CUSTOMERS = [
	("Al Noor Contracting LLC", "100312345600003", "Faisal Rahman", "+971 4 555 0101", "projects@alnoor-contracting.example", "Dubai"),
	("Gulf Horizon Construction LLC", "100298765400003", "Meera Joseph", "+971 2 555 0102", "site@gulfhorizon.example", "Abu Dhabi"),
	("Desert Rose Builders LLC", "100455512300003", "Omar Haddad", "+971 6 555 0103", "ops@desertrose.example", "Sharjah"),
	("Emirates Skyline Developers", "100377788800003", "Priya Nair", "+971 4 555 0104", "procurement@skylinedev.example", "Dubai"),
	("Falcon Infra Projects LLC", "100211122200003", "Khalid Al Mansoori", "+971 2 555 0105", "contracts@falconinfra.example", "Abu Dhabi"),
	("Marina Bay Engineering LLC", "100588899900003", "Sanjay Menon", "+971 4 555 0106", "info@marinabayeng.example", "Dubai"),
	("Pearl Coast Contracting", "100644433300003", "Layla Hassan", "+971 7 555 0107", "site@pearlcoast.example", "Ras Al Khaimah"),
	("Oasis Civil and MEP Works", "100733322200003", "Thomas Verghese", "+971 3 555 0108", "ops@oasiscivil.example", "Al Ain"),
]

# site key, customer index, site name, project name, location, contact, phone
SITES = [
	("S1", 0, "Al Noor - Business Bay Tower B", "Business Bay Residential Tower B", "Business Bay, Dubai", "Imran Qureshi", "+971 50 555 1101"),
	("S2", 0, "Al Noor - Dubai South Warehouses", "Dubai South Logistics Warehouses", "Dubai South, Dubai", "Ravi Kumar", "+971 50 555 1102"),
	("S3", 1, "Gulf Horizon - Yas Island Villas", "Yas Island 48 Villa Development", "Yas Island, Abu Dhabi", "Hamdan Al Ketbi", "+971 50 555 1103"),
	("S4", 2, "Desert Rose - Al Zahia Mixed Use", "Al Zahia Mixed Use Podium", "Al Zahia, Sharjah", "Mustafa Ali", "+971 50 555 1104"),
	("S5", 3, "Skyline - Dubai Creek Harbour Plot 7", "Creek Harbour Plot 7 Tower", "Dubai Creek Harbour", "Anita Pillai", "+971 50 555 1105"),
	("S6", 4, "Falcon - Saadiyat Cultural Annex", "Saadiyat Cultural Annex", "Saadiyat Island, Abu Dhabi", "Yusuf Al Hosani", "+971 50 555 1106"),
	("S7", 5, "Marina Bay - JLT Cluster Podium", "JLT Cluster Podium Works", "Jumeirah Lake Towers, Dubai", "Joseph Mathew", "+971 50 555 1107"),
	("S8", 6, "Pearl Coast - Al Marjan Resort", "Al Marjan Beach Resort Phase 2", "Al Marjan Island, RAK", "Fatima Al Nuaimi", "+971 50 555 1108"),
	("S9", 7, "Oasis - Al Ain Hospital Extension", "Al Ain Hospital Extension Block C", "Al Jimi, Al Ain", "George Thomas", "+971 50 555 1109"),
	("S10", 2, "Desert Rose - Muwaileh Apartments", "Muwaileh Apartment Block 3", "Muwaileh, Sharjah", "Salim Noor", "+971 50 555 1110"),
]

SUPPLIERS = ["Demo Gulf Scaffold Hire FZE", "Demo Emirates Formwork Supplies LLC"]


# --------------------------------------------------------------------------- masters
def get_company(company=None):
	"""An AED company: the one passed in, an existing AED company, or a new demo company."""
	if company:
		if frappe.db.get_value("Company", company, "default_currency") != CURRENCY:
			frappe.throw(f"Company {company} does not use {CURRENCY} (it uses {frappe.db.get_value('Company', company, 'default_currency')})")
		return company
	existing = frappe.db.get_value("Company", {"default_currency": CURRENCY}, "name")
	if existing:
		return existing
	name = "thinkNXG Demo Rentals LLC"
	if not frappe.db.exists("Company", name):
		make({"doctype": "Company", "company_name": name, "abbr": "TDR", "default_currency": CURRENCY,
			"country": "United Arab Emirates", "create_chart_of_accounts_based_on": "Standard Template",
			"chart_of_accounts": "Standard", "enable_perpetual_inventory": 1})
	return name


@section("Company, yards and settings")
def setup_company_and_yards(company):
	from thinknxg_rental.services.setup import ensure_warehouse, setup_company

	frappe.db.set_single_value("Rental Settings", "company", company)
	setup_company(company)
	root = frappe.db.get_value("Warehouse", {"company": company, "is_group": 1, "parent_warehouse": ["in", ["", None]]}, "name")
	settings = frappe.get_doc("Rental Settings")
	have = {r.warehouse for r in settings.own_rental_warehouses}
	yards = []
	for name, location in YARDS:
		wh = ensure_warehouse(name, company, root)
		yards.append(wh)
		if wh not in have:
			settings.append("own_rental_warehouses", {"warehouse": wh, "location": location, "is_active": 1})
	settings.default_billing_cycle = "Monthly"
	settings.default_grace_days = 1
	settings.portal_contact_email = "rentals@thinknxg.com"
	settings.portal_contact_phone = "+971 4 555 0100"
	settings.flags.ignore_permissions = True
	settings.save()
	say(f"   company {company} ({CURRENCY}); yards: {', '.join(yards)}")
	return yards


@section("Item groups, rental items, rental profiles and opening stock")
def setup_items(company, yards):
	root = frappe.db.get_value("Item Group", {"is_group": 1, "parent_item_group": ["in", ["", None]]}, "name") or "All Item Groups"
	for g in ITEM_GROUPS:
		if not frappe.db.exists("Item Group", g):
			make({"doctype": "Item Group", "item_group_name": g, "parent_item_group": root, "is_group": 0})
	made = 0
	for code, name, group, category, daily, weekly, monthly, repl, repair, weight, dims, stock in ITEMS:
		item = PREFIX + code
		new = not frappe.db.exists("Item", item)
		if new:
			make({"doctype": "Item", "item_code": item, "item_name": name, "description": name, "item_group": group,
				"stock_uom": "Nos", "is_stock_item": 1, "is_sales_item": 1, "include_item_in_manufacturing": 0,
				"standard_rate": monthly})
			made += 1
		if not frappe.db.exists("Rental Item Profile", {"item": item}):
			make({"doctype": "Rental Item Profile", "item": item, "category": category, "weight_per_unit": weight,
				"dimensions": dims, "daily_rate": daily, "weekly_rate": weekly, "monthly_rate": monthly,
				"default_rate_basis": "Monthly", "minimum_hire_days": 7,
				"security_deposit_rate": round(repl * 0.1, 2), "replacement_value": repl, "repair_charge": repair,
				"lost_charge": repl, "beyond_repair_charge": round(repl * 0.8, 2),
				"inspection_required": 1 if category in ("Formwork", "Shoring / Props") else 0,
				"show_on_website": 1, "featured": 1 if code in ("FW-AL-6024", "SC-CUP-V25", "SH-PROP-35") else 0,
				"short_description": f"{name} for hire in the UAE. Delivered to site, inspected on return."})
		if new:  # opening stock only for items made now, so a re-run never doubles the yard
			rows = [{"item_code": item, "t_warehouse": yards[i], "qty": qty, "basic_rate": round(repl * 0.75, 2)} for i, qty in stock.items()]
			make({"doctype": "Stock Entry", "stock_entry_type": "Material Receipt", "company": company, "set_posting_time": 1,
				"posting_date": day(-150), "items": rows}, submit=True)
	say(f"   {len(ITEMS)} rental items ({made} new) with profiles; opening stock in {len(yards)} yards")


@section("Job Types")
def setup_job_types():
	group = frappe.db.exists("Item Group", "Rental Services") or "Rental Services"
	if not frappe.db.exists("Item Group", group):
		root = frappe.db.get_value("Item Group", {"is_group": 1, "parent_item_group": ["in", ["", None]]}, "name") or "All Item Groups"
		make({"doctype": "Item Group", "item_group_name": "Rental Services", "parent_item_group": root, "is_group": 0})
	for code, name, desc, rows in JOB_TYPES:
		item = PREFIX + code
		if not frappe.db.exists("Item", item):
			make({"doctype": "Item", "item_code": item, "item_name": name, "description": name, "item_group": "Rental Services",
				"stock_uom": "Nos", "is_stock_item": 0, "is_sales_item": 1, "include_item_in_manufacturing": 0})
		if not frappe.db.exists("Job Type", item):
			make({"doctype": "Job Type", "item_code": item, "description": desc,
				"rental_items": [{"item_code": PREFIX + c, "qty": q} for c, q in rows]})
	say(f"   {len(JOB_TYPES)} job types")


@section("Customers, projects and rental sites")
def setup_parties(company):
	cgroup = frappe.db.get_value("Customer Group", {"is_group": 0, "name": "Commercial"}) or leaf("Customer Group")
	territory = frappe.db.get_value("Territory", {"name": "United Arab Emirates"}) or leaf("Territory")
	sgroup = leaf("Supplier Group")
	customers = []
	for name, trn, contact, phone, email, emirate in CUSTOMERS:
		cust = find("Customer", customer_name=name)
		if not cust:
			cust = make({"doctype": "Customer", "customer_name": name, "customer_type": "Company", "customer_group": cgroup,
				"territory": territory, "tax_id": trn, "default_currency": CURRENCY, "mobile_no": phone, "email_id": email}).name
		customers.append(cust)
	for name in SUPPLIERS:
		if not frappe.db.exists("Supplier", name):
			make({"doctype": "Supplier", "supplier_name": name, "supplier_group": sgroup, "supplier_type": "Company", "default_currency": CURRENCY})
	sites = {}
	for key, ci, site_name, project, location, contact, phone in SITES:
		proj = find("Project", project_name=project)
		if not proj:
			proj = make({"doctype": "Project", "project_name": project, "company": company, "customer": customers[ci],
				"status": "Open", "expected_start_date": day(-120), "expected_end_date": day(240)}).name
		site = find("Rental Site", site_name=site_name)
		if not site:
			site = make({"doctype": "Rental Site", "site_name": site_name, "customer": customers[ci], "project": proj,
				"company": company, "location": location, "site_contact": contact, "contact_phone": phone}).name
		sites[key] = (site, customers[ci], proj)
	say(f"   {len(customers)} customers, {len(SUPPLIERS)} suppliers, {len(sites)} projects and rental sites")
	return customers, sites


@section("Rental rate cards")
def setup_rate_cards(customers):
	cards = [("Demo - Al Noor framework rates 2026", customers[0], 0.9, ["SC-CUP-V25", "SC-CUP-L18", "SC-TUBE-6M", "SC-PLANK-39", "SH-PROP-35"]),
		("Demo - Emirates Skyline formwork rates 2026", customers[3], 0.92, ["FW-AL-6024", "FW-AL-3024", "FW-SLAB-TBL", "SH-PROP-48"])]
	for title, customer, factor, codes in cards:
		if find("Rental Rate Card", title=title):
			continue
		rows = []
		for c in codes:
			p = frappe.db.get_value("Rental Item Profile", {"item": PREFIX + c}, ["daily_rate", "weekly_rate", "monthly_rate"], as_dict=True)
			rows.append({"item_code": PREFIX + c, "daily_rate": round(p.daily_rate * factor, 2),
				"weekly_rate": round(p.weekly_rate * factor, 2), "monthly_rate": round(p.monthly_rate * factor, 2)})
		make({"doctype": "Rental Rate Card", "title": title, "customer": customer, "valid_from": day(-120), "valid_upto": day(245), "items": rows})
	say("   2 customer rate cards")


# --------------------------------------------------------------------------- hire flow
def hire_order(company, site, items, start, back, ref, submit=True, basis="Monthly", cycle="Monthly"):
	"""items: [(code, qty)] priced from the Rental Item Profile."""
	site_name, customer, project = site
	if find("Hire Order", customer_reference=ref):
		return frappe.get_doc("Hire Order", find("Hire Order", customer_reference=ref))
	rows = []
	for code, qty in items:
		p = frappe.db.get_value("Rental Item Profile", {"item": PREFIX + code},
			["monthly_rate", "weekly_rate", "daily_rate", "security_deposit_rate", "replacement_value", "repair_charge", "lost_charge", "beyond_repair_charge"], as_dict=True)
		rate = {"Monthly": p.monthly_rate, "Weekly": p.weekly_rate, "Daily": p.daily_rate}[basis]
		rows.append({"item_code": PREFIX + code, "qty": qty, "rate_basis": basis, "rate": rate, "security_deposit_rate": p.security_deposit_rate,
			"replacement_value": p.replacement_value, "repair_charge": p.repair_charge, "lost_charge": p.lost_charge,
			"beyond_repair_charge": p.beyond_repair_charge})
	return make({"doctype": "Hire Order", "company": company, "customer": customer, "rental_site": site_name, "project": project,
		"order_date": add_days(start, -3), "required_from": start, "expected_return_date": back, "rate_basis": basis,
		"billing_cycle": cycle, "customer_reference": ref, "items": rows,
		"remarks": "Demo data"}, submit=submit)


def contract_from_order(order, start):
	from thinknxg_rental.thinknxg_rental.doctype.hire_order.hire_order import make_contract

	existing = frappe.db.get_value("Rental Contract", {"source_type": "Hire Order", "source_document": order.name, "docstatus": 1})
	if existing:
		return frappe.get_doc("Rental Contract", existing)
	rc = make_contract(order.name)
	rc.contract_date = start
	return make(rc, submit=True)


def reserve_and_deliver(rc, yard, start, deliver=True, driver="Demo Driver"):
	from thinknxg_rental.thinknxg_rental.doctype.hire_delivery_order.hire_delivery_order import get_dispatch_items
	from thinknxg_rental.thinknxg_rental.doctype.rental_contract.rental_contract import make_reservation

	res = frappe.db.get_value("Rental Material Reservation", {"rental_contract": rc.name, "docstatus": 1})
	if not res:
		doc = make_reservation(rc.name)
		doc.source_warehouse = yard
		doc.reservation_date = add_days(start, -2)
		res = make(doc, submit=True).name
	hdo = None
	if deliver and not frappe.db.exists("Hire Delivery Order", {"rental_contract": rc.name, "docstatus": 1}):
		rows = get_dispatch_items(rc.name, res)
		hdo = make({"doctype": "Hire Delivery Order", "company": rc.company, "rental_contract": rc.name,
			"rental_material_reservation": res, "posting_date": start, "vehicle_no": "DXB A 48213", "driver_name": driver,
			"driver_phone": "+971 50 555 2201", "items": rows}, submit=True)
	return res, hdo


def off_hire(rc, when, fraction=None, items=None, reason="Phase completed"):
	"""Return `fraction` of everything at site, or explicit {item_code: qty}."""
	from thinknxg_rental.thinknxg_rental.doctype.hire_off_hire_note.hire_off_hire_note import get_items_at_site

	rows = []
	for r in get_items_at_site(rc.name):
		if items is not None:
			qty = items.get(r["item_code"], 0)
		else:
			qty = round(flt(r["at_site_qty"]) * fraction)
		if qty > 0:
			rows.append({"item_code": r["item_code"], "ownership": r["ownership"], "cross_hire_order": r.get("cross_hire_order"),
				"returned_qty": min(qty, flt(r["at_site_qty"])), "delivered_from": r.get("delivered_from"),
				"return_to_warehouse": r.get("return_to_warehouse")})
	return make({"doctype": "Hire Off-Hire Note", "company": rc.company, "rental_contract": rc.name, "off_hire_date": when,
		"return_date": when, "grace_days": cint(rc.grace_days), "reason": reason, "vehicle_no": "DXB B 20877",
		"driver_name": "Demo Driver", "items": rows}, submit=True)


def inspect(note, repairable_pct=0.05, damaged_pct=0.02, when=None, damage_note="Concrete residue and bent edges"):
	from thinknxg_rental.thinknxg_rental.doctype.hire_off_hire_note.hire_off_hire_note import make_inspection

	insp = make_inspection(note.name)
	insp.inspection_date = when or note.return_date
	for r in insp.items:
		total = flt(r.returned_qty)
		bad = round(total * damaged_pct)
		fix = round(total * repairable_pct)
		r.damaged_qty, r.repairable_qty = bad, fix
		r.good_qty = total - bad - fix
		if bad or fix:
			r.damage_notes = damage_note
	return make(insp, submit=True)


def bill(rc, upto):
	from thinknxg_rental.services.billing import generate_billing

	out = generate_billing(rc.name, upto)
	say(f"   billed {rc.name}: {len(out or [])} schedule(s) / invoice(s)")
	return out


@section("Hire flow: orders, contracts, reservations, deliveries, returns, billing")
def hire_flow(company, yards, sites):
	dubai, abudhabi, sharjah = yards
	S = sites

	# 1. Active scaffolding hire, Business Bay: delivered 75 days ago, 40% returned 20 days ago, billed monthly
	ho = hire_order(company, S["S1"], [("SC-CUP-V25", 600), ("SC-CUP-L18", 1100), ("SC-PLANK-39", 400), ("SC-BASE-JACK", 200), ("AC-TOEBOARD", 250)],
		day(-75), day(120), "DEMO-PO-AN-0142")
	rc = contract_from_order(ho, day(-75))
	reserve_and_deliver(rc, dubai, day(-75))
	if not frappe.db.exists("Hire Off-Hire Note", {"rental_contract": rc.name, "docstatus": 1}):
		off_hire(rc, day(-20), fraction=0.4)
	bill(rc, day(-1))

	# 2. Active formwork hire, Creek Harbour: delivered 38 days ago, nothing returned, monthly billing
	ho = hire_order(company, S["S5"], [("FW-AL-6024", 420), ("FW-AL-3024", 220), ("FW-COL-CLP", 90), ("FW-TIE-15", 3500), ("FW-WING-NUT", 3500)],
		day(-38), day(150), "DEMO-PO-ESD-0377", basis="Monthly")
	rc = contract_from_order(ho, day(-38))
	reserve_and_deliver(rc, dubai, day(-38))
	bill(rc, day(-1))

	# 3. Shoring hire, Yas Island (Abu Dhabi yard), weekly rate, delivered 24 days ago, 25% returned 6 days ago
	ho = hire_order(company, S["S3"], [("SH-PROP-35", 800), ("SH-PROP-48", 300), ("SH-UHEAD", 600), ("FW-PLY-244", 350)],
		day(-24), day(90), "DEMO-PO-GH-0219", basis="Weekly", cycle="Weekly")
	rc = contract_from_order(ho, day(-24))
	reserve_and_deliver(rc, abudhabi, day(-24))
	if not frappe.db.exists("Hire Off-Hire Note", {"rental_contract": rc.name, "docstatus": 1}):
		off_hire(rc, day(-6), fraction=0.25)

	# 4. Completed hire, Al Zahia: delivered 130 days ago, fully returned 35 days ago, inspected with damage, closed and billed
	ho = hire_order(company, S["S4"], [("FW-SLAB-TBL", 60), ("SH-PROP-35", 400), ("SH-UHEAD", 400), ("FW-PLY-244", 300)],
		day(-130), day(-30), "DEMO-PO-DR-0088")
	rc = contract_from_order(ho, day(-130))
	reserve_and_deliver(rc, sharjah, day(-130))
	note = frappe.db.get_value("Hire Off-Hire Note", {"rental_contract": rc.name, "docstatus": 1})
	if not note:
		note = off_hire(rc, day(-35), fraction=1, reason="Project phase complete").name
	if not frappe.db.exists("Rental Return Inspection", {"hire_off_hire_note": note, "docstatus": 1}):
		inspect(frappe.get_doc("Hire Off-Hire Note", note), repairable_pct=0.06, damaged_pct=0.03, when=day(-33))
	bill(rc, day(-30))
	try:
		frappe.get_doc("Rental Contract", rc.name).close_contract()
		say(f"   {rc.name} closed")
	except Exception as e:  # closure needs every damage settled; leave it open rather than fail the demo
		say(f"   {rc.name} left open: {str(e)[:140]}")

	# 5. Reserved, not yet delivered: Skyline podium formwork starts in 9 days
	ho = hire_order(company, S["S7"], [("FW-AL-6024", 180), ("FW-AL-3024", 90), ("SC-HFRAME-17", 300), ("SC-XBRACE", 600)],
		day(9), day(190), "DEMO-PO-MB-0510")
	rc = contract_from_order(ho, day(9))
	reserve_and_deliver(rc, dubai, day(9), deliver=False)

	# 6. Hire Orders waiting: one submitted and open, one draft
	hire_order(company, S["S8"], [("SC-TUBE-6M", 900), ("SC-CPL-FIX", 3500), ("SC-CPL-SWV", 1800), ("SC-PLANK-39", 350)],
		day(14), day(104), "DEMO-PO-PC-0061")
	hire_order(company, S["S9"], [("SH-TOWER-LEG", 240), ("SC-XBRACE", 300), ("AC-STAIR", 20)],
		day(21), day(141), "DEMO-PO-OC-0033", submit=False)

	# 7. Small short hire, Muwaileh: daily rate, delivered 12 days ago, fully returned 2 days ago
	ho = hire_order(company, S["S10"], [("AC-STAIR", 12), ("SC-HFRAME-17", 60), ("SC-XBRACE", 120)], day(-12), day(-2),
		"DEMO-PO-DR-0097", basis="Daily", cycle="Daily")
	rc = contract_from_order(ho, day(-12))
	reserve_and_deliver(rc, sharjah, day(-12))
	if not frappe.db.exists("Hire Off-Hire Note", {"rental_contract": rc.name, "docstatus": 1}):
		off_hire(rc, day(-2), fraction=1, reason="Short hire complete")
	bill(rc, day(-1))
	say("   hire flow done")


# --------------------------------------------------------------------------- job type contracts
def hoc(company, site, lines, ref, start, billing, taxes=None):
	"""lines: [(job type code, location, jobs, included days, contract rate, excess basis, excess rate)]"""
	site_name, customer, project = site
	existing = find("Hire Order Contract", customer_reference=ref)
	if existing:
		return frappe.get_doc("Hire Order Contract", existing)
	items = [{"job_type": PREFIX + jt, "location": loc, "qty": qty, "included_days": days, "nxg_duration": 1,
		"contract_rate": rate, "excess_rate_basis": basis, "excess_rate": ex} for jt, loc, qty, days, rate, basis, ex in lines]
	return make({"doctype": "Hire Order Contract", "company": company, "customer": customer, "rental_site": site_name, "project": project,
		"order_date": add_days(start, -4), "required_from": start, "customer_reference": ref, "items": items,
		"contract_charge_billing": billing, "remarks": "Demo data"}, submit=True)


def rental_contract_from_hoc(doc, start):
	from thinknxg_rental.thinknxg_rental.doctype.hire_order_contract.hire_order_contract import make_rental_contract

	existing = frappe.db.get_value("Rental Contract", {"source_type": "Hire Order Contract", "source_document": doc.name, "docstatus": 1})
	if existing:
		return frappe.get_doc("Rental Contract", existing)
	rc = make_rental_contract(doc.name)
	rc.contract_date = start
	return make(rc, submit=True)


def reserve_hoc(doc, rc, yard, start):
	from thinknxg_rental.thinknxg_rental.doctype.hire_order_contract.hire_order_contract import make_reservation

	if frappe.db.exists("Rental Material Reservation", {"rental_contract": rc.name, "docstatus": 1}):
		return frappe.db.get_value("Rental Material Reservation", {"rental_contract": rc.name, "docstatus": 1})
	res = make_reservation(doc.name)
	res.source_warehouse = yard
	res.rental_contract = rc.name
	res.reservation_date = add_days(start, -2)
	return make(res, submit=True).name


def jcr(doc, line_index, erection, jobs, dismantle=None):
	from thinknxg_rental.thinknxg_rental.doctype.hire_order_contract.hire_order_contract import make_jcr

	line = doc.items[line_index]
	report = make_jcr(doc.name, args={"contract_item": line.name})
	for row in report.job_lines:
		row.job_qty = jobs
		row.erection_date = erection
		if dismantle:
			row.dismantle_date = dismantle
	return make(report, submit=True)


@section("Job type contracts: Hire Order Contracts, JCRs and billing")
def job_type_flow(company, yards, sites):
	from thinknxg_rental.thinknxg_rental.doctype.hire_delivery_order.hire_delivery_order import get_dispatch_items

	dubai, abudhabi, _sharjah = yards
	# A. Wall formwork + shoring tower, Al Noor Dubai South - billed at contract end; one JCR in excess, one dismantled
	d1 = hoc(company, sites["S2"], [
		("JT-WALL-AL", "Warehouse 1 - Core walls", 40, 21, 1850, "Daily", 95),
		("JT-WALL-AL", "Warehouse 2 - Core walls", 30, 21, 1850, "Daily", 95),
		("JT-SHORE-TWR", "Warehouse 1 - Transfer slab", 6, 45, 4200, "Weekly", 1100)],
		"DEMO-HOC-AN-0007", day(-60), "At Contract End")
	rc = rental_contract_from_hoc(d1, day(-60))
	res = reserve_hoc(d1, rc, dubai, day(-60))
	if not frappe.db.exists("Hire Delivery Order", {"rental_contract": rc.name, "docstatus": 1}):
		make({"doctype": "Hire Delivery Order", "company": company, "rental_contract": rc.name, "rental_material_reservation": res,
			"posting_date": day(-60), "vehicle_no": "DXB C 77310", "driver_name": "Demo Driver",
			"items": get_dispatch_items(rc.name, res)}, submit=True)
	if not frappe.db.exists("Job Completion Report", {"hire_order_contract": d1.name, "docstatus": 1}):
		jcr(d1, 0, day(-55), 40, dismantle=day(-20))   # dismantled
		jcr(d1, 1, day(-48), 30)                       # past its 21 included days: in excess
		jcr(d1, 2, day(-30), 6)                        # within contract
	say(f"   {d1.name}: {rc.name} with 3 JCRs")

	# B. Slab tables + cuplock bays, Skyline - billed on erection; recent erection, still within contract
	d2 = hoc(company, sites["S5"], [
		("JT-SLAB-TBL", "Podium Level 3 slab", 4, 30, 9800, "Weekly", 2400),
		("JT-CUP-BAY", "Podium facade access", 25, 60, 780, "Weekly", 190)],
		"DEMO-HOC-ESD-0012", day(-14), "On Erection")
	rc2 = rental_contract_from_hoc(d2, day(-14))
	res2 = reserve_hoc(d2, rc2, dubai, day(-14))
	if not frappe.db.exists("Hire Delivery Order", {"rental_contract": rc2.name, "docstatus": 1}):
		make({"doctype": "Hire Delivery Order", "company": company, "rental_contract": rc2.name, "rental_material_reservation": res2,
			"posting_date": day(-14), "vehicle_no": "DXB D 10458", "driver_name": "Demo Driver",
			"items": get_dispatch_items(rc2.name, res2)}, submit=True)
	if not frappe.db.exists("Job Completion Report", {"hire_order_contract": d2.name, "docstatus": 1}):
		jcr(d2, 0, day(-10), 4)
		jcr(d2, 1, day(-9), 25)
	say(f"   {d2.name}: {rc2.name} with 2 JCRs")

	# C. Contract signed, nothing delivered yet: Falcon Saadiyat annex shoring
	d3 = hoc(company, sites["S6"], [("JT-SHORE-TWR", "Annex roof transfer beams", 8, 60, 4200, "Weekly", 1100)],
		"DEMO-HOC-FI-0003", day(12), "At Contract End")
	say(f"   {d3.name}: open, no rental contract yet")


# --------------------------------------------------------------------------- cross hire
@section("Cross hire: supplier material delivered to a customer site")
def cross_hire_flow(company, yards, sites):
	from thinknxg_rental.services.cross_hire import make_cross_hire_receipt
	from thinknxg_rental.thinknxg_rental.doctype.hire_delivery_order.hire_delivery_order import get_dispatch_items

	dubai = yards[0]
	supplier = SUPPLIERS[0]
	site = sites["S8"]
	ref = "DEMO-PO-PC-0066"
	# the customer asks for more shoring towers than the yards hold, so the balance is cross hired
	ho = hire_order(company, site, [("SH-TOWER-LEG", 700)], day(-18), day(100), ref)
	rc = contract_from_order(ho, day(-18))
	if find("Cross Hire Order", rental_contract=rc.name):
		say("   cross hire already present")
		return
	own = frappe.db.get_value("Bin", {"item_code": PREFIX + "SH-TOWER-LEG", "warehouse": dubai}, "actual_qty") or 0
	cross_qty = 200
	cho = make({"doctype": "Cross Hire Order", "company": company, "supplier": supplier, "rental_contract": rc.name,
		"order_date": day(-22), "hire_from": day(-20), "expected_return_date": day(100), "receive_at": "Cross Hire Yard",
		"items": [{"item_code": PREFIX + "SH-TOWER-LEG", "qty": cross_qty, "rate": 44, "rate_basis": "Monthly"}]}, submit=True)
	po = frappe.db.get_value("Cross Hire Order", cho.name, "purchase_order")
	if po and frappe.db.get_value("Purchase Order", po, "docstatus") == 0:
		frappe.get_doc("Purchase Order", po).submit()
	pr = make_cross_hire_receipt(cho.name)
	pr.posting_date = day(-19)
	make(pr, submit=True)
	res = frappe.db.get_value("Rental Material Reservation", {"rental_contract": rc.name, "docstatus": 1})
	if not res:
		from thinknxg_rental.thinknxg_rental.doctype.rental_contract.rental_contract import make_reservation

		doc = make_reservation(rc.name)
		doc.source_warehouse = dubai
		doc.reservation_date = day(-19)
		res = make(doc, submit=True).name
	make({"doctype": "Hire Delivery Order", "company": company, "rental_contract": rc.name, "rental_material_reservation": res,
		"posting_date": day(-18), "vehicle_no": "RAK E 55120", "driver_name": "Demo Driver",
		"items": get_dispatch_items(rc.name, res)}, submit=True)
	say(f"   own stock {own:.0f}; cross hire {cho.name} ({cross_qty} units from {supplier}) delivered on {rc.name}")


# --------------------------------------------------------------------------- entry points
def load(company=None):
	"""Load the whole demo dataset. Returns a short summary."""
	frappe.flags.in_demo_load = True
	frappe.set_user("Administrator")
	LOG.clear()
	company = get_company(company)
	frappe.db.commit()
	say(f"thinkNXG Rental demo data - company {company}, currency {CURRENCY}")
	yards = setup_company_and_yards(company)
	if not yards:
		return "Company setup failed; see the Error Log"
	setup_items(company, yards)
	setup_job_types()
	parties = setup_parties(company)
	if not parties:
		return "Customer setup failed; see the Error Log"
	customers, sites = parties
	setup_rate_cards(customers)
	hire_flow(company, yards, sites)
	job_type_flow(company, yards, sites)
	cross_hire_flow(company, yards, sites)
	counts = {dt: frappe.db.count(dt) for dt in ("Rental Item Profile", "Rental Site", "Hire Order", "Hire Order Contract", "Rental Contract",
		"Hire Delivery Order", "Hire Off-Hire Note", "Rental Return Inspection", "Job Completion Report", "Cross Hire Order", "Sales Invoice")}
	say("\nDone. Record counts: " + ", ".join(f"{k} {v}" for k, v in counts.items()))
	return counts


def clear(company=None):
	"""Remove the demo transactions and masters (anything created by load). Cancels submitted documents newest first.
	Stock entries are cancelled too, so item stock goes back to nil. Uses the DM- / DEMO- markers only."""
	frappe.set_user("Administrator")
	frappe.flags.ignore_permissions = True
	demo_items = frappe.get_all("Item", filters={"item_code": ["like", PREFIX + "%"]}, pluck="name")
	if not demo_items:
		say("No demo items found; nothing to clear")
		return
	order = ["Sales Invoice", "Rental Billing Schedule", "Job Completion Report", "Rental Return Inspection", "Hire Off-Hire Note",
		"Hire Delivery Order", "Rental Material Reservation", "Purchase Receipt", "Purchase Order", "Cross Hire Order", "Rental Contract",
		"Hire Order Contract", "Hire Order"]
	demo_customers = frappe.get_all("Customer", filters={"customer_name": ["in", [c[0] for c in CUSTOMERS]]}, pluck="name")
	for dt in order:
		meta = frappe.get_meta(dt)
		flt_ = {}
		if meta.has_field("customer"):
			flt_["customer"] = ["in", demo_customers]
		elif dt in ("Purchase Receipt", "Purchase Order", "Cross Hire Order"):
			flt_["supplier"] = ["in", SUPPLIERS]
		else:
			continue
		for name in frappe.get_all(dt, filters=flt_, pluck="name", order_by="creation desc"):
			try:
				doc = frappe.get_doc(dt, name)
				if doc.docstatus == 1:
					doc.cancel()
				frappe.delete_doc(dt, name, force=True, ignore_permissions=True)
			except Exception as e:
				say(f"   could not remove {dt} {name}: {str(e)[:100]}")
	for se in frappe.get_all("Stock Entry Detail", filters={"item_code": ["in", demo_items]}, pluck="parent", distinct=True):
		try:
			doc = frappe.get_doc("Stock Entry", se)
			if doc.docstatus == 1:
				doc.cancel()
			frappe.delete_doc("Stock Entry", se, force=True, ignore_permissions=True)
		except Exception as e:
			say(f"   could not remove Stock Entry {se}: {str(e)[:100]}")
	for dt, key, vals in (("Rental Rate Card", "title", [f"Demo - {t}" for t in ("Al Noor framework rates 2026", "Emirates Skyline formwork rates 2026")]),
		("Rental Site", "site_name", [s[2] for s in SITES]), ("Project", "project_name", [s[3] for s in SITES]),
		("Customer", "customer_name", [c[0] for c in CUSTOMERS]), ("Supplier", "supplier_name", SUPPLIERS)):
		for name in frappe.get_all(dt, filters={key: ["in", vals]}, pluck="name"):
			try:
				frappe.delete_doc(dt, name, force=True, ignore_permissions=True)
			except Exception as e:
				say(f"   could not remove {dt} {name}: {str(e)[:100]}")
	for jt in frappe.get_all("Job Type", filters={"name": ["like", PREFIX + "%"]}, pluck="name"):
		frappe.delete_doc("Job Type", jt, force=True, ignore_permissions=True)
	for item in demo_items:
		for p in frappe.get_all("Rental Item Profile", filters={"item": item}, pluck="name"):
			frappe.delete_doc("Rental Item Profile", p, force=True, ignore_permissions=True)
		try:
			frappe.delete_doc("Item", item, force=True, ignore_permissions=True)
		except Exception as e:
			say(f"   could not remove Item {item}: {str(e)[:100]}")
	frappe.db.commit()
	say("Demo data cleared (the company, yards and item groups are left in place).")
