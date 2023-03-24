create schema coloquios;

create table coloquios.participante (
    id INT PRIMARY KEY Generated Always as Identity,
    nome VARCHAR(70),
    dataNasc DATE,
    curso VARCHAR(50),
    cpf VARCHAR(11)
);

create table coloquios.apresentacao(
    id INT PRIMARY KEY Generated Always as Identity,
    titulo VARCHAR(100),
    dataCol DATE
);

create table coloquios.participacao(
    idPar INT,
    FOREIGN KEY (idPar) REFERENCES coloquios.participante(id),
    idCol INT,
    FOREIGN KEY (idCol) REFERENCES coloquios.apresentacao(id)
);

create table coloquios.palestrante(
    idPal INT,
    FOREIGN KEY (idPal) REFERENCES coloquios.participante(id),
    idCol INT,
    FOREIGN KEY (idCol) REFERENCES coloquios.participante(id)
);

