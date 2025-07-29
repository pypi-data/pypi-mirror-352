# MiPi FileSearch

## About
Search your file system for text files based on their location, name, extension, and content. Remember
to setup your prefrences in `mipi_setup.py`!

## Live Path
Set this using the `Set Live Path` button. It will persist within the session unless you change it again.
This determines where `Export Results` saves the results file and `(0) Live Path` copies individual files.

## Filters
Any Menu which starts with `Filter...` will set the criteria for files to include in the results.
The search results uses `and` logic between filters. For example if you set filters for `extension: .sql & content_includes: UPPER`
the file must meet *BOTH* of those criteria.

### Registered Filters
There may be filters that you apply commonly but dont want to type out every single app session. You can register
parameters in `mipi_setup.py` and toggle them within the search session. The syntax to register a parameter is shown
by filter, note that typehints are included

### Live Filters
These filters are entered manually at the application session. You don't have to set up anything here. Just open
a filter and enter your live filter to use it! All filters support live filtering!

### Filter Search Paths

- OR logic
- Required
- Register syntax: `set_search_directories = [(path_to_directory: str, display_name: str, default_toggle_value: bool), ]

### Filter File Extensions

- OR logic
- Optional: Default include all extensions
- Register syntax: `set_search_extensions = [(.extension: str, default_toggle_value), ]

### Filter Content Includes
filter to by content to include one of the following substrings

- OR logic 
- Optional: Default no filter on content
- Coming soon: 
   - Highlight substrings in output test
   - Toggle between filter on substring vs only highlight substring 

### Filter File Names

COMING SOON!!!!!

## Copy Files
You are likely using this to utilize one or more files. This application has built in functionality copy files from
their source into a new location. You can do this by selecting a file on the results window, and pressing a number key
on your keyboard.

### Live Path (0)
(0) will always be your `Live Path`. If you have not selected one you will be prompted to do so.

### Registered Paths (1-9)
(1-9) can be registered in `mipi_setup.py` using the following syntax:

set_copy_destinations = [ (path/to/destination_dir: str, Display Name On App Footer) ]
