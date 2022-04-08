import random
from time import sleep
from FacebookSpyder import FriendSpyder
from concurrent.futures import ThreadPoolExecutor
import codecs

# these are lists that hold links. ?
to_be_scraped = [

    "https://www.facebook.com/sunny.mcdaneil/friends?lst="
    "100044134714902%3A100042743116015%3A1575540809&source_ref=pb_friends_tl",

    "https://www.facebook.com/joseph.norris.165685",

    "https://www.facebook.com/aDtIdW/friends?lst="
    "100044134714902%3A100000020929223%3A1575543267&source_ref=pb_friends_tl",

    "https://www.facebook.com/cindy.crossno2/friends?lst="
    "100044134714902%3A1222112563%3A1575542392&source_ref=pb_friends_tl",

    "https://www.facebook.com/mike.aaron.56884761"

]

is_being_scraped = []

has_been_scraped = []

black_list = []

keep_going = True

limit = 5


def get_pending():
    return to_be_scraped


def set_limit(num):
    global limit
    limit = num


total_friends = dict()
spyders = []


def create_spyders(num):
    for _ in range(num):
        spyders.append(FriendSpyder())


def run(url):
    global keep_going, limit

    if keep_going:
        spyder = next(x for x in spyders if x.idle)

        spyder.idle = False  # this spyder is now busy

        # url can't be in any of these lists:
        if url in black_list or (url in is_being_scraped or url in has_been_scraped):
            # if it is, then remove from pending list and STOP
            to_be_scraped.remove(url)
            spyder.idle = True  # free the spyder
        else:
            to_be_scraped.remove(url)  # remove from pending
            is_being_scraped.append(url)  # add to processing

            # this is where the magic happens
            returned_friends = spyder.activate(url)

            # if None is returned, then there were no friends to scrape at this url
            if returned_friends is None:
                is_being_scraped.remove(url)  # remove from processing
                black_list.append(url)  # add to black list
                spyder.idle = True  # free the spyder
            else:
                # append new links to pending
                # print(returned_friends.values())
                add_links(returned_friends.values())

                # append names to dict of names (format is {person: [frnd1, frnd2, frnd3...]}
                append_dict(total_friends,
                            list(returned_friends.keys())[0],
                            list(returned_friends.values())[0])

                # save results in a text file for when the program inevitably crashes

                # IMPORTANT: results won't be saved until this is uncommented
                # save_results(total_friends)

                # url has been scraped
                is_being_scraped.remove(url)  # remove from processing
                has_been_scraped.append(url)  # add to processed

                spyder.idle = True  # finally, free the spyder


# if len(has_been_scraped) > limit:
#     keep_going = False


# def create_dict(name, friends):
#     """
#     returns {name: friends}
#     """
#     to_return = dict()
#     to_return[name] = friends
#     return to_return


def append_dict(og_dict, val_key, val_value):
    # if name of person isn't a key in this dict, add it.
    if val_key not in list(og_dict.keys()):  # probably redundant
        og_dict[val_key] = val_value


def save_results(results):
    with codecs.open("results_file.txt", mode='w', encoding='utf-8') as file_:
        for key in results.keys():
            file_.write(f"{key}: {list(results[key].keys())}\n")


def add_links(links):
    links = list(links)
    print(f"adding {len(links[0].values())} links")
    for link in list(links[0].values()):
        if link not in to_be_scraped:
            to_be_scraped.append(link)

    print(f"There are {len(to_be_scraped)} links to be scraped")
