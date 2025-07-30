# **Documentation de MignonFinanceQuant**

![PyPI](https://img.shields.io/pypi/v/mignonfinancequant) 
![License](https://img.shields.io/github/license/Evilafo/mignonfinancequant) 

**MignonFinanceQuant** est une bibliothèque Python complète et modulaire pour les calculs de finance quantitative. Elle inclut des outils pour le pricing d'options, les métriques de risque, la gestion de portefeuille, les simulations stochastiques, et bien plus encore.

## Table des matières

1. [Installation](#installation)
2. [Modules et fonctionnalités](#modules-et-fonctionnalités)
   - [Options](#options)
   - [Métriques de risque](#métriques-de-risque)
   - [Gestion de portefeuille](#gestion-de-portefeuille)
   - [Backtesting](#backtesting)
   - [Mathématiques financières](#mathématiques-financières)
   - [Processus stochastiques](#processus-stochastiques)
   - [Simulations Monte Carlo](#simulations-monte-carlo)
3. [Exemples d'utilisation](#exemples-dutilisation)
4. [Contributions](#contributions)
5. [Licence](#licence)


## Installation

Installez la bibliothèque via `pip` :

```bash
pip install mignonfinancequant
```

Ou clonez le dépôt GitHub :

```bash
git clone https://github.com/Evilafo/mignonfinancequant.git
cd mignonfinancequant
pip install -r requirements.txt
```

Dépendances requises :
- `numpy`
- `scipy`
- `matplotlib`


## Modules et fonctionnalités

### Options

Le module `options.py` fournit des outils pour évaluer différents types d'options.

#### Prix d'une option européenne avec Black-Scholes
```python
from mignonfinancequant.options import black_scholes

price = black_scholes(S=100, K=100, T=1, r=0.05, sigma=0.2, option_type='call')
print(f"Prix de l'option : {price}")
```

#### Sensibilités (Greeks)
```python
from mignonfinancequant.options import greeks

greeks_values = greeks(S=100, K=100, T=1, r=0.05, sigma=0.2, option_type='call')
print(greeks_values)
```

#### Prix d'une option américaine (arbre binomial)
```python
from mignonfinancequant.options import american_option_binomial_tree

price = american_option_binomial_tree(S0=100, K=100, T=1, r=0.05, sigma=0.2, option_type='call', N=100)
print(f"Prix de l'option américaine : {price}")
```


### Métriques de risque

Le module `risk_metrics.py` inclut des fonctions pour calculer des métriques de risque essentielles.

#### Value at Risk (VaR)
```python
from mignonfinancequant.risk_metrics import calculate_var

returns = [-0.02, 0.01, -0.03, 0.02, 0.01]
var = calculate_var(returns, confidence_level=0.95)
print(f"Value at Risk (95%) : {var}")
```

#### Conditional Value at Risk (CVaR)
```python
from mignonfinancequant.risk_metrics import calculate_cvar

cvar = calculate_cvar(returns, confidence_level=0.95)
print(f"Conditional Value at Risk (95%) : {cvar}")
```

#### Ratio de Sharpe
```python
from mignonfinancequant.risk_metrics import sharpe_ratio

sharpe = sharpe_ratio(returns, risk_free_rate=0.0)
print(f"Ratio de Sharpe : {sharpe}")
```

#### Beta du marché
```python
from mignonfinancequant.risk_metrics import beta_market

portfolio_returns = [0.01, 0.02, -0.01]
market_returns = [0.015, 0.025, -0.005]
beta = beta_market(portfolio_returns, market_returns)
print(f"Bêta du marché : {beta}")
```


### Gestion de portefeuille

Le module `portfolio_management.py` permet de gérer un portefeuille d'actifs.

#### Ajouter et supprimer des positions
```python
from mignonfinancequant.portfolio_management import Portfolio

portfolio = Portfolio(initial_cash=100000)
portfolio.add_position(asset="AAPL", quantity=10, price=150)
value = portfolio.portfolio_value(prices={"AAPL": 155})
print(f"Valeur du portefeuille : {value}")
```


### Backtesting

Le module `backtesting.py` permet de tester des stratégies sur des données historiques.

#### Exécution d'un backtest
```python
from mignonfinancequant.backtesting import Backtester
from mignonfinancequant.portfolio_management import Portfolio

class SimpleStrategy:
    def execute(self, portfolio, prices):
        if prices["AAPL"] > 150:
            portfolio.add_position(asset="AAPL", quantity=1, price=prices["AAPL"])

portfolio = Portfolio(initial_cash=100000)
strategy = SimpleStrategy()
backtester = Backtester(portfolio, strategy)
backtester.run_backtest(data)
```


### Mathématiques financières

Le module `mathematics.py` inclut des fonctions mathématiques courantes en finance.

#### Volatilité historique
```python
from mignonfinancequant.mathematics import historical_volatility

returns = [0.01, 0.02, -0.01, 0.03]
volatility = historical_volatility(returns, annualized=True)
print(f"Volatilité historique : {volatility}")
```

#### Rendement ajusté au risque
```python
from mignonfinancequant.mathematics import adjusted_return

adjusted_ret = adjusted_return(returns, risk_free_rate=0.0)
print(f"Rendement ajusté au risque : {adjusted_ret}")
```


### Processus stochastiques

Le module `stochastic_processes.py` simule des processus stochastiques comme le mouvement brownien géométrique.

#### Mouvement brownien géométrique
```python
from mignonfinancequant.stochastic_processes import geometric_brownian_motion
import matplotlib.pyplot as plt

t, paths = geometric_brownian_motion(S0=100, mu=0.05, sigma=0.2, T=1, N=252)
plt.plot(t, paths.T)
plt.show()
```


### Simulations Monte Carlo

Le module `monte_carlo.py` effectue des simulations Monte Carlo pour évaluer des options.

#### Option européenne
```python
from mignonfinancequant.monte_carlo import monte_carlo_option_pricing

price = monte_carlo_option_pricing(S0=100, K=100, T=1, r=0.05, sigma=0.2, option_type='call')
print(f"Prix estimé de l'option européenne : {price}")
```

#### Option asiatique
```python
from mignonfinancequant.monte_carlo import asian_option_pricing

price = asian_option_pricing(S0=100, K=100, T=1, r=0.05, sigma=0.2, option_type='call')
print(f"Prix estimé de l'option asiatique : {price}")
```


## Exemples d'utilisation

Consultez le dossier `examples/` pour des scripts complets montrant comment utiliser chaque fonctionnalité.


## Contributions

Les contributions sont les bienvenues ! Si vous souhaitez contribuer :
1. Fork le dépôt.
2. Créez une branche pour vos modifications.
3. Soumettez une pull request avec une description claire.

Pour signaler des bugs ou demander des fonctionnalités, ouvrez une issue.


## Licence

Ce projet est sous licence MIT. Consultez le fichier [LICENSE](LICENSE) pour plus de détails.