import datetime
import json
import os
import re
import ndjson
from haralyzer import HarParser, HarPage
from langdetect import detect
from pycountry import languages
from PIL import Image
import pytesseract
from werkzeug.utils import secure_filename
from bs4 import BeautifulSoup
import requests
from text_extractor import Pages

DIR_PATH = os.getcwd()
pytesseract.pytesseract.tesseract_cmd = os.getenv('TESSERACT')


def Convert_extract_upload(har_txt, settings, image_obj):
    final = []
    har_parser = HarParser(har_txt)
    for page in har_parser.pages:
        if isinstance(page, HarPage):
            entries = page.filter_entries(content_type='text/html', status_code='2.*')
            for entry in entries:
                if "text" in entry['response']['content']:
                    if "sponsored_data" in entry['response']['content']['text']:
                        try:
                            data = ndjson.loads(entry['response']['content']['text'])
                        except:
                            continue
                        for node in data:
                            node_data = node['data']
                            if (node_data.get('category') == "SPONSORED" and 'node' in node_data.keys()):
                                raw_node = node_data.get('node')
                                if raw_node.get('sponsored_data'):
                                    data = raw_node
                                    dicts = {}
                                    result = {}
                                    total_likes = 0
                                    result['ad_id'] = data['sponsored_data']['ad_id']
                                    result['post_type'] = data['__typename']
                                    result['date'] = datetime.datetime.now()
                                    result['post_image'] = extract_image(data)
                                    for actor in data['comet_sections']['content']['story']['actors']:
                                        result['post_id'] = data['post_id']
                                        result['page_name'] = actor['name']
                                        result['page_url'] = actor['url']
                                        result['page_id'] = actor['id']
                                        result['settings'] = merge_dicts_(actor['name'].replace('.', ''), image_obj)
                                        result['category'] = extract_category(data)

                                    result["post_link"] = data['comet_sections']['content']['story']['wwwURL']
                                    filters = data['comet_sections']['feedback']['story']['feedback_context'][
                                        'feedback_target_with_context'][
                                        'ufi_renderer']['feedback']
                                    if 'comet_ufi_summary_and_actions_renderer' in filters:
                                        likes = filters['comet_ufi_summary_and_actions_renderer']['feedback'][
                                            'cannot_see_top_custom_reactions']['top_reactions']['edges']
                                    else:
                                        likes = None
                                    if 'comet_ufi_summary_and_actions_renderer' in filters:
                                        result['total_share'] = \
                                            filters['comet_ufi_summary_and_actions_renderer']['feedback'][
                                                'share_count'][
                                                'count']
                                    else:
                                        result['total_share'] = 0
                                    if "comments_count_summary_renderer" in filters:
                                        result['total_comment'] = \
                                            filters['comments_count_summary_renderer']['feedback']['comment_count'][
                                                'total_count']
                                    else:
                                        result['total_comment'] = 0
                                    if likes:
                                        for like in likes:
                                            total_likes += like['reaction_count']
                                            dicts.update({like['node']['localized_name']: like['reaction_count']})
                                        result['reactions'] = dicts
                                        result['total_likes'] = total_likes
                                    else:
                                        result['reactions'] = {}
                                        result['total_likes'] = 0
                                    if 'title_with_entities' in \
                                            data['comet_sections']['content']['story']['attachments'][0][
                                                'comet_footer_renderer']['attachment']:
                                        result['title'] = data['comet_sections']['content']['story']['attachments'][0][
                                            'comet_footer_renderer'][
                                            'attachment']['title_with_entities']['text']
                                    else:
                                        result['title'] = ''

                                    action_filter = data['comet_sections']['content']['story']['attachments'][0][
                                        'comet_footer_renderer']['attachment']
                                    result['call_to_action_button'] = extract_call_to_action_button(action_filter)
                                    item_list = data['comet_sections']['content']['story']['attachments'][0]['styles'][
                                        'attachment']
                                    if "media" in item_list:
                                        video_filter_check = item_list['media']
                                        if 'playable_url' in video_filter_check:
                                            result['video_mp4'] = video_filter_check['playable_url']
                                            if 'playable_url_quality_hd' in video_filter_check:
                                                result['video_HD'] = video_filter_check['playable_url_quality_hd']
                                        else:
                                            result['video_mp4'] = ''
                                            result['video_HD'] = ''
                                    else:
                                        result['video_mp4'] = ''
                                        result['video_HD'] = ''
                                    message = data['comet_sections']['content']['story']
                                    result['context'] = extract_context(message, data)
                                    result['lang'] = extract_lang(message, data)
                                    result['setting'] = {"Why Am I Seeming this ads?": settings}
                                    final.append(result)
    return final


