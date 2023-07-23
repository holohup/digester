from bs4 import BeautifulSoup
import httpx

client = httpx.Client()
result = client.get('https://www.ixbt.com/news/?show=tape').text

soup = BeautifulSoup(result, 'html.parser')

parts = soup.find_all('div', class_='item')
entities = []
print(parts)
for part in parts:
    # Extract link to the news page
    link_element = part.find('h2', class_='no-margin').find('a')
    news_link = link_element['href']

    # Extract number of comments if available, otherwise set to 0
    try:
        comments_element = part.find('a', class_='comments_link')
        num_comments = int(comments_element.find('span', class_='b-num').text)
    except AttributeError:
        num_comments = 0

    # Extract tags
    tags_element = part.find('p', class_='b-article__tags__list')
    tags = [tag.text for tag in tags_element.find_all('a')]

    # Create a dictionary to represent the entity
    entity = {
        'link': news_link,
        'num_comments': num_comments,
        'tags': tags
    }

    # Add the entity to the list
    entities.append(entity)

# Print all entities
for idx, entity in enumerate(entities, 1):
    print(f"Entity {idx}:")
    print("Link to the news page:", entity['link'])
    print("Number of comments:", entity['num_comments'])
    print("Tags:", entity['tags'])
    print()