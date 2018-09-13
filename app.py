from flask import Flask, render_template, request, redirect, session
import config
import psycopg2
import random
import string


# Initalize app
app = Flask(__name__)

# app config
dev = config.Development
app.config.from_object(dev)

# connect to db
db = psycopg2.connect(dbname=dev.database, user=dev.user)
con = db.cursor()

def generate_random_string():
    random_string = ''.join(random.choice(string.ascii_letters + 
                            string.digits) for _ in range(32))
    return random_string


def generate_csrf_token():
    if 'csrf_token' not in session:
        session['csrf_token'] = generate_random_string()
    return session['csrf_token']

app.jinja_env.globals['csrf_token'] = generate_csrf_token

@app.route('/queries')
def get_queries():
    """Route to see all query result"""

    # How many films involve a "Crocodile" and a "Shark"?
    con.execute("""select count(*) from film where description like
                '%Crocodile%' and description like '%Shark%'""")
    test = con.fetchall()
    shark_count = test[0][0]

    # Find the names (first and last) of all the actors and costumers whose
    # first name is the same as the first name of the actor with ID 8. Do not
    # return the actor with ID 8 himself. Note that you cannot use the name of
    # the actor with ID 8 as a constant (only the ID).
    con.execute("""select first_name, last_name from actor where first_name in
    (select first_name from actor where actor_id = 8)
    union all
    select first_name, last_name from customer where first_name in
    (select first_name from actor where actor_id = 8)
    """)

    actor = con.fetchall()
    all_names = []
    for index in range(len(actor)):
        first_name, last_name = actor[index]
        all_names.append('{} {}'.format(first_name, last_name))

    # Find all the film categories in which there are between 55 and 65 films.
    # Return the names of these categories and the number of films per
    # category, sorted by the number of films.
    con.execute("""select cat.name, count(fmcat.film_id)
    from category cat
    join film_category fmcat on
    cat.category_id = fmcat.category_id
    group by cat.name having count(fmcat.film_id) between 55 and 65
    """)
    result = con.fetchall()
    movie_category = []
    for category in result:
        name, count = category
        movie_category.append(name + ' ' + str(count))
    return render_template('index.html', shark=shark_count, names=all_names,
                           category=movie_category)


@app.route('/add', methods=['POST', 'GET'])
def add_film():
    """Route to add to film"""
    # Add 3 new films and put in measures to ensure that your application is
    # not susceptible to attacks such as SQL injection and CSRF.
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        year = request.form['year']
        language = int((request.form.get('language')))
        duration = request.form['duration']
        rate = request.form['rate']
        length = request.form['length']
        replacement = request.form['replacement_cost']
        rating = request.form['rating']
        data = (title, description, year, duration,
                language, rate, length, replacement, rating)
        print(data)
        insert_data = """INSERT INTO film (film_id, title, description,
                        release_year, language_id, rental_duration,
                        rental_rate, length, replacement_cost, rating) VALUES
                        (default, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        con.execute(insert_data, (title, description, year, duration,
                                  language, rate, length, replacement, rating,))
        db.commit()
        return redirect('/add')
    return render_template('film.html')


if __name__ == "__main__":
    app.run()
