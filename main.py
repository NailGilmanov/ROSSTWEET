from flask import Flask, render_template

app = Flask(__name__)
app.config['SECRET_KEY'] = 'rosstweet_secret_key'


@app.route("/")
def index():
    return render_template("index.html")


def main():
    app.run()


if __name__ == '__main__':
    main()
