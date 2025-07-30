
## Versão 0.0.7 - 2025-06-04

### Melhorias
- **Relacionamentos**: Permite que `record.relation_table` retorne uma lista dos itens da `relation_table` relacionados ao `record`.

## Versão 0.0.6 - 2025-05-07

### Novas Funcionalidades

- **Relacionamentos**: Adicionado suporte para chaves estrangeiras (foreign keys).

### Melhorias

- **`select`**: Habilitado para buscar um único registro com `.get` e `.filter` retorna todos que correspondem à condição.

### Correções de Bugs

## Versão 0.0.5 - 2025-05-02

### Novas Funcionalidades

### Melhorias

- **Retorno do Método `.update()`**: O método `.update()` agora retorna o registro atualizado como objeto da classe.
- **Retorno do Método `.delete()`**: O método `.delete()` agora retorna um valor booleano indicando se a exclusão foi bem-sucedida.

### Correções de Bugs

- **Migrações de Banco de Dados**: Corrigido um problema que impedia a aplicação de alterações no esquema do banco de dados na versão anterior.

## Version 0.0.3 - 2024-11-01

### New Features

- **ULID for PostgreSQL**: Added support for using ULID (Universally Unique Lexicographically Sortable Identifier) for PostgreSQL database connections.
- **Incremental ID for SQLite and PostgreSQL**: Introduced the use of incremental IDs for SQLite and PostgreSQL connections.
- **Automatic `created_at` Field**: Added automatic `created_at` as a default field for all models.

### Improvements

- **Database Connection Check**: Enhanced CRUD operations to include automatic checks for database connectivity before execution.

### Bug Fixes

- **Query Execution**: Fixed an issue where queries were not being executed on the correct database connection.

---

## Versão 0.0.4 - 2024-11-08

### Novas Funcionalidades

- **Table name**: Usar a nome da classe como nome da tabela.
- **Tabelas em plural**: criar tabelas em plural adicionando 's' no final do nome da classe.

### Melhorias

- \***\*tablename\*\***: Usar o atributo `__tablename__` como nome da tabela exatamente como fornecido.
- **Returnar o registro criado**: no método `.create()` returnar o registro criado como objecto da classe em causa.

### Correções de Bugs

---

# Changelog

## Versão 0.0.3 - 2024-11-01

### Novas Funcionalidades

- **ULID para PostgreSQL**: Adicionado suporte para usar ULID (Identificador Lexicograficamente Ordenável Universalmente Único) nas conexões com bancos de dados PostgreSQL.
- **ID Incremental para SQLite e PostgreSQL**: Introduzido o uso de IDs incrementais para conexões com bancos de dados SQLite e PostgreSQL.
- **Campo `created_at` Automático**: Adicionado o campo `created_at` como padrão para todos os modelos.

### Melhorias

- **Verificação de Conexão com o Banco de Dados**: Melhoradas as operações CRUD para incluir verificações automáticas de conectividade com o banco de dados antes da execução.

### Correções de Bugs

- **Execução de Consultas**: Corrigido um problema onde as consultas não estavam sendo executadas na conexão correta do banco de dados.
