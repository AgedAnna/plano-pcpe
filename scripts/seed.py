"""Gera pcpe_agente.db — edital Agente PCPE 2026, recursos de estudo e plano de TAF."""
import sqlite3, os, urllib.parse, datetime as dt

DB = "pcpe_agente.db"
if os.path.exists(DB):
    os.remove(DB)
con = sqlite3.connect(DB)
cur = con.cursor()

cur.executescript("""
CREATE TABLE materias(
  id INTEGER PRIMARY KEY,
  nome TEXT NOT NULL,
  prova TEXT NOT NULL,            -- P1 Noções de Direito | P2 Conhecimentos Específicos | P3 Discursiva
  peso_estimado TEXT,             -- quanto costuma pesar (orientação, não oficial)
  ordem INTEGER
);
CREATE TABLE topicos(
  id INTEGER PRIMARY KEY,
  materia_id INTEGER NOT NULL REFERENCES materias(id),
  codigo TEXT,
  titulo TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pendente' CHECK(status IN ('pendente','estudando','revisar','dominado')),
  revisoes INTEGER NOT NULL DEFAULT 0,
  anotacao TEXT,
  atualizado_em TEXT
);
CREATE TABLE recursos(
  id INTEGER PRIMARY KEY,
  materia_id INTEGER REFERENCES materias(id),
  topico_id INTEGER REFERENCES topicos(id),
  tipo TEXT NOT NULL CHECK(tipo IN ('lei','video','pdf','questoes','prova_anterior','curso','info')),
  titulo TEXT NOT NULL,
  url TEXT NOT NULL,
  gratuito INTEGER NOT NULL DEFAULT 1,
  fonte TEXT
);
CREATE TABLE cronograma(
  id INTEGER PRIMARY KEY,
  data_inicio TEXT NOT NULL,
  data_fim TEXT,
  evento TEXT NOT NULL
);
CREATE TABLE sessoes_estudo(
  id INTEGER PRIMARY KEY,
  data TEXT NOT NULL,
  topico_id INTEGER REFERENCES topicos(id),
  minutos INTEGER,
  questoes INTEGER,
  acertos INTEGER,
  obs TEXT
);
CREATE TABLE taf_testes(
  id INTEGER PRIMARY KEY,
  teste TEXT NOT NULL,
  minimo_feminino TEXT NOT NULL,
  minimo_masculino TEXT NOT NULL,
  tentativas TEXT,
  regras TEXT
);
CREATE TABLE taf_fases(
  id INTEGER PRIMARY KEY,
  nome TEXT NOT NULL,
  semana_ini INTEGER, semana_fim INTEGER,
  data_ini TEXT, data_fim TEXT,
  objetivo TEXT
);
CREATE TABLE taf_treinos(
  id INTEGER PRIMARY KEY,
  fase_id INTEGER NOT NULL REFERENCES taf_fases(id),
  dia TEXT NOT NULL,
  foco TEXT NOT NULL,
  descricao TEXT NOT NULL,
  minutos INTEGER
);
CREATE TABLE taf_registros(
  id INTEGER PRIMARY KEY,
  data TEXT NOT NULL,
  teste_id INTEGER REFERENCES taf_testes(id),
  resultado REAL,
  unidade TEXT,
  obs TEXT
);
CREATE VIEW v_progresso_materia AS
SELECT m.id, m.nome, m.prova,
       COUNT(t.id) AS total,
       SUM(t.status='dominado') AS dominados,
       SUM(t.status IN ('estudando','revisar')) AS em_andamento,
       ROUND(100.0*SUM(t.status='dominado')/COUNT(t.id),1) AS pct
FROM materias m LEFT JOIN topicos t ON t.materia_id=m.id
GROUP BY m.id ORDER BY m.ordem;
""")

