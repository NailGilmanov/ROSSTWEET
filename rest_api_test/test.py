from requests import get, post, delete

print(delete('http://localhost:5000/api/comments/3/9999').json())
# новости с id = 999 нет в базе

print(delete('http://localhost:5000/api/comments/3/24').json())
for i in range(1, 21):
    delete(f'http://localhost:5000/api/comments/3/{i}')