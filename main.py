import os
import sys
import shutil
import datetime
from PIL import Image
from PIL.ExifTags import TAGS

# default values
input_folder = "./input"
output = "./output"
start_date = datetime.datetime.strptime("2022-11-01", '%Y-%m-%d')
keyword = "Muscu"

# get the input folder from the first argument
if len(sys.argv) > 1:
    input_folder = sys.argv[1]
# get the output folder from the second argument
if len(sys.argv) > 2:
    output = sys.argv[2]
# get the start date from the third argument
if len(sys.argv) > 3:
    start_date = datetime.datetime.strptime(sys.argv[3], '%Y-%m-%d')

print("input folder: " + input_folder + "\noutput folder (this will get cleared): " + output + "\nstart date: " + start_date.strftime('%Y-%m-%d'))

# ask if it needs to filter the input based on folders names
print("Do you want to filter folders starting with \"" + keyword + "\"? (y/n)")
should_sort = (input() == "y")

# ask for confirmation
print("Are you sure you want to continue? (y/n)")
if input() != "y":
    print("cancelled")
    exit()

# delete the output folder if it exists
if os.path.exists(output):
    shutil.rmtree(output)

# create the output folder
os.makedirs(output)

# use walk to get all the files in the input folder and its subfolders
# for each folder in the directory
#   for each file in the folder
#       copy the file with the same path to the output folder
#       rename the file to the difference between the file's date and the start date, following the format xA_xM_xS_xJ, where A is the number of years, M is the number of months, S is the number of weeks, and J is the number of days. If any of these values are 0, they are not included in the name. If the file is older than the start date, the name is prefixed with "old_"


def get_picture_creation_date(file):
    try:
        image = Image.open(file)
        exif_data = image._getexif()
        
        # Iterate through the EXIF data and look for the DateTimeOriginal tag
        for tag, value in exif_data.items():
            tag_name = TAGS.get(tag, tag)
            if tag_name == 'DateTimeOriginal':
                return datetime.datetime.strptime(value, '%Y:%m:%d %H:%M:%S')

    except (AttributeError, KeyError, IndexError):
        # Handle cases where there is no EXIF data or no DateTimeOriginal tag
        print("no exif or no date found for " + file)
        pass

    print("no exif or no date found for " + file)
    # If no date is found, return None or handle accordingly
    return None


def get_video_creation_date(video):
    return datetime.datetime.fromtimestamp(os.path.getmtime(video))


def get_date_diff(date):
    if start_date > date:
        return -1, -1, -1, -1
    diff = date - start_date
    years = diff.days // 365
    remaining = diff.days % 365
    months = remaining // 30
    remaining = remaining % 30
    weeks = remaining // 7
    days = remaining % 7
    return years, months, weeks, days


def get_name(date):
    years, months, weeks, days = get_date_diff(date)
    name = ""
    # months = months % 12
    # weeks = weeks % 4
    # days = days % 7
    #if years > 0:
    if sum([years, months, weeks, days]) >= 0:
        name += str(years) + "A"
        name += str(months) + "M"
        name += str(weeks) + "S"
        name += str(days) + "J"
        # add a _ between each value
        name = name.replace("A", "_A_")
        name = name.replace("M", "_M_")
        name = name.replace("S", "_S_")
        name = name.replace("J", "_J_")
    else:
        name = "AVANT_"
    # remove the first char if _
    if name[0] == "_":
        name = name[1:]
    # remove the last char if _
    if name[-1] == "_":
        name = name[:-1]
    return name


def get_new_name(file):
    if file.endswith(".mp4") or file.endswith(".mov") or file.endswith(".avi") or file.endswith(".mkv"):
        date = get_video_creation_date(file)
    else:
        date = get_picture_creation_date(file)
    name = get_name(date)
    if name == "":
        name = "0J"
    return name + "-" + os.path.splitext(os.path.basename(file))[0]


def copy_file(file):
    # keep the relative path of the file in the input folder (without its name) and add it to the output folder
    relative_path = os.path.relpath(os.path.dirname(file), input_folder)
    new_path = os.path.join(output, relative_path)
    os.makedirs(new_path, exist_ok=True)
    # copy the file
    new_name = get_new_name(file)
    new_file = os.path.join(new_path, new_name + os.path.splitext(file)[1])
    
    new_file_2 = os.path.join(output, os.path.basename(new_file))
    shutil.copyfile(file, new_file)
    shutil.copyfile(new_file, new_file_2)
    print("copied " + file + " to " + new_file)


for root, dirs, files in os.walk(input_folder):
    # print dir name, if should_sort is true, only loop through the files if it contains keyword
    if should_sort:
        if os.path.basename(root).startswith(keyword):
            for file in files:
                copy_file(os.path.join(root, file))

print("done")
# log the date and time in current folder on a new line in the format yyyy-mm-dd hh:mm:ss in the current folder
with open("log.txt", "a") as file:
    file.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n")