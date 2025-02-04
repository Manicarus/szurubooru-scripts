# szurubooru-scripts
Simplify your file uploads and automatically tag your posts.

## Requirements

A python3 release and the required modules. Install those with:

`python3 -m pip install requirements.txt`

## Scripts

### upload_images
This script searches through your specified upload folder in the config file for any image/video files and uploads them to your booru.
After the upload has been completed, the script attempts to delete empty directories under your upload directory.

#### Usage
After editing the config file, we can just execute the script:

`python3 upload_images.py`

### auto_tagger
This script accepts a szurubooru query as a user input, fetches all posts returned by it and attempts to tag it.
In your config you can specify your preferred booru and fallback booru where tags should be fetched from.
If your image was found on neither of those choices, the script attempts to fallback to the best match returned by IQDB.

By default the script searches Danbooru first, Sankaku after that and falls back to the best match.

If no matches from IQDB were found, the script keeps the previously set tags of the post and additionally appends the tag `tagme`.

#### Usage
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

We can generate our API token with following command:
`echo -n username:token | base64`

## ToDo's
* Handle user input better
* Better error handling, especially with said user input
* Add a reverse image search for Sankaku
* Probably a lot of refactoring
* JSON > INI config file
* Use SauceNAO instead of IQDB
