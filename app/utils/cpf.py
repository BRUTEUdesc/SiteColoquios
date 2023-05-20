from app.extensions.database import get_db


def cpf_validate(cpf):
    cpf_list = list(cpf)
    cpf_list[3] = ''
    cpf_list[7] = ''
    cpf_list[11] = ''
    numbers = "".join(cpf_list)

    cpf = [int(char) for char in numbers if char.isdigit()]
    if len(cpf) != 11:
        return False
    if cpf == cpf[::-1]:
        return False
    for i in range(9, 11):
        value = sum((cpf[num] * ((i + 1) - num) for num in range(0, i)))
        digit = ((value * 10) % 11) % 10
        if digit != cpf[i]:
            return False
    return True


def cpf_search(cpf):
    con = get_db()
    with con.cursor() as cur:
        cur.execute('SELECT cpf FROM coloquios.pessoa WHERE cpf = %s;', (cpf,))
        con.commit()
        data_raw = cur.fetchone()
        return data_raw is not None


def cpf_search_palestrante(cpf, id):
    con = get_db()
    with con.cursor() as cur:
        cur.execute(
            'SELECT cpf FROM coloquios.pessoa pessoa '
            'JOIN coloquios.palestrante palestrante ON pessoa.id = palestrante.idpal '
            'WHERE pessoa.cpf = %s and palestrante.idcol = %s;',
            (cpf, id)
        )
        con.commit()
        data_raw = cur.fetchone()
        return data_raw is not None