# ---------- MATÉRIAS E TÓPICOS (Edital nº 1 – PCPE, 2/10/2026, item 22.2.3) ----------
materias = [
 ("Legislação Estadual", "P1 Noções de Direito", "alto (cobrança literal)", [
  "Constituição do Estado de Pernambuco (arts. 101 a 105-B)",
  "Lei nº 6.425/1972 (Estatuto do Policial Civil)",
  "Lei nº 6.123/1968 (Estatuto do Servidor do Estado de PE)",
  "Lei Complementar nº 137/2008 (PCCV da Polícia Civil)",
  "Lei Complementar nº 317/2015 (Delegado de Polícia)",
 ]),
 ("Noções de Direito Constitucional", "P1 Noções de Direito", "alto", [
  "CF/88: princípios fundamentais",
  "Poderes constituintes originário, derivado e decorrente",
  "Aplicabilidade das normas constitucionais",
  "Direitos e garantias fundamentais",
  "Organização político-administrativa: União, estados, DF, municípios e territórios",
  "Administração pública: disposições gerais e servidores públicos",
  "Poder Executivo",
  "Poder Legislativo",
  "Poder Judiciário",
  "Funções essenciais à justiça: MP, Advocacia Pública, Defensoria",
  "Defesa do Estado e das instituições democráticas",
  "Segurança pública na Constituição do Estado de PE",
 ]),
 ("Noções de Direito Administrativo", "P1 Noções de Direito", "médio", [
  "Estado, governo e administração pública",
  "Direito administrativo: conceito e fontes",
  "Ato administrativo",
  "Poderes: hierárquico, disciplinar, regulamentar e de polícia; uso e abuso",
  "Regime jurídico-administrativo e princípios expressos/implícitos",
  "Responsabilidade civil do Estado",
  "Serviços públicos",
  "Organização administrativa: centralização, descentralização, direta e indireta",
  "Controle da administração (administrativo, judicial, legislativo)",
  "Improbidade administrativa (Lei 8.429/1992)",
  "Processo administrativo (Lei 9.784/1999)",
  "Licitações e contratos (Lei 14.133/2021)",
  "Agente público; cargo, emprego e função",
 ]),
 ("Noções de Direito Penal", "P1 Noções de Direito", "alto", [
  "Princípios básicos do direito penal",
  "Crime e contravenção penal",
  "Lei penal no tempo e no espaço; tempo e lugar do crime",
  "Lei excepcional, especial e temporária; territorialidade e extraterritorialidade",
  "Contagem de prazo; irretroatividade",
  "Crimes contra a pessoa",
  "Crimes contra o patrimônio",
  "Crimes contra a dignidade sexual",
  "Crimes contra a administração pública",
  "Crimes hediondos (Lei 8.072/1990)",
  "Preconceito de raça ou cor (Lei 7.716/1989)",
  "Abuso de autoridade (Lei 13.869/2019)",
  "Tortura (Lei 9.455/1997)",
  "ECA (Lei 8.069/1990)",
  "Organizações criminosas (Lei 12.850/2013)",
  "Crimes de trânsito (Lei 9.503/1997)",
  "Lei Maria da Penha (Lei 11.340/2006)",
  "Lei de Drogas (Lei 11.343/2006)",
  "Lei Henry Borel (Lei 14.344/2022)",
  "Crimes ambientais (Lei 9.605/1998)",
  "Estatuto do Desarmamento (Lei 10.826/2003)",
  "Disposições constitucionais aplicáveis ao direito penal",
 ]),
 ("Noções de Direito Processual Penal", "P1 Noções de Direito", "alto", [
  "Lei processual no tempo, no espaço e em relação às pessoas",
  "Inquérito policial",
  "Prova: corpo de delito, perícias, interrogatório, confissão, testemunhas",
  "Reconhecimento, acareação, documentos, indícios, busca e apreensão",
  "Prisão e liberdade provisória",
  "Medidas cautelares diversas da prisão",
  "Prisão temporária (Lei 7.960/1989)",
  "Juizados Especiais Criminais (Lei 9.099/1995)",
  "Investigação criminal pelo delegado (Lei 12.830/2013)",
  "Disposições constitucionais aplicáveis ao processo penal",
 ]),
 ("Língua Portuguesa", "P2 Conhecimentos Específicos", "alto", [
  "Compreensão e interpretação de textos",
  "Tipologia e gêneros textuais",
  "Ortografia oficial",
  "Coesão: referenciação, substituição, conectores",
  "Tempos e modos verbais",
  "Classes de palavras",
  "Coordenação e subordinação",
  "Pontuação",
  "Concordância verbal e nominal",
  "Regência verbal e nominal",
  "Crase",
  "Colocação pronominal",
  "Reescrita: significação, substituição e reorganização",
  "Redação oficial (Manual de Redação da Presidência da República)",
 ]),
 ("Informática", "P2 Conhecimentos Específicos", "médio — sua vantagem", [
  "Windows: janelas, menus, barra de tarefas, área de trabalho",
  "Windows: pastas e arquivos, Explorer, configurações",
  "Word (Microsoft 365): formatação, listas, tabelas, estilos, cabeçalho/rodapé",
  "Excel: fórmulas, referências, funções, formatação, classificação, gráficos",
  "PowerPoint: slides, modos de exibição, slide mestre, animações",
  "Redes: internet, intranet, nuvem, navegadores, deep/dark web",
  "Correio eletrônico",
  "Segurança: malware, antivírus, criptografia, acessos",
  "Backup e armazenamento em nuvem",
 ]),
 ("Raciocínio Lógico", "P2 Conhecimentos Específicos", "médio", [
  "Conjuntos numéricos e operações com conjuntos",
  "Sistema legal de medidas",
  "Razão, proporção, divisão proporcional, regra de três, porcentagem",
  "Equações e inequações de 1º e 2º graus; sistemas lineares",
  "Funções e gráficos",
  "Progressões aritmética e geométrica",
  "Lógica proposicional: proposições, tabelas-verdade, equivalências, De Morgan",
  "Diagramas lógicos e lógica de primeira ordem",
  "Lógica de argumentação",
  "Princípios de contagem e probabilidade",
  "Problemas aritméticos, geométricos e matriciais",
 ]),
 ("Contabilidade Geral", "P2 Conhecimentos Específicos", "médio — exclusiva de Agente", [
  "Conceitos, objetivos e finalidades",
  "Patrimônio e equação fundamental",
  "Atos e fatos administrativos (permutativos, modificativos, mistos)",
  "Contas e plano de contas",
  "Escrituração; regime de competência e de caixa",
  "Operações: juros, descontos, tributos, folha, compras, vendas, provisões, depreciação",
  "Balancete de verificação",
  "Balanço patrimonial",
  "DRE",
  "Normas Brasileiras de Contabilidade",
 ]),
 ("Estatística", "P2 Conhecimentos Específicos", "baixo/médio", [
  "Estatística descritiva: gráficos, tabelas, posição, dispersão, assimetria, curtose",
  "Probabilidade: axiomas, condicional, independência",
  "Amostragem: simples, estratificada, sistemática, conglomerados; tamanho amostral",
 ]),
 ("Redação — Segurança Pública", "P3 Discursiva", "30 pts (mín. 15)", [
  "Estrutura do texto dissertativo Cebraspe (até 30 linhas)",
  "Banco de temas atuais de segurança pública",
  "Treino de redações cronometradas (1 por semana)",
 ]),
]

