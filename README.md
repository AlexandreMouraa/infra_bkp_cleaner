# infra-backup-cleaner

Script em Python para **limpar backups antigos** de um diretório com base em **retenção (dias)**, com modo **dry-run** (simulação), logs e opção de varrer subpastas.

## Por que existe
Em ambientes de infra é comum backups acumularem e **encherem o disco**, causando falhas de backup e impacto na operação.  
Este script automatiza a limpeza por retenção com segurança mínima.

## Recursos
- Define retenção por dias (`--days`)
- Simulação sem apagar nada (`--dry-run`)
- Apaga de verdade apenas com `--force`
- Logs no console e opcionalmente em arquivo (`--log`)
- Varredura recursiva opcional (`--recursive`)
- Proteção básica contra paths perigosos (ex: `/`, home)

## Requisitos
- Python 3.10+ (funciona em 3.8+, mas recomendado 3.10+)
- Linux/WSL recomendado (para uso com cron)

## Como rodar

### 1) Simular (recomendado primeiro)
```bash
python3 main.py --path /caminho/para/backups --days 30 --dry-run
