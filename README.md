# infra-backup-cleaner

Script em Python para **limpar backups antigos** de um diretório com base em **retenção (dias)**, com modo **dry-run** (simulação), logs e opção de varrer subpastas.

## Por que existe

Em ambientes de infra é comum backups acumularem e **encherem o disco**, causando falhas de backup e impacto na operação.  
Este script automatiza a limpeza por retenção com segurança mínima, protegendo contra remoção acidental em paths perigosos.

## Recursos

- Retenção configurável por dias (`--days`)
- Simulação sem apagar nada (`--dry-run`)
- Apaga de verdade apenas com `--force` (dupla proteção)
- Logs no console e opcionalmente em arquivo (`--log`)
- Varredura recursiva opcional (`--recursive`)
- Proteção contra paths perigosos (raiz, home, paths curtos)
- Resumo final com total de arquivos, tamanho e status

## Requisitos

- Python 3.10+ (funciona em 3.8+, mas recomendado 3.10+)
- Sem dependências externas (apenas stdlib)
- Linux/WSL recomendado (para uso com cron)

## Como rodar

### 1) Simular primeiro (recomendado)

```bash
python3 main.py --path /mnt/backup/servidores --days 30 --dry-run
```

Isso lista os arquivos que **seriam** removidos, sem apagar nada.

### 2) Simular com subpastas

```bash
python3 main.py --path /mnt/backup/servidores --days 30 --dry-run --recursive
```

### 3) Apagar de verdade

```bash
python3 main.py --path /mnt/backup/servidores --days 30 --force
```

Sem `--force`, o script lista os candidatos e pede que você confirme rodando novamente.

### 4) Com log em arquivo

```bash
python3 main.py --path /mnt/backup/servidores --days 30 --force --log logs/cleaner.log
```

## Agendamento via Cron

Para rodar automaticamente todos os dias às 03:00:

```bash
# Editar o crontab
crontab -e

# Adicionar a linha:
0 3 * * * /usr/bin/python3 /opt/infra-backup-cleaner/main.py --path /mnt/backup --days 30 --recursive --force --log /var/log/backup-cleaner.log
```

## Argumentos

| Argumento     | Obrigatório | Descrição                                   |
|---------------|-------------|---------------------------------------------|
| `--path`      | Sim         | Diretório dos backups                       |
| `--days`      | Sim         | Dias de retenção (arquivos mais velhos são removidos) |
| `--dry-run`   | Não         | Apenas simula, não apaga nada               |
| `--force`     | Não         | Necessário para apagar de verdade           |
| `--recursive` | Não         | Varre subpastas do diretório                |
| `--log`       | Não         | Caminho do arquivo de log                   |

## Exemplo de saída

```
2025-06-15 03:00:01 | INFO | Escaneando: /mnt/backup/servidores (retenção: 30 dias, recursivo: True)
2025-06-15 03:00:01 | INFO | Iniciando remoção de 12 arquivo(s)...
2025-06-15 03:00:01 | INFO | DELETED: /mnt/backup/servidores/web/bkp_2025-05-01.tar.gz (1.24 GB)
2025-06-15 03:00:02 | INFO | DELETED: /mnt/backup/servidores/web/bkp_2025-05-02.tar.gz (1.18 GB)
...
2025-06-15 03:00:05 | INFO | ============================================================
2025-06-15 03:00:05 | INFO | RESUMO — EXECUÇÃO
2025-06-15 03:00:05 | INFO |   Arquivos encontrados: 12
2025-06-15 03:00:05 | INFO |   Tamanho total:        14.52 GB
2025-06-15 03:00:05 | INFO |   Arquivos removidos:   12
2025-06-15 03:00:05 | INFO | ============================================================
```

## Segurança

O script bloqueia execução em paths considerados perigosos:

- `/` (raiz do sistema)
- `/home` e `/root`
- Home do usuário atual
- Qualquer path com menos de 3 níveis (ex: `/mnt`, `/var`)

Isso evita que um erro de digitação no `--path` cause danos irreversíveis.

## Códigos de retorno

| Código | Significado                                    |
|--------|------------------------------------------------|
| `0`    | Sucesso (ou nada a fazer)                      |
| `1`    | Falha parcial ou falta `--force`               |
| `2`    | Path inválido (não existe ou não é diretório)  |
| `3`    | Path bloqueado por segurança                   |

## Estrutura

```
infra-backup-cleaner/
├── main.py             # Script principal (entry point)
├── tests/
│   └── test_main.py    # Testes unitários
├── README.md
├── LICENSE
└── .gitignore
```

## Licença

MIT
