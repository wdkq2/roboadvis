from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import json

app = Flask(__name__)

# In-memory storage for demo purposes
scenarios = []
features = []

# Placeholder trade execution function
def execute_trade(action, symbol, amount):
    print(f"[MOCK TRADE] {action} {amount} of {symbol}")

# Placeholder news checker
def check_news_for_scenario(scenario):
    print(f"[MOCK NEWS CHECK] Searching news for: {scenario['keywords']}")
    # In a real implementation this would fetch news from an API
    return []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scenario', methods=['GET', 'POST'])
def scenario():
    if request.method == 'POST':
        symbol = request.form['symbol']
        scenario_text = request.form['scenario']
        amount = request.form['amount']
        keywords = request.form['keywords']
        scenario = {
            'symbol': symbol,
            'scenario': scenario_text,
            'amount': amount,
            'keywords': keywords,
            'created': datetime.now()
        }
        scenarios.append(scenario)
        execute_trade('BUY', symbol, amount)
        return redirect(url_for('scenario_result', idx=len(scenarios)-1))
    return render_template('scenario.html')

@app.route('/scenario/<int:idx>')
def scenario_result(idx):
    scenario = scenarios[idx]
    news = check_news_for_scenario(scenario)
    return render_template('scenario_result.html', scenario=scenario, news=news)

@app.route('/feature', methods=['GET', 'POST'])
def feature():
    if request.method == 'POST':
        query = request.form['query']
        # Placeholder for GPT understanding
        structured = {'query': query}
        features.append(structured)
        return redirect(url_for('feature_confirm', idx=len(features)-1))
    return render_template('feature.html')

@app.route('/feature/confirm/<int:idx>', methods=['GET', 'POST'])
def feature_confirm(idx):
    structured = features[idx]
    if request.method == 'POST':
        # Placeholder: assume user confirms and we fetch companies from DART
        companies = ['COMPANY_A', 'COMPANY_B', 'COMPANY_C']
        return render_template('feature_result.html', structured=structured, companies=companies)
    return render_template('feature_confirm.html', structured=structured)

if __name__ == '__main__':
    app.run(debug=True)