topic_ids = {}
for ordem, (nome, prova, peso, tops) in enumerate(materias, 1):
    cur.execute("INSERT INTO materias(nome,prova,peso_estimado,ordem) VALUES(?,?,?,?)", (nome, prova, peso, ordem))
    mid = cur.lastrowid
    for i, t in enumerate(tops, 1):
        cur.execute("INSERT INTO topicos(materia_id,codigo,titulo) VALUES(?,?,?)", (mid, f"{ordem}.{i}", t))
        topic_ids[(nome, t)] = cur.lastrowid

def mid(nome):
    return cur.execute("SELECT id FROM materias WHERE nome=?", (nome,)).fetchone()[0]

def yt(q):
    return "https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(q)

# ---------- VÍDEO: uma busca no YouTube por tópico (sempre atualizada, nunca link morto) ----------
yt_ctx = {
 "Legislação Estadual": "PCPE",
 "Noções de Direito Constitucional": "direito constitucional Cebraspe",
 "Noções de Direito Administrativo": "direito administrativo Cebraspe",
 "Noções de Direito Penal": "direito penal concurso policial",
 "Noções de Direito Processual Penal": "processo penal concurso policial",
 "Língua Portuguesa": "português Cebraspe",
 "Informática": "informática Cebraspe",
 "Raciocínio Lógico": "raciocínio lógico Cebraspe",
 "Contabilidade Geral": "contabilidade geral concurso",
 "Estatística": "estatística concurso Cebraspe",
 "Redação — Segurança Pública": "redação discursiva Cebraspe segurança pública",
}
for (mnome, t), tid in topic_ids.items():
    cur.execute("INSERT INTO recursos(materia_id,topico_id,tipo,titulo,url,fonte) VALUES(?,?,?,?,?,?)",
                (mid(mnome), tid, "video", f"Videoaulas: {t}", yt(f"{t} {yt_ctx[mnome]} aula"), "Busca YouTube"))

