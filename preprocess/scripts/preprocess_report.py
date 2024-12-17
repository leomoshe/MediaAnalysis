import os
import sys
import logging
import argparse
common_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'common'))
sys.path.append(common_path)
import tools

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(filename=os.path.basename(__file__).replace('py', 'log'), mode='w', encoding='utf-8')
console_handler = logging.StreamHandler()
logger.addHandler(file_handler)
logger.addHandler(console_handler)

import csv
 
postfix_len = len("_XXXXXXXX_XXXXXX.tsrt.csv")

class ReportItem:
    def __init__(self, media_path, not_in_srt_report, language, srt_path, ent_path, dst_tsrt):
        self.media_path = media_path
        self.not_in_srt_report = not_in_srt_report
        self.language = language
        self.srt_path = srt_path
        self.ent_path = ent_path
        self.dst_tsrt = dst_tsrt


def basefilename(fullpath):
    return os.path.splitext(os.path.basename(fullpath))[0]


def safe_prop(item, prop_name):
    return item[prop_name] if item else ''


def items2cells(items):
    for item in items:
        yield f"""<tr>
        <td>{os.path.basename(item.media_path)}</td>
        <td>{item.not_in_srt_report}</td>
        <td>{item.language}</td>
        <td>{os.path.basename(item.srt_path)}</td>
        <td>{os.path.basename(item.ent_path)}</td>
        <td>{os.path.basename(item.dst_tsrt)}</td>
        </tr>
        """


if __name__ == "__main__":
    logger.info("Program running")
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--project')
    parser.add_argument('-s', '--source')
    parser.add_argument('-l', '--local_container')
    parser.add_argument('-d', '--destination')


    config = tools.Configuration("preprocess.json", parser)
    report_srt_path = os.path.join(config['local_container'], config['project'], "report_srt.csv")
    report_entities_path = os.path.join(config['local_container'], config['project'], "report_entities.csv")
    logger.info(config)

    report_srt = list(csv.DictReader(open(report_srt_path, 'r', encoding='utf-8'), delimiter='#'))
    report_ent = list(csv.DictReader(open(report_entities_path, 'r', encoding='utf-8'), delimiter='#'))

    arg_path = os.path.normpath(os.path.join(config['source'],config['project']))
    media_filespath = [os.path.join(arg_path, filename) for filename in os.listdir(arg_path) if os.path.isfile(os.path.join(arg_path, filename))]
    dst_folder = os.path.join(config['destination'], config['project'])
    tsrt_filespath = [os.path.join(dst_folder, filename) for filename in os.listdir(dst_folder) if os.path.isfile(os.path.join(dst_folder, filename))]
    #srt_filespath = [os.path.join(arg_path, filename) for filename in os.listdir(arg_path) if os.path.isfile(os.path.join(arg_path, filename))]
    
    '''
    media_filespath_set = set(media_filespath)
    
    report_srt_in_filespath = []
    report_srt_not_in_filespath = []
    report_srt_with_comments = []
    report_srt_file_set = set()

    for srt_item in report_srt:
        if srt_item['Fullpath'] in media_filespath_set:
            report_srt_in_filespath.append(srt_item)
        else:
            report_srt_not_in_filespath.append(srt_item)
        if srt_item['Comment']:
            report_srt_with_comments.append(srt_item)
        report_srt_file_set.add(srt_item['Fullpath'])

    files_not_in_report_srt = media_filespath_set - report_srt_file_set
    '''
    html_items = []
    for filepath in media_filespath:
        filename = basefilename(filepath)
        srt_item = next((item for item in report_srt if basefilename(item['Fullpath']) == filename), None)
        not_in_srt_report = '' if srt_item is not None else '!' 
        ent_item = next((item for item in report_ent if basefilename(item['SrtPath']) == filename), None)
        dst_tsrt = next((item for item in tsrt_filespath if os.path.basename(item)[:-postfix_len] == filename), None)
        report_item = ReportItem(filepath, not_in_srt_report, safe_prop(srt_item, "Language"), safe_prop(ent_item, 'SrtPath'), safe_prop(ent_item, 'EntPath'), dst_tsrt if dst_tsrt else '')
        html_items.append(report_item)
    
    table_items = "\n".join(items2cells(html_items))
    srt_path = os.path.dirname(html_items[0].srt_path) if len(html_items) > 0 else ''
    ent_path = os.path.dirname(html_items[0].ent_path) if len(html_items) > 0 else ''

    table_template_ = f"""<table>
        <tr>
            <th>media_path({arg_path})</th>
                <th>not in srt report</th>
            <th>language</th>
            <th>srt_path({srt_path})</th>
            <th>ent_path({ent_path})</th>
        </tr>
        {table_items}
    </table>
    """
    table_template = f"""<table>
        <tr>
            <th>media in Source</th>
            <th>not in srt report</th>
            <th>language</th>
            <th>srt in Local</th>
            <th>ent in Local</th>
            <th>tsrt in Destination</th>
        </tr>
        {table_items}
    </table>
    """

    table_style = """
    table {
        font-family: arial, sans-serif;
        border-colapse: collapse;
        width: 100%;
    }

    td, th {
        border: 1px solid #dddddd;
        text-align: left;
        padding: 8px;
    }

    tr:nth-child(even) {
        background-color: #dddddd;
    }
    """
    html_template = f"""<html>
    <head>
    <title>preprocess_report</title>
    <style>{table_style}</style>
    </head>
    <body>
    <p>Project: {config['project']}</p>
    <p>Source: {config['source']}</p>
    <p>Local: {config['local_container']}</p>
    <p>Destination: {config['destination']}</p>
    {table_template}
    </body>
    </html>
    """


    with open("preprocess_report.html", 'w') as f:
        f.write(html_template)
    #f = open("preprocess_report.html", 'w')
    #f.write("html_template")
    next