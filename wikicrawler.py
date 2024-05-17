import json
import time
import requests
from bs4 import BeautifulSoup
from collections import deque

def find_shortest_route(start_page, end_page):
    '''
    Breadth-first search approach for finding the shortest path between two QBWiki pages.
    '''
    routes = {}
    routes[start_page] = [start_page]
    queue = deque([start_page])

    while len(queue) != 0:
        current_page = queue.popleft()
        page_links = extract_links(current_page)

        for link in page_links:
            if link == end_page:
                return routes[current_page] + [link]
            if (link not in routes) and (link != current_page):
                routes[link] = routes[current_page] + [link]
                queue.append(link)
    return None

def extract_links(page_url):
    '''
    Retrieves distinct links in a QBWiki page.
    '''
    response = requests.get(page_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    base_url = page_url[:page_url.find('/wiki/')]
    page_links = list({base_url + anchor['href'] for anchor in soup.select('p a[href]') if anchor['href'].startswith('/wiki/')})
    return page_links

def validate_pages(start_page, end_page):
    '''
    Checks that "start" and "end" are valid QBWiki pages.
    '''
    for page in [start_page, end_page]:
        try:
            requests.get(page)
        except:
            print(f'{page} does not appear to be a valid QBWiki page.')
            return False

    if len(extract_links(start_page)) == 0:
        print('Start page is a dead-end page with no QBWiki links.')
        return False

    end_soup = BeautifulSoup(requests.get(end_page).content, 'html.parser')
    if end_soup.find('div', {'id': 'orphaned'}):
        print('End page is an orphan page with no QBWiki pages linking to it.')
        return False
    return True

def resolve_redirect(end_page):
    '''
    Returns the URL that the end page points to (helpful for end pages with redirected URL).
    '''
    response = requests.get(end_page)
    soup = BeautifulSoup(response.content, 'html.parser')
    redirect_tag = soup.find('link', {'rel': 'canonical'})
    if redirect_tag:
        return redirect_tag['href']
    return end_page

def format_result(start_page, end_page, path):
    '''
    Returns JSON object of shortest path result.
    '''
    if path:
        result_path = path
    else:
        result_path = "No path found!"
    result_dict = {"start": start_page, "end": end_page, "path": result_path}
    return json.dumps(result_dict, indent=4)

def main():
    '''
    Prompts the user for the start and end URLs and executes the WikiRacer.
    '''
    start_page = input("Enter the start URL (QBWiki page): ")
    end_page = input("Enter the end URL (QBWiki page): ")

    if validate_pages(start_page, end_page):
        shortest_path = find_shortest_route(start_page, resolve_redirect(end_page))
        json_result = format_result(start_page, end_page, shortest_path)
        print(json_result)
    else:
        print("Invalid start or end URL. Please check the URLs and try again.")

if __name__ == '__main__':
    start_time = time.time()
    main()
    end_time = time.time()
    total_time = end_time - start_time
    print(f'Time: {int(total_time)/60}m {total_time%60:.3f}s')