# ---------- LEGISLAÇÃO OFICIAL ----------
P = "https://www.planalto.gov.br/ccivil_03/"
leis = [
 ("Legislação Estadual", "Constituição do Estado de Pernambuco (texto anotado)", "https://legis.alepe.pe.gov.br/texto.aspx?id=4937", "ALEPE"),
 ("Legislação Estadual", "Lei nº 6.425/1972 – Estatuto do Policial Civil", "https://legis.alepe.pe.gov.br/texto.aspx?id=11", "ALEPE"),
 ("Legislação Estadual", "Lei nº 6.123/1968 – Estatuto do Servidor de PE", "https://legis.alepe.pe.gov.br/texto.aspx?id=10727", "ALEPE"),
 ("Legislação Estadual", "LC nº 137/2008 – PCCV da Polícia Civil", "https://legis.alepe.pe.gov.br/texto.aspx?id=822", "ALEPE"),
 ("Legislação Estadual", "LC nº 317/2015 – Delegado de Polícia", "https://legis.alepe.pe.gov.br/texto.aspx?id=17817", "ALEPE"),
 ("Legislação Estadual", "EC 70/2026 – altera Segurança Pública na CE/PE (art. 101)", "https://legis.alepe.pe.gov.br/texto.aspx?id=88512", "ALEPE"),
 ("Noções de Direito Constitucional", "Constituição Federal de 1988", P+"constituicao/constituicao.htm", "Planalto"),
 ("Noções de Direito Administrativo", "Lei 8.429/1992 – Improbidade", P+"leis/l8429.htm", "Planalto"),
 ("Noções de Direito Administrativo", "Lei 9.784/1999 – Processo Administrativo", P+"leis/l9784.htm", "Planalto"),
 ("Noções de Direito Administrativo", "Lei 14.133/2021 – Licitações e Contratos", P+"_ato2019-2022/2021/lei/l14133.htm", "Planalto"),
 ("Noções de Direito Penal", "Código Penal (compilado)", P+"decreto-lei/del2848compilado.htm", "Planalto"),
 ("Noções de Direito Penal", "Lei 8.072/1990 – Crimes Hediondos", P+"leis/l8072.htm", "Planalto"),
 ("Noções de Direito Penal", "Lei 7.716/1989 – Preconceito de raça ou cor", P+"leis/l7716.htm", "Planalto"),
 ("Noções de Direito Penal", "Lei 13.869/2019 – Abuso de Autoridade", P+"_ato2019-2022/2019/lei/l13869.htm", "Planalto"),
 ("Noções de Direito Penal", "Lei 9.455/1997 – Tortura", P+"leis/l9455.htm", "Planalto"),
 ("Noções de Direito Penal", "Lei 8.069/1990 – ECA", P+"leis/l8069.htm", "Planalto"),
 ("Noções de Direito Penal", "Lei 12.850/2013 – Organizações Criminosas", P+"_ato2011-2014/2013/lei/l12850.htm", "Planalto"),
 ("Noções de Direito Penal", "Lei 9.503/1997 – Código de Trânsito", P+"leis/l9503compilado.htm", "Planalto"),
 ("Noções de Direito Penal", "Lei 11.340/2006 – Maria da Penha", P+"_ato2004-2006/2006/lei/l11340.htm", "Planalto"),
 ("Noções de Direito Penal", "Lei 11.343/2006 – Drogas", P+"_ato2004-2006/2006/lei/l11343.htm", "Planalto"),
 ("Noções de Direito Penal", "Lei 14.344/2022 – Henry Borel", P+"_ato2019-2022/2022/lei/l14344.htm", "Planalto"),
 ("Noções de Direito Penal", "Lei 9.605/1998 – Crimes Ambientais", P+"leis/l9605.htm", "Planalto"),
 ("Noções de Direito Penal", "Lei 10.826/2003 – Estatuto do Desarmamento", P+"leis/2003/l10.826.htm", "Planalto"),
 ("Noções de Direito Processual Penal", "Código de Processo Penal (compilado)", P+"decreto-lei/del3689compilado.htm", "Planalto"),
 ("Noções de Direito Processual Penal", "Lei 7.960/1989 – Prisão Temporária", P+"leis/l7960.htm", "Planalto"),
 ("Noções de Direito Processual Penal", "Lei 9.099/1995 – Juizados Especiais", P+"leis/l9099.htm", "Planalto"),
 ("Noções de Direito Processual Penal", "Lei 12.830/2013 – Investigação Criminal", P+"_ato2011-2014/2013/lei/l12830.htm", "Planalto"),
]
for m, titulo, url, fonte in leis:
    cur.execute("INSERT INTO recursos(materia_id,tipo,titulo,url,fonte) VALUES(?,?,?,?,?)", (mid(m), "lei", titulo, url, fonte))

