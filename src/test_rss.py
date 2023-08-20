""" To test making an RSS feed """
import feedparser
from feedgen.feed import FeedGenerator


def main():
    """ Step 1: Parse the existing Atom feed """
    existing_feed_url = "https://wtangy.se/atom.xml"
    parsed_feed = feedparser.parse(existing_feed_url)
    if parsed_feed.entries == []:
        with open("atom_bootstrap.xml", "r", encoding="utf-8") as boot_strap_feed_file:
            initial_feed = boot_strap_feed_file.read()
            parsed_feed = feedparser.parse(initial_feed)

    # Step 2: Modify the feed entries and metadata
    modified_entries = []
    for entry in parsed_feed.entries:
        # Modify entry attributes as needed
        modified_entries.append(entry)

    # Step 3: Create a new Atom feed using feedgenerator
    new_feed = FeedGenerator()
    new_feed.title("WTANGY Schedule Updates")
    new_feed.description("Was There An NHL Game Yesterday?")
    new_feed.link(href="https://wtangy.se/", rel="alternate")
    new_feed.link(href="https://wtangy.se/atom.xml", rel="self")
    new_feed.language("en")
    new_feed.id("https://wtangy.se/")

    # Add modified entries to the new feed
    for modified_entry in modified_entries:
        entry = new_feed.add_entry()
        entry.id(modified_entry.id)
        entry.title(modified_entry.title)
        entry.description(modified_entry.description)
        entry.link(href=modified_entry.link, rel="alternate")
        entry.updated(modified_entry.updated)
        entry.category([{"term": modified_entry.category}])

    new_update = new_feed.add_entry()
    new_update.id("https://wtangy.se/")
    new_update.title("NHL Schedule Has Been Updated")
    new_update.description("It's available on https://wtangy.se/get_schedule")
    new_update.link(href="https://wtangy.se/get_schedule", rel="alternate")
    new_update.category([{"term": "Testing"}])
    author = {"name": "cron"}
    new_update.author(author)

    # Step 4: Save the new Atom feed as a file
    # new_atom_feed_xml = new_feed.atom_str(pretty=True)
    new_feed.atom_file(pretty=True, filename="test_atom_feed.xml")


if __name__ == "__main__":
    main()
    print("OK: We have updated the feed")