def create_setting(har_txt):
    keywords = ['Communicated', "Set their age to", "A primary location in", "Similarities to their customers"]
    custom_list = []
    values = {}

    for i in har_txt['log']['entries']:
        for __ in i['response']:
            try:
                for ___ in i['response']['content']:
                    if "data" in i['response']['content']['text']:
                        data = json.loads(i['response']['content']['text'])
                        for item in data['data'].keys():
                            for _ in data['data'][item]:
                                if "location_name" in _:
                                    values.update({"location_name": _['location_name']})
                                if 'age_min' in _:
                                    values.update({"age_min": _['age_min']})
                                if 'age_max' in _:
                                    values.update({"age_max": _['age_max']})
                                if 'locales' in _:
                                    values.update({"locales": _['locales']})
            except:
                continue
    for i in har_txt['log']['entries']:
        for __ in i['response']:
            try:
                for _ in i['response']['content']:
                    if "translations" in i['response']['content']['text']:
                        data = json.loads(i['response']['content']['text'])
                        for i in data['translations'].keys():
                            for ikey in keywords:
                                if ikey in data['translations'][i]:
                                    if ikey == "Set their age to":
                                        if "{target age min}" in data['translations'][i]:
                                            custom_list.append(
                                                {"min_age": f"Set their age to {values['age_min']} and older"})
                                        if "{target age max}" in data['translations'][i]:
                                            custom_list.append(
                                                {"max_age": f"Set their age to {values['age_max']} and younger"})
                                        elif "{target age}" in data['translations'][i]:
                                            continue
                                    elif ikey == "A primary location in":
                                        if not values['location_name'] == "":
                                            custom_list.append(
                                                {"location": f"A primary location in {values['location_name']}"})

                                    elif ikey == "Similarities to their customers":
                                        if "Similarities to their customers" in data['translations'][i]:
                                            custom_list.append({"Similarities": "Similarities to their customers"})
                                    elif ikey == 'Communicated':
                                        length = len(values['locales'])
                                        if length > 1:
                                            custom_list.append({
                                                ikey: f"Communicated in {values['locales'][0]}, {values['locales'][1]}"})
                                        else:
                                            custom_list.append({ikey: f"Communicated in {values['locales']}"})
            except:
                continue
    return custom_list


# upload har file ads to database
def upload_to_database(items):
    from app import ads_collection
    result = []
    for item in items:
        if not ads_collection.count_documents({'ad_id': item['ad_id']}, limit=1):
            result.append(item)
    if len(result) > 0:
        ads_collection.insert_many(result)
    return True


def fetch_scrape_data(url, page_name):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    scripts = soup.findAll('script')
    data = {}
    for script in scripts:
        if page_name in script.text:
            replace_data = script.text.replace(
                'requireLazy(["TimeSliceImpl","ServerJS"],function(TimeSlice,ServerJS){var s=(new ServerJS());s.handle(',
                '')
            new_replace_data = replace_data.replace(
                ');requireLazy(["Run"],function(Run){Run.onAfterLoad(function(){s.cleanup(TimeSlice)})});});', '')
            json_obj = json.loads(new_replace_data)
            for index in range(len(json_obj['require'])):
                try:
                    if type(json_obj['require'][index][3][0]) == dict:
                        data = {
                            "link_url": json_obj['require'][index][3][0]['props']['adCard']['snapshot']['link_url'],
                            "images": json_obj['require'][index][3][0]['props']['adCard']['snapshot']['images'],
                            "videos": json_obj['require'][index][3][0]['props']['adCard']['snapshot']['videos'],
                            "button_type": json_obj['require'][index][3][0]['props']['adCard']['snapshot'][
                                'cta_type']
                        }
                except:
                    continue
    return data


def image_list(images, path):
    items_data = []
    for image_file in images:
        image = Image.open(path + str(image_file))
        sample_text = pytesseract.image_to_string(image, lang='chi_sim+kor')
        remove_special_char = re.sub(r'[^\w\s]', '', sample_text).strip()
        items = remove_special_char.split('\n')
        while "" in items:
            items.remove("")
        items_data.append(items)
    return items_data


def remove_files(images, path):
    for file in images:
        image = path + file
        os.remove(str(image))


def image_to_text_data():
    images = os.listdir("screenshots")
    path = str(os.getcwd())+'/screenshots/'
    try:
        items = image_list(images, path)
        pages_client = Pages(items)
        pages_client.parse_pages()
        data = pages_client.show_dict()
        remove_files(images, path)
        return data
    except Exception as e:
        print(str(e))


def merge_dicts_(page_name, image_data):
    for data in image_data:
        if page_name in image_data[data]['page_name'].replace(" ", ""):
            return image_data[data]


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower()


def save_image_to_dir(files):
    file_names = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_names.append(filename)
            file.save(os.path.join(str(os.getcwd())+'/screenshots/', filename))


def extract_image(data):
    for i in data['comet_sections']['content']['story']['attachments']:
        if "media" in i['styles']['attachment']:
            if 'large_share_image' in i['styles']['attachment']['media']:
                return i['styles']['attachment']['media']['large_share_image'][
                    'uri']
            if "card_image" in i['styles']['attachment']['media']:
                return i['styles']['attachment']['media']['card_image'][
                    'uri']
    return ""


def extract_category(data):
    if 'category_type' in data['comet_sections']['content']['story']['comet_sections'][
        'context_layout']['story']['comet_sections']['actor_photo']['story']['actors'][0]:
        return data['comet_sections']['content']['story']['comet_sections'][
            'context_layout'][
            'story']['comet_sections']['actor_photo']['story']['actors'][0][
            'category_type']
    return ''


def extract_context(message, data):
    try:
        if 'message' in message:
            if message['message'] is not None:
                return data['comet_sections']['content']['story']['message']['text']
        return ""
    except:
        return ""


def extract_lang(message, data):
    try:
        if 'message' in message:
            if message['message'] is not None:
                return languages.get(alpha_2=detect(data['comet_sections']['content']['story']['message']['text'])).name
        return ''
    except:
        return ''


def extract_call_to_action_button(action_filter):
    try:
        if 'call_to_action_renderer' in action_filter:
            if 'attachment' in action_filter['call_to_action_renderer']:
                return action_filter['call_to_action_renderer']['action_link']['title']
        return ''
    except:
        return ''

