import json
import os
import requests
import time

def find_target_text(text):
    return (
                (text.find("<a href=") > 0 and text.find('<a href="javascript:void(0)') == -1) 
                and 
                (
                    (text.find('<div class="RowLink">') > 0 and text.find('Cancelled') == -1) or 
                    text.find('>Minutes</a>') > 0
                )
            )

def drop_empty_href_and_corresponding_name(file_name_and_file_path_set):

    new_file_name_and_file_path_set = []
    file_name_and_file_path = []
    for index, text in enumerate(file_name_and_file_path_set):
        if index%2 == 0:
            file_name_and_file_path.append(text)
        else:
            if text.find("href=''")>0:
                file_name_and_file_path = []
            else:
                file_name_and_file_path.append(text)
                new_file_name_and_file_path_set.append(file_name_and_file_path)
                file_name_and_file_path = []
    return new_file_name_and_file_path_set

def remove_cntl_char(meeting_name):
    for chars in [(":&#09;", ""), ("&#13;", ""), ("MBoard", "M "), ("Type", " ")]:
        meeting_name = meeting_name.replace(chars[0], chars[1])
        
    return meeting_name

def get_meeting_name(meeting_html):
    start_index = meeting_html.find('title="')+len('title="')
    end_index = meeting_html.find('Status')
    meeting_name = remove_cntl_char(meeting_html[start_index:end_index])
    return meeting_name

def get_file_path(meeting_html):

    start_index = meeting_html.find("href='") + len("href='")
    end_index = meeting_html.find("' class=")
    return meeting_html[start_index:end_index]

def download_pdf_and_save(url, save_name, failed_url_and_file_name):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(save_name, "wb") as w:
                w.write(response.content)
            return failed_url_and_file_name
    except:
        print("Fail to download {url} at {save_name}")
        failed_url_and_file_name.append([url, save_name])
        return failed_url_and_file_name

def get_pdf_directory_path(store_file_path):

    if os.path.isdir(store_file_path):
        return store_file_path
    else:
        os.mkdir(store_file_path)
        return store_file_path

def get_downloaded_paths(store_file_path):

    file_path_list = []
    for root, dirs, files in os.walk(store_file_path, topdown=False):
        for name in files:
            file_path_list.append(os.path.join(root, name))
    return file_path_list

def main():

    pre_file_path = f"http://cambridgema.iqm2.com/Citizens/"
    store_file_path = get_pdf_directory_path(f"{os.getcwd()}/pdf/")

    with open("page", "r") as r:
        text_line  = r.readlines()
        file_name_and_file_path_set = [text for text in text_line if find_target_text(text)]

    trim_file_name_and_file_path_set = drop_empty_href_and_corresponding_name(file_name_and_file_path_set)
    file_path_list = get_downloaded_paths(store_file_path)
    failed_url_and_file_name = []

    for file_name_and_file_path in trim_file_name_and_file_path_set:
        time.sleep(10)
        meeting_name = get_meeting_name(file_name_and_file_path[0])
        file_path = get_file_path(file_name_and_file_path[1])
        abs_file_url = f"{pre_file_path}{file_path}"
        abs_file_name = f"{store_file_path}{meeting_name}.pdf"
        if not abs_file_name in file_path_list:
            print(f"download and save {abs_file_name}")
            failed_url_and_file_name = download_pdf_and_save(abs_file_url, abs_file_name, failed_url_and_file_name)

    with open(f'{pre_file_path}failed_list', "w") as w:
        w.write(json.loads(failed_url_and_file_name))

if __name__ == '__main__':
    main()
