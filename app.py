import helium as he
import time
from requests_html import HTMLSession
import pandas as pd
import sqlite3


base = 'https://www.monster.com/job-openings/'
JOB_TITLE = 'data scientist'


def format_position(position):
    return position.replace(' ', '+')


def get_links(position):
    he.start_chrome(
        f"https://www.monster.com/jobs/search?q={position}&where=&page=1&so=m.h.sh", headless=True)
    scroll = 0
    links = []
    while scroll < 8 and len(links) < 20:
        time.sleep(1)
        he.scroll_down(900)
        href = he.find_all(he.S("div>a"))
        [links.append(l.web_element.get_attribute('href'))
         for l in href if base in l.web_element.get_attribute('href')]
        scroll += 1
        if scroll == 7:
            he.click('Load more')
            scroll = 5
    return links


def extract_job_info(links):
    jobs = {}

    for i, link in enumerate(links):
        s = HTMLSession()
        r = s.get(link)
        jobs.update({i: {'job_title': [l.text for l in r.html.find('h1')][0],
                         'company': [l.text for l in r.html.find('h2')][0],
                         'location': [l.text for l in r.html.find('h3')][0],
                         'posted': [l.text for l in r.html.find('[data-test-id="svx-jobview-posted"]')][0],
                         'job_description': [l.text for l in r.html.find('[class="descriptionstyles__DescriptionContainer-sc-13ve12b-0 bOxUQy"]')][0],
                         'link': link
                         }}
                    )
    return jobs


def write_db(name):
    conn = sqlite3.connect(name)
    cur = conn.cursor()
    df.to_sql(name=name, con=conn, if_exists='replace')


if __name__ == '__main__':
    POSITION = format_position(JOB_TITLE)
    links = get_links(POSITION)
    data = extract_job_info(links)
    df = pd.DataFrame(data).T
    write_db('monster.db')
