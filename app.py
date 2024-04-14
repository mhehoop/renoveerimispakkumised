from flask import Flask, request, render_template
from business_logic import make_proposal

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():  # put application's code here
    if request.method == 'POST':
        ehr_code = request.form['ehr_code']
        # Call the function that processes the code and returns the result
        proposal = make_proposal(ehr_code)
        return render_template('results.html', proposal_date=proposal['proposalDate'],
                           cost_items=proposal['costItems'], totalCostExclVAT=proposal['totalCostExclVAT'],
                           VAT=proposal['VAT'], totalCost=proposal['totalCost'])
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
