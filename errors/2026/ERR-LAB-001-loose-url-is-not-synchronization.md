# ERR-LAB-001 — Loose URL Treated as Synchronization

Status: `RESOLVED`
Date: `2026-06-28`
Category: `continuity`

## Observed problem

Se asumió que pegar un enlace de GitHub equivalía a una fuente sincronizada y leída automáticamente.

## Correction

Usar Project Instructions para reglas críticas, archivos del Project para snapshots, GitHub conectado para estado vivo y este repositorio como fuente documental.

## Prevention

No declarar una URL como fuente automática sin verificar el mecanismo que la consulta.
