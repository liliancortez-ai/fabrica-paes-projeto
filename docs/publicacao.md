# Publicação no GitHub Pages

O arquivo `docs/index.html` é a versão do dashboard publicada pelo GitHub Pages. Crie um repositório público e envie os arquivos do projeto. Em **Settings → Pages**, escolha **Deploy from a branch**, branch `main`, pasta `/docs`, e salve. O link aparecerá nessa página.

O HTML contém uma fotografia dos dados; depois de alterar a base, atualize o dashboard e a cópia publicada:

```bash
PYTHONPATH=src python -m fabrica_paes.snapshot --db resultados/fabrica_paes.sqlite3 --output resultados/dashboard.html
cp resultados/dashboard.html docs/index.html
```

Envie as alterações ao GitHub para atualizar o site. O arquivo de banco SQLite é ignorado pelo Git e pode ser reconstruído com as instruções em `resultados/README.md`; os dados demonstrativos são versionados em CSV. O PDF original e a matrícula apresentada no painel ficam públicos se forem enviados a um repositório público.
