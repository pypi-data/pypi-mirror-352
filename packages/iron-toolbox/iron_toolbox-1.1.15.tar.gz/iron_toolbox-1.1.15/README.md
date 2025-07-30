# Iron Toolbox
### Utilização da Biblioteca
Para importar a biblioteca, basta usar a nomenclatura **iron_toolbox**.

### Atualização da Biblioteca
Todo commit no repositório vai publicar a atualização automaticamente no **PyPI.org**, por isso sempre que 
for commitar qualquer atualização é necessário modificar a versão no arquivo **setup.py** em 
**setuptools.setup (...version='0.0.00'...)**.

### Atualizar layer na AWS
Todo commit no repositório irá gerar um arquivo zip (**iron_toolbox-iron_toolbox-YYYY-MM-DD.zip.zip**), onde YYYY-MM-DD 
corresponde ao ANO-MES-DIA do commit. Este **.zip** será salvo num bucket do S3 no seguinte caminho 
**s3://iron-datalake-curated/LAMBDA_LAYERS/**.