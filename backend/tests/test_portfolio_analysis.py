"""
Tests für Portfolio-Analyse Endpoints
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json

# Importiere die App (muss nach Initialisierung der Router sein)
from main import app

client = TestClient(app)

# Mock-Daten
MOCK_ANALYSIS = {
    "fundamentalAnalysis": [
        {
            "ticker": "AAPL",
            "summary": "Apple zeigt solide Fundamentaldaten mit starkem Wachstum in Services.",
            "valuation": "fair"
        }
    ],
    "technicalAnalysis": [
        {
            "ticker": "AAPL",
            "trend": "aufwärts",
            "rsi": "55",
            "signal": "buy"
        }
    ],
    "risks": [
        "Klumpenrisiko: Hohe Konzentration auf Tech-Sektor (60%)",
        "Branchenübergewicht: Technologie dominiert Portfolio"
    ],
    "diversification": {
        "regionBreakdown": {"Nordamerika": 70.0, "Europa": 30.0},
        "sectorBreakdown": {"Technologie": 60.0, "Finanzen": 40.0},
        "positionWeights": {"AAPL": 40.0, "MSFT": 30.0, "GOOGL": 30.0}
    },
    "cashAssessment": "Cash-Anteil ist niedrig (5%). Empfehlung: Liquiditätsreserve aufbauen.",
    "suggestedRebalancing": "Reduzierung Tech-Anteil, Erhöhung Diversifikation in andere Sektoren",
    "shortTermAdvice": "Kurzfristig: Profit-Taking bei übergewichteten Positionen erwägen",
    "longTermAdvice": "Langfristig: Erweiterte Diversifikation über verschiedene Assetklassen"
}


@pytest.fixture
def auth_token():
    """Erstellt einen Test-User und gibt Token zurück"""
    # Registriere Test-User
    response = client.post(
        "/api/auth/register",
        json={
            "name": "Test User",
            "email": "test_analysis@example.com",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 201
    
    # Login
    response = client.post(
        "/api/auth/login-json",
        json={
            "email": "test_analysis@example.com",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def authenticated_client(auth_token):
    """Client mit Authentifizierung"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def portfolio_holdings(authenticated_client):
    """Erstellt Test-Portfolio-Positionen"""
    holdings = []
    
    # Erstelle Positionen
    for i, ticker in enumerate(["AAPL", "MSFT", "GOOGL"]):
        response = client.post(
            "/api/portfolio",
            headers=authenticated_client,
            json={
                "name": f"Test Stock {ticker}",
                "ticker": ticker,
                "isin": f"US000000{i:04d}",
                "purchase_date": "2024-01-15",
                "quantity": 10.0 + i,
                "purchase_price": "100.50"
            }
        )
        if response.status_code == 201:
            holdings.append(response.json())
    
    return holdings


class TestPortfolioAnalysis:
    """Test-Klasse für Portfolio-Analyse"""
    
    def test_analyze_portfolio_empty(self, authenticated_client):
        """Test: Analyse mit leerem Portfolio sollte fehlschlagen"""
        with patch('portfolio_analysis_routes.analyze_portfolio'):
            response = client.post(
                "/api/portfolio/analyze",
                headers=authenticated_client,
                json={}
            )
            assert response.status_code == 400
            assert "leer" in response.json()["detail"].lower()
    
    def test_analyze_portfolio_success(
        self, 
        authenticated_client, 
        portfolio_holdings
    ):
        """Test: Erfolgreiche Analyse"""
        with patch('portfolio_analysis_routes.analyze_portfolio') as mock_analyze:
            mock_analyze.return_value = MOCK_ANALYSIS
            
            response = client.post(
                "/api/portfolio/analyze",
                headers=authenticated_client,
                json={}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "fundamentalAnalysis" in data
            assert "technicalAnalysis" in data
            assert "risks" in data
            assert data["cached"] == False
    
    def test_analyze_portfolio_cached(
        self,
        authenticated_client,
        portfolio_holdings
    ):
        """Test: Cache-Funktionalität"""
        with patch('portfolio_analysis_routes.analyze_portfolio') as mock_analyze:
            mock_analyze.return_value = MOCK_ANALYSIS
            
            # Erste Analyse
            response1 = client.post(
                "/api/portfolio/analyze",
                headers=authenticated_client,
                json={}
            )
            assert response1.status_code == 200
            
            # Zweite Analyse (sollte aus Cache kommen)
            response2 = client.post(
                "/api/portfolio/analyze",
                headers=authenticated_client,
                json={"force_refresh": False}
            )
            assert response2.status_code == 200
            assert response2.json()["cached"] == True
    
    def test_analyze_portfolio_force_refresh(
        self,
        authenticated_client,
        portfolio_holdings
    ):
        """Test: Force Refresh ignoriert Cache"""
        with patch('portfolio_analysis_routes.analyze_portfolio') as mock_analyze:
            mock_analyze.return_value = MOCK_ANALYSIS
            
            # Erste Analyse
            client.post(
                "/api/portfolio/analyze",
                headers=authenticated_client,
                json={}
            )
            
            # Force Refresh
            response = client.post(
                "/api/portfolio/analyze",
                headers=authenticated_client,
                json={"force_refresh": True}
            )
            
            assert response.status_code == 200
            assert response.json()["cached"] == False
            assert mock_analyze.call_count == 2
    
    def test_clear_cache(self, authenticated_client):
        """Test: Cache löschen"""
        response = client.delete(
            "/api/portfolio/analyze/cache",
            headers=authenticated_client
        )
        assert response.status_code == 200
        assert "erfolgreich" in response.json()["message"].lower()
    
    def test_analyze_portfolio_rate_limit(
        self,
        authenticated_client,
        portfolio_holdings
    ):
        """Test: Rate Limiting"""
        with patch('portfolio_analysis_routes.analyze_portfolio') as mock_analyze:
            mock_analyze.return_value = MOCK_ANALYSIS
            
            # Sende viele Requests
            for i in range(12):  # Mehr als Limit (10)
                response = client.post(
                    "/api/portfolio/analyze",
                    headers=authenticated_client,
                    json={"force_refresh": True}
                )
                
                if i < 10:
                    assert response.status_code == 200
                else:
                    # Nach Limit sollte 429 zurückkommen
                    assert response.status_code == 429


class TestAnalysisValidation:
    """Tests für Validierung der Analyse-Daten"""
    
    def test_validate_analysis_structure(self):
        """Test: Validierung der Analyse-Struktur"""
        from services.openai_service import validate_and_normalize_analysis
        
        holdings = [
            {"ticker": "AAPL", "name": "Apple", "quantity": 10, "purchase_price": "100"}
        ]
        
        # Valide Analyse
        valid_analysis = {
            "fundamentalAnalysis": [{"ticker": "AAPL", "summary": "Test", "valuation": "fair"}],
            "technicalAnalysis": [{"ticker": "AAPL", "trend": "up", "rsi": "50", "signal": "hold"}],
            "risks": ["Test Risk"],
            "diversification": {
                "regionBreakdown": {},
                "sectorBreakdown": {},
                "positionWeights": {}
            },
            "cashAssessment": "Test",
            "suggestedRebalancing": "Test",
            "shortTermAdvice": "Test",
            "longTermAdvice": "Test"
        }
        
        result = validate_and_normalize_analysis(valid_analysis, holdings)
        assert result["fundamentalAnalysis"][0]["ticker"] == "AAPL"
        assert len(result["risks"]) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])



