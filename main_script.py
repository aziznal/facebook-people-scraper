from concurrent.futures.thread import ThreadPoolExecutor
from functions import run, get_pending, create_spyders
from Tools.MySQL.database import Database
import Tools.myTools.functions as tools
from Tools.WebScraping.scraping_functions import *
from time import sleep, perf_counter
from Tools.WebScraping.Spyder.Spyder import Spyder


start_timer = perf_counter()

starting_list = get_pending()

# create_spyders(2)
# while len(starting_list) != 0:
#     with ThreadPoolExecutor(max_workers=2) as executor:
#         for val in starting_list:
#             executor.submit(run, val)
#             sleep(0.05)


create_spyders(1)

# note: program will scrape the entirety of facebook before stopping.
# to stop, close the browser(s)

# question: how to not do this?
try:
    while True:
        for val in starting_list:
            run(val)
except Exception as e:
    print(f"The code was ended abruptly. {e}")

end_timer = perf_counter()

print(f"Script finished in {round(end_timer - start_timer)} seconds")