# ---------- PDFs, QUESTÕES, PROVAS ANTERIORES, CURSOS ----------
outros = [
 ("Língua Portuguesa", "pdf", "Manual de Redação da Presidência da República (3ª ed., 2018)",
  "https://www4.planalto.gov.br/centrodeestudos/assuntos/manual-de-redacao-da-presidencia-da-republica/manual-de-redacao.pdf", 1, "Planalto"),
 ("Legislação Estadual", "questoes", "Questões – Estatuto do Policial Civil (Lei 6.425/72)",
  "https://qlegislacao.com.br/questoes/questoes_bloco.php?id=158405", 1, "QLegislação"),
 ("Legislação Estadual", "questoes", "Questões – LC 137/2008",
  "https://qlegislacao.com.br/questoes/questoes_bloco.php?id=172408", 1, "QLegislação"),
 ("Legislação Estadual", "questoes", "Questões – LC 317/2015",
  "https://qlegislacao.com.br/questoes/questoes_bloco.php?id=435484", 1, "QLegislação"),
 ("Legislação Estadual", "questoes", "Questões da PCPE (legislação dos órgãos)",
  "https://questoes.grancursosonline.com.br/questoes-de-concursos/legislacao-dos-orgaos-policia-civil-do-estado-de-pernambuco-pc-pe-400443", 1, "Gran Questões"),
 ("Legislação Estadual", "questoes", "Questões – Lei 6.123/1968",
  "https://questoes.grancursosonline.com.br/questoes-de-concursos/legislacao-estadual-distrital-e-municipal-estatuto-dos-funcionarios-publicos-do-estado-de-pernambuco-lei-no-6-123-1968-395075", 1, "Gran Questões"),
 ("Legislação Estadual", "pdf", "Resumo do Estatuto dos Servidores de PE (blog)",
  "https://www.estrategiaconcursos.com.br/blog/estatuto-servidores-pernambuco/", 1, "Estratégia"),
 ("Legislação Estadual", "prova_anterior", "Questões comentadas – Estatuto Policial Civil (prova PCPE 2024)",
  "https://www.estrategiaconcursos.com.br/blog/gabarito-pcpe-estatuto-dos-policiais-civis-de-pernambuco/", 1, "Estratégia"),
 (None, "prova_anterior", "Concurso PCPE 2023/24 (Cebraspe) – provas, gabaritos e editais",
  "https://www.cebraspe.org.br/concursos/pc_pe_23", 1, "Cebraspe"),
 (None, "prova_anterior", "Gabarito comentado PCPE 2024 – Agente (todas as matérias)",
  "https://www.estrategiaconcursos.com.br/blog/gabarito-extraoficial-pc-pe-agente/", 1, "Estratégia"),
 (None, "prova_anterior", "Matriz com justificativas – Conhecimentos Básicos PCPE 2024",
  "https://cdn.cebraspe.org.br/concursos/PC_PE_23/arquivos/MATRIZ_954PC_PECB1_00_COM_JUSTIFICATIVA.PDF", 1, "Cebraspe"),
 (None, "info", "Página oficial do concurso PCPE 2026 (Cebraspe)",
  "http://www.cebraspe.org.br/concursos/pc_pe_26", 1, "Cebraspe"),
 (None, "curso", "Direção Concursos – Agente e Escrivão PCPE (pago, tem aulas gratuitas no YouTube)",
  "https://www.direcaoconcursos.com.br/cursos/curso-para-agente-e-escrivao-da-policia-civil-de-pernambuco-pc-pe", 0, "Direção"),
 (None, "curso", "Gran – Agente PCPE pós-edital com orientação de TAF (pago)",
  "https://www.grancursosonline.com.br/cursos/por-concurso/pc-pe-policia-civil-do-estado-de-pernambuco-agente-de-policia-com-orientacao-para-o-taf", 0, "Gran"),
 (None, "video", "Aulões gratuitos PCPE 2026 (busca YouTube)", yt("PCPE 2026 agente aulão gratuito"), 1, "Busca YouTube"),
 (None, "video", "Revisão de véspera Cebraspe policial (busca YouTube)", yt("revisão de véspera polícia civil Cebraspe"), 1, "Busca YouTube"),
 ("Redação — Segurança Pública", "video", "Como fazer a discursiva do Cebraspe (busca YouTube)", yt("discursiva Cebraspe agente polícia civil como fazer"), 1, "Busca YouTube"),
]
for m, tipo, titulo, url, grat, fonte in outros:
    cur.execute("INSERT INTO recursos(materia_id,tipo,titulo,url,gratuito,fonte) VALUES(?,?,?,?,?,?)",
                (mid(m) if m else None, tipo, titulo, url, grat, fonte))

