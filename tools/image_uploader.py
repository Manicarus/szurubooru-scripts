import os
import json
import shutil
import requests
import argparse
import dryable
import pprint
from glob import glob
from tqdm import tqdm
from classes.user_input import UserInput
from classes.api import API
from classes.post import Post

def get_files(upload_dir):
    """
    Reads recursively images/videos from upload_dir.

    Args:
        upload_dir: The directory on the local system which contains the images/videos you want to upload

    Returns:
        files: A list which contains the full path of each found images/videos (includes subdirectories)
    """

    allowed_extensions = ['jpg', 'jpeg', 'png', 'mp4', 'webm', 'gif', 'swf']
    files_raw          = list(filter(None, [glob(upload_dir + '/**/*.' + extension, recursive = True) for extension in allowed_extensions]))
    files              = [y for x in files_raw for y in x]

    return files

def get_image_token(api, image):
    """
    Upload the image to the temporary uploads endpoint.
    We can access our temporary image with the image token.

    Args:
        image: The file object of the image
        file: The path to the file

    Returns:
        image_token: An image token from szurubooru

    Raises:
        Exception
    """

    post_url = api.booru_api_url + '/uploads'

    try:
        response    = requests.post(post_url, files={'content': image}, headers=api.headers)

        if 'description' in response.json():
            raise Exception(response.json()['description'])
        else:
            image_token = response.json()['token']
            return image_token
    except Exception as e:
        print()
        print(f'An error occured while getting the image token: {e}')

def check_similarity(api, image_token):
    """
    Do a reverse image search with the temporary uploaded image.

    Args:
        image_token: An image token from szurubooru

    Returns:
        exact_post: Includes meta data of the post if an exact match was found
        similar_posts: Includes a list with all similar posts

    Raises:
        Exception
    """

    post_url = api.booru_api_url + '/posts/reverse-search'
    metadata = json.dumps({'contentToken': image_token})

    try:
        response = requests.post(post_url, headers=api.headers, data=metadata)

        if 'description' in response.json():
            raise Exception(response.json()['description'])
        else:
            exact_post = response.json()['exactPost']
            similar_posts = response.json()['similarPosts']
            return exact_post, similar_posts
    except Exception as e:
        print()
        print(f'An error occured during the similarity check: {e}')

@dryable.Dryable(True)
def upload_file(api, post, file_path):
    """
    Uploads/Moves our temporary image to 'production' with similar posts if any were found.
    Deletes file after upload has been completed.

    Args:
        image_token: An image token from szurubooru
        similar_posts: Includes a list with all similar posts

    Raises:
        Exception
    """

    success = False
    post_url = api.booru_api_url + '/posts'
    metadata = json.dumps({'tags': post.tags, 'safety': post.rating, 'relations': post.similar_posts, 'contentToken': post.image_token})

    try:
        response = requests.post(post_url, headers=api.headers, data=metadata)

        if 'description' in response.json():
            raise Exception(response.json()['description'])

        success = True
    except Exception as e:
        print()
        print(f'An error occured during the upload: {e}')

    return success

@dryable.Dryable()
def cleanup_dirs(dir):
    """
    Remove empty directories recursively from bottom to top

    Args:
        dir: The directory under which to cleanup - dir is the root level and won't get deleted.

    Raises:
        OSError
    """

    for root, dirs, files in os.walk(dir, topdown=False):
        for name in files:
            # Remove Thumbs.db file created by Windows
            if name == 'Thumbs.db': os.remove(os.path.join(root, name))
        for name in dirs:
            # Remove @eaDir directory created on Synology systems
            if name == '@eaDir': shutil.rmtree(os.path.join(root, name))
            try:
                os.rmdir(os.path.join(root, name))
            except OSError:
                pass

@dryable.Dryable()
def delete_posts(api, start_id, finish_id):
    """
    If some posts unwanted posts were uploaded, you can delete those within the range of start_id to finish_id.

    Args:
        start_id: Start deleting from this post id
        finish_id: Stop deleting until this post id

    Raises:
        Exception
    """

    for id in range(start_id, finish_id + 1):
        post_url = api.booru_api_url + '/post/' + str(id)
        try:
            response = requests.delete(post_url, headers=api.headers, data=json.dumps({'version': '1'}))
            if 'description' in response.json():
                raise Exception(response.json()['description'])
        except Exception as e:
            print(f'An error occured while deleting posts: {e}')

def main():
    """
    Main logic of the script.
    """

    post       = Post()
    user_input = UserInput()
    user_input.parse_config()
    user_input.parse_input()
    api        = API(
        booru_address   = user_input.booru_address,
        booru_api_token = user_input.booru_api_token,
        booru_offline   = user_input.booru_offline,
    )

    user_input.describe()

    files_to_upload = []
    for source in user_input.source:
        files_to_upload.extend(get_files(source))

    print()
    print('Uploading :')
    pprint.PrettyPrinter().pprint(files_to_upload)

    if files_to_upload:
        print()
        print('Found ' + str(len(files_to_upload)) + ' images. Starting upload...')

        for file_to_upload in tqdm(files_to_upload, ncols=80, position=0, leave=False):
            upload_success = False

            with open(file_to_upload, 'rb') as f:
                post.image = f.read()

            post.image_token = get_image_token(api, post.image)
            post.exact_post, similar_posts = check_similarity(api, post.image_token)

            if not post.exact_post:
                post.tags = user_input.tags
                post.rating = user_input.rating
                post.similar_posts = []
                for entry in similar_posts:
                    post.similar_posts.append(entry['post']['id'])
                upload_success = upload_file(api, post, file_to_upload)
            else:
                upload_success = True

            if upload_success:
                if user_input.remove:
                    cleanup_file(file_to_upload)
            else:
                failsafe_handling(file_to_upload, user_input.failsafe_path)

        print()
        print('Script has finished uploading.')
    else:
        print('No images found to upload.')

@dryable.Dryable()
def failsafe_handling(file_to_upload, failsafe_path):
    '''
    hard link, if possible, otherwise copy the failed-to-upload file to the failsafe directory
    '''
    source = file_to_upload
    filename = os.path.basename(source)
    dest = os.path.join(failsafe_path, filename)

    # safety check for failsafe directory
    os.makedirs(failsafe_path, exist_ok=True)

    try:
        os.link(source, dest)

    except Exception as e:
        print(f'\nAn error occured while creating hard link: {e}')
        print('Falling back to copy operation')
        shutil.copyfile(source, dest)

@dryable.Dryable()
def cleanup_file(file):
    """
    Remove file. Wrapped with dryable decorator.

    Args:
        file: The single file targeted for deletion
    """

    os.remove(file)




if __name__ == '__main__':
    main()
