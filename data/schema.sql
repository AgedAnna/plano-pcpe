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
