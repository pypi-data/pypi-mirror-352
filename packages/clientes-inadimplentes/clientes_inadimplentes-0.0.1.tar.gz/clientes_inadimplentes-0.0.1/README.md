# package_name

Description. 
The package clientes_inadimplentes is used to:
	- clientes_inadimplentes
	
## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install package_name

```bash
pip install clientes_inadimplentes
```

## Usage

```
- O objetivo é identificar quem são os clientes inadimplentes e enviar essa lista de clientes para o setor de cobrança poder fazer a cobrança dos clientes.
- A função deve receber uma lista de clientes, analisar quais clientes estão inadimplentes, e retornar uma lista com os clientes inadimplentes (apenas o CPF deles)
- A inadimplência nessa empresa é calculada da seguinte forma:
	1. Se o cliente dever mais de 1.000 reais por mais de 20 dias, ele é considerado inadimplente.
	2. Isso significa que caso ou cliente esteja devendo 2.000 reais a 10 dias, ele não é inadimplente, pois não se passaram 20 dias ainda. Da mesma forma, se ele estiver devendo 500 reais por 40 dias, ele também não é inadimplente, dado que ele deve menos de 1.000 reais.
	3. As informações vêm no formato (cpf, valor_devido, qtde_de_dias)
```

```python
from clientes_inadimplentes import clientes_inadimplentes

clientes_devedores = [('462.286.561-65',14405,24),('251.569.170-81',16027,1),('297.681.579-21',8177,28),('790.223.154-40',9585,10),('810.442.219-10',18826,29),('419.210.299-79',11421,15),('908.507.760-43',12445,24),('911.238.364-17',1345,4),('131.115.339-28',11625,8),('204.169.467-27',5364,22),('470.806.376-11',932,29),('938.608.980-69',13809,19),('554.684.165-26',11227,2)]

inadimplentes = clientes_inadimplentes(clientes_devedores)
print(inadimplentes)
```

## Author
ArturJBraga

## License
[MIT](https://choosealicense.com/licenses/mit/)