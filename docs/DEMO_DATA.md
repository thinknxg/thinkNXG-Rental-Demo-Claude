# thinkNXG Rental demo data (AED)

A ready-to-load demo dataset for UAE / GCC formwork, scaffolding and shoring hire, priced in AED.

```bash
bench --site <site> execute thinknxg_rental.demo.demo_data.load                 # load
bench --site <site> execute thinknxg_rental.demo.demo_data.load --kwargs '{"company": "My AED Company"}'
bench --site <site> execute thinknxg_rental.demo.demo_data.clear                # remove it again
```

The site needs ERPNext v16 and thinkNXG Rental installed. The loader uses an existing company whose currency is AED, or
creates **thinkNXG Demo Rentals LLC** (AED, United Arab Emirates). It is safe to run twice: every record is looked up first.
Each section runs on its own, so one failure is printed and logged (Error Log) without stopping the rest.

| Area | What you get |
|---|---|
| Yards | Dubai (Jebel Ali), Abu Dhabi (Mussafah), Sharjah (Industrial Area 4) as own rental warehouses |
| Items | 22 rental items (`DM-` prefix) in Formwork, Scaffolding, Shoring and Props, Accessories, each with a Rental Item Profile (daily / weekly / monthly AED rates, deposit, replacement, repair and loss charges) and opening stock |
| Job Types | Aluminium wall formwork, slab table set, cuplock bay, shoring tower |
| Parties | 8 customers with 15-digit TRNs, 10 projects and rental sites, 2 customer rate cards, 2 cross hire suppliers |
| Hire flow | active scaffolding hire with partial return and monthly billing; active formwork hire; weekly shoring hire; a completed hire with an inspection (repairable and beyond-repair material) and closure; a reserved hire starting in 9 days; one open and one draft Hire Order; a short daily-rate hire |
| Job type contracts | Hire Order Contracts billed *At Contract End* and *On Erection*, with Job Completion Reports that are within contract, in excess and dismantled; one signed contract with nothing delivered yet |
| Cross hire | shoring towers short in the yards, cross hired from a supplier (Cross Hire Order, Purchase Order, receipt) and delivered to the customer site |

Customer and supplier names are fictional. Dates are relative to the day you load, so the data always looks current.
`clear` cancels and deletes what `load` created (by the `DM-` / `DEMO-` markers and demo customer names); the company, yards and item groups stay.
