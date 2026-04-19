from app.services.nlp_service import nlp_service


def test_news_ingest_and_sentiment_pipeline(client) -> None:
    ingest = client.post('/api/v1/news/ingest', json={'tickers': ['AAPL', 'TSLA'], 'limit_per_ticker': 2})
    assert ingest.status_code == 200
    assert len(ingest.json()) == 4

    sentiment = client.post(
        '/api/v1/sentiment/analyze',
        json={
            'ticker': 'AAPL',
            'source': 'news',
            'text': 'Apple beats estimates and posts strong services growth.',
        },
    )
    assert sentiment.status_code == 200
    body = sentiment.json()
    assert body['ticker'] == 'AAPL'
    assert 'label' in body
    assert 0 <= body['score'] <= 1

    aggregate = client.get('/api/v1/analytics/ticker/AAPL')
    assert aggregate.status_code == 200
    aggregation_body = aggregate.json()
    assert aggregation_body['ticker'] == 'AAPL'
    assert aggregation_body['article_count'] >= 1

    signal = client.get('/api/v1/signals/ticker/AAPL')
    assert signal.status_code == 200
    assert signal.json()['signal'] in {'BUY', 'SELL', 'HOLD'}


def test_sentiment_fallback_scoring() -> None:
    label, score = nlp_service._fallback_score('Company beats earnings and records strong growth')
    assert label == 'positive'
    assert score > 0.5