# ---------- CRONOGRAMA (Anexo I) ----------
crono = [
 ("2026-10-15","2026-11-12","Pedido de isenção da taxa"),
 ("2026-10-15","2026-12-16","Inscrições (Agente R$ 250, boleto)"),
 ("2026-12-15",None,"Resultado final da isenção"),
 ("2026-12-17","2026-12-18","Conferir/reenviar foto da inscrição"),
 ("2026-12-18",None,"Último dia para pagar o boleto"),
 ("2027-02-22",None,"Edital com consulta aos locais de prova"),
 ("2027-03-07",None,"PROVA objetiva + discursiva — Agente (tarde)"),
 ("2027-03-09",None,"Padrão preliminar da discursiva"),
 ("2027-03-10","2027-03-11","Recursos contra gabarito/discursiva"),
 ("2027-04-13",None,"Resultado final objetivas + provisório discursiva"),
 ("2027-05-19","2027-05-20","Envio de documentos da investigação social"),
 ("2027-05-19","2027-05-30","Envio dos exames médicos"),
 ("2027-05-21","2027-05-30","Exame clínico presencial"),
 ("2027-07-30","2027-08-11","TAF — prova de capacidade física"),
 ("2028-01-09",None,"Avaliação psicológica"),
]
cur.executemany("INSERT INTO cronograma(data_inicio,data_fim,evento) VALUES(?,?,?)", crono)

# ---------- TAF ----------
taf = [
 ("Barra estática", "15 s com queixo acima da barra", "3 flexões dinâmicas", "2 (intervalo ≥5 min)",
  "Sem luvas, sem apoiar o queixo, sem pedalar/chutar, pernas estendidas."),
 ("Impulsão horizontal", "1,35 m", "1,65 m", "2",
  "Pés paralelos, sem tocar a linha; mede até a marca mais próxima da linha (calcanhar)."),
 ("Natação 50 m", "até 80 s", "até 70 s", "2",
  "Piscina de 25 m, saída em pé da borda, qualquer estilo; pode tocar a borda e impulsionar na virada, sem parar."),
 ("Corrida 12 min", "1.800 m", "2.200 m", "1 (única)",
  "Pode alternar correr/caminhar; pista marcada de 10 em 10 m."),
]
cur.executemany("INSERT INTO taf_testes(teste,minimo_feminino,minimo_masculino,tentativas,regras) VALUES(?,?,?,?,?)", taf)

inicio = dt.date(2026, 10, 19)  # segunda-feira
def sem(n): return (inicio + dt.timedelta(weeks=n-1)).isoformat()
def semfim(n): return (inicio + dt.timedelta(weeks=n-1, days=6)).isoformat()

