import React, { useState } from 'react';
import './App.css';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const result = await axios.post(`${API_URL}/api/query`, {
        query: query
      });
      console.log('APIレスポンス:', result.data);
      setResponse(result.data);
    } catch (err) {
      console.error('APIエラー:', err);
      setError(err.response?.data?.detail || err.message || 'エラーが発生しました');
    } finally {
      setLoading(false);
    }
  };

  const exampleQueries = [
    '20代の顧客の平均注文金額を教えて',
    '最も人気のある商品トップ5は？',
    '東京都の顧客とその他の地域の顧客の平均年齢を比較して',
    '月別の売上推移を教えて',
    '性別ごとの平均注文金額を分析して'
  ];

  return (
    <div className="App">
      <div className="container">
        <header className="header">
          <h1>🍝 マーケティング分析AIエージェント</h1>
          <p>自然言語で質問して、データ分析結果を取得できます</p>
        </header>

        <form onSubmit={handleSubmit} className="query-form">
          <div className="input-group">
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="例: 20代の顧客の平均注文金額を教えて"
              rows="3"
              disabled={loading}
              className="query-input"
            />
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="submit-button"
            >
              {loading ? '分析中...' : '分析実行'}
            </button>
          </div>
        </form>

        <div className="examples">
          <h3>例文:</h3>
          <div className="example-buttons">
            {exampleQueries.map((example, idx) => (
              <button
                key={idx}
                onClick={() => setQuery(example)}
                disabled={loading}
                className="example-button"
              >
                {example}
              </button>
            ))}
          </div>
        </div>

        {error && (
          <div className="error-message">
            <h3>❌ エラー</h3>
            <p>{error}</p>
          </div>
        )}

        {response && (
          <div className="results">
            <div className="result-section">
              <h2>📊 分析結果</h2>
              <div className="summary-box">
                <h3>サマリー</h3>
                <div className="summary-content">
                  {response.summary && response.summary.trim() ? (
                    response.summary.split('\n').map((line, idx) => (
                      <p key={idx}>{line || '\u00A0'}</p>
                    ))
                  ) : (
                    <p>サマリーが生成されませんでした。結果データを参照してください。</p>
                  )}
                </div>
              </div>
            </div>

            {response.sql && (
              <div className="result-section">
                <h3>🔍 実行されたSQL</h3>
                <pre className="sql-code">{response.sql}</pre>
              </div>
            )}

            {response.result && response.result.length > 0 && (
              <div className="result-section">
                <h3>📋 データ結果 ({response.result.length}件)</h3>
                <div className="table-container">
                  <table className="data-table">
                    <thead>
                      <tr>
                        {Object.keys(response.result[0]).map((key) => (
                          <th key={key}>{key}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {response.result.map((row, idx) => (
                        <tr key={idx}>
                          {Object.values(row).map((value, cellIdx) => (
                            <td key={cellIdx}>
                              {value !== null && value !== undefined
                                ? String(value)
                                : '-'}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;


