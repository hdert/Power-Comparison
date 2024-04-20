To use the ContactEnergyDownloader:

1. Run `python -m venv .venv`
2. Run `source .venv/bin/activate`
3. Run `pip install -r requirements.txt`
4. Run `python power_comparison.py`
5. Profit!

---

## If you want to run the tools manually

1. Copy config/credentials.env.example to config/credentials.env and fill in the file with your details
2. Install ContactEnergyNz from pypi, and it's dependencies aiohttp and others
3. From the project source directory run `python contact_energy_downloader.py`

To use the DataProcessor:

1. From the project source directory run `python data_processor.py [usage_file] [analysis_file]`, adding an optional
   `--from-date 1970-01-01` argument if you want a rolling average calculation.

To use the StatisticsGenerator:

1. Create a new directory in profiles, and populate that directory with power plan profiles in the
   format of `profiles/example.csv`, or use the provided `Christchurch-Apr-2024` profiles if you live in
   Christchurch
2. From the project source directory run `python statistics_generator.py [analysis_file] [profiles/<Your profile directory here>]`
3. Profit!
