# thinkNXG Rental - Demo Data (AED)

Demo dataset loader for [thinkNXG Rental](https://github.com/thinknxg/ThinkNXG-Rental) on Frappe/ERPNext v16, priced in AED
(UAE / GCC formwork, scaffolding and shoring hire).

## Install into the app

Copy `thinknxg_rental/demo/` into the app's Python package (`apps/thinknxg_rental/thinknxg_rental/demo/`), then:

```bash
bench --site <site> execute thinknxg_rental.demo.demo_data.load
bench --site <site> execute thinknxg_rental.demo.demo_data.clear   # remove it again
```

See [docs/DEMO_DATA.md](docs/DEMO_DATA.md) for what is created.

Note: not yet run against a live site; try it on staging first.
