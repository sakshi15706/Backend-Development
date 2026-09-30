from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "backend server is running"

@app.route("/details")
def details():
    data = {
        "name": "Sakshi",
        "batch": "5",
        "sap": "590015706"
    }
    return f"<h1>Name = {data['name']}, Batch = {data['batch']}, SAP = {data['sap']}</h1>"

@app.route("/data")
def dataroute():
    data = {
        "name": "Sakshi",
        "batch": "5",
        "sap": "590015706"
    }
    return data

if __name__ == "__main__":
    app.run(debug=True)