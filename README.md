# szurubooru-scripts
Simplify your file uploads and automatically tag your posts.

## Installation

Under virtual environment:

`python -m pip install <szurubooru-script-directory>` 

If you want to install szuru-toolkit editable mode(developer mode):

`python -m pip install -e <szurubooru-script-directory>` 

In order to undo the installation:

`python -m pip uninstall szuru-toolkit`

## image_uploader
This script searches through your specified upload folder in the config file for any image/video files and uploads them to your booru.
After the upload has been completed, the script attempts to delete empty directories under your upload directory.

### Usage

We can just call the executable:

`szuru-upload`

It will be terminated with some errors stating that it needs a configuration file in a certain location.
You can copy and paste the given config.ini to the specified path.

In short, if you have created virtual environment using venv, it will be:

`<venv-directory>/config/szuru-toolkit/config.ini`

If you are not using venv, it will be system's default configuration folder.

## auto_tagger

NOTICE: Executable is under development

This script accepts a szurubooru query as a user input, fetches all posts returned by it and attempts to tag it.
In your config you can specify your preferred booru and fallback booru where tags should be fetched from.
If your image was found on neither of those choices, the script attempts to fallback to the best match returned by IQDB.

By default the script searches Danbooru first, Sankaku after that and falls back to the best match.

If no matches from IQDB were found, the script keeps the previously set tags of the post and additionally appends the tag `tagme`.

### Usage
After editing the config file, we can just execute the script with our query:

* `python3 auto_tagger.py 'date:today tag-count:0'`
* `python3 auto_tagger.py 'date:2021-04-07'`
* `python3 auto_tagger.py 'tagme'`
* `python3 auto_tagger.py 'id:100,101'`

If we want to tag a single post, we can omit the keyword `id` in our query:

* `python3 auto_tagger.py 100`

Alternatively, we can tag a single post and specify `--sankaku_url` to fetch the tags from the supplied URL:

`python3 auto_tagger.py --sankaku_url https://chan.sankakucomplex.com/post/show/<id> 100`

This is especially useful since IQDB hasn't updated their Sankaku database in over three years+ now.

## User configuration
The config file accepts following input:
```INI
[szurubooru]
address   = https://szuru.example.com
api_token = my_api_token
offline   = True

[options]
upload_dir      = /local/path/to/upload/dir
preferred_booru = danbooru
fallback_booru  = sankaku
tags            = tagme,tag1,tag2,tag3
```
Input should be formatted like the provided example, meaning:
* No quotes around strings
* Separate tags by comma with no whitespaces

You'll probably want to create another Token for szurubooru account since Web Login Token changes everytime you login.
Please be aware that the Token that is created within the web interface cannot be used for `config.ini`.
The actual API Token must be generated with the following command:
`echo -n <username>:<token> | base64`

## ToDo's
* Handle user input better
* Better error handling, especially with said user input
* Add a reverse image search for Sankaku
* Probably a lot of refactoring
* JSON > INI config file
* Use SauceNAO instead of IQDB
* szuru-upload executable
  - parse arguments for safe/unsafe flag 
  - parse arguments for specifying source file/directory for uploading images
  - make it not refer configuration file for uploading images