fases = [
 ("1 · Base", 1, 8, "Criar hábito sem roubar tempo de estudo: 3x/semana, ~35 min. Teste inicial na semana 1."),
 ("2 · Construção", 9, 20, "Até a prova (7/3): 3x/semana. Ganhar fôlego e força de pegada; aprender/ajustar o nado."),
 ("3 · Específica", 21, 34, "Pós-prova: 4–5x/semana. Treinar os 4 testes no formato do edital, simulado a cada 4 semanas."),
 ("4 · Polimento", 35, 41, "Manter, simular o TAF completo na ordem e reduzir volume na última semana."),
]
for nome, a, b, obj in fases:
    cur.execute("INSERT INTO taf_fases(nome,semana_ini,semana_fim,data_ini,data_fim,objetivo) VALUES(?,?,?,?,?,?)",
                (nome, a, b, sem(a), semfim(b), obj))

treinos = {
 1: [
  ("Seg","Corrida","Caminhada rápida 5 min + 8x (1 min trote / 2 min caminhada) + 5 min caminhada.",35),
  ("Qua","Força","Circuito em casa 3 voltas: 10 agachamentos, 8 flexões de joelho no chão, prancha 20 s, 10 afundos por perna. Pendurar na barra 3x 10–15 s (praça/academia ao ar livre).",30),
  ("Sex","Natação/técnica","Se tiver piscina: 20 min de adaptação (respiração, pernada com prancha). Sem piscina: 30 min caminhada + mobilidade.",30),
  ("Sáb","Teste (sem. 1 e 8)","Registrar: barra estática (s), impulsão (m), 12 min (m). Anotar na aba TAF.",20),
 ],
 2: [
  ("Seg","Corrida","Aquecer 5 min + 20–25 min contínuos em ritmo leve (conversando). Aumentar 2 min por semana.",35),
  ("Qua","Força + barra","3 voltas: 12 agachamentos com salto leve, 10 flexões, prancha 30 s, 12 elevações de quadril. Barra: subir com apoio (banco) e segurar no topo 4x máx. tempo; descer devagar 3x (negativa).",35),
  ("Sex","Natação","Aulas no Compaz (vagas abertas na última semana de cada mês, precisa comprovante de residência do Recife) ou piscina disponível: 10x 25 m crawl com 40 s de pausa.",40),
 ],
 3: [
  ("Seg","Corrida intervalada","Aquecer 10 min + 6–8x (400 m forte / 200 m caminhada). Meta do ritmo: 400 m em ≤2:40 (≈ 1.800 m em 12 min).",40),
  ("Ter","Natação","Aquecer 100 m + 6x 50 m (pausa 1 min) buscando ≤80 s; treinar a virada na borda.",40),
  ("Qua","Barra + impulsão","Barra estática 5x máx. (pausa 2 min). Impulsão: 6 séries de 3 saltos com braço, medir o melhor. Pliometria: 3x 8 saltos no caixote/degrau.",40),
  ("Sex","Corrida contínua","25–30 min em ritmo moderado ou 12 min no ritmo da prova + 10 min leve.",40),
  ("Sáb","Simulado (a cada 4 sem.)","Fazer os 4 testes na ordem do edital com 5 min entre eles. Registrar.",60),
 ],
 4: [
  ("Seg","Corrida","12 min no ritmo-alvo + educativos. Última semana: só 15 min leves.",30),
  ("Qua","Natação + barra","4x 50 m no ritmo de prova + barra estática 3x 20 s.",35),
  ("Sex","Impulsão + mobilidade","4 saltos de qualidade + alongamento/mobilidade. Última semana: descanso.",25),
  ("Sáb","Simulado completo","Semanas 35 e 38: TAF completo com atestado-modelo já providenciado (Anexo IV, ≤15 dias antes da prova real).",60),
 ],
}
for fase_id, lst in treinos.items():
    for d, foco, desc, mins in lst:
        cur.execute("INSERT INTO taf_treinos(fase_id,dia,foco,descricao,minutos) VALUES(?,?,?,?,?)", (fase_id, d, foco, desc, mins))

con.commit()
for row in cur.execute("SELECT (SELECT COUNT(*) FROM materias),(SELECT COUNT(*) FROM topicos),(SELECT COUNT(*) FROM recursos),(SELECT COUNT(*) FROM taf_treinos)"):
    print("materias, topicos, recursos, treinos:", row)
con.close()
