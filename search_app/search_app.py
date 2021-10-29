# python libraries

import subprocess
import sys

# installing required packages to run this cde
packages = ['pip>=21.2.4', 'flask>=2.0.1', 'bs4', 'requests>=2.25.1', ]
for package in packages:
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# import necessary library

from flask import Flask, render_template, request, redirect, session
from datetime import timedelta
from bs4 import BeautifulSoup
from requests import get

# empty list to save search results
search_results = []


# Modified code ~ (SOURCE: https://github.com/Nv7-GitHub/googlesearch)
def search(term, num_results=10, lang="en", proxy=None):
    usr_agent = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (HTML, like Gecko) '
                      'Chrome/61.0.3163.100 Safari/537.36'}

    def fetch_results(search_term, number_results, language_code):

        google_url = 'https://www.google.com/search?q={}&num={}&hl={}'.format(search_term, number_results + 1,
                                                                              language_code)
        proxies = None
        if proxy:
            if proxy[:5] == "https":
                proxies = {"https": proxy}
            else:
                proxies = {"http": proxy}

        response = get(google_url, headers=usr_agent, proxies=proxies)
        response.raise_for_status()

        return response.text

    def parse_results(raw_html):
        soup = BeautifulSoup(raw_html, 'html.parser')
        result_block = soup.find_all('div', attrs={'class': 'g'})
        search_results.append("<br>{ </br>")
        for result in result_block:
            link = result.find('a', href=True)
            title = result.find('h3')
            if link and title:
                search_results.append("<br>" + "<span" + " " + "style" + "=" + '"padding-left:30px"' + ">" + "{" +
                           '"' + str(
                    title.get_text()) + '"' + " : " + "<a" + " " + "target =" + '"_blank"' + " " + "href=" + '"' + link[
                               'href'] + '"' + ">" + '"'
                           + str(link['href']) + '"' + "</a>" + "}" + "</br>" + "</span>")
        search_results.append("<br>}</br>")

        return search_results

    html = fetch_results(term, num_results, lang)
    return parse_results(html)


# App config
app = Flask(__name__, template_folder='../search_app/')
app.secret_key = "Bosch@@2021"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=120)

# creation of user
user = {"username": "Bosch", "password": "Bosch_2021"}


# home page with route host/
@app.route('/', methods=['GET'])
def home():
    return render_template('login_button.html')


# login page with route host/login
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == user['username'] and password == user['password']:
            session['user'] = username
            session.permanent = True
            app.permanent_session_lifetime = timedelta(seconds=120)

            return redirect('/bosch_search_engine')

        return render_template('wrong_user.html')

    return render_template('login_page.html')


# search_engine page with route host/bosch_search_engine
@app.route('/bosch_search_engine')
def dashboard():
    if 'user' in session and session['user'] == user['username']:
        return render_template('search.html')

    return render_template('Not_login.html')


# empty list to save user query
res = []


# search result page with route host/result
@app.route('/result', methods=['GET', 'POST'])
def result():
    res.append(request.args.get('q'))
    text = res[0]
    html = open('../search_app/result.html', 'r', errors='ignore').read()

    file = BeautifulSoup(html, 'html.parser')
    search(text)

    search_results_tags = ",".join(search_results).replace(',', '')
    file.p.clear()

    file.p.append(BeautifulSoup(search_results_tags, 'html.parser'))

    open('../search_app/result.html', 'w', encoding='utf-8', errors='ignore').write(str(file))
    res.clear()
    search_results.clear()

    if 'user' in session and session['user'] == user['username']:
        return render_template('result.html', errors='ignore')

    return render_template('Not_login.html', )


# Logout process
@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/')


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
