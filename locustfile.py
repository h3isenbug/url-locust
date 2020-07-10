from locust import HttpUser, SequentialTaskSet, between, task
import random
import string

short_urls = []


def random_string(length):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))


class UserAuthenticate(SequentialTaskSet):
    @task
    def on_start(self):
        username = random_string(10)
        password = random_string(10)
        email = random_string(10) + '@gmail.com'

        resp = self.client.post('/register',
                                json={'username': username, 'email': email, 'password': password})
        resp = self.client.post('/login',
                                json={'identifier': email, 'password': password}).json()
        self.token = resp['data']['token']


class GuestUser(HttpUser):
    wait_time = between(0, 0)

    @task(1)
    class CreateShortURL(UserAuthenticate):
        @task
        def create_url(self):
            global short_urls
            short_url = random_string(10)
            resp = self.client.post('/panel/urls',
                                    json={'longURL': random_string(40), 'shortPath': short_url}, headers={'AuthToken': self.token})
            if resp.status_code != 200:
                print(resp.text)
                exit()
            short_urls.append(short_url)

    @task(2)
    class GetAnalytics(UserAuthenticate):
        @task
        def get_analytics(self):
            global short_urls
            if len(short_urls) == 0:
                return
            self.client.get('/panel/analytics/' +
                            random.choice(short_urls), headers={'AuthToken': self.token})

    @task(17)
    def get_long_url(self):
        global short_urls
        if len(short_urls) == 0:
            return
        self.client.get('/r/'+random.choice(short_urls), allow_redirects=False)
