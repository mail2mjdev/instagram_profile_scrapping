import requests
from json import JSONDecoder
import json
import os

#insta_profile settings
insta_profile_name = '' #enter the profile name
url = 'https://www.instagram.com/{}/'.format(insta_profile_name)
print(url)

sub_query = 'https://www.instagram.com/graphql/query'

#local config
log_dir = "logs/"
list_of_elems = []
page_info = {}
total_count = 0
account_id = ""
query_hash = ""

headers = {'Content-type': 'text/html; charset=utf-8', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}

r = requests.get(url = url, headers=headers) 

print(r)



def extract_json_objects(text, decoder=JSONDecoder()):
    """Find JSON objects in text, and yield the decoded JSON data

    Does not attempt to look for JSON arrays, text, or other JSON types outside
    of a parent JSON object.

    """
    pos = 0
    while True:
        match = text.find('{', pos)
        if match == -1:
            break
        try:
            result, index = decoder.raw_decode(text[match:])
            yield result
            pos = match + index
        except ValueError:
            pos = match + 1



for result in extract_json_objects(r.text):
    res = bool(result)
    if res and 'config' in result:

        f = open(log_dir+"first_data_extraction.txt","a", encoding="utf-8")
        f.write(str(result['entry_data']))
        f.close()
        
        # data info
        # ---------->
        # result['entry_data']['ProfilePage'][0]['graphql']['user'] -> id - gets id
        # result['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media'] -> count, pageinfo {has_next_page, end_cursor-key}, edges[]
        # result['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges'] -> has all timeline elems

        account_id = result['entry_data']['ProfilePage'][0]['graphql']['user']["id"]
        total_count = result['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['count']
        page_info = result['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['page_info']
        loop_over_elems = result['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges']

        for k in loop_over_elems:
            tempDict = { 'id': k['node']['id'], 'url': k['node']['display_url']}
            list_of_elems.append(tempDict)
    # else:
    #     f = open("objfile","a", encoding="utf-8")
    #     f.write("\n"+str(result))
    #     f.close()

def url_encode(string_val):
    temp_str = string_val.replace(":", "%3A")
    temp_str = temp_str.replace(",", "%2C")
    temp_str = temp_str.replace("=", "%3D")
    return temp_str

while page_info["has_next_page"]:
    #base_query_url = "https://www.instagram.com/graphql/query/"
    nested_json_payload = '{"id":'+account_id+',"first":12,"after":"'+page_info["end_cursor"]+'"}'
    base_query_url = sub_query +'/?query_hash=2c5d4d8b70cad329c4a6ebe3abb6eedd&variables='+ url_encode(nested_json_payload)

    r = requests.get(url = base_query_url)
    request_data_in_dict = r.json()

    # for logs
    # ---------->
    # print(str(data_dict["data"]["user"]))
    # fp = open(log_dir+"/json.txt", "w")
    # fp.write(str(r.json) + "\n")
    # fp.close()

    page_info = request_data_in_dict["data"]["user"]["edge_owner_to_timeline_media"]['page_info']
    loop_over_elems = request_data_in_dict["data"]['user']['edge_owner_to_timeline_media']["edges"]

    for k in loop_over_elems:
        tempDict = { 'id': k['node']['id'], 'url': k['node']['display_url']}
        list_of_elems.append(tempDict)


for elems in list_of_elems:

    r = requests.get(url = elems["url"])

    elem_name = elems["id"]
    if ".jpg" in elems["url"]:
        elem_name += ".jpg"
    elif ".mov" in elems["url"]:
        elem_name += ".mov"
    elif ".mp4" in elems["url"]:
        elem_name += ".mp4"
    else:
        elem_name += ".jpg"

    download_path = "download/{}/".format(insta_profile_name)
    try:
        os.makedirs(os.path.dirname(download_path))
    except Exception as e:
        print("Already Exist! folder : "+ insta_profile_name)
    
    download_path +=elem_name
    
    fp = open(download_path, 'wb')
    fp.write(r.content)
    fp.close()
