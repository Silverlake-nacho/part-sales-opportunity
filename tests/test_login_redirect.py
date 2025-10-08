import sys
import urllib.parse
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app import app as flask_app, df


def test_login_redirects_back_to_original_query_and_runs_search():
    flask_app.config['TESTING'] = True
    client = flask_app.test_client()

    data_row = df.dropna(subset=['Model', 'IC Start Year', 'IC End Year']).iloc[0]
    model = str(data_row['Model']).strip()
    year = int(data_row['IC Start Year'])

    model_param = urllib.parse.quote_plus(model)
    search_path = f"/?Model={model_param}&Year={year}"

    with client:
        response = client.get(search_path, follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.headers['Location']
        assert 'next=' in response.headers['Location']

        login_response = client.post(
            '/login',
            data={
                'username': 'admin',
                'password': 'Silverlake1!',
                'next': search_path,
            },
            follow_redirects=False,
        )
        assert login_response.status_code == 302
        assert login_response.headers['Location'].endswith(search_path)

        final_response = client.get(login_response.headers['Location'])
        assert final_response.status_code == 200
        assert f"Top Parts for {model}" in final_response.get_data(as_text=True)
